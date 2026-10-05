# -*- coding: utf-8 -*-
"""
양소정 담당 - 관리자: 공지사항관리

진료과 관리(admin/department_routes.py)와 같은 방식으로 목록/등록/상세/수정
4개 페이지로 분리했습니다.
- 목록(admin_notice)        : 제목 목록만 보여주고, 제목을 클릭하면 상세로 이동
- 등록(admin_notice_create) : 제목/내용/구분(일반·긴급)을 입력해서 새로 등록
- 상세(admin_notice_detail) : 제목/내용/구분을 예쁘게 보여주고, 삭제는 확인 모달을 거쳐 처리
- 수정(admin_notice_edit)   : 상세에서 [수정] 버튼을 눌러야만 제목/내용/구분을 바꿀 수 있음
"""

from flask import render_template, request, redirect, url_for, flash
from db import get_db_connection, admin_required
from admin import admin_bp


@admin_bp.route("/admin/notice", methods=["GET"])
@admin_required
def admin_notice():
    """공지사항 목록 전용 페이지. 제목을 클릭하면 상세 페이지로 이동합니다."""
    keyword = request.args.get("q", "").strip()
    notice_type = request.args.get("type", "").strip()
    where, params = [], []
    if keyword:
        like = f"%{keyword}%"
        where.append("(title LIKE %s OR content LIKE %s)")
        params.extend([like, like])
    if notice_type in ("일반", "긴급"):
        where.append("notice_type=%s")
        params.append(notice_type)
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM notice{where_sql} ORDER BY created_at DESC", params)
        notices = cur.fetchall()
    conn.close()
    return render_template("admin_notice.html", notices=notices, keyword=keyword, notice_type=notice_type)


@admin_bp.route("/admin/notice/create", methods=["GET", "POST"])
@admin_required
def admin_notice_create():
    """공지사항 등록 전용 페이지."""
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form.get("content", "").strip()
        notice_type = request.form.get("notice_type")
        if notice_type not in ("일반", "긴급"):
            notice_type = "일반"

        if not title or not content:
            flash("제목과 내용을 모두 입력해주세요.")
            return render_template(
                "admin_notice_create.html",
                form_data={"title": title, "content": content, "notice_type": notice_type},
            )

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notice (title, content, notice_type) VALUES (%s, %s, %s)",
                (title, content, notice_type),
            )
        conn.commit()
        conn.close()
        flash("공지사항이 등록되었습니다.")
        return redirect(url_for("admin.admin_notice"))

    return render_template("admin_notice_create.html", form_data={"notice_type": "일반"})


@admin_bp.route("/admin/notice/<int:notice_id>", methods=["GET", "POST"])
@admin_required
def admin_notice_detail(notice_id):
    """
    공지사항 상세 - 제목/내용/구분을 보여주고, 삭제만 처리합니다.
    (내용 수정은 admin_notice_edit()에서 별도 페이지로 처리)
    """
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            with conn.cursor() as cur:
                cur.execute("DELETE FROM notice WHERE notice_id=%s", (notice_id,))
            conn.commit()
            conn.close()
            flash("공지사항이 삭제되었습니다.")
            return redirect(url_for("admin.admin_notice"))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notice WHERE notice_id=%s", (notice_id,))
        notice = cur.fetchone()
    conn.close()

    if not notice:
        flash("존재하지 않는 공지사항입니다.")
        return redirect(url_for("admin.admin_notice"))

    return render_template("admin_notice_detail.html", notice=notice)


@admin_bp.route("/admin/notice/<int:notice_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_notice_edit(notice_id):
    """공지사항 수정 전용 페이지."""
    conn = get_db_connection()

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notice WHERE notice_id=%s", (notice_id,))
        notice = cur.fetchone()

    if not notice:
        conn.close()
        flash("존재하지 않는 공지사항입니다.")
        return redirect(url_for("admin.admin_notice"))

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form.get("content", "").strip()
        notice_type = request.form.get("notice_type")
        if notice_type not in ("일반", "긴급"):
            notice_type = "일반"

        if not title or not content:
            conn.close()
            flash("제목과 내용을 모두 입력해주세요.")
            return redirect(url_for("admin.admin_notice_edit", notice_id=notice_id))

        with conn.cursor() as cur:
            cur.execute(
                "UPDATE notice SET title=%s, content=%s, notice_type=%s WHERE notice_id=%s",
                (title, content, notice_type, notice_id),
            )
        conn.commit()
        conn.close()
        flash("공지사항이 수정되었습니다.")
        return redirect(url_for("admin.admin_notice_detail", notice_id=notice_id))

    conn.close()
    return render_template("admin_notice_edit.html", notice=notice)
