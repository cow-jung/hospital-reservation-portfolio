# =====================================================================
# 유민정 담당
#
# - 신규 예약
# - 과거이력 재예약
# - 예약 가능한 시간 조회
# - 마이페이지
# - 예약 조회 / 수정 / 취소
# =====================================================================

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from werkzeug.security import generate_password_hash
from datetime import datetime

from auth.routes import validate_password

# 공통 DB 연결 함수 / 로그인 확인
from db import get_db_connection, login_required


# =====================================================================
# Blueprint 생성
# =====================================================================

reservation_bp = Blueprint(
    "reservation",
    __name__
)


# =====================================================================
# 1. 신규 예약 / 과거이력 재예약
# =====================================================================

@reservation_bp.route(
    "/reservation",
    methods=["GET", "POST"]
)
@login_required
def reservation():

    """
    GET
    - 진료과 조회
    - 의료진 조회
    - 로그인한 회원의 과거 예약 이력 조회

    POST
    - 신규 예약 또는 재예약 등록
    """


    # DB 연결
    conn = get_db_connection()


    # =================================================================
    # POST - 예약 등록
    # =================================================================

    if request.method == "POST":

        # 의료진 번호
        doctor_id = request.form["doctor_id"]

        # 예약 날짜
        reservation_date = request.form["reservation_date"]

        # 예약 시간
        reservation_time = request.form["reservation_time"]

        # 증상 / 방문 사유
        memo = request.form.get(
            "memo",
            ""
        )


        try:

            with conn.cursor() as cur:

                # -----------------------------------------------------
                # 의료진 정보 / 토요일 진료 여부 확인
                # -----------------------------------------------------

                cur.execute(
                    """
                    SELECT
                        doctor_id,
                        dept_id,
                        saturday_available

                    FROM doctors

                    WHERE doctor_id = %s
                    """,
                    (
                        doctor_id,
                    )
                )

                selected_doctor = cur.fetchone()


                # 의료진 정보가 없는 경우
                if not selected_doctor:

                    flash(
                        "의료진 정보를 찾을 수 없습니다."
                    )

                    return redirect(
                        url_for(
                            "reservation.reservation"
                        )
                    )


                # -----------------------------------------------------
                # 예약 날짜를 date 객체로 변환
                # -----------------------------------------------------

                selected_date = datetime.strptime(
                    reservation_date,
                    "%Y-%m-%d"
                ).date()


                # -----------------------------------------------------
                # 토요일 진료 여부 검사
                #
                # weekday()
                #
                # 월요일 = 0
                # 화요일 = 1
                # 수요일 = 2
                # 목요일 = 3
                # 금요일 = 4
                # 토요일 = 5
                # 일요일 = 6
                # -----------------------------------------------------

                if (
                    selected_date.weekday() == 5
                    and
                    selected_doctor[
                        "saturday_available"
                    ] == 0
                ):

                    flash(
                        "해당 의료진은 토요일 진료가 없습니다."
                    )

                    return redirect(
                        url_for(
                            "reservation.reservation",
                            dept_id=
                                selected_doctor[
                                    "dept_id"
                                ],
                            doctor_id=doctor_id
                        )
                    )


                # -----------------------------------------------------
                # 동일 의료진 / 동일 날짜 / 동일 시간
                # 중복 예약 확인
                # -----------------------------------------------------

                cur.execute(
                    """
                    SELECT
                        reservation_id

                    FROM reservations

                    WHERE doctor_id = %s

                      AND reservation_date = %s

                      AND reservation_time = %s

                      AND status != '취소'
                    """,
                    (
                        doctor_id,
                        reservation_date,
                        reservation_time
                    )
                )

                duplicate = cur.fetchone()


                if duplicate:

                    flash(
                        "이미 예약된 시간입니다. "
                        "다른 시간을 선택해주세요."
                    )

                    return redirect(
                        url_for(
                            "reservation.reservation",
                            dept_id=
                                selected_doctor[
                                    "dept_id"
                                ],
                            doctor_id=doctor_id
                        )
                    )


                # -----------------------------------------------------
                # 예약 등록
                #
                # 신규예약과 재예약 모두
                # 기존 예약을 수정하지 않고
                # 새로운 예약을 INSERT
                # -----------------------------------------------------

                cur.execute(
                    """
                    INSERT INTO reservations
                    (
                        user_id,
                        doctor_id,
                        reservation_date,
                        reservation_time,
                        memo,
                        status
                    )

                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        '대기'
                    )
                    """,
                    (
                        session["user_id"],
                        doctor_id,
                        reservation_date,
                        reservation_time,
                        memo
                    )
                )


            # DB 반영
            conn.commit()


        finally:

            conn.close()


        flash(
            "예약이 신청되었습니다."
        )


        # 예약 완료 후 예약내역으로 이동
        return redirect(
            url_for(
                "reservation.mypage_reservation"
            )
        )


    # =================================================================
    # GET
    # =================================================================

    # 예약하기 버튼에서 전달받은 값
    selected_dept_id = request.args.get(
        "dept_id"
    )

    selected_doctor_id = request.args.get(
        "doctor_id"
    )


    try:

        with conn.cursor() as cur:

            # -----------------------------------------------------
            # 선택한 의료진의 실제 진료과 조회
            # -----------------------------------------------------

            if selected_doctor_id:

                cur.execute(
                    """
                    SELECT
                        doctor_id,
                        dept_id

                    FROM doctors

                    WHERE doctor_id = %s
                    """,
                    (
                        selected_doctor_id,
                    )
                )

                selected_doctor = cur.fetchone()


                # 의료진이 존재하면
                # 소속 진료과 번호 저장
                if selected_doctor:

                    selected_dept_id = (
                        selected_doctor[
                            "dept_id"
                        ]
                    )


            # ---------------------------------------------------------
            # 진료과 목록
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    dept_id,
                    dept_name

                FROM departments

                ORDER BY dept_id
                """
            )

            departments = cur.fetchall()


            # ---------------------------------------------------------
            # 의료진 목록
            #
            # saturday_available 포함
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    d.doctor_id,
                    d.doctor_name,
                    d.dept_id,
                    d.specialty,
                    d.work_hours,
                    d.saturday_available,
                    dept.dept_name

                FROM doctors d

                JOIN departments dept
                    ON d.dept_id = dept.dept_id

                ORDER BY
                    d.dept_id,
                    d.doctor_id
                """
            )

            doctors = cur.fetchall()


            # ---------------------------------------------------------
            # 로그인 회원의 과거 예약 이력
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    r.*,

                    doc.doctor_name,
                    doc.saturday_available,

                    dept.dept_name

                FROM reservations r

                JOIN doctors doc
                    ON r.doctor_id =
                       doc.doctor_id

                JOIN departments dept
                    ON doc.dept_id =
                       dept.dept_id

                WHERE r.user_id = %s

                ORDER BY
                    r.reservation_date DESC,
                    r.reservation_time DESC
                """,
                (
                    session["user_id"],
                )
            )

            history = cur.fetchall()


    finally:

        conn.close()


    return render_template(
        "reservation.html",

        departments=departments,
        doctors=doctors,
        history=history,

        selected_dept_id=
            selected_dept_id,

        selected_doctor_id=
            selected_doctor_id
    )


# =====================================================================
# 2. 예약 가능한 시간 조회
# =====================================================================

@reservation_bp.route(
    "/reservation/available-times"
)
@login_required
def reservation_available_times():

    """
    선택한 의료진 + 날짜 기준

    1. 의료진 토요일 진료 여부 확인
    2. 이미 예약된 시간 조회
    """


    # 의료진 번호
    doctor_id = request.args.get(
        "doctor_id"
    )


    # 선택 날짜
    reservation_date = request.args.get(
        "date"
    )


    # 필수값이 없는 경우
    if (
        not doctor_id
        or
        not reservation_date
    ):

        return jsonify(
            {
                "reserved_times": [],
                "saturday_closed": False
            }
        )


    conn = get_db_connection()


    try:

        with conn.cursor() as cur:

            # ---------------------------------------------------------
            # 의료진 토요일 진료 여부 조회
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    doctor_id,
                    saturday_available

                FROM doctors

                WHERE doctor_id = %s
                """,
                (
                    doctor_id,
                )
            )

            doctor = cur.fetchone()


            if not doctor:

                return jsonify(
                    {
                        "reserved_times": [],
                        "saturday_closed": False
                    }
                ), 404


            # ---------------------------------------------------------
            # 선택 날짜 변환
            # ---------------------------------------------------------

            try:

                selected_date = datetime.strptime(
                    reservation_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return jsonify(
                    {
                        "reserved_times": [],
                        "saturday_closed": False
                    }
                ), 400


            # ---------------------------------------------------------
            # 토요일이고
            # 해당 의료진이 토요일 진료를 하지 않는 경우
            # ---------------------------------------------------------

            if (
                selected_date.weekday() == 5
                and
                doctor[
                    "saturday_available"
                ] == 0
            ):

                return jsonify(
                    {
                        "reserved_times": [],
                        "saturday_closed": True
                    }
                )


            # ---------------------------------------------------------
            # 해당 의사의 해당 날짜 예약 시간 조회
            #
            # 취소 예약은 다시 예약 가능하므로 제외
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    TIME_FORMAT(
                        reservation_time,
                        '%%H:%%i'
                    ) AS reservation_time

                FROM reservations

                WHERE doctor_id = %s

                  AND reservation_date = %s

                  AND status != '취소'

                ORDER BY reservation_time
                """,
                (
                    doctor_id,
                    reservation_date
                )
            )

            reserved_rows = cur.fetchall()


            # ["09:30", "10:00"] 형태
            reserved_times = [
                row["reservation_time"]
                for row in reserved_rows
            ]


            return jsonify(
                {
                    "reserved_times":
                        reserved_times,

                    "saturday_closed":
                        False
                }
            )


    finally:

        conn.close()


# =====================================================================
# 3. 마이페이지
# =====================================================================

@reservation_bp.route(
    "/mypage"
)
@login_required
def mypage():

    conn = get_db_connection()


    try:

        with conn.cursor() as cur:

            # ---------------------------------------------------------
            # 현재 회원 정보
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT *

                FROM users

                WHERE user_id = %s
                """,
                (
                    session["user_id"],
                )
            )

            user = cur.fetchone()


            # ---------------------------------------------------------
            # 진료 / 예약 이력
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    r.*,

                    doc.doctor_name,

                    dept.dept_name

                FROM reservations r

                JOIN doctors doc
                    ON r.doctor_id =
                       doc.doctor_id

                JOIN departments dept
                    ON doc.dept_id =
                       dept.dept_id

                WHERE r.user_id = %s

                ORDER BY
                    r.reservation_date DESC,
                    r.reservation_time DESC
                """,
                (
                    session["user_id"],
                )
            )

            treatment_history = (
                cur.fetchall()
            )


    finally:

        conn.close()


    return render_template(
        "mypage.html",
        user=user,
        treatment_history=
            treatment_history
    )


# =====================================================================
# 4. 회원정보 수정
# =====================================================================

@reservation_bp.route(
    "/mypage/edit",
    methods=["GET", "POST"]
)
@login_required
def mypage_edit():

    conn = get_db_connection()


    # ---------------------------------------------------------
    # 수정 저장
    # ---------------------------------------------------------

    if request.method == "POST":

        name = request.form[
            "name"
        ]

        phone = request.form.get(
            "phone"
        )

        email = request.form.get(
            "email"
        )


        new_password = (
            request.form.get(
                "new_password",
                ""
            )
        )


        new_password_confirm = (
            request.form.get(
                "new_password_confirm",
                ""
            )
        )


        # -----------------------------------------------------
        # 비밀번호를 변경하는 경우
        # -----------------------------------------------------

        if new_password:

            # 비밀번호 조건 확인
            if not validate_password(
                new_password
            ):

                conn.close()

                flash(
                    "비밀번호 형식을 확인해주세요."
                )

                return redirect(
                    url_for(
                        "reservation.mypage_edit"
                    )
                )


            # 비밀번호 확인
            if (
                new_password
                !=
                new_password_confirm
            ):

                conn.close()

                flash(
                    "새 비밀번호가 일치하지 않습니다."
                )

                return redirect(
                    url_for(
                        "reservation.mypage_edit"
                    )
                )


            # 비밀번호 암호화
            hashed_password = (
                generate_password_hash(
                    new_password
                )
            )


            with conn.cursor() as cur:

                cur.execute(
                    """
                    UPDATE users

                    SET
                        name = %s,
                        phone = %s,
                        email = %s,
                        password = %s

                    WHERE user_id = %s
                    """,
                    (
                        name,
                        phone,
                        email,
                        hashed_password,
                        session["user_id"]
                    )
                )


        # -----------------------------------------------------
        # 비밀번호 변경 안 함
        # -----------------------------------------------------

        else:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    UPDATE users

                    SET
                        name = %s,
                        phone = %s,
                        email = %s

                    WHERE user_id = %s
                    """,
                    (
                        name,
                        phone,
                        email,
                        session["user_id"]
                    )
                )


        conn.commit()

        conn.close()


        # 세션 이름도 변경
        session["name"] = name


        flash(
            "회원정보가 수정되었습니다."
        )


        return redirect(
            url_for(
                "reservation.mypage"
            )
        )


    # ---------------------------------------------------------
    # GET - 현재 회원정보
    # ---------------------------------------------------------

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *

                FROM users

                WHERE user_id = %s
                """,
                (
                    session["user_id"],
                )
            )

            user = cur.fetchone()


    finally:

        conn.close()


    return render_template(
        "mypage_edit.html",
        user=user
    )


# =====================================================================
# 5. 회원 탈퇴
# =====================================================================

@reservation_bp.route(
    "/mypage/withdraw",
    methods=["POST"]
)
@login_required
def mypage_withdraw():

    # 선택한 탈퇴 사유
    withdraw_reason = (
        request.form.get(
            "withdraw_reason"
        )
    )


    # 직접 입력 사유
    withdraw_reason_direct = (
        request.form.get(
            "withdraw_reason_direct",
            ""
        )
    )


    # 직접 입력 선택 시
    if (
        withdraw_reason
        ==
        "직접 입력"
    ):

        withdraw_reason = (
            withdraw_reason_direct
        )


    conn = get_db_connection()


    try:

        with conn.cursor() as cur:

            # 현재 DB 구조에서는
            # 탈퇴 사유 저장 컬럼이 없으므로
            # 회원 데이터 삭제
            cur.execute(
                """
                DELETE FROM users

                WHERE user_id = %s
                """,
                (
                    session["user_id"],
                )
            )


        conn.commit()


    finally:

        conn.close()


    # 로그인 세션 삭제
    session.clear()


    flash(
        "회원 탈퇴가 완료되었습니다."
    )


    return redirect(
        url_for(
            "index"
        )
    )


# =====================================================================
# 6. 예약 내역 조회
# =====================================================================

@reservation_bp.route(
    "/mypage/reservation"
)
@login_required
def mypage_reservation():

    conn = get_db_connection()


    try:

        with conn.cursor() as cur:

            # ---------------------------------------------------------
            # 로그인한 회원의 예약 내역 조회
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    r.*,

                    d.doctor_name,
                    d.dept_id,

                    dp.dept_name

                FROM reservations r

                JOIN doctors d
                    ON r.doctor_id =
                       d.doctor_id

                JOIN departments dp
                    ON d.dept_id =
                       dp.dept_id

                WHERE r.user_id = %s

                ORDER BY
                    r.reservation_date DESC,
                    r.reservation_time DESC
                """,
                (
                    session["user_id"],
                )
            )

            reservations = cur.fetchall()


    finally:

        conn.close()


    return render_template(
        "reservation_list.html",
        reservations=reservations
    )


