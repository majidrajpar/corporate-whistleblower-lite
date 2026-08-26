import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Ollama Cloud Configuration
# IMPORTANT: Set OLLAMA_API_KEY as environment variable
# NEVER commit API keys to version control
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "kimi-k2.6")

def get_llm(temperature: float = 0.1):
    """Get the LLM instance configured for Ollama Cloud."""
    if not OLLAMA_API_KEY:
        raise ValueError(
            "OLLAMA_API_KEY environment variable is required. "
            "Set it with: export OLLAMA_API_KEY='your-key-here'"
        )
    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=OLLAMA_API_KEY,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
        max_tokens=8192,
    )

def invoke_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1):
    """Invoke the LLM with system and user prompts."""
    llm = get_llm(temperature)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    return llm.invoke(messages)
