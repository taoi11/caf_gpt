from pydantic_settings import BaseSettings


class EmailConfig(BaseSettings):
    # IMAP settings
    imap_host: str
    imap_port: int = 993
    imap_username: str
    imap_password: str
    agent_email: str  # Bot's email

    # SMTP settings
    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str

    # Email processing
    delete_after_process: bool = True
    email_process_interval: int = 30  # seconds


class LLMConfig(BaseSettings):
    openrouter_api_key: str
    model: str = "openai/gpt-4o-mini"  # Default model
    

class StorageConfig(BaseSettings):
    # Storage settings (S3-compatible)
    s3_bucket_name: str
    s3_endpoint_url: str = ""  # Optional for Cloudflare R2, MinIO
    s3_access_key: str
    s3_secret_key: str
    s3_region: str = ""


class AppConfig(BaseSettings):
    # App-level settings
    dev_mode: bool = False
    
    email: EmailConfig
    llm: LLMConfig
    storage: StorageConfig
    
    class Config:
        env_nested_delimiter = "__"


# Global config instance
config = AppConfig()
