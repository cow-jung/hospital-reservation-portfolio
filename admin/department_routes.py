# -*- coding: utf-8 -*-
"""
임주혁 담당 - 관리자: 진료과 관리

원래는 hospital_bp(=hospital/admin_routes.py)에 있었지만, 관리자 메뉴이므로
이번에 admin_bp로 옮겼습니다. 그래서 이 파일 안의 url_for()들과, 이 라우트를
가리키던 템플릿들의 url_for()도 "hospital.admin_department..." 에서
"admin.admin_department..."로 함께 바뀌었습니다.
(URL 경로 자체(/admin/department 등)는 그대로입니다)

이미지 업로드 처리 함수(_save_uploaded_image)는 계속 hospital/routes.py에
있는 것을 그대로 가져다 씁니다. (병원소개/진료과·의료진 조회 쪽과 공용으로 쓰는
헬퍼라서 hospital 쪽에 남겨뒀습니다)
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from db import get_db_connection, admin_required
from hospital.routes import _save_uploaded_image
from admin import admin_bp


@admin_bp.route("/admin/department", methods=["GET", "POST"])
@admin_required
def admin_department():
    """
    진료과 목록 전용 페이지. 진료과명/소개/표시순서/사용여부를 보여줍니다.
    등록은 admin_department_create(), 상세/수정/삭제는 admin_department_detail()로 분리했습니다.

    ?q=검색어 로 요청하면 진료과명 또는 소개에 검색어가 포함된 것만 보여줍니다.
    (예: /admin/department?q=내과)
    """
    keyword = request.args.get("q", "").strip()

    conn = get_db_connection()
    with conn.cursor() as cur:
        if keyword:
            like_pattern = f"%{keyword}%"
            cur.execute(
                """SELECT * FROM departments
                   WHERE dept_name LIKE %s OR dept_description LIKE %s
                   ORDER BY display_order, dept_id""",
                (like_pattern, like_pattern),
            )
        else:
            cur.execute("SELECT * FROM departments ORDER BY display_order, dept_id")
        departments = cur.fetchall()
    conn.close()
    return render_template("admin_department.html", departments=departments, keyword=keyword)


@admin_bp.route("/admin/department/reorder", methods=["POST"])
@admin_required
def admin_department_reorder():
    """
    진료과 목록 화면에서 드래그로 순서를 바꾼 뒤 호출되는 API.
    JSON 형식으로 { "order": [dept_id, dept_id, ...] } 를 받아서,
    배열에 나열된 순서 그대로 display_order를 1, 2, 3...으로 다시 매깁니다.

    화면 새로고침 없이 fetch()로 호출되므로, 성공/실패를 JSON으로만 응답합니다.
    (admin_department.js 참고)
    """
    data = request.get_json(silent=True) or {}
    dept_ids = data.get("order", [])

    if not dept_ids or not isinstance(dept_ids, list):
        return jsonify(success=False, message="순서 정보가 없습니다."), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for index, dept_id in enumerate(dept_ids, start=1):
                cur.execute(
                    "UPDATE departments SET display_order=%s WHERE dept_id=%s",
                    (index, dept_id),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        return jsonify(success=False, message="순서 저장 중 오류가 발생했습니다."), 500

    conn.close()
    return jsonify(success=True)


@admin_bp.route("/admin/department/create", methods=["GET", "POST"])
@admin_required
def admin_department_create():
    """진료과 등록 전용 페이지."""
    if request.method == "POST":
        dept_name = request.form["dept_name"].strip()

        conn = get_db_connection()

        # 진료과명 중복 체크
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM departments WHERE dept_name=%s", (dept_name,))
            already_exists = cur.fetchone()["cnt"] > 0

        if already_exists:
            conn.close()
            flash(f"'{dept_name}' 진료과는 이미 등록되어 있습니다.")
            # 입력했던 내용을 그대로 다시 보여줌 (처음부터 다시 입력하지 않도록)
            return render_template(
                "admin_department_create.html",
                form_data={
                    "dept_name": dept_name,
                    "dept_description": request.form.get("dept_description", ""),
                    "dept_description": request.form.get("dept_description", ""),
                    "display_order": request.form.get("display_order", ""),
                },
            )

        # 이미지는 파일 업로드가 우선이고, 파일을 안 올렸으면 직접 입력한 경로 텍스트를 사용
        uploaded_path = _save_uploaded_image(request.files.get("dept_image_file"), "departments")
        dept_image = uploaded_path or request.form.get("dept_image")

        # 표시순서를 안 적었으면 맨 뒤에 붙도록 현재 최댓값+1을 사용
        display_order = request.form.get("display_order", "").strip()
        if not display_order:
            with conn.cursor() as cur:
                cur.execute("SELECT COALESCE(MAX(display_order), 0) AS max_order FROM departments")
                display_order = cur.fetchone()["max_order"] + 1

        is_active = 1 if request.form.get("is_active") == "on" else 0

        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO departments
                   (dept_name, dept_description, dept_image, display_order, is_active)
                   VALUES (%s, %s, %s, %s, %s)""",
                (dept_name, request.form.get("dept_description"), dept_image, display_order, is_active),
            )
        conn.commit()
        conn.close()
        flash("진료과가 등록되었습니다.")
        return redirect(url_for("admin.admin_department"))

    return render_template("admin_department_create.html", form_data={})


