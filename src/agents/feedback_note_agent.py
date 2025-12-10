"""
src/agents/feedback_note_agent.py

Agent for generating feedback notes based on rank competencies.
Handles rank request loop similar to prime_foo's research loop.

Top-level declarations:
- FeedbackNoteAgent: Agent handling feedback note generation with rank-specific competencies
- FeedbackNoteResponse: Parsed response structure
"""

import logging
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET
from pydantic import BaseModel

from src.utils.document_retriever import document_retriever
from src.config import config
from src.agents.prompt_manager import PromptManager
from src.agents.types import XMLParseError
from src.agents.llm_utils import call_llm_with_retry, circuit_breaker, increment_circuit_breaker
from src.agents.utils.xml_parser import parse_xml_response

logger = logging.getLogger(__name__)

# Mapping of rank names to their file names in S3
RANK_FILES = {
    "cpl": "cpl.md",
    "mcpl": "mcpl.md",
    "sgt": "sgt.md",
    "wo": "wo.md",
}


class FeedbackNoteResponse(BaseModel):
    # Parsed response structure for feedback note agent
    type: str  # 'no_response', 'reply', 'rank'
    content: Optional[str] = None
    rank: Optional[str] = None


class FeedbackNoteAgent:
    # Agent handling feedback note generation with rank-specific competencies

    def __init__(self, prompt_manager: PromptManager):
        # Initialize with prompt manager (uses shared document_retriever)
        self.prompt_manager = prompt_manager
        self.s3_category = "paceNote"

    @circuit_breaker(max_calls=3)
    def process_email(self, email_context: str) -> FeedbackNoteResponse:
        # Main loop: send to LLM, parse response, handle rank request loop similar to prime_foo
        # Get base prompt with placeholders
        base_prompt = self._get_base_prompt()

        messages = [
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": email_context},
        ]

        increment_circuit_breaker()
        response, parsed = call_llm_with_retry(
            messages, config.llm.pacenote_model, self._parse_response, log_response=True
        )
        logger.info(
            f"Parsed response type: {parsed.type}, content: {parsed.content}, rank: {parsed.rank}"
        )

        # Loop to handle rank requests (similar to research loop in prime_foo)
        while True:
            if parsed.type == "no_response":
                return parsed

            elif parsed.type == "reply":
                return parsed

            elif parsed.type == "rank":
                # Add None check
                if not parsed.rank:
                    raise RuntimeError("Rank type received but rank value is None")

                # Load competencies for requested rank
                competency_list = self._load_competencies(parsed.rank)
                examples = self._load_examples()

                # Continue conversation by appending to existing messages
                messages.append({"role": "assistant", "content": response})
                messages.append(
                    {
                        "role": "user",
                        "content": f"Here are the competencies and examples for {parsed.rank.upper()}. Now please generate the feedback note.\n\n<competencies>\n{competency_list}\n</competencies>\n\n<examples>\n{examples}\n</examples>",
                    }
                )

                increment_circuit_breaker()
                response, parsed = call_llm_with_retry(
                    messages,
                    config.llm.pacenote_model,
                    self._parse_response,
                    log_response=True,
                )
                logger.info(
                    f"Parsed follow-up response type: {parsed.type}, content: {parsed.content}, rank: {parsed.rank}"
                )

            else:
                # Unknown response type should not happen - XMLParseError handles bad tags
                raise RuntimeError(f"Unexpected response type: {parsed.type}")

    def _get_base_prompt(self) -> str:
        # Load the base feedback_notes prompt with placeholders
        return self.prompt_manager.get_prompt("feedback_notes")

    def _parse_response(self, response: str) -> FeedbackNoteResponse:
        # Parse XML response using shared parser with rank handler
        # Raises XMLParseError if response is not valid XML
        def handle_rank(root: ET.Element) -> Dict[str, Any]:
            # Extract rank value and convert to lowercase
            content = root.text.strip() if root.text else ""
            return {"rank": content.lower()}

        parsed = parse_xml_response(response, type_handlers={"rank": handle_rank})

        # Convert ParsedXMLResponse to FeedbackNoteResponse
        rank = parsed.extra.get("rank") if parsed.extra else None
        return FeedbackNoteResponse(type=parsed.type, content=parsed.content, rank=rank)

    def _load_competencies(self, rank: str) -> str:
        # Load rank-specific competencies from S3
        rank_file = RANK_FILES.get(rank.lower())

        if rank_file is None:
            logger.warning(f"Unknown rank: {rank}, defaulting to cpl")
            rank_file = RANK_FILES["cpl"]

        return self._load_document(
            rank_file, f"competencies for rank {rank}", "Competencies not available at this time."
        )

    def _load_examples(self) -> str:
        # Load examples from S3
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
