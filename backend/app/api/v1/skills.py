from fastapi import APIRouter
from app.agents import skill_registry

router = APIRouter()


@router.get("/skills")
async def get_skills():
    """Trả về catalog skill (name + description). Nội dung đầy đủ nạp on-demand qua tool load_skill."""
    return [
        {"name": s.name, "description": s.description}
        for s in skill_registry.list_all()
    ]
