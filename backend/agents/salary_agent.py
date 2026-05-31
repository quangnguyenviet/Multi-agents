from .workflow_state import MultiAgentState
from .instances import salary_agent_with_skills
from data import database as db

# === NODE AGENT 2: QUẢN LÝ LƯƠNG (Salary Agent sử dụng skill system) ===
async def salary_management_node(state: MultiAgentState) -> MultiAgentState:
    query = state["query"]
    user_role = state["user_role"]
    user_name = state["user_name"]
    
    context = {}
    if user_role == "employee":
        context["salary_data"] = db.get_salary_data(user_name) or {}
        context["access_level"] = "self"
    else:
        context["salary_data"] = db.get_all_salaries()
        context["access_level"] = "all"
    
    context["user_name"] = user_name
    context["user_role"] = user_role
    
    response = await salary_agent_with_skills.process(query, user_role, context)
    state["agent_response"] = response
    return state
