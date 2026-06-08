"""
User store — Postgres only.
Bảng users(id, username, password_hash, name, role, created_at).
"""
import uuid
import bcrypt
import psycopg

from config.settings import settings


def _conn():
    return psycopg.connect(settings.DATABASE_URL, autocommit=True)


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")


def _verify(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def init_table():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            TEXT PRIMARY KEY,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name          TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'user',
                created_at    TIMESTAMPTZ DEFAULT NOW()
            )
        """)
    print("[USER] Bang users da san sang.")


def seed_default_users():
    """Chèn user mặc định nếu bảng rỗng."""
    with _conn() as conn:
        row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        if row[0] > 0:
            return
        defaults = [
            (uuid.uuid4().hex, "admin", _hash("admin123"), "Admin",        "admin"),
            (uuid.uuid4().hex, "user1", _hash("user123"),  "Nguyen Van A", "user"),
        ]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO users (id, username, password_hash, name, role) VALUES (%s, %s, %s, %s, %s)",
                defaults,
            )
    print(f"[USER] Da seed {len(defaults)} user mac dinh.")


def verify_password(username: str, password: str):
    """Trả về dict user nếu credentials đúng, ngược lại None."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, name, role FROM users WHERE username = %s",
            (username,),
        ).fetchone()
    if row and _verify(password, row[2]):
        return {"id": row[0], "username": row[1], "name": row[3], "role": row[4]}
    return None


def get_by_id(user_id: str):
    with _conn() as conn:
        row = conn.execute(
            "SELECT id, username, name, role FROM users WHERE id = %s",
            (user_id,),
        ).fetchone()
    if row:
        return {"id": row[0], "username": row[1], "name": row[2], "role": row[3]}
    return None


def list_all():
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, username, name, role, created_at FROM users ORDER BY created_at"
        ).fetchall()
    return [
        {"id": r[0], "username": r[1], "name": r[2], "role": r[3], "created_at": str(r[4])}
        for r in rows
    ]


def create_user(username: str, password: str, name: str, role: str = "user") -> dict:
    uid = uuid.uuid4().hex
    with _conn() as conn:
        conn.execute(
            "INSERT INTO users (id, username, password_hash, name, role) VALUES (%s, %s, %s, %s, %s)",
            (uid, username, _hash(password), name, role),
        )
    return {"id": uid, "username": username, "name": name, "role": role}


def update_user(user_id: str, name: str = None, role: str = None, password: str = None):
    fields, vals = [], []
    if name is not None:
        fields.append("name = %s"); vals.append(name)
    if role is not None:
        fields.append("role = %s"); vals.append(role)
    if password is not None:
        fields.append("password_hash = %s"); vals.append(_hash(password))
    if not fields:
        return
    vals.append(user_id)
    with _conn() as conn:
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = %s", vals)


def delete_user(user_id: str):
    with _conn() as conn:
        conn.execute("DELETE FROM users WHERE id = %s", (user_id,))
