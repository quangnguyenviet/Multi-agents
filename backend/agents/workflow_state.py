from typing import TypedDict

class MultiAgentState(TypedDict):
    user_id: str
    user_name: str
    query: str
    agent_response: str
