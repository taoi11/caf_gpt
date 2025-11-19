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


class EmailConfig(BaseSettings):
    # Pydantic settings for IMAP email configuration, including host, credentials, and processing options
    imap_host: str
    imap_port: int = 993
    imap_username: str
    imap_password: str
    agent_email: Optional[str] = None
    agent_emails: List[str] = Field(default_factory=list)

    delete_after_process: bool = True
    email_process_interval: int = 30

    model_config = SettingsConfigDict(env_prefix="EMAIL__", extra="ignore")

    @model_validator(mode="before")
    def _normalize_agent_emails(cls, values: Mapping[str, object]) -> Mapping[str, object]:
        # Normalize agent_emails input: split comma-separated string into list or set empty list if None
        agent_emails = values.get("agent_emails")
        if isinstance(agent_emails, str):
            values = dict(values)
            values["agent_emails"] = [w.strip() for w in agent_emails.split(",") if w.strip()]
        elif agent_emails is None:
            values = dict(values)
            values["agent_emails"] = []
        return values


class LLMConfig(BaseSettings):
    # Pydantic settings for LLM configuration, including API key, model selection, temperature, and timeout
    openrouter_api_key: str
    model: str = "openai/gpt-4o-mini"
    temperature: float = 0.2
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
    json_logging: bool = False

    model_config = SettingsConfigDict(env_prefix="LOG__", extra="ignore")



class AppConfig(BaseSettings):
    # Main aggregated configuration class loading sub-configs from environment variables and .env file
    dev_mode: bool = False
    email: EmailConfig
    llm: LLMConfig
    storage: StorageConfig
    log: LogConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


config = AppConfig()
