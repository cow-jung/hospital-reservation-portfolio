# -*- coding: utf-8 -*-
"""
병원예약시스템 app.py
- 병원예약시스템_폴더구조및라우트설계서.md 의 Route(URL) 설계를 기준으로 작성
- 담당자별 기능상세설계서(1~5) 내용을 반영
- DB: MySQL (병원예약시스템_DB설계서.md 스키마 기준, schema.sql 참고)

[다른 팀원들을 위한 안내]
- 이 파일 하나에 모든 라우트(페이지 주소)가 담당자 구역별로 나뉘어 있습니다.
- 본인이 담당한 기능 부분의 주석("00 담당" 표시)만 봐도 이해할 수 있도록
  각 함수마다 어떤 SQL을 실행하는지, 어떤 값을 템플릿(html)로 넘기는지 설명을 달았습니다.
- 템플릿(html)에서 데이터를 쓸 때는 render_template()에 넘겨준 변수 이름
  그대로 Jinja 문법({% for %}, {{ }})으로 꺼내 쓰면 됩니다.
"""

import os
# os : .env에서 읽어온 값을 os.environ으로 꺼내 쓰기 위한 파이썬 기본 라이브러리.
from dotenv import load_dotenv
# load_dotenv : 같은 폴더의 .env 파일을 읽어서 환경변수로 등록해주는 함수.
# (.env는 git에 올라가지 않으므로, 비밀번호 같은 값을 코드에서 분리할 수 있음)
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
# pymysql: 파이썬에서 MySQL에 접속해서 쿼리를 실행하는 라이브러리.
# mysql.connector와 하는 일은 완전히 같고, 문법도 거의 비슷합니다.
from werkzeug.security import generate_password_hash, check_password_hash
# generate_password_hash : 비밀번호를 암호화(해시)해서 DB에 저장하기 위한 함수
# check_password_hash    : 로그인 시, 입력한 비밀번호와 DB의 암호화 값을 비교하는 함수
# → 회원가입/로그인 담당자는 이 두 함수를 어디서 호출하는지만 알면 됩니다.
from functools import wraps
# wraps : 아래 login_required / admin_required 데코레이터를 만들 때 쓰는 파이썬 기본 기능.
# "로그인 안 했으면 로그인 페이지로 보내기"를 함수마다 반복해서 안 쓰려고 만든 것.

load_dotenv()  # 이 줄이 .env 파일을 읽어서 os.environ에 등록해줌 (다른 코드보다 먼저 실행되어야 함)

# app.py가 legacy/ 폴더 안으로 옮겨졌으므로,
# 한 단계 위(프로젝트 최상위)에 있는 legacy_templates/, legacy_static/ 폴더를 그대로 바라보도록 경로를 지정합니다.
app = Flask(
    __name__,
    template_folder="../legacy_templates",
    static_folder="../legacy_static",
)
app.secret_key = os.environ["SECRET_KEY"]
# secret_key는 로그인 상태(session)를 안전하게 유지하기 위해 Flask가 내부적으로 사용하는 값.
# 코드에 직접 적지 않고 .env의 SECRET_KEY 값을 가져와서 씀.

# -----------------------------
# MySQL 접속 설정
# -----------------------------
# 예전에는 이 자리에 host/user/password를 직접 적었지만,
# 그러면 이 파일을 GitHub에 올릴 때 비밀번호가 그대로 공개됨.
# 그래서 .env 파일에 값을 적어두고, 여기서는 os.environ["키이름"]으로 불러오기만 함.
DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"],
    "charset": "utf8mb4",      # 한글 깨짐 방지용 문자셋 (이 값은 비밀번호가 아니라서 그대로 둬도 됨)
    "cursorclass": pymysql.cursors.DictCursor,
    # DictCursor로 설정하면 조회 결과를 row["컬럼명"] 형태로 꺼낼 수 있습니다.
    # (mysql.connector의 cursor(dictionary=True)와 같은 역할)
}


def get_db_connection():
    """라우트 함수마다 이 함수를 호출해서 새로운 DB 연결을 하나씩 받아 씁니다."""
    return pymysql.connect(**DB_CONFIG)


