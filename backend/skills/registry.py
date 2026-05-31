# skill registry
from typing import Dict, List, Optional
from .base import Skill

class SkillRegistry:
    """Quản lý tất cả skills trong hệ thống"""
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._agent_skills: Dict[str, List[str]] = {}  # agent_id -> list skill_ids
        
    def register(self, skill: Skill, agent_ids: List[str]):
        """Đăng ký skill cho một hoặc nhiều agent"""
        self._skills[skill.id] = skill
        for agent_id in agent_ids:
            if agent_id not in self._agent_skills:
                self._agent_skills[agent_id] = []
            if skill.id not in self._agent_skills[agent_id]:
                self._agent_skills[agent_id].append(skill.id)
        print(f"✅ Registered skill: {skill.name} (id: {skill.id}) for agents: {agent_ids}")
        
    def get(self, skill_id: str) -> Optional[Skill]:
        """Lấy skill theo ID"""
        return self._skills.get(skill_id)
    
    def get_skills_for_agent(self, agent_id: str, user_role: str = None) -> List[Skill]:
        """Lấy danh sách skill mà agent có thể dùng, có filter theo quyền"""
        skill_ids = self._agent_skills.get(agent_id, [])
        skills = []
        for skill_id in skill_ids:
            skill = self._skills.get(skill_id)
            if skill:
                if user_role and skill.permission.required_roles:
                    if user_role not in skill.permission.required_roles:
                        continue
                skills.append(skill)
        return skills
    
    def find_by_keywords(self, query: str, agent_id: str, user_role: str) -> List[tuple]:
        """Tìm skill phù hợp với câu hỏi (dùng từ khóa đơn giản)"""
        skills = self.get_skills_for_agent(agent_id, user_role)
        query_lower = query.lower()
        
        relevant = []
        for skill in skills:
            score = 0
            # Check keywords in metadata
            keywords = skill.metadata.get("keywords", [])
            for kw in keywords:
                if kw.lower() in query_lower:
                    score += 1
            
            # Check examples
            for example in skill.examples:
                if example.lower() in query_lower:
                    score += 2  # Examples quan trọng hơn
            
            if score > 0:
                relevant.append((skill, score))
        
        # Sort by score descending
        relevant.sort(key=lambda x: x[1], reverse=True)
        return relevant
    
    def list_all(self) -> List[Skill]:
        """Liệt kê tất cả skills"""
        return list(self._skills.values())

    def remove(self, skill_id: str):
        """Xóa skill khỏi Registry và tất cả Agent tương ứng"""
        if skill_id in self._skills:
            del self._skills[skill_id]
        for agent_id in self._agent_skills:
            if skill_id in self._agent_skills[agent_id]:
                self._agent_skills[agent_id].remove(skill_id)
        print(f"❌ Removed skill from registry: {skill_id}")