from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    query: str
    active_agent: Optional[str] = None

class AgentPromptRequest(BaseModel):
    user_id: str
    system_prompt: str

class CreateAgentRequest(BaseModel):
    user_id: str
    id: str
    name: str
    icon: str = "fa-laptop-code"
    description: str = ""
    welcome: str = ""
    system_prompt: str = ""

