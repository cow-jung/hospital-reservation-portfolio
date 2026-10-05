# -*- coding: utf-8 -*-

"""
백민욱 담당
- 로그인
- 로그아웃
- 회원가입
- 아이디 중복확인
- 비밀번호 정책
- 로그인 IP 차단
- 로그인 성공/실패 기록
- 로그인 3회 실패 시 1분 계정 잠금
- 최근 로그인 시간/IP 기록
- 비밀번호 변경 후 30일 경과 알림
"""

from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from db import (
    get_db_connection,
    get_client_ip,
    is_ip_blocked,
)


# =========================================================
# Blueprint
# =========================================================

auth_bp = Blueprint("auth", __name__)


# =========================================================
# 비밀번호 정책 검사
# =========================================================

def validate_password(password):
    """
    비밀번호 정책

    1. 8자 이상
    2. 영문자 1개 이상
    3. 숫자 1개 이상
    4. 특수문자 1개 이상
    """

    if len(password) < 8:
        return False, "비밀번호는 8자 이상이어야 합니다."

    if not any(c.isalpha() for c in password):
        return False, "비밀번호에 영문자를 포함해야 합니다."

    if not any(c.isdigit() for c in password):
        return False, "비밀번호에 숫자를 포함해야 합니다."

    if not any(not c.isalnum() for c in password):
        return False, "비밀번호에 특수문자를 포함해야 합니다."

    return True, None


# =========================================================
# 로그인 시도 기록
# =========================================================

def _log_login_attempt(
    username,
    ip_address,
    success,
    reason,
    user_id=None
):
    """
    로그인 시도 결과를 security_logs 테이블에 기록.

    존재하는 회원이면 user_id도 함께 저장하고,
    존재하지 않는 아이디나 로그인 전 IP 차단이면 NULL로 저장.
    """

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO security_logs
                (
                    user_id,
                    username,
                    ip_address,
                    success,
                    reason
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    username,
                    ip_address,
                    1 if success else 0,
                    reason,
                ),
            )

        conn.commit()

    finally:
        conn.close()


# =========================================================
# 로그인
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        client_ip = get_client_ip(request)

        # -----------------------------------------------------
        # 1. 필수 입력값 검사
        # -----------------------------------------------------

        if not username or not password:

            _log_login_attempt(
                username=username,
                ip_address=client_ip,
                success=False,
                reason="아이디 또는 비밀번호 미입력",
            )

            flash("아이디와 비밀번호를 입력해주세요.")
            return redirect(url_for("auth.login"))

        # -----------------------------------------------------
        # 2. 로그인 차단 IP 검사
        # -----------------------------------------------------

        if is_ip_blocked(client_ip, "login"):

            _log_login_attempt(
                username=username,
                ip_address=client_ip,
                success=False,
                reason="차단된 IP",
            )

            flash("현재 접속 위치에서는 로그인이 제한되어 있습니다.")
            return redirect(url_for("auth.login"))

        # -----------------------------------------------------
        # 3. 사용자 조회
        # -----------------------------------------------------

        conn = get_db_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE username = %s
                    """,
                    (username,),
                )

                user = cur.fetchone()

        finally:
            conn.close()

        # -----------------------------------------------------
        # 4. 존재하지 않는 아이디
        # -----------------------------------------------------

        if not user:

            _log_login_attempt(
                username=username,
                ip_address=client_ip,
                success=False,
                reason="아이디 또는 비밀번호 불일치",
            )

            flash("아이디 또는 비밀번호가 올바르지 않습니다.")
            return redirect(url_for("auth.login"))

        now = datetime.now()

        # -----------------------------------------------------
        # 5. 현재 계정 잠금 여부 확인
        # -----------------------------------------------------

        if (
            user["locked_until"] is not None
            and user["locked_until"] > now
        ):

            _log_login_attempt(
                username=username,
                ip_address=client_ip,
                success=False,
                reason="계정 일시 잠금",
                user_id=user["user_id"],
            )

            flash(
                "로그인 실패 횟수 초과로 계정이 잠겨 있습니다. "
                "잠시 후 다시 시도해주세요."
            )

            return redirect(url_for("auth.login"))

        # -----------------------------------------------------
        # 6. 비밀번호 검사
        # -----------------------------------------------------

        if not check_password_hash(
            user["password"],
            password
        ):

            failed_count = user["failed_login_count"] + 1

            conn = get_db_connection()

            try:

                # ---------------------------------------------
                # 로그인 3회 실패
                # → 1분 계정 잠금
                # ---------------------------------------------

                if failed_count >= 3:

                    locked_until = now + timedelta(minutes=1)

                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE users
                            SET
                                failed_login_count = 0,
                                locked_until = %s
                            WHERE user_id = %s
                            """,
                            (
                                locked_until,
                                user["user_id"],
                            ),
                        )

                    conn.commit()

                    _log_login_attempt(
                        username=username,
                        ip_address=client_ip,
                        success=False,
                        reason="로그인 3회 실패 - 1분 잠금",
                        user_id=user["user_id"],
                    )

                    flash(
                        "로그인에 3회 실패하여 "
                        "계정이 1분간 잠겼습니다."
                    )

                    return redirect(url_for("auth.login"))

                # ---------------------------------------------
                # 아직 3회 미만
                # ---------------------------------------------

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE users
                        SET failed_login_count = %s
                        WHERE user_id = %s
                        """,
                        (
                            failed_count,
                            user["user_id"],
                        ),
                    )

                conn.commit()

            finally:
                conn.close()

            _log_login_attempt(
                username=username,
                ip_address=client_ip,
                success=False,
                reason="아이디 또는 비밀번호 불일치",
                user_id=user["user_id"],
            )

            flash("아이디 또는 비밀번호가 올바르지 않습니다.")
            return redirect(url_for("auth.login"))

        # -----------------------------------------------------
        # 7. 로그인 성공
        #
        # 실패 횟수 초기화
        # 계정 잠금 해제
        # 최근 로그인 시간/IP 기록
        # -----------------------------------------------------

        conn = get_db_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET
                        failed_login_count = 0,
                        locked_until = NULL,
                        last_login_at = NOW(),
                        last_login_ip = %s
                    WHERE user_id = %s
                    """,
                    (
                        client_ip,
                        user["user_id"],
                    ),
                )

            conn.commit()

        finally:
            conn.close()

        # -----------------------------------------------------
        # 8. 로그인 세션 생성
        # -----------------------------------------------------

        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        # -----------------------------------------------------
        # 9. 로그인 성공 기록
        # -----------------------------------------------------

        _log_login_attempt(
            username=username,
            ip_address=client_ip,
            success=True,
            reason="로그인 성공",
            user_id=user["user_id"],
        )

        # -----------------------------------------------------
        # 10. 비밀번호 변경 후 30일 경과 검사
        # -----------------------------------------------------

        password_changed_at = user["password_changed_at"]

        if password_changed_at is not None:

            password_age = now - password_changed_at

            if password_age >= timedelta(days=30):

                flash(
                    "비밀번호를 변경한 지 30일이 지났습니다. "
                    "보안을 위해 비밀번호 변경을 권장합니다."
                )

        return redirect(url_for("index"))

    # GET 요청
    return render_template("login.html")


