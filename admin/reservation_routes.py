# -*- coding: utf-8 -*-
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
                cur.execute("UPDATE reservations SET status=%s WHERE reservation_id=%s",
                            (request.form["status"], reservation_id))
            elif action == "delete":
                cur.execute("DELETE FROM reservations WHERE reservation_id=%s", (reservation_id,))
        conn.commit()

    keyword = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    where, params = [], []
    if keyword:
        like = f"%{keyword}%"
        where.append("(u.name LIKE %s OR dept.dept_name LIKE %s OR doc.doctor_name LIKE %s OR r.memo LIKE %s)")
        params.extend([like, like, like, like])
    if status in ("대기", "확정", "취소"):
        where.append("r.status=%s")
        params.append(status)
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""

    with conn.cursor() as cur:
        cur.execute(f"""SELECT r.*, u.name AS user_name, doc.doctor_name, dept.dept_name FROM reservations r
                        JOIN users u ON r.user_id=u.user_id
                        JOIN doctors doc ON r.doctor_id=doc.doctor_id
                        JOIN departments dept ON doc.dept_id=dept.dept_id
                        {where_sql}
                        ORDER BY r.reservation_date DESC, r.reservation_time DESC""", params)
        reservations = cur.fetchall()
    conn.close()
    return render_template("admin_reservation.html", reservations=reservations, keyword=keyword, status=status)
