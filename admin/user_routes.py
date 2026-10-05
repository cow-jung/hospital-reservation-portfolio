# -*- coding: utf-8 -*-
"""
양소정 담당 - 관리자: 회원관리
로직은 기존 admin/routes.py와 동일합니다.
"""

from flask import render_template, request
from db import get_db_connection, admin_required
from admin import admin_bp


@admin_bp.route("/admin/user", methods=["GET", "POST"])
@admin_required
def admin_user():
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
        cur.execute("SELECT * FROM users WHERE role='user'")
        users = cur.fetchall()
    conn.close()
    return render_template("admin_user.html", users=users)