# -----------------------------
# 로그인 / 권한 체크 데코레이터
# -----------------------------
# 아래 두 함수는 "로그인이 필요한 페이지" / "관리자만 들어갈 수 있는 페이지" 를
# 매번 if문으로 체크하지 않고, 함수 위에 @login_required 처럼 한 줄만 붙이면
# 자동으로 체크되도록 만든 것입니다. (동작 결과는 함수 안에서 직접 if문을 쓰는 것과 동일)
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            # 로그인 시 session["user_id"]를 저장해두기 때문에,
            # 이 값이 없다는 건 로그인을 안 했다는 뜻입니다.
            flash("로그인이 필요합니다.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            # users 테이블의 role 컬럼이 'admin'인 회원만 통과
            flash("관리자만 접근할 수 있습니다.")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped


# =====================================================================
# 공통 - 메인 (담당자 미지정)
# =====================================================================
@app.route("/")
def index():
    """
    메인 페이지.
    공지사항 최신 5개, 게시판 최신 글 5개를 뽑아서 index.html로 넘겨줍니다.
    index.html에서는 {% for n in notices %} 형태로 반복해서 출력하면 됩니다.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notice ORDER BY created_at DESC LIMIT 5")
        notices = cur.fetchall()
        cur.execute("SELECT * FROM board ORDER BY created_at DESC LIMIT 5")
        latest_posts = cur.fetchall()
    conn.close()
    return render_template("index.html", notices=notices, latest_posts=latest_posts)


# =====================================================================
# 백민욱 담당 - 로그인 / 로그아웃 / 회원가입
# =====================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  : login.html 화면을 보여줌
    POST : login.html의 <form>에서 아이디/비밀번호를 입력해 제출했을 때 실행됨
    """
    if request.method == "POST":
        # request.form["필드명"] 은 <input name="필드명"> 으로 보낸 값을 받는 부분.
        # 즉 login.html의 input name과 아래 이름이 반드시 같아야 함.
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        with conn.cursor() as cur:
            # 아이디로 회원을 조회. 이 시점의 user["password"]는 암호화된 값임.
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
        conn.close()

        # check_password_hash(DB에 저장된 암호화 값, 사용자가 입력한 평문 비밀번호)
        # → 두 값이 같은 원본에서 나온 게 맞으면 True를 돌려줌.
        if user and check_password_hash(user["password"], password):
            # 로그인 성공 시 session에 정보를 저장해서, 이후 다른 페이지에서
            # "로그인 되어 있음"을 계속 알 수 있게 함.
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect(url_for("index"))
        else:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.")
            return redirect(url_for("login"))

    # GET 요청이면 그냥 로그인 폼 화면만 보여줌
    return render_template("login.html")


@app.route("/logout")
def logout():
    """session을 전부 비워서 로그인 상태를 해제함."""
    session.clear()
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    GET  : signup.html 화면을 보여줌
    POST : signup.html의 <form> 제출을 처리함
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]
        name = request.form["name"]
        phone = request.form.get("phone")   # .get()은 값이 없어도 에러 안 나고 None 반환
        email = request.form.get("email")

        if password != password_confirm:
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for("signup"))

        # 비밀번호를 암호화해서 hashed_pw에 담고, DB에는 이 값을 저장함.
        # (원본 password 문자열은 DB에 절대 저장하지 않음)
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO users (username, password, name, phone, email, role)
                   VALUES (%s, %s, %s, %s, %s, 'user')""",
                (username, hashed_pw, name, phone, email),
            )
        conn.commit()  # INSERT/UPDATE/DELETE 후에는 반드시 commit() 필요
        conn.close()

        flash("회원가입이 완료되었습니다. 로그인해주세요.")
        return redirect(url_for("login"))

    return render_template("signup.html")


# =====================================================================
# 임주혁 담당 - 병원소개 / 진료과·의료진 조회
# =====================================================================
@app.route("/hospital")
def hospital():
    """DB 조회 없이 정적인 병원 소개 화면만 보여줌."""
    return render_template("hospital.html")


@app.route("/department")
def department():
    """진료과 전체 목록을 조회해서 department.html로 넘겨줌."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM departments")
        departments = cur.fetchall()
    conn.close()
    return render_template("department.html", departments=departments)


