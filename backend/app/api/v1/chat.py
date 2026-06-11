import asyncio
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agents import chatbot, skill_registry
from app.repositories import conversation_repo
from app.tools.file_tools import _upload_store

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
            _upload_store[file_id] = await file.read()
            full_query = (
                f"{query}\n\n"
                f"[Attached file: '{file.filename}', file_id={file_id}]"
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

        artifacts = []
        skill_used = None
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, HumanMessage):
                break
            if isinstance(msg, ToolMessage) and "__artifact__:" in (msg.content or ""):
                for token in (msg.content or "").split():
                    if token.startswith("__artifact__:"):
                        parts = token.split(":", 2)
                        if len(parts) == 3:
                            atype, aid = parts[1], parts[2]
                            artifacts.append({
                                "type": atype,
                                "url": f"/api/artifacts/download/{atype}/{aid}",
                            })
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get("name") == "load_skill" and not skill_used:
                        skill_used = tc.get("args", {}).get("skill_name")
                        logger.info("[ROUTE /chat] Skill selected for query '%s': %s",
                                    query[:80], skill_used)

        conversation_repo.upsert(conversation_id, user_id, query)

        response_data: dict = {"response": result.get("agent_response", "")}
        if artifacts:
            response_data["artifacts"] = artifacts
        if skill_used:
            response_data["skill_used"] = skill_used
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")
