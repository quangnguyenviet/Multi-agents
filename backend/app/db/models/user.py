from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(String, primary_key=True)
    username      = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=True)
    role          = Column(String, nullable=False, default="user")
    created_at    = Column(DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc))