# =========================================================
# 로그아웃
# =========================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


# =========================================================
# 회원가입
# =========================================================

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        password = request.form.get("password", "")
        password_confirm = request.form.get(
            "password_confirm",
            ""
        )

        name = request.form.get("name", "").strip()

        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        # -----------------------------------------------------
        # 1. 필수 입력값 검사
        # -----------------------------------------------------

        if (
            not username
            or not password
            or not password_confirm
            or not name
        ):
            flash("필수 입력 항목을 모두 입력해주세요.")
            return redirect(url_for("auth.signup"))

        # -----------------------------------------------------
        # 2. 비밀번호 확인값 검사
        # -----------------------------------------------------

        if password != password_confirm:

            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for("auth.signup"))

        # -----------------------------------------------------
        # 3. 비밀번호 패턴 검사
        # -----------------------------------------------------

        password_valid, password_message = (
            validate_password(password)
        )

        if not password_valid:

            flash(password_message)
            return redirect(url_for("auth.signup"))

        # -----------------------------------------------------
        # 4. 아이디 중복 검사
        # -----------------------------------------------------

        conn = get_db_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE username = %s
                    """,
                    (username,),
                )

                existing_user = cur.fetchone()

        finally:
            conn.close()

        if existing_user:

            flash("이미 사용 중인 아이디입니다.")
            return redirect(url_for("auth.signup"))

        # -----------------------------------------------------
        # 5. 중복검사 통과 후 비밀번호 해시 생성
        # -----------------------------------------------------

        hashed_pw = generate_password_hash(password)

        # -----------------------------------------------------
        # 6. 회원정보 DB 저장
        # -----------------------------------------------------

        conn = get_db_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users
                    (
                        username,
                        password,
                        name,
                        phone,
                        email,
                        role,
                        password_changed_at
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        'user',
                        NOW()
                    )
                    """,
                    (
                        username,
                        hashed_pw,
                        name,
                        phone if phone else None,
                        email if email else None,
                    ),
                )

            conn.commit()

        finally:
            conn.close()

        flash(
            "회원가입이 완료되었습니다. 로그인해주세요."
        )

        return redirect(url_for("auth.login"))

    # GET 요청
    return render_template("signup.html")


# =========================================================
# 아이디 중복확인
# =========================================================

@auth_bp.route("/check-username")
def check_username():

    """
    회원가입 화면의 AJAX 아이디 중복확인 API.

    예:
    /check-username?username=abc123

    반환:
    {
        "available": true
    }
    """

    username = request.args.get(
        "username",
        ""
    ).strip()

    if not username:

        return jsonify({
            "available": False
        })

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id
                FROM users
                WHERE username = %s
                """,
                (username,),
            )

            existing = cur.fetchone()

    finally:
        conn.close()

    return jsonify({
        "available": existing is None
    })