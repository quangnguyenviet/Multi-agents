from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from core.settings import settings
from .workflow_state import MultiAgentState
from .llm_node import llm_node, TOOLS


def build_multi_agent_system(checkpointer=None):
    workflow = StateGraph(MultiAgentState)
    workflow.add_node("llm", llm_node)
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.set_entry_point("llm")
    workflow.add_conditional_edges("llm", tools_condition)
    workflow.add_edge("tools", "llm")
    return workflow.compile(checkpointer=checkpointer)


def _make_checkpointer():
    pool = ConnectionPool(
        settings.DATABASE_URL,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
        open=True,
    )
    cp = PostgresSaver(pool)
    cp.setup()
    print("[CHAT] Checkpointer: PostgreSQL")
    return cp


_checkpointer = _make_checkpointer()
chatbot = build_multi_agent_system(_checkpointer)


def delete_thread(thread_id: str):
    """Xóa toàn bộ checkpoint của một cuộc hội thoại (thread_id)."""
    try:
        _checkpointer.delete_thread(thread_id)
    except Exception as e:
        print(f"[CHAT] delete_thread error: {e}")
