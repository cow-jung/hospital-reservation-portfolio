# -*- coding: utf-8 -*-
"""양소정 담당 - 관리자: 게시판관리"""

from flask import render_template, request
from db import get_db_connection, admin_required
from admin import admin_bp


@admin_bp.route("/admin/board", methods=["GET", "POST"])
@admin_required
def admin_board():
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "delete_post":
                cur.execute("DELETE FROM board WHERE board_id=%s", (request.form["board_id"],))
            elif action == "delete_comment":
                cur.execute("DELETE FROM board_comments WHERE comment_id=%s", (request.form["comment_id"],))
        conn.commit()

    keyword = request.args.get("q", "").strip()
    with conn.cursor() as cur:
        if keyword:
            like_pattern = f"%{keyword}%"
            cur.execute(
                """SELECT b.*, u.name FROM board b
                   JOIN users u ON b.user_id = u.user_id
                   WHERE b.title LIKE %s OR b.content LIKE %s OR u.name LIKE %s
                   ORDER BY b.created_at DESC""",
                (like_pattern, like_pattern, like_pattern),
            )
        else:
            cur.execute(
                """SELECT b.*, u.name FROM board b
                   JOIN users u ON b.user_id = u.user_id
                   ORDER BY b.created_at DESC"""
            )
        posts = cur.fetchall()
    conn.close()
    return render_template("admin_board.html", posts=posts, keyword=keyword)
