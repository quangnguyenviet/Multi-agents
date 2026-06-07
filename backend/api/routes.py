import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Form, File, UploadFile
from langchain_core.messages import ToolMessage
from data import database as db
from tools.cv_tools import _pdf_store, _cv_html_store, _cv_docx_store

# Import storage modules
from storage import agent_store

# Import Pydantic schemas
from .models import AgentPromptRequest, CreateAgentRequest

# Import skill registry and chatbot graph
from agents import chatbot, skill_registry

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

# API get all skills (read-only — source of truth là file Markdown trong skills/library)
@router.get("/skills")
async def get_skills():
    """Trả về catalog skill (name + description). Nội dung đầy đủ nạp on-demand qua tool load_skill."""
    return [
        {"name": s.name, "description": s.description}
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

# Skill là read-only: thêm/sửa skill = tạo/sửa file .md trong skills/library/ → restart server.


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