# =====================================================================
# 7. 예약 변경 페이지
# =====================================================================

@reservation_bp.route(
    "/mypage/reservation/<int:reservation_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def reservation_edit(
    reservation_id
):

    conn = get_db_connection()


    try:

        with conn.cursor() as cur:

            # ---------------------------------------------------------
            # 수정하려는 예약 조회
            #
            # saturday_available 포함
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    r.*,

                    d.doctor_name,
                    d.dept_id,
                    d.saturday_available,

                    dp.dept_name

                FROM reservations r

                JOIN doctors d
                    ON r.doctor_id =
                       d.doctor_id

                JOIN departments dp
                    ON d.dept_id =
                       dp.dept_id

                WHERE r.reservation_id = %s

                  AND r.user_id = %s
                """,
                (
                    reservation_id,
                    session["user_id"]
                )
            )

            reservation = cur.fetchone()


            # 예약이 없는 경우
            if not reservation:

                flash(
                    "예약 정보를 찾을 수 없습니다."
                )

                return redirect(
                    url_for(
                        "reservation.mypage_reservation"
                    )
                )


            # ---------------------------------------------------------
            # 확정 예약은 변경 불가
            # ---------------------------------------------------------

            if (
                reservation[
                    "status"
                ]
                ==
                "확정"
            ):

                flash(
                    "확정된 예약은 온라인에서 변경할 수 없습니다."
                )

                return redirect(
                    url_for(
                        "reservation.mypage_reservation"
                    )
                )


            # ---------------------------------------------------------
            # 취소된 예약도 변경 불가
            # ---------------------------------------------------------

            if (
                reservation[
                    "status"
                ]
                ==
                "취소"
            ):

                flash(
                    "취소된 예약은 변경할 수 없습니다."
                )

                return redirect(
                    url_for(
                        "reservation.mypage_reservation"
                    )
                )


            # =========================================================
            # POST - 실제 예약 변경
            # =========================================================

            if request.method == "POST":

                new_date = request.form.get(
                    "reservation_date"
                )

                new_time = request.form.get(
                    "reservation_time"
                )


                # 날짜 또는 시간이 없는 경우
                if (
                    not new_date
                    or
                    not new_time
                ):

                    flash(
                        "변경할 날짜와 시간을 모두 선택해주세요."
                    )

                    return redirect(
                        url_for(
                            "reservation.reservation_edit",
                            reservation_id=
                                reservation_id
                        )
                    )


                # -----------------------------------------------------
                # 변경할 날짜 변환
                # -----------------------------------------------------

                selected_new_date = (
                    datetime.strptime(
                        new_date,
                        "%Y-%m-%d"
                    ).date()
                )


                # -----------------------------------------------------
                # 토요일 진료 여부 확인
                # -----------------------------------------------------

                if (
                    selected_new_date.weekday()
                    == 5
                    and
                    reservation[
                        "saturday_available"
                    ] == 0
                ):

                    flash(
                        "해당 의료진은 토요일 진료가 없습니다."
                    )

                    return redirect(
                        url_for(
                            "reservation.reservation_edit",
                            reservation_id=
                                reservation_id
                        )
                    )


                # -----------------------------------------------------
                # 동일 의료진 / 동일 날짜 / 동일 시간
                # 예약 중복 확인
                #
                # 현재 수정 중인 예약번호는 제외
                # -----------------------------------------------------

                cur.execute(
                    """
                    SELECT
                        reservation_id

                    FROM reservations

                    WHERE doctor_id = %s

                      AND reservation_date = %s

                      AND reservation_time = %s

                      AND status != '취소'

                      AND reservation_id != %s
                    """,
                    (
                        reservation[
                            "doctor_id"
                        ],
                        new_date,
                        new_time,
                        reservation_id
                    )
                )

                duplicate = cur.fetchone()


                if duplicate:

                    flash(
                        "이미 예약된 시간입니다. "
                        "다른 시간을 선택해주세요."
                    )

                    return redirect(
                        url_for(
                            "reservation.reservation_edit",
                            reservation_id=
                                reservation_id
                        )
                    )


                # -----------------------------------------------------
                # 예약 변경
                # -----------------------------------------------------

                cur.execute(
                    """
                    UPDATE reservations

                    SET
                        reservation_date = %s,
                        reservation_time = %s

                    WHERE reservation_id = %s

                      AND user_id = %s
                    """,
                    (
                        new_date,
                        new_time,
                        reservation_id,
                        session["user_id"]
                    )
                )


                conn.commit()


                flash(
                    "예약이 변경되었습니다."
                )


                return redirect(
                    url_for(
                        "reservation.mypage_reservation"
                    )
                )


    finally:

        conn.close()


    return render_template(
        "reservation_edit.html",
        reservation=reservation
    )


# =====================================================================
# 8. 예약 변경 페이지 - 예약된 시간 조회
# =====================================================================

@reservation_bp.route(
    "/mypage/reservation/<int:reservation_id>/available-times"
)
@login_required
def reservation_edit_available_times(
    reservation_id
):

    reservation_date = request.args.get(
        "date"
    )


    if not reservation_date:

        return jsonify(
            {
                "reserved_times": [],
                "saturday_closed": False
            }
        )


    conn = get_db_connection()


    try:

        with conn.cursor() as cur:

            # ---------------------------------------------------------
            # 현재 변경 중인 예약 의료진 확인
            #
            # saturday_available 포함
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    r.doctor_id,
                    d.saturday_available

                FROM reservations r

                JOIN doctors d
                    ON r.doctor_id =
                       d.doctor_id

                WHERE r.reservation_id = %s

                  AND r.user_id = %s
                """,
                (
                    reservation_id,
                    session["user_id"]
                )
            )

            reservation = cur.fetchone()


            if not reservation:

                return jsonify(
                    {
                        "reserved_times": [],
                        "saturday_closed": False
                    }
                ), 404


            # ---------------------------------------------------------
            # 선택 날짜
            # ---------------------------------------------------------

            try:

                selected_date = (
                    datetime.strptime(
                        reservation_date,
                        "%Y-%m-%d"
                    ).date()
                )

            except ValueError:

                return jsonify(
                    {
                        "reserved_times": [],
                        "saturday_closed": False
                    }
                ), 400


            # ---------------------------------------------------------
            # 토요일 + 토요일 진료 안 하는 의료진
            # ---------------------------------------------------------

            if (
                selected_date.weekday() == 5
                and
                reservation[
                    "saturday_available"
                ] == 0
            ):

                return jsonify(
                    {
                        "reserved_times": [],
                        "saturday_closed": True
                    }
                )


            # ---------------------------------------------------------
            # 해당 의료진의 선택 날짜 예약시간 조회
            #
            # 현재 수정 중인 예약 제외
            # 취소된 예약 제외
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    TIME_FORMAT(
                        reservation_time,
                        '%%H:%%i'
                    ) AS reservation_time

                FROM reservations

                WHERE doctor_id = %s

                  AND reservation_date = %s

                  AND status != '취소'

                  AND reservation_id != %s

                ORDER BY reservation_time
                """,
                (
                    reservation[
                        "doctor_id"
                    ],
                    reservation_date,
                    reservation_id
                )
            )

            rows = cur.fetchall()


            reserved_times = [
                row["reservation_time"]
                for row in rows
            ]


            return jsonify(
                {
                    "reserved_times":
                        reserved_times,

                    "saturday_closed":
                        False
                }
            )


    finally:

        conn.close()


# =====================================================================
# 9. 예약 취소
# =====================================================================

@reservation_bp.route(
    "/mypage/reservation/<int:reservation_id>/cancel",
    methods=["POST"]
)
@login_required
def reservation_cancel(
    reservation_id
):

    # 취소 사유
    cancel_reason = (
        request.form.get(
            "cancel_reason"
        )
    )


    # 직접 입력
    cancel_reason_direct = (
        request.form.get(
            "cancel_reason_direct",
            ""
        )
    )


    # 직접 입력 선택
    if (
        cancel_reason
        ==
        "직접 입력"
    ):

        cancel_reason = (
            cancel_reason_direct.strip()
        )


    # 사유가 없는 경우
    if not cancel_reason:

        flash(
            "예약 취소 사유를 선택해주세요."
        )

        return redirect(
            url_for(
                "reservation.mypage_reservation"
            )
        )


    conn = get_db_connection()


    try:

        with conn.cursor() as cur:

            # ---------------------------------------------------------
            # 현재 예약 상태 확인
            # ---------------------------------------------------------

            cur.execute(
                """
                SELECT
                    status

                FROM reservations

                WHERE reservation_id = %s

                  AND user_id = %s
                """,
                (
                    reservation_id,
                    session["user_id"]
                )
            )

            reservation = cur.fetchone()


            if not reservation:

                flash(
                    "예약 정보를 찾을 수 없습니다."
                )

                return redirect(
                    url_for(
                        "reservation.mypage_reservation"
                    )
                )


            if (
                reservation[
                    "status"
                ]
                ==
                "취소"
            ):

                flash(
                    "이미 취소된 예약입니다."
                )

                return redirect(
                    url_for(
                        "reservation.mypage_reservation"
                    )
                )


            # ---------------------------------------------------------
            # 예약 취소 처리
            #
            # 실제 삭제하지 않고 상태를 취소로 변경
            # ---------------------------------------------------------

            cur.execute(
                """
                UPDATE reservations

                SET
                    status = '취소',

                    cancel_reason = %s

                WHERE reservation_id = %s

                  AND user_id = %s
                """,
                (
                    cancel_reason,
                    reservation_id,
                    session["user_id"]
                )
            )


            conn.commit()


    finally:

        conn.close()


    flash(
        "예약이 취소되었습니다."
    )


    return redirect(
        url_for(
            "reservation.mypage_reservation"
        )
    )