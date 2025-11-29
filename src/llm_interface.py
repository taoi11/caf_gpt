"""
src/llm_interface.py

Centralized service for all LLM interactions using OpenRouter API.
"""

import requests
import structlog
from typing import List, Dict, Optional

from src.config import config

logger = structlog.get_logger()


class LLMInterface:
    """
    Interface for interacting with LLMs via OpenRouter API.
    """

    def __init__(self):
        self.config = config.llm

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        openrouter_model: Optional[str] = None,
    ) -> str:
        """
        Generate a response from OpenRouter API.

        Args:
            messages: List of message dicts (role, content)
            temperature: Optional override for temperature
            openrouter_model: Optional override for OpenRouter model

        Returns:
            The generated text response
        """
        temp = temperature if temperature is not None else self.config.temperature
        return self._call_openrouter(messages, temp, openrouter_model)

    def _call_openrouter(
        self, messages: List[Dict[str, str]], temperature: float, model: Optional[str] = None
    ) -> str:
        """
        Call the OpenRouter API.
        """
        use_model = model if model else self.config.openrouter_model
        logger.info("calling_openrouter", model=use_model)

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
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected OpenRouter response format: {data}")

        except requests.RequestException as e:
            logger.error("openrouter_call_failed", error=str(e))
            raise RuntimeError(f"Failed to get response from OpenRouter: {str(e)}")


# Global instance
llm_client = LLMInterface()
