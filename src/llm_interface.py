
"""
src/llm_interface.py

Centralized service for all LLM interactions.
Implements a two-tier architecture:
1. Primary: Local Ollama instance
2. Secondary: OpenRouter API (fallback)
"""

import time
import requests
import structlog
from typing import List, Dict, Any, Optional
import ollama

from src.config import config

logger = structlog.get_logger()

class LLMInterface:
    """
    Interface for interacting with LLMs using a two-tier strategy.
    """

    def __init__(self):
        self.config = config.llm
        self.ollama_client = ollama.Client(host=self.config.ollama_base_url)

    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        ollama_model: Optional[str] = None,
        openrouter_model: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM using the two-tier strategy.
        
        Args:
            messages: List of message dicts (role, content)
            temperature: Optional override for temperature
            ollama_model: Optional override for Ollama model
            openrouter_model: Optional override for OpenRouter model
            
        Returns:
            The generated text response
        """
        temp = temperature if temperature is not None else self.config.temperature
        
        # Tier 1: Try Ollama
        if self._check_ollama_health():
            try:
                return self._call_ollama(messages, temp, ollama_model)
            except Exception as e:
                logger.warning("ollama_call_failed", error=str(e))
                # Fall through to Tier 2
        else:
            logger.info("ollama_unavailable_skipping")

        # Tier 2: OpenRouter Fallback
        return self._call_openrouter(messages, temp, openrouter_model)

    def _check_ollama_health(self) -> bool:
        """
        Ping the Ollama instance to check if it's reachable.
        """
        try:
            # Simple ping to the version endpoint or just a root get
            # The ollama python client doesn't have a dedicated ping, 
            # but we can try a lightweight list call or just a raw request to the base url
            response = requests.get(self.config.ollama_base_url, timeout=2.0)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _call_ollama(self, messages: List[Dict[str, str]], temperature: float, model: Optional[str] = None) -> str:
        """
        Call the local Ollama instance.
        """
        use_model = model if model else self.config.ollama_model
        logger.info("calling_ollama", model=use_model)
        
        # The ollama library handles the request. 
        # Note: The library doesn't strictly enforce a client-side timeout in the chat() call 
        # in the same way requests does, but we can rely on the server's behavior or 
        # wrap it if strictly necessary. For now, we use the library's default behavior 
        # but ensure stream=False as requested.
        
        response = self.ollama_client.chat(
            model=use_model,
            messages=messages,
            options={
                "temperature": temperature,
            },
            stream=False
        )
        
        return response['message']['content']

    def _call_openrouter(self, messages: List[Dict[str, str]], temperature: float, model: Optional[str] = None) -> str:
        """
        Call the OpenRouter API as a fallback.
        """
        use_model = model if model else self.config.openrouter_model
        logger.info("calling_openrouter", model=use_model)
        
        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/taoi11/caf_gpt", 
            "X-Title": "CAF-GPT"
        }
        
        payload = {
            "model": use_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.config.request_timeout_seconds
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
