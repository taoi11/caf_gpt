from __future__ import annotations

from typing import List, Mapping, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailConfig(BaseSettings):
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
        agent_emails = values.get("agent_emails")
        if isinstance(agent_emails, str):
            values = dict(values)
            values["agent_emails"] = [w.strip() for w in agent_emails.split(",") if w.strip()]
        elif agent_emails is None:
            values = dict(values)
            values["agent_emails"] = []
        return values


class LLMConfig(BaseSettings):
    openrouter_api_key: str
    model: str = "openai/gpt-4o-mini"
    temperature: float = 0.2
    request_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(env_prefix="LLM__", extra="ignore")


class StorageConfig(BaseSettings):
    s3_bucket_name: str
    s3_endpoint_url: str = ""
    s3_access_key: str
    s3_secret_key: str
    s3_region: str = ""
    use_path_style_endpoint: bool = False

    model_config = SettingsConfigDict(env_prefix="STORAGE__", extra="ignore")


class AppConfig(BaseSettings):
    dev_mode: bool = False
    email: EmailConfig
    llm: LLMConfig
    storage: StorageConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


config = AppConfig()
