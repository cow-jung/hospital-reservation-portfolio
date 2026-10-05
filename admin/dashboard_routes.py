# -*- coding: utf-8 -*-
"""
양소정 담당 - 관리자 메인 대시보드 (담당자 미지정 공통 화면)
로직은 기존 admin/routes.py와 동일하고, admin_bp를 admin 패키지(__init__.py)에서
가져다 쓰는 것만 바뀌었습니다.
"""

from flask import render_template
from db import get_db_connection, admin_required
from admin import admin_bp


@admin_bp.route("/admin")
@admin_required
def admin():
    """
    관리자 메인 대시보드.
    회원 수, 예약 건수 등 요약 현황을 조회해서 admin.html에 전달합니다.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role='user'")
        user_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM reservations")
        reservation_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM reservations WHERE status='대기'")
        pending_reservation_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM board")
        board_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM notice")
        notice_count = cur.fetchone()["cnt"]
    conn.close()

    return render_template(
        "admin.html",
        user_count=user_count,
        reservation_count=reservation_count,
        pending_reservation_count=pending_reservation_count,
        board_count=board_count,
        notice_count=notice_count,
    )
