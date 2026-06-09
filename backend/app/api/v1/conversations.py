import asyncio
from fastapi import APIRouter, HTTPException, Query
from langchain_core.messages import AIMessage, HumanMessage

from app.agents import chatbot
from app.agents.workflow import delete_thread
from app.repositories import conversation_repo

router = APIRouter()


@router.get("/conversations")
async def list_conversations(user_id: str = Query(...)):
    """Danh sách cuộc hội thoại của user (mới nhất trước)."""
    return conversation_repo.list_for_user(user_id)


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, user_id: str = Query(...)):
    """Nạp lại tin nhắn của một cuộc hội thoại từ checkpointer."""
    conv_owner = conversation_repo.owner(conversation_id)
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
    ok = conversation_repo.delete(conversation_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hội thoại")
    await asyncio.to_thread(delete_thread, conversation_id)
    return {"success": True}
