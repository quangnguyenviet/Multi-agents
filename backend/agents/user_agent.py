from .workflow_state import MultiAgentState
from .instances import user_management_agent_with_skills

# === NODE AGENT 4: QUẢN LÝ USER DEMO (User Management Node) ===
async def user_management_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    context = {
        "user_name": user_name,
        "user_role": user_role
    }
    
    response = await user_management_agent_with_skills.process(query, user_role, context)
    state["agent_response"] = response
    return state
