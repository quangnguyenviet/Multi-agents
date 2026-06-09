from sqlalchemy import Column, String, Float
from app.db.models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id         = Column(String, primary_key=True)
    user_id    = Column(String, nullable=False, index=True)
    title      = Column(String, nullable=False, default="")
    created_at = Column(Float, nullable=False)
    updated_at = Column(Float, nullable=False)
