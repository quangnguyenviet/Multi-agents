from langgraph.graph import StateGraph, END
from .workflow_state import MultiAgentState
from .router import router_node, route_to_agent
from .hr_agent import hr_policies_node
from .salary_agent import salary_management_node
from .admin_agent import system_admin_node
from .user_agent import user_management_node
from .general_handler import general_handler_node

# === XÂY DỰNG ĐỒ THỊ ===
def build_multi_agent_system():
    workflow = StateGraph(MultiAgentState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("hr_policies", hr_policies_node)
    workflow.add_node("salary_management", salary_management_node)
    workflow.add_node("system_admin", system_admin_node)
    workflow.add_node("user_management", user_management_node)
    workflow.add_node("general_handler", general_handler_node)
    
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "hr_policies": "hr_policies",
            "salary_management": "salary_management",
            "system_admin": "system_admin",
            "user_management": "user_management",
            "general_handler": "general_handler",
            "end": END
        }
    )
    
    workflow.add_edge("hr_policies", END)
    workflow.add_edge("salary_management", END)
    workflow.add_edge("system_admin", END)
    workflow.add_edge("user_management", END)
    workflow.add_edge("general_handler", END)
    
    return workflow.compile()

# Compile chatbot once on import
chatbot = build_multi_agent_system()
