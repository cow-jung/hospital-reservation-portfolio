# -*- coding: utf-8 -*-
"""
정고은 담당 - 문의 게시판 / 공지사항
로직은 기존 app.py와 동일하고, @app.route -> @board_bp.route 만 바뀌었습니다.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db_connection, login_required

board_bp = Blueprint("board", __name__)


@board_bp.route("/board")
def board():
    # ========== ▼ 게시글 목록 및 검색 기능 ▼ ==========
    # 작성자 이름을 같이 보여주기 위해 users와 JOIN."""
    # 1. 화면에서 보낸 검색 조건(search_type)과 검색어(search_keyword)를 가져옵니다.
    search_type = request.args.get("search_type")
    search_keyword = request.args.get("search_keyword")

    conn = get_db_connection()
    with conn.cursor() as cur:
        # 1. 첫 번째 if문 (검색어가 있는 경우)
        if search_keyword:
            keyword = f"%{search_keyword}%"

            # 1-1. 안쪽 if문 (이름 검색 vs 제목 검색)
            if search_type == "name":
                cur.execute(
                    """SELECT b.*, u.name, 
                              (SELECT COUNT(*) FROM board_comments c JOIN users cu ON c.user_id = cu.user_id WHERE c.board_id = b.board_id AND cu.role = 'admin') AS admin_reply_count,
                              (SELECT COUNT(*) FROM board_comments c WHERE c.board_id = b.board_id) AS comment_count
                       FROM board b
                       JOIN users u ON b.user_id = u.user_id
                       WHERE u.name LIKE %s
                       ORDER BY b.created_at DESC""",
                    (keyword,)
                )
            # 1-2. 안쪽 else문
            else:
                cur.execute(
                    """SELECT b.*, u.name, 
                              (SELECT COUNT(*) FROM board_comments c JOIN users cu ON c.user_id = cu.user_id WHERE c.board_id = b.board_id AND cu.role = 'admin') AS admin_reply_count,
                              (SELECT COUNT(*) FROM board_comments c WHERE c.board_id = b.board_id) AS comment_count
                       FROM board b
                       JOIN users u ON b.user_id = u.user_id
                       WHERE b.title LIKE %s
                       ORDER BY b.created_at DESC""",
                    (keyword,)
                )

        # 2. 바깥쪽 else문 (검색어가 없는 경우 - 첫 번째 if와 같은 세로줄에 위치!)
        else:
            # 여기도 안으로 한 번 들여쓰기를 해줍니다!
            cur.execute(
                """SELECT b.*, u.name, 
                          (SELECT COUNT(*) FROM board_comments c JOIN users cu ON c.user_id = cu.user_id WHERE c.board_id = b.board_id AND cu.role = 'admin') AS admin_reply_count,
                          (SELECT COUNT(*) FROM board_comments c WHERE c.board_id = b.board_id) AS comment_count
                   FROM board b
                   JOIN users u ON b.user_id = u.user_id
                   ORDER BY b.created_at DESC"""
            )

        posts = cur.fetchall()
    conn.close()
    return render_template("board.html", posts=posts)
    # ======================== ▲ 여기까지 ▲ ===========================


@board_bp.route("/board/write", methods=["GET", "POST"])
@login_required
def board_write():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        # ========== ▼ 비밀글 기능 ▼ ==========#
        # 체크박스가 선택되지 않았다면 기본값 0을 줍니다.
        is_secret = request.form.get("is_secret", 0)

        conn = get_db_connection()
        with conn.cursor() as cur:
            # ▼ 추가된 부분: is_secret 컬럼에도 값을 넣도록 SQL(INSERT) 수정
            cur.execute(
                "INSERT INTO board (user_id, title, content, is_secret) VALUES (%s, %s, %s, %s)",
                (session["user_id"], title, content, is_secret),
            )
            # ============= ▲ 여기까지 ▲ =============
        conn.commit()
        conn.close()
        return redirect(url_for("board.board"))

    return render_template("board_write.html")


