import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Form, File, UploadFile
from langchain_core.messages import ToolMessage
from data import database as db
from config.settings import settings
from skills.base import Skill, SkillType, Parameter, Permission
from tools.cv_tools import _pdf_store, _cv_html_store, _cv_docx_store

# Import storage modules
from storage import agent_store

# Import Pydantic schemas
from .models import CreateSkillRequest, PublishSkillRequest
from .models import AgentPromptRequest, CreateAgentRequest

# Import skill registry, factory and chatbot graph
from agents import chatbot, skill_registry, skill_factory

# Import TOOLS list (source of truth for tool registry)
from agents.llm_node import TOOLS

router = APIRouter()

# API get user info (dùng cho login)
@router.get("/user")
async def get_user(user_id: str = Query(...)):
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    return {
        "user_id": user_id,
        "name": user_info["name"],
        "role": user_info["role"],
    }

# API get all skills
@router.get("/skills")
async def get_skills():
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "system_prompt": s.system_prompt,
        }
        for s in skill_registry.list_all()
    ]

# API chat with Multi-Agent system
@router.post("/chat")
async def chat(
    user_id: str = Form(...),
    query: str = Form(...),
    file: Optional[UploadFile] = File(None),
):
    try:
        full_query = query

        file_id = None
        if file:
            file_id = uuid.uuid4().hex[:8]
            _pdf_store[file_id] = await file.read()
            full_query = (
                f"{query}\n\n"
                f"[Người dùng đã upload file: {file.filename}. file_id: {file_id}. "
                f"Hãy dùng tool phù hợp để xử lý file này.]"
            )

        result = await chatbot.ainvoke({
            "user_id": user_id,
            "user_name": user_id,
            "query": full_query,
            "agent_response": ""
        })

        # Tìm HTML output từ bất kỳ tool nào trả về __html_id__
        rich_html = None
        word_download_url = None
        messages = result.get("messages", [])
        for msg in reversed(messages):
            content = msg.content or ""
            if not isinstance(msg, ToolMessage):
                continue
            if rich_html is None and "__html_id__:" in content:
                html_id = content.split("__html_id__:")[-1].strip().split()[0]
                rich_html = _cv_html_store.get(html_id)
            if word_download_url is None and "__docx_id__:" in content:
                docx_id = content.split("__docx_id__:")[-1].strip().split()[0]
                if docx_id in _cv_docx_store:
                    word_download_url = f"/api/cv/download-word/{docx_id}"
            if rich_html and word_download_url:
                break

        if file_id:
            _pdf_store.pop(file_id, None)

        final_response = result.get("agent_response", "")
        response_data: dict = {"response": final_response}
        if rich_html:
            response_data["rich_html"] = rich_html
        if word_download_url:
            response_data["word_download_url"] = word_download_url
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")

# API draft new skill dynamically (Pha 1: AI sinh bản nháp)
@router.post("/skills/draft")
async def draft_skill(req: CreateSkillRequest):
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    name = user_info["name"]

    if role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền thiết kế nháp skill mới")

    try:
        draft = await skill_factory.create_from_description(
            user_description=req.description,
            created_by=name
        )
        return {"success": True, "skill": draft.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi thiết kế nháp skill: {e}")

# API publish reviewed skill dynamically (Pha 2: Admin duyệt & xuất bản)
@router.post("/skills/publish")
async def publish_skill(req: PublishSkillRequest):
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền xuất bản skill")

    try:
        skill_data = req.skill_data
        published_skill = Skill(
            id=skill_data["id"],
            name=skill_data["name"],
            version=skill_data.get("version", "1.0.0"),
            description=skill_data["description"],
            skill_type=SkillType(skill_data["skill_type"]),
            parameters=[Parameter(**p) for p in skill_data.get("parameters", [])],
            system_prompt=skill_data["system_prompt"],
            permission=Permission(required_roles=skill_data.get("permission", {}).get("required_roles", [])),
            examples=skill_data.get("examples", []),
            metadata=skill_data.get("metadata", {}),
            created_at=datetime.now(),
            created_by=user_info["name"]
        )

        skill_registry.register(published_skill, [])

        skill_file = os.path.join(settings.SKILLS_DIR, f"{published_skill.id}.json")
        os.makedirs(os.path.dirname(skill_file), exist_ok=True)
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(published_skill.model_dump_json(indent=4))

        return {"success": True, "skill": {"id": published_skill.id, "name": published_skill.name, "description": published_skill.description}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất bản skill: {e}")

# API create new skill dynamically (Admin only)
@router.post("/create_skill")
async def create_skill(req: CreateSkillRequest):
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền tạo skill mới")

    try:
        new_skill = await skill_factory.create_from_description(
            user_description=req.description,
            created_by=user_info["name"]
        )

        skill_registry.register(new_skill, [])

        skill_file = os.path.join(settings.SKILLS_DIR, f"{new_skill.id}.json")
        os.makedirs(os.path.dirname(skill_file), exist_ok=True)
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(new_skill.model_dump_json(indent=4))

        return {"success": True, "skill": {"id": new_skill.id, "name": new_skill.name, "description": new_skill.description}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo skill: {e}")

@router.delete("/delete_skill")
async def delete_skill(skill_id: str, user_id: str):
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    role = user_info["role"]
    
    if role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền xóa skill")
        
    # Check if skill exists
    skill = skill_registry.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy kỹ năng có ID {skill_id}")
        
    # Remove from registry
    skill_registry.remove(skill_id)
    
    # Delete from custom skills disk path if applicable
    skill_file = os.path.join(settings.SKILLS_DIR, f"{skill_id}.json")
    if os.path.exists(skill_file):
        try:
            os.remove(skill_file)
            print(f"🗑️ Deleted custom skill file: {skill_file}")
        except Exception as e:
            print(f"⚠️ Error deleting file: {e}")
            
    return {"success": True, "message": f"Đã xóa thành công kỹ năng {skill_id}"}


# ============================================================
# TOOL API ENDPOINTS (read-only — source of truth là code)
# ============================================================

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


# ============================================================
# AGENT MANAGEMENT API ENDPOINTS
# ============================================================

@router.get("/agents/config")
async def get_agents_config(user_id: str = Query(...)):
    """Return full agent configs including system_prompt (admin only)."""
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được xem cấu hình agent")

    agents = agent_store.load_agents()
    return agents


@router.put("/agents/{agent_id}/prompt")
async def save_agent_prompt(agent_id: str, req: AgentPromptRequest):
    """Save the system prompt for an agent (admin only)."""
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền lưu prompt")

    try:
        agent_store.update_agent_prompt(agent_id, req.system_prompt)
        return {"success": True, "message": f"Đã lưu prompt cho Agent {agent_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/agents")
async def create_agent(req: CreateAgentRequest):
    """Create a new custom agent (admin only)."""
    user_info = db.get_user_info(req.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền tạo agent")

    clean_id = req.id.strip().lower().replace(" ", "_")
    try:
        new_agent = agent_store.add_agent({
            "id": clean_id,
            "name": req.name,
            "icon": req.icon,
            "description": req.description,
            "welcome": req.welcome,
            "system_prompt": req.system_prompt,
            "created_by": user_info["name"]
        })
        return {"success": True, "agent": new_agent}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, user_id: str = Query(...)):
    """Delete a custom agent (admin only). Builtin agents cannot be deleted."""
    user_info = db.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User ID không tồn tại")
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới được quyền xóa agent")

    try:
        agent_store.delete_agent(agent_id)
        return {"success": True, "message": f"Đã xóa thành công agent {agent_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
