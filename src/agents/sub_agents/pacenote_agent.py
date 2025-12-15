"""
src/agents/sub_agents/pacenote_agent.py

Specialized sub-agent for generating feedback notes based on rank competencies.

Top-level declarations:
- PacenoteAgent: Agent handling feedback note generation with rank-specific competencies
- RANK_FILES: Mapping of rank names to their S3 file names
"""

import logging
from typing import Dict, List, Optional

from src.utils.document_retriever import document_retriever
from src.agents.llm_utils import llm_client
from src.config import config
from src.agents.prompt_manager import PromptManager

logger = logging.getLogger(__name__)

# Mapping of rank names to their file names in S3
RANK_FILES = {
    "cpl": "cpl.md",
    "mcpl": "mcpl.md",
    "sgt": "sgt.md",
    "wo": "wo.md",
}


class PacenoteAgent:
    # Agent handling feedback note generation with rank-specific competencies

    def __init__(self, prompt_manager: Optional[PromptManager] = None):
        # Initialize with prompt manager (uses shared document_retriever)
        self.prompt_manager = prompt_manager
        self.s3_category = "paceNote"

    def generate_note(self, rank: str, context: str) -> str:
        # Main entry for feedback note generation: load competencies, build prompt, call LLM
        # Returns the generated feedback note text
        try:
            competencies = self._load_competencies(rank)
            examples = self._load_examples()

            messages = self._build_prompt(rank, context, competencies, examples)

            response = self._call_with_context(messages)
            return response
        except Exception as e:
            logger.error(f"Error in pacenote generation: {e}")
            return "I'm sorry, but I couldn't generate the feedback note at this time."

    def _load_competencies(self, rank: str) -> str:
        # Load rank-specific competencies from S3
        rank_lower = rank.lower()
        rank_file = RANK_FILES.get(rank_lower)

        if rank_file is None:
            logger.warning(f"Unknown rank: {rank}, defaulting to cpl")
            rank_file = RANK_FILES["cpl"]

        return self._load_document(
            rank_file,
            f"competencies for rank {rank}",
            "Competencies not available at this time.",
        )

    def _load_examples(self) -> str:
        # Load feedback note examples from S3
        return self._load_document(
            "examples.md", "examples", "Examples not available at this time."
        )

    def _load_document(self, filename: str, doc_type: str, fallback_message: str) -> str:
        # Load a document from S3 with consistent error handling and logging
        document = document_retriever.get_document(self.s3_category, filename)

        if document is None:
            logger.error(f"Failed to load {doc_type}")
            return fallback_message

        logger.info(f"Successfully loaded {doc_type}")
        return document

    def _build_prompt(
        self, rank: str, context: str, competencies: str, examples: str
    ) -> List[Dict[str, str]]:
        # Build LLM messages with pacenote prompt, competencies, and event context
        if self.prompt_manager is None:
            raise ValueError("PromptManager is required for PacenoteAgent")

        base_prompt = self.prompt_manager.get_prompt("pacenote")

        # Inject competencies and examples into prompt
        system_prompt = base_prompt.replace("{{competencies}}", competencies)
        system_prompt = system_prompt.replace("{{examples}}", examples)
        system_prompt = system_prompt.replace("{{rank}}", rank.upper())

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context},
        ]

    def _call_with_context(self, messages: List[Dict[str, str]]) -> str:
        # Call llm_client with messages using pacenote model
        return llm_client.generate_response(messages, openrouter_model=config.llm.pacenote_model)
