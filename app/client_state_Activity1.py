"""State schema for the A2A client agent graph."""

from typing import TypedDict, List, Any, Annotated
from langgraph.graph.message import add_messages


class ClientAgentState(TypedDict):
    """State schema for the A2A client agent, storing conversation and research context."""
    messages: Annotated[List, add_messages]  # Conversation history
    research_context: List[str]              # Accumulated research information
    current_task: str                        # Current research task being pursued
    a2a_responses: List[Any]                # Responses from A2A server
