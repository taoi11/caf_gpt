"""
Base LangChain wrapper for OpenRouter integration.

This module provides a simple interface for interacting with LLMs through OpenRouter.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Union

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.pydantic_v1 import root_validator

logger = logging.getLogger(__name__)

class OpenRouterError(Exception):
    """Base exception class for OpenRouter errors."""
    pass

class OpenRouterChatModel(BaseChatModel):
    """
    Chat model implementation for OpenRouter.
    
    This class provides a LangChain compatible interface for OpenRouter's chat completion API.
    """
    
    openrouter_api_key: Optional[str] = None
    model_name: str = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    http_referer: Optional[str] = None
    request_timeout: Optional[float] = None
    streaming: bool = False
    
    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that API key exists in environment."""
        openrouter_api_key = values.get("openrouter_api_key")
        if openrouter_api_key is None:
            openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
            if openrouter_api_key is None:
                raise ValueError(
                    "OpenRouter API key must be provided either through "
                    "openrouter_api_key parameter or OPENROUTER_API_KEY environment variable."
                )
            values["openrouter_api_key"] = openrouter_api_key
            
        http_referer = values.get("http_referer")
        if http_referer is None:
            http_referer = os.environ.get("OPENROUTER_HTTP_REFERER", "https://caf-gpt.example.com")
            values["http_referer"] = http_referer
        
        # Ensure model_name is set
        if values.get("model_name") is None:
            values["model_name"] = os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            
        return values
    
    def _convert_messages_to_openrouter_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages to OpenRouter format."""
        openrouter_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                openrouter_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                openrouter_messages.append({"role": "assistant", "content": message.content})
            elif isinstance(message, SystemMessage):
                openrouter_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, ChatMessage):
                openrouter_messages.append({"role": message.role, "content": message.content})
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return openrouter_messages
    
    def _create_chat_result(self, response: Dict[str, Any]) -> ChatResult:
        """Create a ChatResult from the OpenRouter API response."""
        generations = []
        for choice in response.get("choices", []):
            message = choice.get("message", {})
            text = message.get("content", "")
            generation_info = {
                "finish_reason": choice.get("finish_reason"),
            }
            
            # Create appropriate message type based on role
            role = message.get("role", "assistant")
            if role == "assistant":
                message = AIMessage(content=text)
            elif role == "user":
                message = HumanMessage(content=text)
            elif role == "system":
                message = SystemMessage(content=text)
            else:
                message = ChatMessage(role=role, content=text)
                
            generations.append(ChatGeneration(
                message=message,
                generation_info=generation_info
            ))
            
        # Extract token usage information
        token_usage = response.get("usage", {})
        
        return ChatResult(
            generations=generations,
            llm_output={
                "token_usage": token_usage,
                "model_name": response.get("model", self.model_name),
            }
        )
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat completion using OpenRouter API."""
        # Convert messages to OpenRouter format
        openrouter_messages = self._convert_messages_to_openrouter_format(messages)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openrouter_api_key}",
        }
        
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
            
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "messages": openrouter_messages,
            "temperature": self.temperature,
            "stream": self.streaming,
        }
        
        # Add optional parameters if provided
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if stop is not None:
            payload["stop"] = stop
            
        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
                
        try:
            # Make API request
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=self.request_timeout,
            )
            
            # Check for errors
            if response.status_code != 200:
                error_data = response.json().get("error", {})
                error_message = error_data.get("message", response.text)
                raise OpenRouterError(f"API error {response.status_code}: {error_message}")
                    
            # Parse response
            response_data = response.json()
            
            # Create and return ChatResult
            return self._create_chat_result(response_data)
            
        except requests.exceptions.Timeout:
            raise OpenRouterError("Request to OpenRouter API timed out")
        except requests.exceptions.RequestException as e:
            raise OpenRouterError(f"Request to OpenRouter API failed: {str(e)}")
        except json.JSONDecodeError:
            raise OpenRouterError(f"Failed to parse response from OpenRouter API: {response.text}")
        except Exception as e:
            raise OpenRouterError(f"Unexpected error: {str(e)}")
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "openrouter"
        
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "streaming": self.streaming,
        }

class LangChainWrapper:
    """
    Simple wrapper for LangChain functionality with OpenRouter.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        streaming: bool = False,
    ):
        """
        Initialize the LangChain wrapper.
        
        Args:
            model_name: The model to use for chat completions (defaults to OPENROUTER_MODEL env var).
            temperature: Controls randomness in responses (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var).
            streaming: Whether to stream the response (defaults to False).
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        
        # Initialize the chat model
        self.chat_model = OpenRouterChatModel(
            openrouter_api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
        )
        
        logger.info(f"LangChain wrapper initialized with model: {self.chat_model.model_name}")
    
    def chat(
        self,
        system_prompt: Optional[str] = None,
        user_prompt: str = "",
        chat_history: Optional[List[BaseMessage]] = None,
    ) -> str:
        """
        Send a prompt to the chat model and get a response.
        
        Args:
            system_prompt: Optional system prompt to set context.
            user_prompt: The user's prompt/question.
            chat_history: Optional list of previous messages for context.
            
        Returns:
            The model's response text.
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)
        
        # Add user prompt
        messages.append(HumanMessage(content=user_prompt))
        
        try:
            # Get response from model
            response = self.chat_model.invoke(messages)
            
            # Return the content of the response
            return response.content
            
        except OpenRouterError as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}")
            raise OpenRouterError(f"Failed to get response: {str(e)}") 