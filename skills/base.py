# base class for skills
from typing import Dict, List, Optional, Callable, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class SkillType(str, Enum):
    QUERY = "query"          # Truy vấn dữ liệu
    ACTION = "action"        # Hành động (gửi mail, tạo ticket...)
    TRANSFORM = "transform"  # Biến đổi dữ liệu
    VALIDATE = "validate"    # Kiểm tra hợp lệ

class Parameter(BaseModel):
    name: str
    type: Literal["string", "number", "boolean", "date", "array"]
    required: bool = True
    description: str
    example: Optional[str] = None

class Permission(BaseModel):
    required_roles: List[str] = Field(default_factory=list)  # employee, accountant, admin
    required_departments: List[str] = Field(default_factory=list)
    max_access_level: int = 1  # 1: self, 2: department, 3: all

class Skill(BaseModel):
    """Skill định nghĩa một khả năng cụ thể của Agent"""
    id: str
    name: str
    version: str = "1.0.0"
    description: str
    skill_type: SkillType
    parameters: List[Parameter] = Field(default_factory=list)
    system_prompt: str
    permission: Permission = Field(default_factory=Permission)
    examples: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Runtime fields
    created_at: Optional[datetime] = None
    created_by: str = "system"
    
    def dict(self):
        return self.model_dump()