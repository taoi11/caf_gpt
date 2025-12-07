"""
src/agents/sub_agents/leave_foo_agent.py

Specialized sub-agent for leave policy research, inheriting from BaseAgent.

Top-level declarations:
- LeaveFooAgent: Agent handling leave-related queries with policy document integration
"""

import logging
from typing import Dict, List, Optional

from ...storage.document_retriever import DocumentRetriever
from src.llm_interface import llm_client

logger = logging.getLogger(__name__)


class LeaveFooAgent:
    # Agent handling leave-related queries with policy document integration

    def __init__(self, prompt_manager: Optional["PromptManager"] = None):
        # Initialize with prompt manager and document retriever
        self.prompt_manager = prompt_manager
        self.document_retriever = DocumentRetriever()  # Initialize the document retriever

    def research(self, query: str) -> str:
        # Main entry for leave policy research: retrieve policy, build prompt, call LLM
        try:
            # Retrieve leave policy document
            policy = self._retrieve_leave_policy()

            # Build prompt with policy and question
            messages = self._build_leave_foo_prompt(policy, query)

            # Call OpenRouter with context
            response = self._call_with_context(messages)
            return response
        except Exception as e:
            logger.error(f"Error in leave foo research: {e}")
            return "I'm sorry, but I couldn't retrieve the leave policy information at this time."

    def _retrieve_leave_policy(self) -> str:
        # Fetch leave policy from storage using DocumentRetriever
        policy_content = self.document_retriever.get_document("leave", "leave_policy_2025.md")
        if policy_content is None:
            logger.error("Leave policy document not found in storage.")
            return "I'm sorry, but I couldn't retrieve the leave policy information at this time."

        logger.info("Successfully retrieved leave policy document")
        return policy_content

    def _build_leave_foo_prompt(self, policy: str, question: str) -> List[Dict[str, str]]:
        # Load leave_foo prompt and inject policy via placeholder
        if self.prompt_manager is None:
            raise ValueError("PromptManager is required for LeaveFooAgent")

        leave_foo_prompt = self.prompt_manager.get_prompt("leave_foo")
        leave_foo_prompt = leave_foo_prompt.replace("{{leave_policy}}", policy)

        return [
            {"role": "system", "content": leave_foo_prompt},
            {"role": "user", "content": question},
        ]

    def _call_with_context(self, messages: List[Dict[str, str]]) -> str:
        # Call llm_client with messages using specific model for leave queries
        return llm_client.generate_response(messages, openrouter_model="x-ai/grok-4.1-fast")
