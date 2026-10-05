# -*- coding: utf-8 -*-
"""
임주혁 담당 - 관리자: 의료진 관리

원래는 hospital_bp(=hospital/admin_routes.py)에 있었지만, 관리자 메뉴이므로
이번에 admin_bp로 옮겼습니다. 그래서 이 파일 안의 url_for()들과, 이 라우트를
가리키던 템플릿들의 url_for()도 "hospital.admin_doctor..." 에서
"admin.admin_doctor..."로 함께 바뀌었습니다.
(URL 경로 자체(/admin/doctor 등)는 그대로입니다)

이미지 업로드 처리 함수(_save_uploaded_image)는 계속 hospital/routes.py에
있는 것을 그대로 가져다 씁니다.
"""

from flask import render_template, request, redirect, url_for, flash
from db import get_db_connection, admin_required
from hospital.routes import _save_uploaded_image
from admin import admin_bp


@admin_bp.route("/admin/doctor", methods=["GET", "POST"])
@admin_required
def admin_doctor():
    """
    의료진 목록 전용 페이지.
    등록은 admin_doctor_create(), 상세/수정/삭제는 admin_doctor_detail()/admin_doctor_edit()로 분리했습니다.

    ?q=검색어 로 요청하면 의료진명 또는 전문분야에 검색어가 포함된 것만 보여줍니다.
    ?dept_id=진료과ID 로 요청하면 해당 진료과 소속 의료진만 보여줍니다.
    (진료과 상세 페이지에서 "소속 의료진 보기" 링크로 넘어올 때 사용)
    """
    keyword = request.args.get("q", "").strip()
    dept_id = request.args.get("dept_id", "").strip()

    where_clauses = []
    params = []

    if keyword:
        where_clauses.append("(d.doctor_name LIKE %s OR d.specialty LIKE %s)")
        like_pattern = f"%{keyword}%"
        params.extend([like_pattern, like_pattern])

    if dept_id:
        where_clauses.append("d.dept_id = %s")
        params.append(dept_id)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT d.*, dept.dept_name FROM doctors d
                JOIN departments dept ON d.dept_id = dept.dept_id
                {where_sql}
                ORDER BY d.doctor_id""",
            params,
        )
        doctors = cur.fetchall()

        dept_name = None
        if dept_id:
            cur.execute("SELECT dept_name FROM departments WHERE dept_id=%s", (dept_id,))
            dept_row = cur.fetchone()
            dept_name = dept_row["dept_name"] if dept_row else None
    conn.close()
    return render_template(
        "admin_doctor.html",
        doctors=doctors,
        keyword=keyword,
        dept_id=dept_id,
        dept_name=dept_name,
    )


@admin_bp.route("/admin/doctor/create", methods=["GET", "POST"])
@admin_required
def admin_doctor_create():
    """의료진 등록 전용 페이지."""
    conn = get_db_connection()

    if request.method == "POST":
        uploaded_path = _save_uploaded_image(request.files.get("photo_file"), "doctors")
        photo = uploaded_path or request.form.get("photo")

        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO doctors (dept_id, doctor_name, specialty, profile, photo, work_hours)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    request.form["dept_id"],
                    request.form["doctor_name"],
                    request.form.get("specialty"),
                    request.form.get("profile"),
                    photo,
                    request.form.get("work_hours"),
                ),
            )
        conn.commit()
        conn.close()
        flash("의료진이 등록되었습니다.")
        return redirect(url_for("admin.admin_doctor"))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM departments ORDER BY display_order, dept_id")
        departments = cur.fetchall()
    conn.close()
    return render_template("admin_doctor_create.html", departments=departments)


@admin_bp.route("/admin/doctor/<int:doctor_id>", methods=["GET", "POST"])
@admin_required
def admin_doctor_detail(doctor_id):
    """
    의료진 상세 - 등록된 내용 확인 + 삭제.
    이 의료진에게 걸린 예약이 있으면 삭제를 막습니다.
    (doctors 삭제 시 reservations가 ON DELETE CASCADE로 걸려있어서,
     예약이 있는 채로 의료진을 지우면 그 예약 기록까지 전부 같이 삭제되기 때문)
    """
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "delete":
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS cnt FROM reservations WHERE doctor_id=%s", (doctor_id,))
                reservation_count = cur.fetchone()["cnt"]

            if reservation_count > 0:
                conn.close()
                flash(
                    f"이 의료진에게 걸린 예약이 {reservation_count}건 있어 삭제할 수 없습니다. "
                    f"예약관리에서 먼저 처리해주세요."
                )
                return redirect(url_for("admin.admin_doctor_detail", doctor_id=doctor_id))

            with conn.cursor() as cur:
                cur.execute("DELETE FROM doctors WHERE doctor_id=%s", (doctor_id,))
            conn.commit()
            conn.close()
            flash("의료진이 삭제되었습니다.")
            return redirect(url_for("admin.admin_doctor"))

    with conn.cursor() as cur:
        cur.execute(
            """SELECT d.*, dept.dept_name FROM doctors d
               JOIN departments dept ON d.dept_id = dept.dept_id
               WHERE d.doctor_id=%s""",
            (doctor_id,),
        )
        doctor = cur.fetchone()

        reservation_count = 0
        if doctor:
            cur.execute("SELECT COUNT(*) AS cnt FROM reservations WHERE doctor_id=%s", (doctor_id,))
            reservation_count = cur.fetchone()["cnt"]
    conn.close()

    if not doctor:
        flash("존재하지 않는 의료진입니다.")
        return redirect(url_for("admin.admin_doctor"))

    return render_template("admin_doctor_detail.html", doctor=doctor, reservation_count=reservation_count)


@admin_bp.route("/admin/doctor/<int:doctor_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_doctor_edit(doctor_id):
    """의료진 수정 전용 페이지."""
    conn = get_db_connection()

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM doctors WHERE doctor_id=%s", (doctor_id,))
        doctor = cur.fetchone()

    if not doctor:
        conn.close()
        flash("존재하지 않는 의료진입니다.")
        return redirect(url_for("admin.admin_doctor"))

    if request.method == "POST":
        uploaded_path = _save_uploaded_image(request.files.get("photo_file"), "doctors")
        photo = uploaded_path or request.form.get("photo")

        with conn.cursor() as cur:
            cur.execute(
                """UPDATE doctors SET dept_id=%s, doctor_name=%s, specialty=%s,
                   profile=%s, photo=%s, work_hours=%s WHERE doctor_id=%s""",
                (
                    request.form["dept_id"],
                    request.form["doctor_name"],
                    request.form.get("specialty"),
                    request.form.get("profile"),
                    photo,
                    request.form.get("work_hours"),
                    doctor_id,
                ),
            )
        conn.commit()
        conn.close()
        flash("의료진 정보가 수정되었습니다.")
        return redirect(url_for("admin.admin_doctor"))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM departments ORDER BY display_order, dept_id")
        departments = cur.fetchall()
    conn.close()
    return render_template("admin_doctor_edit.html", doctor=doctor, departments=departments)
