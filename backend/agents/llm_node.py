from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
from .workflow_state import MultiAgentState

SYSTEM_PROMPT = (
    "Bạn là trợ lý AI nội bộ thân thiện. "
    "Hãy trả lời câu hỏi của người dùng một cách chính xác, rõ ràng và hữu ích."
)

def llm_node(state: MultiAgentState) -> dict:
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=0.7
    )
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["query"])
    ]
    response = llm.invoke(messages)
    return {"agent_response": response.content}