@app.route("/doctor")
def doctor():
    """
    의료진 조회.
    department.html에서 진료과를 클릭하면 /doctor?dept_id=1 처럼 넘어온다고 가정.
    dept_id가 있으면 해당 진료과 의료진만, 없으면 전체 의료진을 보여줌.
    """
    dept_id = request.args.get("dept_id")  # 쿼리스트링(?dept_id=1)에서 값 꺼내기
    conn = get_db_connection()
    with conn.cursor() as cur:
        if dept_id:
            cur.execute(
                """SELECT d.*, dept.dept_name FROM doctors d
                   JOIN departments dept ON d.dept_id = dept.dept_id
                   WHERE d.dept_id = %s""",
                (dept_id,),
            )
        else:
            cur.execute(
                """SELECT d.*, dept.dept_name FROM doctors d
                   JOIN departments dept ON d.dept_id = dept.dept_id"""
            )
        doctors = cur.fetchall()
    conn.close()
    return render_template("doctor.html", doctors=doctors)


# =====================================================================
# 유민정 담당 - 예약하기(신규 / 과거이력) / 마이페이지
# =====================================================================
@app.route("/reservation", methods=["GET", "POST"])
@login_required  # 로그인 안 하면 이 페이지에 못 들어옴 (자동으로 /login으로 이동)
def reservation():
    """
    GET  : 의료진 목록 + 본인의 과거 예약 이력을 함께 보여줌
           → reservation.html에서 "신규 예약" 탭은 doctors를 사용하고,
             "과거이력으로 예약" 탭은 history를 사용해서 만들면 됨.
    POST : 예약 신청 처리 (신규 예약이든 과거이력을 선택한 예약이든
           최종적으로는 진료과/의료진/날짜/시간을 받아서 INSERT하는 흐름은 동일함)
    """
    conn = get_db_connection()

    if request.method == "POST":
        doctor_id = request.form["doctor_id"]
        reservation_date = request.form["reservation_date"]
        reservation_time = request.form["reservation_time"]
        memo = request.form.get("memo", "")

        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO reservations
                   (user_id, doctor_id, reservation_date, reservation_time, memo, status)
                   VALUES (%s, %s, %s, %s, %s, '대기')""",
                (session["user_id"], doctor_id, reservation_date, reservation_time, memo),
            )
        conn.commit()
        conn.close()
        flash("예약이 신청되었습니다.")
        return redirect(url_for("mypage_reservation"))

    with conn.cursor() as cur:
        # 신규 예약용 - 전체 의료진 목록
        cur.execute("SELECT * FROM doctors")
        doctors = cur.fetchall()

        # 과거이력으로 예약용 - 로그인한 본인의 예약 이력만 조회
        cur.execute(
            """SELECT r.*, doc.doctor_name, dept.dept_name FROM reservations r
               JOIN doctors doc ON r.doctor_id = doc.doctor_id
               JOIN departments dept ON doc.dept_id = dept.dept_id
               WHERE r.user_id = %s ORDER BY r.created_at DESC""",
            (session["user_id"],),
        )
        history = cur.fetchall()
    conn.close()
    return render_template("reservation.html", doctors=doctors, history=history)


@app.route("/mypage", methods=["GET", "POST"])
@login_required
def mypage():
    """
    마이페이지 - 내 정보 수정 / 진료조회 / 회원 탈퇴
    request.form["action"] 값으로 어떤 버튼을 눌렀는지 구분해서 처리함.
    (mypage.html에서 <input type="hidden" name="action" value="update"> 처럼
     폼마다 action 값을 다르게 넣어주면 됨)
    """
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update":
            # 내 정보 수정
            name = request.form["name"]
            phone = request.form.get("phone")
            email = request.form.get("email")
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET name=%s, phone=%s, email=%s WHERE user_id=%s",
                    (name, phone, email, session["user_id"]),
                )
            conn.commit()
            flash("회원 정보가 수정되었습니다.")

        elif action == "withdraw":
            # 회원 탈퇴 - users에서 삭제하면 reservations, board 등도
            # schema.sql에 ON DELETE CASCADE로 설정되어 있어 함께 정리됨
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE user_id=%s", (session["user_id"],))
            conn.commit()
            conn.close()
            session.clear()  # 탈퇴했으니 로그인 상태도 해제
            flash("회원 탈퇴가 완료되었습니다.")
            return redirect(url_for("index"))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_id=%s", (session["user_id"],))
        user = cur.fetchone()
        # 진료조회: 지금까지의 예약(진료) 이력 전체
        cur.execute(
            """SELECT r.*, doc.doctor_name, dept.dept_name FROM reservations r
               JOIN doctors doc ON r.doctor_id = doc.doctor_id
               JOIN departments dept ON doc.dept_id = dept.dept_id
               WHERE r.user_id=%s ORDER BY r.reservation_date DESC""",
            (session["user_id"],),
        )
        treatment_history = cur.fetchall()
    conn.close()
    return render_template("mypage.html", user=user, treatment_history=treatment_history)


@app.route("/mypage/reservation", methods=["GET", "POST"])
@login_required
def mypage_reservation():
    """예약 조회 / 수정 / 삭제(취소) 전용 페이지."""
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        reservation_id = request.form.get("reservation_id")

        with conn.cursor() as cur:
            if action == "update":
                new_date = request.form["reservation_date"]
                new_time = request.form["reservation_time"]
                # AND user_id=%s 를 꼭 넣어서, 본인 예약만 수정 가능하도록 함
                cur.execute(
                    """UPDATE reservations SET reservation_date=%s, reservation_time=%s
                       WHERE reservation_id=%s AND user_id=%s""",
                    (new_date, new_time, reservation_id, session["user_id"]),
                )
                flash("예약이 수정되었습니다.")
            elif action == "cancel":
                # 실제로 행을 삭제하지 않고 상태만 '취소'로 바꿔서 이력은 남겨둠
                cur.execute(
                    "UPDATE reservations SET status='취소' WHERE reservation_id=%s AND user_id=%s",
                    (reservation_id, session["user_id"]),
                )
                flash("예약이 취소되었습니다.")
        conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            """SELECT r.*, doc.doctor_name, dept.dept_name FROM reservations r
               JOIN doctors doc ON r.doctor_id = doc.doctor_id
               JOIN departments dept ON doc.dept_id = dept.dept_id
               WHERE r.user_id=%s ORDER BY r.reservation_date DESC""",
            (session["user_id"],),
        )
        reservations = cur.fetchall()
    conn.close()
    return render_template("reservation_list.html", reservations=reservations)


# =====================================================================
# 정고은 담당 - 문의 게시판 / 공지사항
# =====================================================================
@app.route("/board")
def board():
    """게시글 목록. 작성자 이름을 같이 보여주기 위해 users와 JOIN."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT b.*, u.name FROM board b
               JOIN users u ON b.user_id = u.user_id
               ORDER BY b.created_at DESC"""
        )
        posts = cur.fetchall()
    conn.close()
    return render_template("board.html", posts=posts)


@app.route("/board/write", methods=["GET", "POST"])
@login_required
def board_write():
    """게시글 작성. 로그인한 사람만 글을 쓸 수 있어야 하므로 @login_required."""
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO board (user_id, title, content) VALUES (%s, %s, %s)",
                (session["user_id"], title, content),
            )
        conn.commit()
        conn.close()
        return redirect(url_for("board"))

    return render_template("board_write.html")


@app.route("/board/view/<int:board_id>", methods=["GET", "POST"])
def board_view(board_id):
    """
    게시글 상세 조회 + 댓글.
    URL 안의 <int:board_id> 부분이 실제 접속 시에는 /board/view/3 처럼
    숫자로 들어오고, 그 값이 이 함수의 board_id 매개변수로 전달됨.
    """
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "comment" and "user_id" in session:
            # 댓글 작성 (로그인한 사람만)
            content = request.form["content"]
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO board_comments (board_id, user_id, content) VALUES (%s, %s, %s)",
                    (board_id, session["user_id"], content),
                )
            conn.commit()

        elif action == "delete":
            # 게시글 삭제 (본인 글만 삭제되도록 user_id 조건 포함)
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM board WHERE board_id=%s AND user_id=%s",
                    (board_id, session.get("user_id")),
                )
            conn.commit()
            conn.close()
            return redirect(url_for("board"))

    with conn.cursor() as cur:
        # 이 게시글을 열람할 때마다 조회수 +1
        cur.execute("UPDATE board SET view_count = view_count + 1 WHERE board_id=%s", (board_id,))
        conn.commit()

        cur.execute(
            """SELECT b.*, u.name FROM board b
               JOIN users u ON b.user_id = u.user_id
               WHERE b.board_id=%s""",
            (board_id,),
        )
        post = cur.fetchone()

        cur.execute(
            """SELECT c.*, u.name FROM board_comments c
               JOIN users u ON c.user_id = u.user_id
               WHERE c.board_id=%s ORDER BY c.created_at ASC""",
            (board_id,),
        )
        comments = cur.fetchall()
    conn.close()
    return render_template("board_view.html", post=post, comments=comments)


@app.route("/notice")
def notice():
    """공지사항 목록"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notice ORDER BY created_at DESC")
        notices = cur.fetchall()
    conn.close()
    return render_template("notice.html", notices=notices)


