import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from config.settings import settings
from .workflow_state import MultiAgentState
from tools.company_tools import (
    get_company_info,
    get_current_datetime,
    calculate,
    get_company_employee_list,
    get_demo_users_list,
)
from tools.cv_tools import read_cv_file, generate_cv_file, generate_cv_word_file
from tools.skill_tools import load_skill

logger = logging.getLogger(__name__)

BASE_SYSTEM_PROMPT = (
    "Bạn là trợ lý AI nội bộ thân thiện. "
    "Hãy trả lời câu hỏi của người dùng một cách chính xác, rõ ràng và hữu ích."
)

TOOLS = [
    get_company_info, get_current_datetime, calculate,
    get_company_employee_list, get_demo_users_list,
    read_cv_file, generate_cv_file, generate_cv_word_file,
    load_skill,
]

llm_with_tools = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0.7,
).bind_tools(TOOLS)


def _build_system_prompt() -> str:
    """Ghép BASE_SYSTEM_PROMPT với CATALOG skill (chỉ name + description).

    Progressive disclosure: không nhồi nội dung skill vào prompt. Khi yêu cầu
    người dùng khớp một skill, LLM tự gọi tool `load_skill(name)` để lấy hướng
    dẫn đầy đủ rồi mới thực hiện.
    """
    try:
        from .instances import skill_registry
        skills = skill_registry.list_all()
    except Exception:
        skills = []

    if not skills:
        return BASE_SYSTEM_PROMPT

    catalog = "\n".join(f"- {s.name}: {s.description}" for s in skills)
    instruction = (
        "## SKILLS KHẢ DỤNG\n"
        "Dưới đây là các skill (quy trình chuyên biệt) bạn có thể dùng. "
        "Khi yêu cầu của người dùng khớp mô tả một skill, hãy gọi tool "
        "`load_skill` với đúng tên skill để lấy hướng dẫn chi tiết TRƯỚC khi thực hiện.\n"
        f"{catalog}"
    )
    return f"{BASE_SYSTEM_PROMPT}\n\n{instruction}"


def llm_node(state: MultiAgentState) -> dict:
    existing_messages = state.get("messages") or []
    system_msg = SystemMessage(content=_build_system_prompt())
    human_msg = HumanMessage(content=state["query"])

    is_reentry = existing_messages and isinstance(existing_messages[-1], ToolMessage)

    if not is_reentry:
        messages_to_send = [system_msg, human_msg]
        logger.info("[LLM NODE] First call — query: %s", state["query"][:120])
    else:
        # Re-entry sau ToolNode: giữ system + query gốc để LLM không quên ngữ cảnh
        messages_to_send = [system_msg, human_msg] + list(existing_messages)
        logger.info("[LLM NODE] Re-entry after ToolNode — history length: %d", len(existing_messages))
        for msg in existing_messages:
            label = type(msg).__name__
            content_preview = (msg.content or "")[:200]
            logger.info("  [%s] %s", label, content_preview)

    response = llm_with_tools.invoke(messages_to_send)

    if response.tool_calls:
        for tc in response.tool_calls:
            args_preview = str(tc.get("args", {}))[:200]
            logger.info("[LLM NODE] Tool call → %s | args: %s", tc["name"], args_preview)
    else:
        logger.info("[LLM NODE] Final response (first 200 chars): %s", response.content[:200])

    return {
        "messages": [response],
        "agent_response": response.content if not response.tool_calls else "",
    }
