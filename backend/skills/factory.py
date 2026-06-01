# skill factory
import json
import hashlib
from datetime import datetime
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import settings
from .base import Skill, SkillType, Parameter, Permission

class SkillFactory:
    """User tự mô tả skill, AI sẽ tạo skill hoàn chỉnh"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=0.3
        )
        
    async def create_from_description(
        self, 
        user_description: str,
        agent_id: str,
        created_by: str
    ) -> Skill:
        """Tạo skill từ mô tả bằng ngôn ngữ tự nhiên"""
        
        prompt = f"""
Bạn là chuyên gia thiết kế Skill cho hệ thống Multi-Agent. Hãy chuyển mô tả sau thành cấu trúc Skill chuẩn.

MÔ TẢ CỦA USER:
{user_description}

YÊU CẦU: Hãy tạo một Skill với các thông tin sau (trả về định dạng JSON):

{{
    "name": "tên_skill_ngắn_gọn_bằng_tiếng_anh",
    "description": "mô tả ngắn về skill này làm gì, tối đa 100 từ",
    "skill_type": "query hoặc action hoặc transform hoặc validate",
    "parameters": [
        {{"name": "param1", "type": "string", "required": true, "description": "mô tả"}}
    ],
    "system_prompt": "prompt chi tiết hướng dẫn AI thực hiện skill này, bao gồm quy trình, công thức, ví dụ",
    "required_roles": ["employee", "accountant", "admin"],
    "keywords": ["từ_khóa1", "từ_khóa2", "từ_khóa3"],
    "examples": ["ví dụ câu hỏi 1", "ví dụ câu hỏi 2"]
}}

QUAN TRỌNG: 
- system_prompt phải đủ chi tiết để AI có thể tự thực thi
- required_roles chỉ gồm các role: employee, accountant, admin
- Trả về DUY NHẤT JSON, không có text nào khác
"""

        response = self.llm.invoke([
            SystemMessage(content="Bạn là chuyên gia tạo cấu trúc Skill. Chỉ trả về JSON hợp lệ."),
            HumanMessage(content=prompt)
        ])
        
        # Parse response
        raw_content = response.content.strip()
        
        # Hàm trích xuất JSON nằm giữa dấu ngoặc nhọn đầu tiên và cuối cùng
        def extract_json_block(text: str) -> str:
            first_brace = text.find("{")
            last_brace = text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                return text[first_brace:last_brace + 1]
            return text
            
        json_str = extract_json_block(raw_content)
        
        try:
            skill_data = json.loads(json_str)
        except json.JSONDecodeError as je:
            print(f"⚠️ Lỗi parse JSON từ phản hồi LLM. Phản hồi thô: {raw_content}")
            raise je
        
        # Tạo skill ID từ description
        skill_id = f"custom_{hashlib.md5(user_description.encode()).hexdigest()[:12]}"
        
        # Tạo skill object
        skill = Skill(
            id=skill_id,
            name=skill_data["name"],
            version="1.0.0",
            description=skill_data["description"],
            skill_type=SkillType(skill_data["skill_type"]),
            parameters=[Parameter(**p) for p in skill_data.get("parameters", [])],
            system_prompt=skill_data["system_prompt"],
            permission=Permission(required_roles=skill_data.get("required_roles", [])),
            examples=skill_data.get("examples", []),
            metadata={
                "keywords": skill_data.get("keywords", []),
                "created_by": created_by,
                "created_at": datetime.now().isoformat(),
                "user_description": user_description,
                "agent_id": agent_id
            },
            created_at=datetime.now(),
            created_by=created_by
        )
        
        return skill