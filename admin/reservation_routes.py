# -*- coding: utf-8 -*-
"""
양소정 담당 - 관리자: 예약관리
로직은 기존 admin/routes.py와 동일합니다.
"""

from flask import render_template, request
from db import get_db_connection, admin_required
from admin import admin_bp


@admin_bp.route("/admin/reservation", methods=["GET", "POST"])
@admin_required
def admin_reservation():
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
