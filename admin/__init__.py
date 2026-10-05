# -*- coding: utf-8 -*-
"""
admin 패키지
----------------------------------------------------------------------
관리자 메뉴(대시보드 / 회원관리 / 예약관리 / 게시판관리 / 공지사항관리 /
보안관제 / 진료과관리 / 의료진관리)의 라우트를 메뉴별 파일로 나눠서 관리합니다.

모든 관리자 라우트는 이 admin_bp 블루프린트 "하나"를 공유합니다.
그래야 URL(/admin/...)과 템플릿의 url_for("admin.xxx")가 예전과 동일하게 유지됩니다.
(진료과관리/의료진관리는 원래 hospital_bp 소속이었지만, 관리자 메뉴이므로
 이번에 admin_bp로 옮기고 엔드포인트 이름도 hospital.xxx -> admin.xxx로 바뀌었습니다.
 이에 맞춰 관련 템플릿의 url_for 호출도 함께 수정했습니다.)

파일 구성 (담당자는 기존 app.py 분담 기준):
  dashboard_routes.py   : 관리자 메인 대시보드            (/admin)                    - 양소정
  user_routes.py        : 회원관리                       (/admin/user)               - 양소정
  reservation_routes.py : 예약관리                       (/admin/reservation)        - 양소정
  board_routes.py       : 게시판관리                     (/admin/board)              - 양소정
  notice_routes.py      : 공지사항관리                   (/admin/notice)             - 양소정
  security_routes.py    : 보안관제(IP차단/로그인기록)     (/admin/security...)        - 백민욱
  department_routes.py  : 진료과관리                     (/admin/department...)      - 임주혁
  doctor_routes.py      : 의료진관리                     (/admin/doctor...)          - 임주혁

주의: 이 파일들이 실제로 라우트로 등록되려면, app_blueprint.py에서
"import admin.dashboard_routes" 처럼 각 파일이 반드시 한 번은 import되어야 합니다.
(admin_bp 객체만 가져오는 것으로는 부족하고, 파일 자체가 import되면서
 그 안의 @admin_bp.route(...) 데코레이터들이 실행되어야 라우트가 등록됩니다)
"""

from flask import Blueprint

admin_bp = Blueprint("admin", __name__)
