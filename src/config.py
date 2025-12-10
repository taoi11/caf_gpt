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

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Email address for policy-related agents (prime_foo)
# Only emails sent to this address should trigger the prime_foo agent workflow
POLICY_AGENT_EMAIL = "agent@caf-gpt.com"

# Email address for feedback note agent (pacenote)
# Only emails sent to this address should trigger the feedback note agent workflow
PACENOTE_AGENT_EMAIL = "pacenote@caf-gpt.com"


def should_trigger_agent(to_addresses: List[str]) -> Optional[str]:
    # Determine which agent should process the email based on recipient address
    # Returns: "policy" for policy agent, "pacenote" for feedback note agent, None if no agent needed
    # Priority: If both addresses present, prefer the more specific pacenote agent
    has_policy = POLICY_AGENT_EMAIL in to_addresses
    has_pacenote = PACENOTE_AGENT_EMAIL in to_addresses
    
    # If both present, prefer pacenote (more specific)
    if has_pacenote:
        return "pacenote"
    if has_policy:
        return "policy"
    return None


class EmailConfig(BaseSettings):
    # Pydantic settings for IMAP email configuration, including host, credentials, and processing options
    imap_host: str
    imap_port: int = 993
    imap_username: str
    imap_password: str

    email_process_interval: int = 60

    # SMTP settings for sending replies
    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    model_config = SettingsConfigDict(env_prefix="EMAIL__", extra="ignore")


class LLMConfig(BaseSettings):
    # Pydantic settings for LLM configuration, including API key, model selection, temperature, and timeout

    # OpenRouter API
    openrouter_api_key: str
    openrouter_model: str = "x-ai/grok-code-fast-1"

    # Agent-specific models
    pacenote_model: str = "anthropic/claude-haiku-4.5"
    prime_foo_model: str = "mistralai/mistral-large-2512"
    leave_foo_model: str = "x-ai/grok-4.1-fast"

    # Common
    temperature: float = 0.7
    request_timeout_seconds: float = 60.0

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


config = AppConfig()  # type: ignore[call-arg]