@app.route("/notice/view/<int:notice_id>")
def notice_view(notice_id):
    """공지사항 상세 - 열람할 때마다 조회수 +1"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE notice SET view_count = view_count + 1 WHERE notice_id=%s", (notice_id,))
        conn.commit()
        cur.execute("SELECT * FROM notice WHERE notice_id=%s", (notice_id,))
        notice_item = cur.fetchone()
    conn.close()
    return render_template("notice_view.html", notice=notice_item)


# =====================================================================
# 관리자 메인 (담당자 미지정)
# =====================================================================
@app.route("/admin")
@admin_required  # role이 'admin'인 사람만 들어올 수 있음
def admin():
    return render_template("admin.html")


# =====================================================================
# 임주혁 담당 - 관리자: 진료과 관리 / 의료진 관리
# =====================================================================
@app.route("/admin/department", methods=["GET", "POST"])
@admin_required
def admin_department():
    """
    진료과 등록/수정/삭제를 한 페이지에서 처리.
    admin_department.html의 각 폼(등록 폼, 수정 폼, 삭제 버튼)에
    <input type="hidden" name="action" value="create/update/delete"> 를 넣어서
    어떤 동작인지 구분함.
    """
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "create":
                cur.execute(
                    "INSERT INTO departments (dept_name, dept_description, dept_image) VALUES (%s, %s, %s)",
                    (request.form["dept_name"], request.form.get("dept_description"), request.form.get("dept_image")),
                )
            elif action == "update":
                cur.execute(
                    """UPDATE departments SET dept_name=%s, dept_description=%s, dept_image=%s
                       WHERE dept_id=%s""",
                    (
                        request.form["dept_name"],
                        request.form.get("dept_description"),
                        request.form.get("dept_image"),
                        request.form["dept_id"],
                    ),
                )
            elif action == "delete":
                cur.execute("DELETE FROM departments WHERE dept_id=%s", (request.form["dept_id"],))
        conn.commit()

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM departments")
        departments = cur.fetchall()
    conn.close()
    return render_template("admin_department.html", departments=departments)


@app.route("/admin/doctor", methods=["GET", "POST"])
@admin_required
def admin_doctor():
    """의료진 등록/수정/삭제. 위 admin_department()와 구조가 동일함."""
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "create":
                cur.execute(
                    """INSERT INTO doctors (dept_id, doctor_name, specialty, profile, photo, work_hours)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        request.form["dept_id"],
                        request.form["doctor_name"],
                        request.form.get("specialty"),
                        request.form.get("profile"),
                        request.form.get("photo"),
                        request.form.get("work_hours"),
                    ),
                )
            elif action == "update":
                cur.execute(
                    """UPDATE doctors SET dept_id=%s, doctor_name=%s, specialty=%s,
                       profile=%s, photo=%s, work_hours=%s WHERE doctor_id=%s""",
                    (
                        request.form["dept_id"],
                        request.form["doctor_name"],
                        request.form.get("specialty"),
                        request.form.get("profile"),
                        request.form.get("photo"),
                        request.form.get("work_hours"),
                        request.form["doctor_id"],
                    ),
                )
            elif action == "delete":
                cur.execute("DELETE FROM doctors WHERE doctor_id=%s", (request.form["doctor_id"],))
        conn.commit()

    with conn.cursor() as cur:
        # 목록에 소속 진료과 이름도 같이 보여주기 위해 JOIN
        cur.execute(
            """SELECT d.*, dept.dept_name FROM doctors d
               JOIN departments dept ON d.dept_id = dept.dept_id"""
        )
        doctors = cur.fetchall()
        # 등록/수정 폼의 진료과 선택 목록(select box)용
        cur.execute("SELECT * FROM departments")
        departments = cur.fetchall()
    conn.close()
    return render_template("admin_doctor.html", doctors=doctors, departments=departments)


