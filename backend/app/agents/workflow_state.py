from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    user_id: str
    user_name: str
    query: str
    agent_response: str
    messages: Annotated[list, add_messages]
