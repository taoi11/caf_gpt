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

    def __init__(self, prompt_manager: Optional["PromptManager"] = None):
        # Initialize with prompt manager and document retriever
        self.prompt_manager = prompt_manager
        self.document_retriever = DocumentRetriever()
        self.s3_category = "paceNote"

    def process_email(self, email_context: str) -> str:
        # Main loop: send to LLM, parse response, handle rank request loop similar to prime_foo
        try:
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
            response = llm_client.generate_response(
                messages, openrouter_model=config.llm.pacenote_model
            )
            logger.info(f"LLM raw response: {response}")
            parsed = self._parse_response(response)
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
                    # Add the assistant's rank request and a user message with competencies
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": f"Here are the competencies and examples for {parsed.rank.upper()}. Now please generate the feedback note.\n\n<competencies>\n{competency_list}\n</competencies>\n\n<examples>\n{examples}\n</examples>"
                    })

                    llm_call_count += 1
                    response = llm_client.generate_response(
                        messages, openrouter_model=config.llm.pacenote_model
                    )
                    logger.info(f"LLM follow-up raw response: {response}")
                    parsed = self._parse_response(response)
                    logger.info(
                        f"Parsed follow-up response type: {parsed.type}, content: {parsed.content}, rank: {parsed.rank}"
                    )

                else:
                    # Unknown response type
                    logger.warning(f"Unknown response type: {parsed.type}")
                    return """<reply>
  <body>
  I apologize, but I encountered an error while processing your request. Please try again.

  Regards,
  </body>
</reply>"""

        except Exception as e:
            logger.error(f"Error in feedback note generation: {e}")
            return """<reply>
  <body>
  I apologize, but I encountered an error while processing your request. Please try again.

  Regards,
  </body>
</reply>"""

    def _get_base_prompt(self) -> str:
        # Load the base feedback_notes prompt with placeholders
        if self.prompt_manager is None:
            raise ValueError("PromptManager is required for FeedbackNoteAgent")

        return self.prompt_manager.get_prompt("feedback_notes")

    def _parse_response(self, response: str) -> FeedbackNoteResponse:
        # Parse XML response to determine type (no_response, reply, or rank)
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
                logger.warning(f"Unknown XML tag: {type_}")
                return FeedbackNoteResponse(type="unknown")

        except ET.ParseError:
            # Fallback parsing for non-XML responses
            if "<no_response>" in response:
                return FeedbackNoteResponse(type="no_response")

            elif "<reply>" in response:
                start = response.find("<reply>") + 7
                end = response.find("</reply>", start)
                if end > start:
                    body_start = response.find("<body>", start) + 6
                    body_end = response.find("</body>", body_start)
                    if body_end > body_start:
                        content = response[body_start:body_end].strip()
                    else:
                        content = response[start:end].strip()
                return FeedbackNoteResponse(type="reply", content=content)

            elif "<rank>" in response:
                start = response.find("<rank>") + 6
                end = response.find("</rank>", start)
                if end > start:
                    rank = response[start:end].strip().lower()
                    return FeedbackNoteResponse(type="rank", rank=rank)

            # Default to unknown
            logger.warning(f"Could not parse response: {response[:100]}")
            return FeedbackNoteResponse(type="unknown")

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
