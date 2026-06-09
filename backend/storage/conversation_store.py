"""
Conversation store — SQLAlchemy + Postgres.
Chỉ lưu metadata (id, user_id, title, timestamps).
Nội dung tin nhắn do LangGraph checkpointer giữ.
"""
import time
from core.database import SessionLocal
from models.conversation import Conversation


def upsert(conversation_id: str, user_id: str, title_seed: str = ""):
    now = time.time()
    title = (title_seed or "Cuộc trò chuyện mới").strip()[:60] or "Cuộc trò chuyện mới"
    with SessionLocal() as s:
        existing = s.get(Conversation, conversation_id)
        if existing:
            existing.updated_at = now
        else:
            s.add(Conversation(id=conversation_id, user_id=user_id,
                               title=title, created_at=now, updated_at=now))
        s.commit()


def list_for_user(user_id: str) -> list:
    with SessionLocal() as s:
        rows = (s.query(Conversation)
                .filter_by(user_id=user_id)
                .order_by(Conversation.updated_at.desc())
                .all())
        return [{"id": c.id, "title": c.title, "updated_at": c.updated_at} for c in rows]


def owner(conversation_id: str):
    with SessionLocal() as s:
        c = s.get(Conversation, conversation_id)
        return c.user_id if c else None


def delete(conversation_id: str, user_id: str) -> bool:
    with SessionLocal() as s:
        c = (s.query(Conversation)
             .filter_by(id=conversation_id, user_id=user_id)
             .first())
        if not c:
            return False
        s.delete(c)
        s.commit()
        return True
