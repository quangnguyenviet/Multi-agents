from typing import TypedDict, Literal

class MultiAgentState(TypedDict):
    user_id: str
    user_role: Literal["employee", "accountant", "admin"]
    user_name: str
    query: str
    target_agent: Literal["hr_policies", "salary_management", "system_admin", "unknown"]
    access_granted: bool
    agent_response: str
