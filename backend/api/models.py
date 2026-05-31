from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    query: str
    active_agent: str

class CreateSkillRequest(BaseModel):
    user_id: str
    agent_id: str
    name: str
    description: str

class PublishSkillRequest(BaseModel):
    user_id: str
    agent_id: str
    skill_data: dict
