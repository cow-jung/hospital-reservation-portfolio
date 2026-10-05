# -*- coding: utf-8 -*-
"""
db.py
- 모든 블루프린트가 공통으로 가져다 쓰는 부분을 여기에 모아둡니다.
- get_db_connection() : DB 연결
- login_required / admin_required : 로그인 · 관리자 권한 체크 데코레이터

기존 app.py에 있던 것과 내용은 완전히 동일합니다.
(블루프린트로 나누면서 여러 파일에서 같이 써야 하는 부분만 이 파일로 옮긴 것)
"""

import os
import ipaddress
from functools import wraps
from flask import session, flash, redirect, url_for
import pymysql

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"],
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("로그인이 필요합니다.")
            # auth 블루프린트 안의 login 함수를 가리킴 -> "auth.login"
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("관리자만 접근할 수 있습니다.")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped


def get_client_ip(req):
    """
    요청을 보낸 클라이언트의 IP 주소를 가져옵니다.
    프록시(리버스 프록시, 로드밸런서)를 거치는 경우 X-Forwarded-For 헤더에
    실제 클라이언트 IP가 담겨 오므로, 있으면 그 값을 우선 사용합니다.
    """
    forwarded = req.headers.get("X-Forwarded-For", "")
    if forwarded:
        # "클라이언트IP, 프록시1IP, 프록시2IP" 형태이므로 맨 앞 값만 사용
        return forwarded.split(",")[0].strip()
    return req.remote_addr


def is_ip_blocked(ip_address, scope):
    """
    security_ip_rules 테이블을 확인해서, 주어진 ip_address가
    scope('login' 또는 'site')에 해당하는 활성화된 차단 규칙에 걸리는지 확인합니다.

    scope='site'  로 호출하면 사이트 전체 차단 규칙만 확인
    scope='login' 으로 호출하면 로그인 차단 규칙만 확인
    ('site' 차단은 로그인 여부와 상관없이 전체 접속 자체를 막는 규칙이므로,
     로그인 화면에서는 site 차단과 login 차단을 모두 확인해야 함 - login() 쪽에서 별도로 처리)
    """
    if not ip_address:
        return False

    try:
        client_ip_obj = ipaddress.ip_address(ip_address)
    except ValueError:
        # IP 형식이 아니면(예: 테스트 환경의 '::1' 등 처리 불가 값) 차단하지 않음
        return False

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT network FROM security_ip_rules WHERE block_scope=%s AND enabled=1",
                (scope,),
            )
            rules = cur.fetchall()
    finally:
        conn.close()

    for rule in rules:
        network_text = rule["network"].strip()
        try:
            # CIDR 표기가 아니면(예: 192.168.2.30) /32 단일 IP로 취급
            if "/" not in network_text:
                network_text += "/32"
            network_obj = ipaddress.ip_network(network_text, strict=False)
            if client_ip_obj in network_obj:
                return True
        except ValueError:
            # 잘못 입력된 네트워크 값은 건너뜀
            continue

    return False
