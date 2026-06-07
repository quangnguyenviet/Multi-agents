# Skill registry — tra cứu skill theo name (phẳng, không phân biệt agent)
from typing import Dict, List, Optional
from .base import Skill


class SkillRegistry:
    """Quản lý tất cả skills trong hệ thống."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill):
        """Đăng ký skill (key theo name)."""
        self._skills[skill.name] = skill
        print(f"[SKILL] Registered: {skill.name}")

    def get(self, name: str) -> Optional[Skill]:
        """Lấy skill theo name."""
        return self._skills.get(name)

    def list_all(self) -> List[Skill]:
        """Liệt kê tất cả skills."""
        return list(self._skills.values())