# =====================================================================
# 양소정 담당 - 관리자: 회원관리 / 예약관리 / 게시판관리 / 공지사항관리
# =====================================================================
@app.route("/admin/user", methods=["GET", "POST"])
@admin_required
def admin_user():
    """회원 목록 조회, 정보 수정, 삭제(탈퇴 처리)."""
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "update":
                cur.execute(
                    "UPDATE users SET name=%s, phone=%s, email=%s WHERE user_id=%s",
                    (request.form["name"], request.form.get("phone"), request.form.get("email"), request.form["user_id"]),
                )
            elif action == "delete":
                cur.execute("DELETE FROM users WHERE user_id=%s", (request.form["user_id"],))
        conn.commit()

    with conn.cursor() as cur:
        # role='user' 조건으로 관리자 계정은 목록에서 제외
        cur.execute("SELECT * FROM users WHERE role='user'")
        users = cur.fetchall()
    conn.close()
    return render_template("admin_user.html", users=users)


@app.route("/admin/reservation", methods=["GET", "POST"])
@admin_required
def admin_reservation():
    """전체 예약 목록 조회, 예약 상태 변경(확정/취소), 삭제."""
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        reservation_id = request.form["reservation_id"]
        with conn.cursor() as cur:
            if action == "update_status":
                cur.execute(
                    "UPDATE reservations SET status=%s WHERE reservation_id=%s",
                    (request.form["status"], reservation_id),
                )
            elif action == "delete":
                cur.execute("DELETE FROM reservations WHERE reservation_id=%s", (reservation_id,))
        conn.commit()

    with conn.cursor() as cur:
        # 예약자 이름, 담당 의료진, 진료과까지 한 번에 보여주기 위해 3개 테이블 JOIN
        cur.execute(
            """SELECT r.*, u.name AS user_name, doc.doctor_name, dept.dept_name FROM reservations r
               JOIN users u ON r.user_id = u.user_id
               JOIN doctors doc ON r.doctor_id = doc.doctor_id
               JOIN departments dept ON doc.dept_id = dept.dept_id
               ORDER BY r.reservation_date DESC"""
        )
        reservations = cur.fetchall()
    conn.close()
    return render_template("admin_reservation.html", reservations=reservations)


