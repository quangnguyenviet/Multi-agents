import asyncio
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agents import chatbot, skill_registry
from app.repositories import conversation_repo
from app.tools.cv_tools import _pdf_store, _cv_docx_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat(
    user_id: str = Form(...),
    query: str = Form(default=""),
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
                f"[File đính kèm: '{file.filename}' (file_id: {file_id}). "
                f"Hãy dùng tool read_file_content để đọc nội dung file trước, "
                f"sau đó phản hồi phù hợp với nội dung thực tế của file.]"
            )

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

        word_download_url = None
        skill_used = None
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, HumanMessage):
                break
            if isinstance(msg, ToolMessage) and "__docx_id__:" in (msg.content or ""):
                docx_id = msg.content.split("__docx_id__:")[-1].strip().split()[0]
                if docx_id in _cv_docx_store:
                    word_download_url = f"/api/cv/download-word/{docx_id}"
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get("name") == "load_skill" and not skill_used:
                        skill_used = tc.get("args", {}).get("skill_name")
                        logger.info("[ROUTE /chat] Skill selected for query '%s': %s",
                                    query[:80], skill_used)

        if file_id:
            _pdf_store.pop(file_id, None)

        conversation_repo.upsert(conversation_id, user_id, query)

        response_data: dict = {"response": result.get("agent_response", "")}
        if word_download_url:
            response_data["word_download_url"] = word_download_url
        if skill_used:
            response_data["skill_used"] = skill_used
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")
