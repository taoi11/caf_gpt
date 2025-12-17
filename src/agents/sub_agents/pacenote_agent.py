"""
src/agents/sub_agents/pacenote_agent.py

Specialized sub-agent for generating feedback notes based on rank competencies.

Top-level declarations:
- PacenoteAgent: Agent handling feedback note generation with rank-specific competencies
- RANK_FILES: Mapping of rank names to their S3 file names
"""

import logging
from typing import Dict, List, Optional

from src.config import config
from src.agents.prompt_manager import PromptManager
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Mapping of rank names to their file names in S3
RANK_FILES = {
    "cpl": "cpl.md",
    "mcpl": "mcpl.md",
    "sgt": "sgt.md",
    "wo": "wo.md",
}


class PacenoteAgent(BaseAgent):
    # Agent handling feedback note generation with rank-specific competencies

    def __init__(self, prompt_manager: Optional[PromptManager] = None):
        # Initialize with prompt manager (uses shared document_retriever)
        super().__init__(prompt_manager)
        self.s3_category = "paceNote"

    def generate_note(self, rank: str, context: str) -> str:
        # Main entry for feedback note generation: load competencies, build prompt, call LLM
        # Returns the generated feedback note text
        try:
            rank_file = RANK_FILES.get(rank.lower(), RANK_FILES["cpl"])
            competencies = self._load_document(
                "paceNote",
                rank_file,
                f"competencies for rank {rank}",
                "Competencies not available.",
            )
            examples = self._load_document(
                "paceNote", "examples.md", "examples", "Examples not available."
            )

            # Build prompt with policy and question
            replacements = {
                "{{competencies}}": competencies,
                "{{examples}}": examples,
                "{{rank}}": rank.upper(),
            }
            messages = self._build_prompt_with_replacements("pacenote", replacements, context)

            # Call OpenRouter with context
            response = self._call_with_context(messages, config.llm.pacenote_model)
            return response
        except Exception as e:
            logger.error(f"Error in pacenote generation: {e}")
            return "I'm sorry, but I couldn't generate the feedback note at this time."