@app.route("/admin/board", methods=["GET", "POST"])
@admin_required
def admin_board():
    """게시글/댓글 관리(삭제)."""
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "delete_post":
                cur.execute("DELETE FROM board WHERE board_id=%s", (request.form["board_id"],))
            elif action == "delete_comment":
                cur.execute("DELETE FROM board_comments WHERE comment_id=%s", (request.form["comment_id"],))
        conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            """SELECT b.*, u.name FROM board b
               JOIN users u ON b.user_id = u.user_id
               ORDER BY b.created_at DESC"""
        )
        posts = cur.fetchall()
    conn.close()
    return render_template("admin_board.html", posts=posts)


@app.route("/admin/notice", methods=["GET", "POST"])
@admin_required
def admin_notice():
    """공지사항 등록/수정/삭제."""
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "create":
                cur.execute(
                    "INSERT INTO notice (title, content) VALUES (%s, %s)",
                    (request.form["title"], request.form["content"]),
                )
            elif action == "update":
                cur.execute(
                    "UPDATE notice SET title=%s, content=%s WHERE notice_id=%s",
                    (request.form["title"], request.form["content"], request.form["notice_id"]),
                )
            elif action == "delete":
                cur.execute("DELETE FROM notice WHERE notice_id=%s", (request.form["notice_id"],))
        conn.commit()

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notice ORDER BY created_at DESC")
        notices = cur.fetchall()
    conn.close()
    return render_template("admin_notice.html", notices=notices)


if __name__ == "__main__":
    # debug=True로 실행하면 코드 수정 시 서버가 자동으로 재시작되고,
    # 에러 발생 시 브라우저에 상세 에러 페이지가 나와서 개발 중에 편리함.
    # (실제 배포 시에는 반드시 False로 변경)
    app.run(debug=True)