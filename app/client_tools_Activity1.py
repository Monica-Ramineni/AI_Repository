"""A2A tools for communicating with the running A2A server (using SDK)."""

import asyncio
from uuid import uuid4
from typing import List

import httpx
from langchain_core.tools import tool

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest


async def _send_via_a2a_async(message_text: str, base_url: str = "http://localhost:10000") -> str:
    """Resolve agent card and send a message via A2A using a single async context."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        client = A2AClient(agent_card=agent_card, httpx_client=httpx_client)

        send_message_payload: dict = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message_text}],
                "message_id": uuid4().hex,
            }
        }
        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**send_message_payload))
        response = await client.send_message(request)

        # Extract first text artifact if present; otherwise return serialized response
        data = response.model_dump(mode="json", exclude_none=True)
        result = data.get("result") or data.get("root", {}).get("result")
        if isinstance(result, dict):
            artifacts = result.get("artifacts")
            if isinstance(artifacts, list) and artifacts:
                parts = artifacts[0].get("parts")
                if isinstance(parts, list):
                    for p in parts:
                        if p.get("kind") == "text" and p.get("text"):
                            return p["text"]
        return str(data)


def _send_via_a2a(message_text: str) -> str:
    """Sync wrapper that runs the async sender in a fresh event loop."""
    return asyncio.run(_send_via_a2a_async(message_text))


# No tools needed - client agent sends queries directly to A2A server
# The server's LLM intelligently decides which tools to use

def get_client_tool_belt() -> List:
    """Return empty tool belt - client agent doesn't need tools."""
    return []
