# backend/agents/instances.py
from skills.registry import SkillRegistry
from skills.factory import SkillFactory
from skills.loader import SkillLoader

skill_registry = SkillRegistry()
skill_factory = SkillFactory()

SkillLoader.load_custom_skills(skill_registry)
