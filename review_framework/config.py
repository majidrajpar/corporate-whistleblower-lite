"""
CrewAI Meta-Review Framework - Configuration
============================================

Note: CrewAI requires Python < 3.14. For Python 3.14+, we use the standalone
review script (run_quick_review.py) which uses langchain directly.

This config provides LLM setup for both modes.
"""

import os

# Ollama Cloud Configuration (same as main framework)
OLLAMA_API_KEY = "[REDACTED]"
OLLAMA_BASE_URL = "https://ollama.com/v1/"
MODEL_NAME = "kimi-k2.6"

try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

def get_llm():
    """Get the LLM instance for review agents."""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("langchain-openai not available. Install: pip install langchain-openai")
    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=OLLAMA_API_KEY,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
        max_tokens=4096,
    )

# Attempt CrewAI import (will fail on Python 3.14+)
try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

# Shared LLM for CrewAI agents (if available)
review_llm = None
if LANGCHAIN_AVAILABLE:
    review_llm = get_llm()
