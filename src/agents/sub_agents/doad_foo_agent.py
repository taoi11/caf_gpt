"""
src/agents/sub_agents/doad_foo_agent.py

Specialized sub-agent for DOAD policy research using a two-call pattern.

Top-level declarations:
- DoadFooAgent: Agent handling DOAD-related queries with dynamic document selection
"""

import logging
import re
from typing import Optional

from src.config import config
from src.agents.prompt_manager import PromptManager
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

MAX_DOAD_FILES = 3


class DoadFooAgent(BaseAgent):
    # Agent handling DOAD-related queries using selector -> answer two-call pattern

    def __init__(self, prompt_manager: Optional[PromptManager] = None):
        # Initialize with prompt manager (uses shared document_retriever)
        super().__init__(prompt_manager)

    def research(self, query: str) -> str:
        # Main entry: select relevant DOAD files, load them, answer query
        try:
            doad_numbers = self._select_files(query)

            if not doad_numbers:
                return "I couldn't identify relevant DOAD documents for this question."

            doad_content = self._load_doad_files(doad_numbers)

            if not doad_content:
                return "No relevant DOAD files found for this question."

            return self._answer_query(query, doad_content)

        except Exception as e:
            logger.error(f"Error in DOAD foo research: {e}")
            return "I'm sorry, but I couldn't retrieve the DOAD policy information at this time."

    def _select_files(self, query: str) -> list[str]:
        # Call 1: Use selector prompt with DOAD table to pick relevant document numbers
        if self.prompt_manager is None:
            raise ValueError("PromptManager is required for DoadFooAgent")

        doad_table = self.prompt_manager.get_prompt("DOAD_Table")

        replacements = {"{{doad_table}}": doad_table}
        messages = self._build_prompt_with_replacements("doad_foo_selector", replacements, query)

        response = self._call_with_context(messages, config.llm.doad_foo_model)

        return self._parse_doad_numbers(response)

    def _parse_doad_numbers(self, response: str) -> list[str]:
        # Extract DOAD numbers from <doad_numbers> XML tag, max 3
        match = re.search(r"<doad_numbers>(.+?)</doad_numbers>", response, re.DOTALL)

        if not match:
            logger.warning(f"No <doad_numbers> tag found in selector response: {response[:200]}")
            return []

        raw_numbers = match.group(1)
        numbers = [n.strip() for n in raw_numbers.split(",") if n.strip()]

        return numbers[:MAX_DOAD_FILES]

    def _load_doad_files(self, numbers: list[str]) -> str:
        # Fetch DOAD documents from S3, wrap each in XML tags
        loaded_docs: list[str] = []

        for num in numbers:
            filename = f"{num}.md"
            doc = self._load_document("doad", filename, f"DOAD {num}", "")

            if doc:
                # Wrap each DOAD in its own XML tag
                loaded_docs.append(f"<DOAD_{num}>\n{doc}\n</DOAD_{num}>")

        return "\n\n".join(loaded_docs)

    def _answer_query(self, query: str, doad_content: str) -> str:
        # Call 2: Use answer prompt with loaded documents to respond to query
        replacements = {"{{doad_content}}": doad_content}
        messages = self._build_prompt_with_replacements("doad_foo_answer", replacements, query)

        return self._call_with_context(messages, config.llm.doad_foo_model)
