"""
/workspace/caf_gpt/src/agents/sub_agents/leave_foo_agent.py

Specialized sub-agent for leave policy research, inheriting from BaseAgent.

Top-level declarations:
- LeaveFooAgent: Agent handling leave-related queries with policy document integration
"""

import logging
from typing import List, Optional

from ..types import Message
from ...storage.document_retriever import DocumentRetriever
from src.llm_interface import llm_client

logger = logging.getLogger(__name__)


class LeaveFooAgent:
    def __init__(self, prompt_manager: Optional["PromptManager"] = None):
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
        # Updated to use new file path: leave/leave_policy_2025.md in the 'policies' bucket
        policy_content = self.document_retriever.get_document("leave", "leave_policy_2025.md")
        if policy_content is None:
            logger.error("Leave policy document not found in storage.")
            return "I'm sorry, but I couldn't retrieve the leave policy information at this time."

        logger.info("Successfully retrieved leave policy document")
        return policy_content

    def _build_leave_foo_prompt(self, policy: str, question: str) -> List[Message]:
        # Load leave_foo prompt, inject policy via {{leave_policy}} placeholder, construct messages
        if self.prompt_manager is None:
            raise ValueError("PromptManager is required for LeaveFooAgent")

        leave_foo_prompt = self.prompt_manager.get_prompt("leave_foo")
        leave_foo_prompt = leave_foo_prompt.replace("{{leave_policy}}", policy)

        system_message = Message(role="system", content=leave_foo_prompt)
        user_message = Message(role="user", content=question)
        return [system_message, user_message]

    def _call_with_context(self, messages: List[Message]) -> str:
        # Convert messages to dicts and call llm_client with temperature
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        return llm_client.generate_response(
            formatted_messages, ollama_model="llama3", openrouter_model="x-ai/grok-4.1-fast"
        )
