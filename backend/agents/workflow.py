from langgraph.graph import StateGraph, END
from .workflow_state import MultiAgentState
from .llm_node import llm_node

def build_multi_agent_system():
    workflow = StateGraph(MultiAgentState)
    workflow.add_node("llm", llm_node)
    workflow.set_entry_point("llm")
    workflow.add_edge("llm", END)
    return workflow.compile()

# Compile chatbot once on import
chatbot = build_multi_agent_system()
