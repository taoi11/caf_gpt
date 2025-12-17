"""
src/agents/sub_agents/base_agent.py

Base class providing common functionality for all sub-agents.

Top-level declarations:
- BaseAgent: Base class with shared document retrieval, prompt building, and LLM calling
"""

import logging
from typing import Dict, List, Optional

from src.utils.document_retriever import document_retriever
from src.agents.llm_utils import llm_client
from src.config import config
from src.agents.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class BaseAgent:
    # Base class providing common functionality for all sub-agents

    def __init__(self, prompt_manager: Optional[PromptManager] = None):
        # Initialize with prompt manager
        self.prompt_manager = prompt_manager

    def _load_document(
        self, category: str, filename: str, doc_type: str, fallback_message: str
    ) -> str:
        # Load a document from S3 with consistent error handling and logging
        document = document_retriever.get_document(category, filename)

        if document is None:
            logger.error(f"Failed to load {doc_type}")
            return fallback_message

        logger.info(f"Successfully loaded {doc_type}")
        return document

    def _build_prompt_with_replacements(
        self, prompt_name: str, replacements: Dict[str, str], user_content: str
    ) -> List[Dict[str, str]]:
        # Build LLM messages with prompt template and replacements
        if self.prompt_manager is None:
            raise ValueError("PromptManager is required for BaseAgent")

        base_prompt = self.prompt_manager.get_prompt(prompt_name)

        # Apply all replacements
        for placeholder, value in replacements.items():
            base_prompt = base_prompt.replace(placeholder, value)

        return [
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": user_content},
        ]

    def _call_with_context(self, messages: List[Dict[str, str]], model_name: str) -> str:
        # Call llm_client with messages using specified model
        return llm_client.generate_response(messages, openrouter_model=model_name)