@admin_bp.route("/admin/department/<int:dept_id>", methods=["GET", "POST"])
@admin_required
def admin_department_detail(dept_id):
    """
    진료과 상세 - 등록된 내용 확인 + 삭제.
    이미지 경로가 등록되어 있으면 실제 <img>로 미리보기를 보여줍니다.
    소속된 의료진 목록도 함께 보여주고, 의료진이 있으면 삭제를 막습니다.
    (departments 삭제 시 doctors가 ON DELETE CASCADE로 걸려있어서,
     의료진이 있는 채로 진료과를 지우면 그 의료진들과 관련 예약까지 전부 같이 삭제되기 때문)

    내용 수정은 admin_department_edit()에서 별도 페이지로 처리합니다.
    """
    conn = get_db_connection()

    if request.method == "POST":
        # 이 페이지에 남은 POST 동작은 "삭제"뿐입니다. (수정은 admin_department_edit로 분리됨)
        action = request.form.get("action")

        if action == "delete":
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS cnt FROM doctors WHERE dept_id=%s", (dept_id,))
                doctor_count = cur.fetchone()["cnt"]

            if doctor_count > 0:
                conn.close()
                flash(
                    f"이 진료과에 소속된 의료진이 {doctor_count}명 있어 삭제할 수 없습니다. "
                    f"의료진관리에서 먼저 소속을 옮기거나 삭제해주세요."
                )
                return redirect(url_for("admin.admin_department_detail", dept_id=dept_id))

            with conn.cursor() as cur:
                cur.execute("DELETE FROM departments WHERE dept_id=%s", (dept_id,))
            conn.commit()
            conn.close()
            flash("진료과가 삭제되었습니다.")
            return redirect(url_for("admin.admin_department"))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM departments WHERE dept_id=%s", (dept_id,))
        dept = cur.fetchone()

        doctors = []
        if dept:
            cur.execute(
                "SELECT doctor_id, doctor_name, specialty FROM doctors WHERE dept_id=%s ORDER BY doctor_name",
                (dept_id,),
            )
            doctors = cur.fetchall()
    conn.close()

    if not dept:
        flash("존재하지 않는 진료과입니다.")
        return redirect(url_for("admin.admin_department"))

    return render_template("admin_department_detail.html", dept=dept, doctors=doctors)


@admin_bp.route("/admin/department/<int:dept_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_department_edit(dept_id):
    """진료과 수정 전용 페이지."""
    conn = get_db_connection()

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM departments WHERE dept_id=%s", (dept_id,))
        dept = cur.fetchone()

    if not dept:
        conn.close()
        flash("존재하지 않는 진료과입니다.")
        return redirect(url_for("admin.admin_department"))

    if request.method == "POST":
        dept_name = request.form["dept_name"].strip()

        # 진료과명 중복 체크 (자기 자신은 제외)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM departments WHERE dept_name=%s AND dept_id!=%s",
                (dept_name, dept_id),
            )
            already_exists = cur.fetchone()["cnt"] > 0

        if already_exists:
            conn.close()
            flash(f"'{dept_name}' 진료과는 이미 등록되어 있습니다.")
            return redirect(url_for("admin.admin_department_edit", dept_id=dept_id))

        # 새 파일을 올렸으면 그걸 쓰고, 아니면 직접 입력한 경로 텍스트,
        # 그것도 비어있으면 기존 이미지를 그대로 유지
        uploaded_path = _save_uploaded_image(request.files.get("dept_image_file"), "departments")
        dept_image = uploaded_path or request.form.get("dept_image")

        display_order = request.form.get("display_order", "").strip() or 0
        is_active = 1 if request.form.get("is_active") == "on" else 0

        with conn.cursor() as cur:
            cur.execute(
                """UPDATE departments
                   SET dept_name=%s, dept_description=%s, dept_image=%s,
                       display_order=%s, is_active=%s
                   WHERE dept_id=%s""",
                (dept_name, request.form.get("dept_description"), dept_image,
                 display_order, is_active, dept_id),
            )
        conn.commit()
        conn.close()
        flash("진료과 정보가 수정되었습니다.")
        return redirect(url_for("admin.admin_department"))

    conn.close()
    return render_template("admin_department_edit.html", dept=dept)
