# -*- coding: utf-8 -*-

"""
app_blueprint.py
- 블루프린트 구조의 진입점입니다.
- 실행하려면: python app_blueprint.py
- templates/, static/, .env가 전부 이 파일과 같은 폴더(프로젝트 루트)에 있다고
  가정합니다. (admin/, auth/, board/, hospital/, reservation/, db.py도 마찬가지로
  전부 루트에 있어야 합니다)
"""

import os
import time
from flask import Flask, render_template, request, session, flash, redirect, url_for
from dotenv import load_dotenv


# 중요: 아래에서 blueprint(auth.routes 등)를 import하는 순간
# 그 안에서 db.py도 함께 불러오는데, db.py는 import되는 시점에
# 바로 os.environ["DB_HOST"] 등을 읽습니다.
# 그래서 load_dotenv()를 blueprint를 import하기 "전에" 반드시 먼저 실행해야 합니다.
# (순서가 바뀌면 .env 값을 아직 못 읽은 상태라 KeyError가 납니다)
load_dotenv()

from auth.routes import auth_bp
from hospital.routes import hospital_bp
from reservation.routes import reservation_bp
from board.routes import board_bp

from admin import admin_bp
import admin.dashboard_routes
import admin.user_routes
import admin.reservation_routes
import admin.board_routes
import admin.notice_routes
import admin.security_routes
import admin.department_routes
import admin.doctor_routes

from db import get_db_connection, get_client_ip, is_ip_blocked

# templates/, static/이 전부 이 파일과 같은 폴더에 있으므로
# 경로를 따로 지정할 필요 없이 Flask 기본 설정을 그대로 씁니다.
app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

# 각 담당자의 블루프린트를 등록.
# url_prefix를 따로 안 줬기 때문에, 라우트 경로(/login, /board 등)는 기존 app.py와 완전히 동일합니다.
app.register_blueprint(auth_bp)
app.register_blueprint(hospital_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(board_bp)
app.register_blueprint(admin_bp)


# 로그인 세션 무활동 제한시간
# 시연용: 3분 = 180초
SESSION_IDLE_TIMEOUT = 180


# =====================================================================
# 백민욱 담당 - 보안관제: 사이트 전체 차단
# ---------------------------------------------------------------------
# 모든 요청이 각 라우트에 도달하기 전에 실행됩니다.
# 차단된 IP면 blocked.html을 보여주고, 그 라우트의 원래 로직은 실행되지 않습니다.
# =====================================================================
@app.before_request
def check_site_wide_ip_block():
    if request.path.startswith("/static/"):
        return None

    client_ip = get_client_ip(request)

    if is_ip_blocked(client_ip, "site"):
        return render_template("blocked.html", client_ip=client_ip), 403

    # -----------------------------------------------------
    # 로그인된 사용자의 3분 무활동 세션 제한
    # -----------------------------------------------------
    if "user_id" in session:
        now = time.time()
        last_activity = session.get("last_activity")

        # 마지막 활동 후 3분이 지났으면 자동 로그아웃
        if last_activity is not None:
            if now - last_activity >= SESSION_IDLE_TIMEOUT:
                session.clear()
                flash("3분 동안 활동이 없어 자동 로그아웃되었습니다.")
                return redirect(url_for("auth.login"))

        # 로그인 차단 IP라면 기존 세션은 즉시 종료하지 않지만
        # 활동시간을 갱신하지 않음
        if is_ip_blocked(client_ip, "login"):
            if last_activity is None:
                session["last_activity"] = now

            return None

        # 정상 접속 IP라면 활동할 때마다 세션 시간 갱신
        session["last_activity"] = now

    return None


# 메인 페이지는 특정 담당자 블루프린트가 아니라 공통이라 여기 그대로 둠
@app.route("/")
def index():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notice ORDER BY created_at DESC LIMIT 5")
        notices = cur.fetchall()
        cur.execute("SELECT * FROM board ORDER BY created_at DESC LIMIT 5")
        latest_posts = cur.fetchall()
    conn.close()
    return render_template("index.html", notices=notices, latest_posts=latest_posts)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)