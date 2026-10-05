# -*- coding: utf-8 -*-
"""
유민정 담당 - 병원소개 / 진료과·의료진 조회
로직은 기존 app.py와 동일하고, @app.route -> @hospital_bp.route 만 바뀌었습니다.

"""
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db_connection, admin_required

hospital_bp = Blueprint("hospital", __name__)

# 업로드로 허용할 이미지 확장자
# (admin_routes.py의 등록/수정 화면에서 이미지 업로드할 때도 이 값을 그대로 가져다 씁니다)
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp"}

def _get_extension(filename):
    if "." not in filename:
        return None
    return filename.rsplit(".", 1)[1].lower()


def _save_uploaded_image(file_storage, subfolder):
    """
    업로드된 이미지 파일을 static/images/<subfolder>/ 에 저장하고,
    DB에 저장할 상대경로("images/<subfolder>/파일명")를 돌려줍니다.
    파일이 없거나 이미지 확장자가 아니면 None을 돌려줍니다.

    주의: werkzeug의 secure_filename()은 한글 등 비ASCII 문자를 전부 지워버려서
    "새진료과.svg" 같은 한글 파일명이 "svg"처럼 통째로 날아가는 문제가 있습니다.
    그래서 원본 파일명을 그대로 쓰지 않고, 확장자만 남기고 무작위 이름을
    새로 만들어서 저장합니다. (한글 파일명 문제 방지 + 파일명 중복 방지 둘 다 해결)
    """
    if not file_storage or file_storage.filename == "":
        return None

    ext = _get_extension(file_storage.filename)
    if ext is None or ext not in ALLOWED_IMAGE_EXTENSIONS:
        flash("이미지 파일(png, jpg, jpeg, gif, svg, webp)만 업로드할 수 있습니다.")
        return None

    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.root_path, "static", "images", subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, filename)
    file_storage.save(save_path)

    return f"images/{subfolder}/{filename}"

# 병원소개
@hospital_bp.route("/hospital")
def hospital():
    return render_template("hospital.html")

# =====================================================================
# 1. 진료과 전체 조회
# =====================================================================

@hospital_bp.route("/department")
def department():

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM departments
                ORDER BY dept_id
                """
            )

            departments = cur.fetchall()

    finally:
        conn.close()

    return render_template(
        "department.html",
        departments=departments
    )


# =====================================================================
# 2. 진료과 상세 조회
# =====================================================================

@hospital_bp.route("/department/<int:dept_id>")
def department_detail(dept_id):

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:

            # 선택한 진료과 정보
            cur.execute(
                """
                SELECT 
                    dept_id,
                    dept_name,
                    dept_description,
                    dept_image
                    
                FROM departments
                
                WHERE dept_id = %s
                """,
                (dept_id,)
            )

            department = cur.fetchone()


            # 해당 진료과 의료진
            cur.execute(
                """
                SELECT *
                FROM doctors
                WHERE dept_id = %s
                ORDER BY doctor_id
                """,
                (dept_id,)
            )

            doctors = cur.fetchall()

    finally:
        conn.close()


    return render_template(
        "department_detail.html",
        department=department,
        doctors=doctors
    )


# =====================================================================
# 3. 의료진 전체 조회
# =====================================================================

@hospital_bp.route("/doctor")
def doctor():

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    d.doctor_id,
                    d.doctor_name,
                    d.dept_id,
                    d.specialty,
                    d.profile,
                    d.photo,
                    d.work_hours,
                    dept.dept_name

                FROM doctors d

                JOIN departments dept
                    ON d.dept_id = dept.dept_id

                ORDER BY
                    d.doctor_name
                """
            )

            doctors = cur.fetchall()

    finally:
        conn.close()


    return render_template(
        "doctor.html",
        doctors=doctors
    )


