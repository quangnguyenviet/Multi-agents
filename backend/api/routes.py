import asyncio
import time
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Form, File, UploadFile
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from data import database as db
from tools.cv_tools import _pdf_store, _cv_docx_store

# Import storage modules
from storage import agent_store, conversation_store

# Import Pydantic schemas
from .models import AgentPromptRequest, CreateAgentRequest

# Import skill registry and chatbot graph
from agents import chatbot, skill_registry
from agents.workflow import delete_thread

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
    conversation_id: str = Form(...),
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

        # thread_id = conversation_id → checkpointer SQLite tự nạp/lưu lịch sử của cuộc
        config = {"configurable": {"thread_id": conversation_id}}
        result = await asyncio.to_thread(
            chatbot.invoke,
            {
                "user_id": user_id,
                "user_name": user_id,
                "query": full_query,
                "agent_response": "",
            },
            config,
        )

        # Tìm Word output từ tool trả về __docx_id__ — CHỈ trong lượt hiện tại
        # (quét ngược, dừng khi gặp HumanMessage = ranh giới đầu lượt) để không lấy nhầm file lượt cũ
        word_download_url = None
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, HumanMessage):
                break
            if isinstance(msg, ToolMessage) and "__docx_id__:" in (msg.content or ""):
                docx_id = msg.content.split("__docx_id__:")[-1].strip().split()[0]
                if docx_id in _cv_docx_store:
                    word_download_url = f"/api/cv/download-word/{docx_id}"
                    break

        if file_id:
            _pdf_store.pop(file_id, None)

        # Lưu/cập nhật metadata cuộc hội thoại (title = câu hỏi đầu tiên)
        conversation_store.upsert(conversation_id, user_id, query)

        final_response = result.get("agent_response", "")
        response_data: dict = {"response": final_response}
        if word_download_url:
            response_data["word_download_url"] = word_download_url
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")


# ============================================================
# CONVERSATION API — danh sách / nạp lại / xóa cuộc hội thoại
# ============================================================

@router.get("/conversations")
async def list_conversations(user_id: str = Query(...)):
    """Danh sách cuộc hội thoại của user (mới nhất trước)."""
    return conversation_store.list_for_user(user_id)


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, user_id: str = Query(...)):
    """Nạp lại tin nhắn của một cuộc hội thoại từ checkpointer."""
    conv_owner = conversation_store.owner(conversation_id)
    if conv_owner is None:
        return {"messages": []}
    if conv_owner != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập cuộc hội thoại này")

    config = {"configurable": {"thread_id": conversation_id}}
    state = await asyncio.to_thread(chatbot.get_state, config)
    raw = (state.values or {}).get("messages", []) if state else []

    messages = []
    for m in raw:
        if isinstance(m, HumanMessage):
            text = m.content or ""
            # Bỏ phần ghi chú file đính kèm injected trong query
            marker = "\n\n[Người dùng đã upload file"
            if marker in text:
                text = text.split(marker)[0].strip()
            messages.append({"role": "user", "text": text})
        elif isinstance(m, AIMessage) and m.content:
            messages.append({"role": "assistant", "text": m.content})
    return {"messages": messages}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: str = Query(...)):
    """Xóa cuộc hội thoại (metadata + checkpoint)."""
    ok = conversation_store.delete(conversation_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hội thoại")
    await asyncio.to_thread(delete_thread, conversation_id)
    return {"success": True}


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