@board_bp.route("/board/view/<int:board_id>", methods=["GET", "POST"])
def board_view(board_id):
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")

        # 1. 댓글 작성 기능 (첫 조건이므로 if로 시작합니다!)
        if action == "comment" and "user_id" in session:
            content = request.form["content"]
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO board_comments (board_id, user_id, content) VALUES (%s, %s, %s)",
                    (board_id, session["user_id"], content),
                )
            conn.commit()

        # ========== ▼ 2. 댓글 수정 기능 ▼ ==========
        elif action == "edit_comment":
            comment_id = request.form.get("comment_id")
            content = request.form.get("content")

            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE board_comments SET content=%s WHERE comment_id=%s AND user_id=%s",
                    (content, comment_id, session.get("user_id"))
                )
            conn.commit()
            flash("댓글이 수정되었습니다.")
        # ========== ▲ 여기까지 ▲ ==========

        # 3. 게시글 삭제 기능
        elif action == "delete":
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM board WHERE board_id=%s AND user_id=%s",
                    (board_id, session.get("user_id")),
                )
            conn.commit()
            conn.close()
            return redirect(url_for("board.board"))

        # ========== ▼ 4. 댓글 삭제 기능 ▼ ==========
        elif action == "delete_comment":
            comment_id = request.form.get("comment_id")
            with conn.cursor() as cur:
                # 관리자('admin')인 경우 작성자 확인 없이 무조건 삭제
                if session.get("role") == "admin":
                    cur.execute(
                        "DELETE FROM board_comments WHERE comment_id=%s",
                        (comment_id,)
                    )
                # 일반 회원인 경우 본인이 작성한 댓글만 삭제
                else:
                    cur.execute(
                        "DELETE FROM board_comments WHERE comment_id=%s AND user_id=%s",
                        (comment_id, session.get("user_id"))
                    )
            conn.commit()
        # ========== ▲ 여기까지 ▲ ==========

    with conn.cursor() as cur:
        # ========== ▼ 비밀글 및 조회수 기능 ▼ ==========
        # 1. 글 정보를 가장 먼저 가져옵니다. (비밀글 확인용)
        cur.execute(
            """SELECT b.*, u.name FROM board b
               JOIN users u ON b.user_id = u.user_id
               WHERE b.board_id=%s""",
            (board_id,),
        )
        post = cur.fetchone()

        # 2. 비밀글(is_secret == 1) 권한 검사
        if post["is_secret"] == 1:
            if "user_id" not in session or (session["user_id"] != post["user_id"] and session.get("role") != "admin"):
                flash("비밀글은 작성자와 관리자만 볼 수 있습니다.")
                conn.close()
                return redirect(url_for("board.board"))

        # 3. 권한 검사를 통과했으므로 DB의 조회수를 1 올립니다.
        cur.execute("UPDATE board SET view_count = view_count + 1 WHERE board_id=%s", (board_id,))
        conn.commit()

        # 4. 화면에 띄워줄 데이터(post)도 DB와 맞추기 위해 파이썬에서 1을 더해줍니다!
        # (이렇게 하면 밖으로 나갔을 때 조회수가 또 오르는 착시를 막을 수 있습니다)
        post["view_count"] += 1

        # 5. 댓글 목록을 가져옵니다
        cur.execute(
            """SELECT c.*, u.name FROM board_comments c
               JOIN users u ON c.user_id = u.user_id
               WHERE c.board_id=%s ORDER BY c.created_at ASC""",
            (board_id,),
        )
        comments = cur.fetchall()

    conn.close()
    return render_template("board_view.html", post=post, comments=comments)
    # ========== ▲ 여기까지 ▲ ==========

@board_bp.route("/notice")
def notice():
    # ========== ▼ 공지사항 목록 및 검색 기능 ▼ ==========
    search_keyword = request.args.get("search_keyword")

    conn = get_db_connection()
    with conn.cursor() as cur:
        if search_keyword:
            # 공지사항은 작성자가 따로 없으므로 '제목'으로만 검색합니다.
            keyword = f"%{search_keyword}%"
            cur.execute(
                "SELECT * FROM notice WHERE title LIKE %s ORDER BY created_at DESC",
                (keyword,)
            )
        else:
            cur.execute("SELECT * FROM notice ORDER BY created_at DESC")

        notices = cur.fetchall()
    conn.close()
    return render_template("notice.html", notices=notices)
    # ========== ▲ 여기까지 ▲ ==========


@board_bp.route("/notice/view/<int:notice_id>")
def notice_view(notice_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE notice SET view_count = view_count + 1 WHERE notice_id=%s", (notice_id,))
        conn.commit()
        cur.execute("SELECT * FROM notice WHERE notice_id=%s", (notice_id,))
        notice_item = cur.fetchone()
    conn.close()
    return render_template("notice_view.html", notice=notice_item)


# ========== ▼ 문의 게시판 수정 기능 ▼ ==========
@board_bp.route("/board/edit/<int:board_id>", methods=["GET", "POST"])
@login_required
def board_edit(board_id):
    conn = get_db_connection()

    # [POST] 사용자가 '수정 완료' 버튼을 눌렀을 때
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        is_secret = request.form.get("is_secret", 0)

        with conn.cursor() as cur:
            # 본인이 작성한 글만 수정되도록 user_id 조건을 반드시 포함합니다!
            cur.execute(
                "UPDATE board SET title=%s, content=%s, is_secret=%s WHERE board_id=%s AND user_id=%s",
                (title, content, is_secret, board_id, session.get("user_id"))
            )
        conn.commit()
        conn.close()
        # 수정이 완료되면 다시 해당 게시글 상세 보기 화면으로 이동합니다.
        return redirect(url_for("board.board_view", board_id=board_id))

    # [GET] 수정 화면에 처음 들어왔을 때 기존 데이터를 불러옵니다.
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM board WHERE board_id=%s", (board_id,))
        post = cur.fetchone()
    conn.close()

    # 글이 없거나, 접속한 사람이 작성자가 아니면 튕겨냅니다.
    if not post or post["user_id"] != session.get("user_id"):
        flash("글을 수정할 권한이 없습니다.")
        return redirect(url_for("board.board_view", board_id=board_id))

    # 기존 데이터(post)를 담아서 수정 폼 화면으로 보냅니다.
    return render_template("board_edit.html", post=post)

# ========== ▲ 여기까지 ▲ ==========