"""Toolbelt assembly for agents.

Collects third-party tools and local tools (like RAG) into a single list that
graphs can bind to their language models.
"""
from __future__ import annotations

from typing import List
import os

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from app.rag import retrieve_information


def get_tool_belt() -> List:
    """Return the list of tools available to agents (Tavily, Arxiv, RAG)."""
    tools: List = [ArxivQueryRun(), retrieve_information]
    api_key = os.getenv("TAVILY_API_KEY")
    if api_key:
        tools.insert(0, TavilySearchResults(max_results=5, tavily_api_key=api_key))
    return tools


