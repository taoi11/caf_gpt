"""
Service for Open Router API integration.
"""
import os
import json
import logging
import requests

logger = logging.getLogger(__name__)


class OpenRouterService:
    """
    Service for Open Router API integration.
    """

    def __init__(self, model=None):
        """
        Initialize the Open Router service with API key from environment variables.

        Args:
            model: The model to use for generation. Defaults to "anthropic/claude-3.5-haiku:beta".
        """
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # Default model
        self.model = model or "anthropic/claude-3.5-haiku:beta"

    def generate_completion(self, prompt, temperature=0.3, max_tokens=500):
        """
        Generate a completion using the Open Router API.

        Args:
            prompt: The prompt to send to the model.
            temperature: Controls randomness. Lower values are more deterministic.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://caf-gpt.com",
                "X-Title": "CAF-GPT"
            }

            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            logger.info(f"Sending request to Open Router API with model: {self.model}")

            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data),
                timeout=60  # 60 second timeout
            )

            if response.status_code == 200:
                result = response.json()
                # Extract the generated text from the response
                generated_text = result['choices'][0]['message']['content']
                logger.info("Successfully generated completion from Open Router API")
                return generated_text
            else:
                logger.error(f"Error from Open Router API: {response.status_code} - {response.text}")
                return f"Error generating completion. Status code: {response.status_code}"

        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return f"Error generating completion: {str(e)}"
