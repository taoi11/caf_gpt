"""
src/agents/llm_utils.py

Centralized LLM utilities including the OpenRouter client interface, retry patterns, and circuit breakers.

Top-level declarations:
- LLMInterface: Interface for interacting with LLMs via OpenRouter API
- llm_client: Global instance of LLMInterface for application-wide use
- call_llm_with_retry: Shared retry logic for LLM calls with XML parsing
- circuit_breaker: Decorator to limit number of LLM calls in a method
"""

import logging
import requests
from functools import wraps
from typing import Callable, TypeVar, List, Dict, Optional, Any

from src.config import config
from .types import XMLParseError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class LLMInterface:
    # Interface for interacting with LLMs via OpenRouter API

    def __init__(self) -> None:
        # Initialize with LLM configuration from app settings
        self.config = config.llm

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        openrouter_model: Optional[str] = None,
    ) -> str:
        # Generate a response from OpenRouter API with optional parameter overrides
        # :param messages: List of message dicts (role, content)
        # :param temperature: Optional override for temperature
        # :param openrouter_model: Optional override for OpenRouter model
        # :return: The generated text response
        temp = temperature if temperature is not None else self.config.temperature
        return self._call_openrouter(messages, temp, openrouter_model)

    def _call_openrouter(
        self, messages: List[Dict[str, str]], temperature: float, model: Optional[str] = None
    ) -> str:
        # Call the OpenRouter API with specified parameters and error handling
        use_model = model if model else self.config.openrouter_model
        logger.info(f"Calling OpenRouter with model={use_model}")

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/taoi11/caf_gpt",
            "X-Title": "CAF-GPT",
        }

        payload = {
            "model": use_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.config.request_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                return str(data["choices"][0]["message"]["content"])
            else:
                raise ValueError(f"Unexpected OpenRouter response format: {data}")

        except requests.RequestException as e:
            logger.error(f"OpenRouter call failed: {e}")
            raise RuntimeError(f"Failed to get response from OpenRouter: {str(e)}")


# Global instance for application-wide use
llm_client = LLMInterface()


def circuit_breaker(max_calls: int = 3) -> Callable[[Callable[..., T]], Callable[..., T]]:
    # Decorator to limit the number of LLM calls within a method execution
    # Tracks calls across the decorated method's execution and raises RuntimeError when exceeded
    # Default limit is 3 calls for backward compatibility
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
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


def increment_circuit_breaker() -> None:
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
