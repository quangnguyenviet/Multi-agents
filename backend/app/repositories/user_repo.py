"""
User repository — SQLAlchemy + Postgres.
"""
import uuid
import bcrypt
from app.db.session import SessionLocal
from app.db.models.user import User


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")


def _verify(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def _row(u: User) -> dict:
    return {"id": u.id, "username": u.username, "name": u.name, "role": u.role}


def seed_default_users():
    with SessionLocal() as s:
        if s.query(User).count() > 0:
            return
        defaults = [
            User(id=uuid.uuid4().hex, username="admin",
                 password_hash=_hash("admin123"), name="Admin", role="admin"),
            User(id=uuid.uuid4().hex, username="user1",
                 password_hash=_hash("user123"), name="Nguyen Van A", role="user"),
        ]
        s.add_all(defaults)
        s.commit()
    print(f"[USER] Da seed {len(defaults)} user mac dinh.")


def verify_password(username: str, password: str):
    with SessionLocal() as s:
        u = s.query(User).filter_by(username=username).first()
        if u and _verify(password, u.password_hash):
            return _row(u)
    return None


def get_by_id(user_id: str):
    with SessionLocal() as s:
        u = s.get(User, user_id)
        return _row(u) if u else None


def list_all():
    with SessionLocal() as s:
        users = s.query(User).order_by(User.created_at).all()
        return [{**_row(u), "created_at": str(u.created_at)} for u in users]


def create_user(username: str, password: str, name: str, role: str = "user") -> dict:
    uid = uuid.uuid4().hex
    with SessionLocal() as s:
        s.add(User(id=uid, username=username,
                   password_hash=_hash(password), name=name, role=role))
        s.commit()
    return {"id": uid, "username": username, "name": name, "role": role}


def update_user(user_id: str, name: str = None, role: str = None, password: str = None):
    with SessionLocal() as s:
        u = s.get(User, user_id)
        if not u:
            return
        if name is not None:
            u.name = name
        if role is not None:
            u.role = role
        if password is not None:
            u.password_hash = _hash(password)
        s.commit()


def delete_user(user_id: str):
    with SessionLocal() as s:
        u = s.get(User, user_id)
        if u:
            s.delete(u)
            s.commit()
