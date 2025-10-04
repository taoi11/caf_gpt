"""
Service for Open Router API integration.
"""
import os
import json
import logging
import requests
import re

logger = logging.getLogger(__name__)


class OpenRouterService:
    """
    Service for Open Router API integration.
    """

    def __init__(self, model):
        """
        Initialize the Open Router service with API key from environment variables.

        Args:
            model: The model to use for generation. Must be explicitly specified (no default).
        """
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # No default model - must be explicitly provided
        if not model:
            raise ValueError("LLM model must be explicitly specified")

        self.model = model

    def generate_completion(self, prompt, temperature=0.3):
        """
        Generate a completion using the Open Router API.

        Args:
            prompt: The prompt to send to the model.
            temperature: Controls randomness. Lower values are more deterministic.

        Returns:
            The generated text.
        """
        try:
            # Validate prompt input
            if not prompt or not isinstance(prompt, (str, list)) or (isinstance(prompt, str) and not prompt.strip()):
                logger.error("Empty or invalid prompt provided to OpenRouter API")
                return "Input must have at least 1 token"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://caf-gpt.com",
                "X-Title": "CAF-GPT"
            }

            # Format messages properly based on input type
            if isinstance(prompt, list):
                messages = prompt  # Already formatted as messages
            else:
                messages = [{"role": "user", "content": prompt}]

            data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }

            logger.info(f"Sending request to Open Router API with model: {self.model}")
            logger.debug(f"OpenRouter Request Data: {json.dumps(data)}")  # Log request data

            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data),
                timeout=60  # 60 second timeout
            )

            if response.status_code == 200:
                result = response.json()

                # Check if the response contains an error
                gen_id = result.get('id')  # Extract the generation ID
                if 'error' in result:
                    error_code = result['error'].get('code')
                    error_message = result['error'].get('message')
                    logger.error(f"OpenRouter API error {error_code} (id: {gen_id}): {error_message}")
                    return f"OpenRouter API error {error_code}: {error_message}"

                # Only try to access 'choices' if there's no error
                if 'choices' in result:
                    generated_text = result['choices'][0]['message']['content']

                    # Strip out any <think>...</think> blocks if present (for "thinking" models)
                    # This ensures only the assistant's final answer is returned to the frontend.
                    if isinstance(generated_text, str):
                        try:
                            # Use DOTALL so newlines are matched inside the think tags
                            generated_text = re.sub(r"<think>[\s\S]*?</think>", "", generated_text, flags=re.IGNORECASE)
                            generated_text = generated_text.strip()
                        except Exception as clean_ex:
                            logger.warning(f"Failed to strip <think> blocks: {clean_ex}")

                    logger.info(f"Successfully generated completion from Open Router API (id: {gen_id})")
                    return generated_text
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return "Unexpected response format from API"
            else:
                logger.error(f"Error from Open Router API: {response.status_code} - {response.text}")
                return f"Error generating completion. Status code: {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error(f"OpenRouter API request timed out after 60 seconds for model {self.model}.")
            return "Error generating completion: Request timed out"
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return f"Error generating completion: {str(e)}"
