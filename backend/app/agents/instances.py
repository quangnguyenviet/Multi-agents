from app.core.config import settings
from app.skills.registry import SkillRegistry
from app.skills.loader import load_skills_from_minio

skill_registry = SkillRegistry(
    ttl_seconds=settings.SKILLS_CACHE_TTL,
    fetch_fn=load_skills_from_minio,
)

skill_registry.warm()
