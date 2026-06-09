from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    user_id: str
    query: str
    active_agent: Optional[str] = None
