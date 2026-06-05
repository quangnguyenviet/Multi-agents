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
from tools.cv_tools import read_cv_file, generate_cv_file

BASE_SYSTEM_PROMPT = (
    "Bạn là trợ lý AI nội bộ thân thiện. "
    "Hãy trả lời câu hỏi của người dùng một cách chính xác, rõ ràng và hữu ích."
)

TOOLS = [
    get_company_info, get_current_datetime, calculate,
    get_company_employee_list, get_demo_users_list,
    read_cv_file, generate_cv_file,
]

llm_with_tools = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0.7,
).bind_tools(TOOLS)


def _build_system_prompt() -> str:
    """Ghép BASE_SYSTEM_PROMPT với system_prompt của các skill thuộc llm_node."""
    try:
        from .instances import skill_registry
        skill_prompts = [
            skill.system_prompt
            for skill in skill_registry.list_all()
            if skill.metadata.get("agent_id") == "llm_node" and skill.system_prompt
        ]
    except Exception:
        skill_prompts = []

    if not skill_prompts:
        return BASE_SYSTEM_PROMPT

    combined = "\n\n".join(skill_prompts)
    return f"{BASE_SYSTEM_PROMPT}\n\n{combined}"


def llm_node(state: MultiAgentState) -> dict:
    existing_messages = state.get("messages") or []

    # Lần đầu gọi: seed từ query. Re-entry sau ToolNode: dùng history có sẵn
    if not existing_messages or not isinstance(existing_messages[-1], ToolMessage):
        messages_to_send = [
            SystemMessage(content=_build_system_prompt()),
            HumanMessage(content=state["query"]),
        ]
    else:
        messages_to_send = existing_messages

    response = llm_with_tools.invoke(messages_to_send)

    return {
        "messages": [response],
        "agent_response": response.content if not response.tool_calls else "",
    }
