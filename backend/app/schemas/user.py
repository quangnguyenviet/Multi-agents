from pydantic import BaseModel
from typing import Optional


class CreateUserRequest(BaseModel):
    username: str
    password: str
    name: str
    role: str = "user"


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
