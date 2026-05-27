# base agent class
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import settings
from skills.registry import SkillRegistry
from skills.base import Skill

class BaseAgent:
    """Agent cơ bản có khả năng sử dụng skills"""
    
    def __init__(self, name: str, agent_id: str, skill_registry: SkillRegistry):
        self.name = name
        self.agent_id = agent_id
        self.skill_registry = skill_registry
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=0.2
        )
        self.enabled_skill_ids: List[str] = []
        
    def enable_skill(self, skill_id: str):
        """Bật một skill cho agent này"""
        if skill_id not in self.enabled_skill_ids:
            self.enabled_skill_ids.append(skill_id)
            print(f"✅ Enabled skill {skill_id} for agent {self.name}")
            
    def disable_skill(self, skill_id: str):
        """Tắt skill"""
        if skill_id in self.enabled_skill_ids:
            self.enabled_skill_ids.remove(skill_id)
            print(f"❌ Disabled skill {skill_id} for agent {self.name}")
    
    def get_available_skills(self, user_role: str) -> List[Skill]:
        """Lấy danh sách skills khả dụng (đã bật + có quyền)"""
        all_skills = self.skill_registry.get_skills_for_agent(self.agent_id, user_role)
        return [s for s in all_skills if s.id in self.enabled_skill_ids]
    
    def _select_best_skill(self, query: str, user_role: str) -> Optional[Skill]:
        """Chọn skill phù hợp nhất cho câu hỏi"""
        # Tìm skills theo từ khóa
        relevant = self.skill_registry.find_by_keywords(query, self.agent_id, user_role)
        
        if not relevant:
            return None
            
        # Chọn skill có điểm cao nhất
        best_skill, best_score = relevant[0]
        print(f"🎯 Selected skill: {best_skill.name} (score: {best_score})")
        return best_skill
    
    async def process(self, query: str, user_role: str, context: Dict = None) -> str:
        """Xử lý câu hỏi - chọn và thực thi skill phù hợp"""
        
        # 1. Tìm skill phù hợp
        selected_skill = self._select_best_skill(query, user_role)
        
        if not selected_skill:
            # 2. Fallback: dùng prompt mặc định
            return await self._default_response(query, context)
        
        # 3. Thực thi skill được chọn
        return await self._execute_skill(selected_skill, query, context)
    
    async def _execute_skill(self, skill: Skill, query: str, context: Dict) -> str:
        """Thực thi một skill cụ thể"""
        
        skill_prompt = f"""
{skill.system_prompt}

Dữ liệu context (nếu có):
{context if context else 'Không có context bổ sung'}

Câu hỏi của người dùng: {query}

Hãy trả lời dựa trên hướng dẫn của skill này. Trả lời bằng tiếng Việt, thân thiện và chuyên nghiệp.
"""
        
        response = self.llm.invoke([
            SystemMessage(content="Bạn là trợ lý AI thực thi skill được chỉ định."),
            HumanMessage(content=skill_prompt)
        ])
        
        return response.content
    
    async def _default_response(self, query: str, context: Dict) -> str:
        """Phản hồi mặc định khi không có skill phù hợp"""
        response = self.llm.invoke([
            SystemMessage(content=f"Bạn là {self.name} agent. Hãy trả lời câu hỏi của người dùng một cách hữu ích."),
            HumanMessage(content=query)
        ])
        return response.content