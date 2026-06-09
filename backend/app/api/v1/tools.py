from fastapi import APIRouter
from app.agents.llm_node import TOOLS

router = APIRouter()


@router.get("/tools")
async def get_tools():
    """Return tools derived from the actual TOOLS list bound to the LLM."""
    return [
        {
            "id": t.name,
            "name": t.name,
            "description": t.description,
            "active": True,
        }
        for t in TOOLS
    ]
