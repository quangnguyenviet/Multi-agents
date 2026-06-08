# backend/agents/instances.py
from config.settings import settings
from skills.registry import SkillRegistry
from skills.loader import load_skills_from_minio

skill_registry = SkillRegistry(
    ttl_seconds=settings.SKILLS_CACHE_TTL,
    fetch_fn=load_skills_from_minio,
)

# Nạp ngay lúc startup + log; lỗi MinIO không làm sập server (registry rỗng, tự thử lại sau TTL)
skill_registry.warm()
