from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from .workflow_state import MultiAgentState
from .llm_node import llm_node, TOOLS

def build_multi_agent_system():
    workflow = StateGraph(MultiAgentState)
    workflow.add_node("llm", llm_node)
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.set_entry_point("llm")
    workflow.add_conditional_edges("llm", tools_condition)
    workflow.add_edge("tools", "llm")
    return workflow.compile()

chatbot = build_multi_agent_system()
