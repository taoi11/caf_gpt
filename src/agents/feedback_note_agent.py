"""
src/agents/feedback_note_agent.py

Agent for generating feedback notes based on rank competencies.
Handles rank request loop similar to prime_foo's research loop.

Top-level declarations:
- FeedbackNoteAgent: Agent handling feedback note generation with rank-specific competencies
- FeedbackNoteResponse: Parsed response structure
"""

import logging
from typing import Optional
import xml.etree.ElementTree as ET
from pydantic import BaseModel

from src.utils.document_retriever import document_retriever
from src.config import config
from src.agents.prompt_manager import PromptManager
from src.agents.types import XMLParseError
from src.agents.llm_utils import call_llm_with_retry, circuit_breaker, increment_circuit_breaker

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
        # Parse XML response to determine type (no_response, reply, or rank)
        # Raises XMLParseError if response is not valid XML
        try:
            root = ET.fromstring(response)
            type_ = root.tag
            content = root.text.strip() if root.text else ""

            if type_ == "rank":
                # Extract rank from <rank>mcpl</rank>
                return FeedbackNoteResponse(type="rank", rank=content.lower())

            elif type_ == "reply":
                # Extract body from reply
                body_elem = root.find("body")
                if body_elem is not None and body_elem.text:
                    content = body_elem.text.strip()
                return FeedbackNoteResponse(type="reply", content=content)

            elif type_ == "no_response":
                return FeedbackNoteResponse(type="no_response")

            else:
                raise XMLParseError(response, f"Unknown XML tag: {type_}")

        except ET.ParseError as e:
            raise XMLParseError(response, str(e))

    def _load_competencies(self, rank: str) -> str:
        # Load rank-specific competencies from S3
        rank_file = RANK_FILES.get(rank.lower())

        if rank_file is None:
            logger.warning(f"Unknown rank: {rank}, defaulting to cpl")
            rank_file = RANK_FILES["cpl"]

        competencies = document_retriever.get_document(self.s3_category, rank_file)

        if competencies is None:
            logger.error(f"Failed to load competencies for rank {rank}")
            return "Competencies not available at this time."

        logger.info(f"Successfully loaded competencies for rank {rank}")
        return competencies

    def _load_examples(self) -> str:
        # Load examples from S3
        examples = document_retriever.get_document(self.s3_category, "examples.md")

        if examples is None:
            logger.error("Failed to load examples")
            return "Examples not available at this time."

        logger.info("Successfully loaded examples")
        return examples
