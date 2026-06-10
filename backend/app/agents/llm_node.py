import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from app.core.config import settings
from .workflow_state import AgentState
from app.tools.company_tools import get_current_datetime, calculate
from app.tools.file_tools import read_file_content
from app.tools.cv_tools import read_cv_file, generate_cv_word_file
from app.tools.skill_tools import load_skill

logger = logging.getLogger(__name__)

BASE_SYSTEM_PROMPT = (
    "Bạn là trợ lý AI"
    "Hãy trả lời câu hỏi của người dùng một cách chính xác, rõ ràng và hữu ích."
)

TOOLS = [
    get_current_datetime, calculate,
    read_file_content, read_cv_file, generate_cv_word_file,
    load_skill,
]

llm_with_tools = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0.3,
).bind_tools(TOOLS)


def _build_system_prompt() -> str:
    """Ghép BASE_SYSTEM_PROMPT với CATALOG skill (chỉ name + description)."""
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


def llm_node(state: AgentState) -> dict:
    existing_messages = list(state.get("messages") or [])
    is_reentry = bool(existing_messages) and isinstance(existing_messages[-1], ToolMessage)

    new_messages = []
    if not is_reentry:
        new_messages.append(HumanMessage(content=state["query"]))
        logger.info("[LLM NODE] New turn — query: %s | history len: %d",
                    state["query"][:120], len(existing_messages))
    else:
        logger.info("[LLM NODE] Re-entry after ToolNode — history len: %d", len(existing_messages))

    system_msg = SystemMessage(content=_build_system_prompt())
    messages_to_send = [system_msg] + existing_messages + new_messages

    response = llm_with_tools.invoke(messages_to_send)
    new_messages.append(response)

    if response.tool_calls:
        for tc in response.tool_calls:
            args_preview = str(tc.get("args", {}))[:200]
            logger.info("[LLM NODE] Tool call → %s | args: %s", tc["name"], args_preview)
    else:
        logger.info("[LLM NODE] Final response (first 200 chars): %s", response.content[:200])

    return {
        "messages": new_messages,
        "agent_response": response.content if not response.tool_calls else "",
    }
