# Lưu metadata các cuộc hội thoại theo user. Backend: SQLite (dev) | PostgreSQL (production).
# Nội dung tin nhắn do checkpointer giữ; bảng này chỉ giữ id/user/title/thời gian.
import os
import time

from config.settings import settings

_IS_PG = settings.DB_BACKEND == "postgres"
_PH = "%s" if _IS_PG else "?"  # placeholder theo dialect

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "conversations.db")


def _connect():
    if _IS_PG:
        import psycopg  # lazy import
        return psycopg.connect(settings.DATABASE_URL, autocommit=True)
    import sqlite3
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _run(sql: str, params=(), fetch: str = None):
    """Thực thi 1 câu SQL, đóng connection. fetch: 'all' | 'one' | None (trả rowcount)."""
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        if fetch == "all":
            result = cur.fetchall()
        elif fetch == "one":
            result = cur.fetchone()
        else:
            result = cur.rowcount
        if not _IS_PG:  # sqlite không autocommit; psycopg đã autocommit=True
            conn.commit()
        return result
    finally:
        conn.close()


def init_db():
    ts_type = "DOUBLE PRECISION" if _IS_PG else "REAL"
    _run(
        f"""CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            created_at {ts_type} NOT NULL,
            updated_at {ts_type} NOT NULL
        )"""
    )
    _run("CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id)")


def upsert(conversation_id: str, user_id: str, title_seed: str = ""):
    """Tạo mới (title = title_seed) nếu chưa có; nếu có rồi chỉ cập nhật updated_at."""
    now = time.time()
    title = (title_seed or "Cuộc trò chuyện mới").strip()[:60] or "Cuộc trò chuyện mới"
    _run(
        f"INSERT INTO conversations (id, user_id, title, created_at, updated_at) "
        f"VALUES ({_PH}, {_PH}, {_PH}, {_PH}, {_PH}) "
        f"ON CONFLICT (id) DO UPDATE SET updated_at = EXCLUDED.updated_at",
        (conversation_id, user_id, title, now, now),
    )


def list_for_user(user_id: str) -> list:
    rows = _run(
        f"SELECT id, title, updated_at FROM conversations WHERE user_id={_PH} ORDER BY updated_at DESC",
        (user_id,),
        fetch="all",
    )
    return [{"id": r[0], "title": r[1], "updated_at": r[2]} for r in rows]


def owner(conversation_id: str):
    row = _run(f"SELECT user_id FROM conversations WHERE id={_PH}", (conversation_id,), fetch="one")
    return row[0] if row else None


def delete(conversation_id: str, user_id: str) -> bool:
    rowcount = _run(
        f"DELETE FROM conversations WHERE id={_PH} AND user_id={_PH}",
        (conversation_id, user_id),
    )
    return rowcount > 0


init_db()
