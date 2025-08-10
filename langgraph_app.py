import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model

# Load environment variables
load_dotenv()

# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "mcp-proper-graph"

async def main():
    """Main function using proper LangGraph approach"""
    
    print("🐕 Proper MCP LangGraph Agent 🐕")
    print("Connecting to MCP server...")
    
    # Initialize the model
    model = init_chat_model("openai:gpt-4o-mini")
    
    # Create MultiServerMCPClient for your server.py
    client = MultiServerMCPClient(
        {
            "mcp-server": {
                "command": "uv",
                "args": ["--directory", os.getcwd(), "run", "server.py"],
                "transport": "stdio",
            }
        }
    )
    
    # Get tools from your MCP server
    tools = await client.get_tools()
    print(f"✅ Loaded {len(tools)} tools: {[tool.name for tool in tools]}")
    
    # Define the model call function
    def call_model(state: MessagesState):
        response = model.bind_tools(tools).invoke(state["messages"])
        return {"messages": response}
    
    # Build the StateGraph
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    
    # Compile the graph
    graph = builder.compile()
    print("✅ Graph compiled and ready!")
    print("Type 'bye' to exit.\n")
    
    # Chat loop
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["bye", "goodbye", "exit", "quit"]:
            print("Goodbye! 🐾")
            break
        
        try:
            # Invoke the graph with your question
            response = await graph.ainvoke({"messages": user_input})
            print(f"Assistant: {response['messages'][-1].content}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())

# Export graph for langgraph dev
async def _build_graph():
    """Build and return the graph for langgraph dev"""
    # Initialize the model
    model = init_chat_model("openai:gpt-4o-mini")
    
    # Create MultiServerMCPClient for your server.py
    client = MultiServerMCPClient(
        {
            "mcp-server": {
                "command": "uv",
                "args": ["--directory", os.getcwd(), "run", "server.py"],
                "transport": "stdio",
            }
        }
    )
    
    # Get tools from your MCP server
    tools = await client.get_tools()
    
    # Define the model call function
    def call_model(state: MessagesState):
        response = model.bind_tools(tools).invoke(state["messages"])
        return {"messages": response}
    
    # Build the StateGraph
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    
    return builder.compile()

# Export the graph for langgraph dev
graph = asyncio.run(_build_graph())
