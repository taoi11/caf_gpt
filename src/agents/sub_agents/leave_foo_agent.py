"""
src/agents/sub_agents/leave_foo_agent.py

Specialized sub-agent for leave policy research, inheriting from BaseAgent.

Top-level declarations:
- LeaveFooAgent: Agent handling leave-related queries with policy document integration
"""

import logging
from typing import Optional

from src.config import config
from src.agents.prompt_manager import PromptManager
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LeaveFooAgent(BaseAgent):
    # Agent handling leave-related queries with policy document integration

    def __init__(self, prompt_manager: Optional[PromptManager] = None):
        # Initialize with prompt manager (uses shared document_retriever)
        super().__init__(prompt_manager)

    def research(self, query: str) -> str:
        # Main entry for leave policy research: retrieve policy, build prompt, call LLM
        try:
            # Retrieve leave policy document
            policy = self._load_document(
                "leave", "leave_policy_2025.md", "leave policy", "Leave policy document unavailable"
            )

            # Build prompt with policy and question
            replacements = {"{{leave_policy}}": policy}
            messages = self._build_prompt_with_replacements("leave_foo", replacements, query)

            # Call OpenRouter with context
            response = self._call_with_context(messages, config.llm.leave_foo_model)
            return response
        except Exception as e:
            logger.error(f"Error in leave foo research: {e}")
            return "I'm sorry, but I couldn't retrieve the leave policy information at this time."
