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

from src.storage.document_retriever import DocumentRetriever
from src.llm_interface import llm_client
from src.config import config
from src.agents.prompt_manager import PromptManager
from src.agents.types import XMLParseError

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
        # Initialize with prompt manager and document retriever
        self.prompt_manager = prompt_manager
        self.document_retriever = DocumentRetriever()
        self.s3_category = "paceNote"

    def _call_llm_with_retry(self, messages: list) -> tuple[str, FeedbackNoteResponse]:
        # Call LLM and parse response, with 1 retry on XML parse failure
        response = llm_client.generate_response(
            messages, openrouter_model=config.llm.pacenote_model
        )
        logger.info(f"LLM raw response: {response}")
        try:
            parsed = self._parse_response(response)
            return response, parsed
        except XMLParseError as e:
            logger.warning(f"XML parse failed, retrying: {e.parse_error}")
            # Send error feedback and retry once
            retry_messages = messages + [
                {"role": "assistant", "content": response},
                {"role": "user", "content": f"Your response was not valid XML. Parse error: {e.parse_error}. Please respond with properly formatted XML."},
            ]
            response = llm_client.generate_response(
                retry_messages, openrouter_model=config.llm.pacenote_model
            )
            logger.info(f"LLM retry response: {response}")
            # No more retries - let it raise if it fails again
            parsed = self._parse_response(response)
            return response, parsed

    def process_email(self, email_context: str) -> str:
        # Main loop: send to LLM, parse response, handle rank request loop similar to prime_foo
        # Get base prompt with placeholders
        base_prompt = self._get_base_prompt()

        messages = [
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": email_context},
        ]

        # Circuit breaker: limit to 3 LLM calls per email
        max_llm_calls = 3
        llm_call_count = 0

        llm_call_count += 1
        response, parsed = self._call_llm_with_retry(messages)
        logger.info(
            f"Parsed response type: {parsed.type}, content: {parsed.content}, rank: {parsed.rank}"
        )

        # Loop to handle rank requests (similar to research loop in prime_foo)
        while True:
            if parsed.type == "no_response":
                return response

            elif parsed.type == "reply":
                return response

            elif parsed.type == "rank":
                # Check circuit breaker before making another LLM call
                if llm_call_count >= max_llm_calls:
                    logger.error(
                        f"Circuit breaker triggered: exceeded maximum {max_llm_calls} LLM calls per email"
                    )
                    raise RuntimeError(
                        f"Circuit breaker: exceeded maximum {max_llm_calls} LLM calls per email"
                    )

                # Load competencies for requested rank
                competency_list = self._load_competencies(parsed.rank)
                examples = self._load_examples()

                # Continue conversation by appending to existing messages
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": f"Here are the competencies and examples for {parsed.rank.upper()}. Now please generate the feedback note.\n\n<competencies>\n{competency_list}\n</competencies>\n\n<examples>\n{examples}\n</examples>"
                })

                llm_call_count += 1
                response, parsed = self._call_llm_with_retry(messages)
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
        
        # Strip markdown code fences if present
        response = response.strip()
        if response.startswith("```xml"):
            response = response[6:]  # Remove ```xml
        elif response.startswith("```"):
            response = response[3:]  # Remove ```
        if response.endswith("```"):
            response = response[:-3]  # Remove trailing ```
        response = response.strip()
        
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

        competencies = self.document_retriever.get_document(self.s3_category, rank_file)

        if competencies is None:
            logger.error(f"Failed to load competencies for rank {rank}")
            return "Competencies not available at this time."

        logger.info(f"Successfully loaded competencies for rank {rank}")
        return competencies

    def _load_examples(self) -> str:
        # Load examples from S3
        examples = self.document_retriever.get_document(self.s3_category, "examples.md")

        if examples is None:
            logger.error("Failed to load examples")
            return "Examples not available at this time."

        logger.info("Successfully loaded examples")
        return examples
