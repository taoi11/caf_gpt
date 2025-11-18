
"""
/workspace/caf_gpt/src/agents/base_agent.py

Base class for all agents with OpenRouter API integration and logging.

Top-level declarations:
- BaseAgent: Base class handling API calls to OpenRouter
"""

import logging
import requests
from typing import List
from .types import Message

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        # Initialize with API key and optional base URL; set up headers for authentication
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def call_openrouter(
        self, messages: List[Message], model: str = "anthropic/claude-3.5-sonnet", temperature: float = 0.7
    ) -> str:
        # Make LLM API calls to OpenRouter with error handling for requests and response parsing
        try:
            payload = self._build_request(messages, model, temperature)
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return self._handle_api_error(e)
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            return self._handle_api_error(e)

    def _build_request(self, messages: List[Message], model: str, temperature: float):
        # Construct OpenRouter request payload from messages, model, and temperature
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        return {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": 4096,
        }

    def _handle_api_error(self, error):
        # Handle API failures gracefully with logging and fallback message
        logger.error(f"Handling API error: {error}")
        return "I'm sorry, but I encountered an error processing your request. Please try again later."
