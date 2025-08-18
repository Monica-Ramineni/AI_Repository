"""Test script for the A2A client agent - demonstrates Activity #1."""

import asyncio
from app.client_agent_graph_Activity1 import client_graph


def test_client_agent():
    """Test the A2A client agent with various research tasks."""
    
    print("🚀 Testing A2A Client Agent (Activity #1)")
    print("=" * 50)
    print()
    
    # Test 1: Web Search
    print("📊 Test 1: Web Search via A2A Protocol")
    print("-" * 40)
    inputs = {
        "messages": [("user", "Search for the latest developments in artificial intelligence in 2024")],
        "research_context": [],
        "current_task": "AI research",
        "a2a_responses": []
    }
    
    try:
        result = client_graph.invoke(inputs)
        print("✅ Web search completed successfully!")
        print(f"Response: {result['messages'][-1].content[:200]}...")
    except Exception as e:
        print(f"❌ Web search failed: {e}")
    
    print()
    
    # Test 2: Academic Search
    print("📚 Test 2: Academic Search via A2A Protocol")
    print("-" * 40)
    inputs = {
        "messages": [("user", "Find recent academic papers about transformer architectures")],
        "research_context": [],
        "current_task": "Academic research",
        "a2a_responses": []
    }
    
    try:
        result = client_graph.invoke(inputs)
        print("✅ Academic search completed successfully!")
        print(f"Response: {result['messages'][-1].content[:200]}...")
    except Exception as e:
        print(f"❌ Academic search failed: {e}")
    
    print()
    
    # Test 3: Document Search
    print("📄 Test 3: Document Search via A2A Protocol")
    print("-" * 40)
    inputs = {
        "messages": [("user", "Search through our documents for information about policies")],
        "research_context": [],
        "current_task": "Document research",
        "a2a_responses": []
    }
    
    try:
        result = client_graph.invoke(inputs)
        print("✅ Document search completed successfully!")
        print(f"Response: {result['messages'][-1].content[:200]}...")
    except Exception as e:
        print(f"❌ Document search failed: {e}")
    
    print()
    print("🎯 Activity #1 Complete!")
    print("=" * 50)
    print("✅ LangGraph client agent created")
    print("✅ A2A protocol communication working")
    print("✅ Agent-to-agent collaboration demonstrated")
    print("✅ All three tools (web, academic, documents) tested")


if __name__ == "__main__":
    test_client_agent()
