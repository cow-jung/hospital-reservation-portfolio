# -*- coding: utf-8 -*-
"""
백민욱 담당 - 관리자: 보안관제 (IP/CIDR 차단, 로그인 기록)
로직은 기존 admin/routes.py와 동일합니다.
"""

from flask import render_template, request, redirect, url_for, flash
from db import get_db_connection, admin_required
from admin import admin_bp


@admin_bp.route("/admin/security")
@admin_required
def admin_security():
    """
    보안관제 페이지.
    현재 등록된 IP 차단 규칙 목록과, 최근 로그인 시도 기록(성공/실패)을 보여줍니다.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM security_ip_rules ORDER BY created_at DESC")
        ip_rules = cur.fetchall()

        cur.execute("SELECT * FROM security_logs ORDER BY created_at DESC LIMIT 200")
        logs = cur.fetchall()
    conn.close()
    return render_template("security_logs.html", ip_rules=ip_rules, logs=logs)


@admin_bp.route("/admin/security/ip/add", methods=["POST"])
@admin_required
def admin_security_ip_add():
    """새 IP/CIDR 차단 규칙을 등록합니다."""
    network = request.form["network"].strip()
    description = request.form.get("description", "")
    block_scope = request.form.get("block_scope", "login")

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO security_ip_rules (network, block_scope, description, enabled)
               VALUES (%s, %s, %s, 1)""",
            (network, block_scope, description),
        )
    conn.commit()
    conn.close()
    flash("차단 규칙이 등록되었습니다.")
    return redirect(url_for("admin.admin_security"))


@admin_bp.route("/admin/security/ip/<int:rule_id>/toggle", methods=["POST"])
@admin_required
def admin_security_ip_toggle(rule_id):
    """차단 규칙의 활성/비활성 상태를 반전시킵니다."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE security_ip_rules SET enabled = NOT enabled WHERE rule_id=%s",
            (rule_id,),
        )
    conn.commit()
    conn.close()
    return redirect(url_for("admin.admin_security"))


@admin_bp.route("/admin/security/ip/<int:rule_id>/delete", methods=["POST"])
@admin_required
def admin_security_ip_delete(rule_id):
    """차단 규칙을 삭제합니다."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM security_ip_rules WHERE rule_id=%s", (rule_id,))
    conn.commit()
    conn.close()
    flash("차단 규칙이 삭제되었습니다.")
    return redirect(url_for("admin.admin_security"))


@admin_bp.route("/admin/security/logs/clear", methods=["POST"])
@admin_required
def admin_security_logs_clear():
    """로그인 기록을 전부 삭제합니다."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM security_logs")
    conn.commit()
    conn.close()
    flash("로그인 기록이 초기화되었습니다.")
    return redirect(url_for("admin.admin_security"))
