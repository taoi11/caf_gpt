"""
src/agents/llm_utils.py

Shared LLM utilities for agent retry patterns and common operations.

Top-level declarations:
- call_llm_with_retry: Shared retry logic for LLM calls with XML parsing
"""

import logging
from typing import Callable, TypeVar

from src.llm_interface import llm_client
from .types import XMLParseError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def call_llm_with_retry(
    messages: list[dict[str, str]],
    model: str,
    parser: Callable[[str], T],
    log_response: bool = False,
) -> tuple[str, T]:
    # Shared retry logic for LLM calls with XML parsing
    # Calls LLM, parses response, retries once on XML parse failure
    # Returns tuple of (raw_response, parsed_object)
    response = llm_client.generate_response(messages, openrouter_model=model)

    if log_response:
        logger.info(f"LLM raw response: {response}")

    try:
        parsed = parser(response)
        return response, parsed
    except XMLParseError as e:
        logger.warning(f"XML parse failed, retrying: {e.parse_error}")
        # Send error feedback and retry once
        retry_messages = messages + [
            {"role": "assistant", "content": response},
            {
                "role": "user",
                "content": f"Your response was not valid XML. Parse error: {e.parse_error}. Please respond with properly formatted XML.",
            },
        ]
        response = llm_client.generate_response(retry_messages, openrouter_model=model)

        if log_response:
            logger.info(f"LLM retry response: {response}")

        # No more retries - let it raise if it fails again
        parsed = parser(response)
        return response, parsed
