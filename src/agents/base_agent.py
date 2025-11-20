
"""
src/agents/base_agent.py

Base class for all agents, delegating LLM interactions to the centralized LLMInterface.
"""

import structlog
from typing import List, Optional
from .types import Message
from src.llm_interface import llm_client

logger = structlog.get_logger()

class BaseAgent:
    """
    Base class for agents.
    Delegates actual LLM calls to the global llm_client.
    """
    
    def __init__(self):
        # No longer need to pass api_key or base_url here, 
        # as llm_client handles configuration globally.
        pass

    def call_llm(
        self, 
        messages: List[Message], 
        model: Optional[str] = None, 
        temperature: Optional[float] = None
    ) -> str:
        """
        Unified entry point for LLM calls.
        Delegates to llm_client.generate_response.
        """
        # Convert Pydantic Message objects to dicts for the interface
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        try:
            return llm_client.generate_response(
                messages=formatted_messages,
                temperature=temperature
            )
        except Exception as e:
            logger.error("agent_llm_call_failed", error=str(e))
            return "I'm sorry, but I encountered an error processing your request. Please try again later."
