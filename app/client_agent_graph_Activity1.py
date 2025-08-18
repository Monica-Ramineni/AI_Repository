"""A minimal A2A client agent graph.

The graph:
- Calls a chat model bound to A2A client tools.
- If the last message requested tool calls, routes to a ToolNode.
- Otherwise, terminates.
"""

from __future__ import annotations

from typing import Dict, Any
import os

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from app.client_state_Activity1 import ClientAgentState


def _build_model_with_tools():
    """Return a chat model instance for the client agent."""
    model = ChatOpenAI(
        model=os.getenv('TOOL_LLM_NAME', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        openai_api_base=os.getenv('TOOL_LLM_URL', 'https://api.openai.com/v1'),
        temperature=0,
    )
    return model


def call_model(state: ClientAgentState) -> Dict[str, Any]:
    """Send user query to A2A server and let the server's LLM decide which tools to use."""
    messages = state["messages"]
    
    # Get the last user message
    last_message = messages[-1] if messages else None
    if last_message and hasattr(last_message, 'content'):
        user_query = last_message.content
        print(f"🔍 Processing query: '{user_query}'")
        
        # Send the query directly to the A2A server
        # The server's LLM will intelligently choose which tools to use
        from app.client_tools_Activity1 import _send_via_a2a
        result = _send_via_a2a(user_query)
        
        print(f"\n🤖 A2A SERVER RESPONSE:\n{result}\n")
        return {"messages": [f"A2A Server Response: {result}"]}
    
    # Fallback - don't call OpenAI, just acknowledge
    return {"messages": ["I'm ready to help you with web searches, academic papers, or document queries."]}


# No conditional routing needed - client agent just sends query to A2A server


def build_client_graph():
    """Build an A2A client agent graph that sends queries to the A2A server."""
    graph = StateGraph(ClientAgentState)
    
    graph.add_node("agent", call_model)
    graph.set_entry_point("agent")
    
    # No tool execution needed - just send query to A2A server and end
    graph.add_edge("agent", END)
    
    return graph


# Export compiled graph for use
client_graph = build_client_graph().compile()
