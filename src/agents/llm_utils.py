"""
src/agents/llm_utils.py

Shared LLM utilities for agent retry patterns and common operations.

Top-level declarations:
- call_llm_with_retry: Shared retry logic for LLM calls with XML parsing
- circuit_breaker: Decorator to limit number of LLM calls in a method
"""

import logging
from functools import wraps
from typing import Callable, TypeVar

from src.utils.llm_interface import llm_client
from .types import XMLParseError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def circuit_breaker(max_calls: int = 3):
    # Decorator to limit the number of LLM calls within a method execution
    # Tracks calls across the decorated method's execution and raises RuntimeError when exceeded
    # Default limit is 3 calls for backward compatibility
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Store call count in wrapper closure
            wrapper.llm_call_count = 0  # type: ignore[attr-defined]
            wrapper.max_llm_calls = max_calls  # type: ignore[attr-defined]
            try:
                return func(*args, **kwargs)
            finally:
                # Clean up after execution
                delattr(wrapper, "llm_call_count")
                delattr(wrapper, "max_llm_calls")

        return wrapper

    return decorator


def increment_circuit_breaker():
    # Helper to increment and check circuit breaker from within decorated method
    # Call this before each LLM invocation to enforce the limit
    import inspect

    frame = inspect.currentframe()
    if frame and frame.f_back:
        caller_frame = frame.f_back
        # Find the wrapper function in the call stack
        for frame_info in inspect.getouterframes(caller_frame):
            func = frame_info.frame.f_locals.get("wrapper")
            if func and hasattr(func, "llm_call_count"):
                func.llm_call_count += 1
                if func.llm_call_count > func.max_llm_calls:
                    logger.error(
                        f"Circuit breaker triggered: exceeded maximum {func.max_llm_calls} LLM calls"
                    )
                    raise RuntimeError(
                        f"Circuit breaker: exceeded maximum {func.max_llm_calls} LLM calls per email"
                    )
                return
    # Fallback: if we can't find wrapper, just log warning
    logger.warning("increment_circuit_breaker called outside decorated method")


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
