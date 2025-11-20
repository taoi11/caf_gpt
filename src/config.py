"""
src/config.py

Centralized configuration management using Pydantic for the application, including email, LLM, and storage settings.

Top-level declarations:
- EmailConfig: Configuration for IMAP email access and processing
- LLMConfig: Settings for the LLM model and API
- StorageConfig: S3 storage configuration
- AppConfig: Main application configuration aggregating sub-configs
- config: Global instance of AppConfig
"""

from __future__ import annotations

from typing import List, Mapping, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Email address for policy-related agents (prime_foo)
# Only emails sent to this address should trigger the prime_foo agent workflow
POLICY_AGENT_EMAIL = "policy@caf-gpt.com"


def should_trigger_agent(to_addresses: List[str]) -> bool:
    """
    Determine if an email should trigger the prime_foo agent based on its recipient address.

    Args:
        to_addresses: List of email addresses the message was sent to

    Returns:
        True if the email was sent to the policy agent address, False otherwise
    """
    return POLICY_AGENT_EMAIL in to_addresses


class EmailConfig(BaseSettings):
    # Pydantic settings for IMAP email configuration, including host, credentials, and processing options
    imap_host: str
    imap_port: int = 993
    imap_username: str
    imap_password: str

    delete_after_process: bool = True
    email_process_interval: int = 30

    model_config = SettingsConfigDict(env_prefix="EMAIL__", extra="ignore")


class LLMConfig(BaseSettings):
    # Pydantic settings for LLM configuration, including API key, model selection, temperature, and timeout

    # OpenRouter (Secondary)
    openrouter_api_key: str
    openrouter_model: str = "x-ai/grok-code-fast-1"

    # Ollama (Primary)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Common
    temperature: float = 0.7
    request_timeout_seconds: float = 120.0  # Increased to 2 min for Ollama

    model_config = SettingsConfigDict(env_prefix="LLM__", extra="ignore")


class StorageConfig(BaseSettings):
    # Pydantic settings for S3-compatible storage, including bucket, credentials, endpoint, and path style options
    s3_bucket_name: str = "policies"  # Default to 'policies' bucket
    s3_endpoint_url: str = ""
    s3_access_key: str
    s3_secret_key: str
    s3_region: str = ""
    use_path_style_endpoint: bool = False

    model_config = SettingsConfigDict(env_prefix="STORAGE__", extra="ignore")


class LogConfig(BaseSettings):
    # Pydantic settings for logging configuration
    log_level: str = "INFO"
    json_logging: bool = False

    model_config = SettingsConfigDict(env_prefix="LOG__", extra="ignore")


class AppConfig(BaseSettings):
    # Main aggregated configuration class loading sub-configs from environment variables and .env file
    dev_mode: bool = False
    email: EmailConfig
    llm: LLMConfig
    storage: StorageConfig
    log: LogConfig = Field(default_factory=LogConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


config = AppConfig()
