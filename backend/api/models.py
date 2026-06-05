from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    query: str
    active_agent: Optional[str] = None

class CreateSkillRequest(BaseModel):
    user_id: str
    agent_id: str
    name: str
    description: str

class PublishSkillRequest(BaseModel):
    user_id: str
    agent_id: str
    skill_data: dict

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

class CreateToolRequest(BaseModel):
    user_id: str
    id: str
    icon: str = "fa-globe"
    description: str = ""
    agent: str = "system_admin"
    category: str = "Database Query"

class UpdateToolRequest(BaseModel):
    user_id: str
    active: Optional[bool] = None
    description: Optional[str] = None
    category: Optional[str] = None
    agent: Optional[str] = None
