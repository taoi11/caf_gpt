from __future__ import annotations

import os

# Ensure environment contains required sections before importing config
os.environ.setdefault("EMAIL__IMAP_HOST", "imap.test")
os.environ.setdefault("EMAIL__IMAP_USERNAME", "user")
os.environ.setdefault("EMAIL__IMAP_PASSWORD", "secret")
os.environ.setdefault("LLM__OPENROUTER_API_KEY", "key")
os.environ.setdefault("STORAGE__S3_BUCKET_NAME", "bucket")
os.environ.setdefault("STORAGE__S3_ACCESS_KEY", "access")
os.environ.setdefault("STORAGE__S3_SECRET_KEY", "secret")
os.environ.setdefault("STORAGE__S3_REGION", "us-west-2")

from src.config import EmailConfig


def test_agent_emails_string_is_split_into_list() -> None:
    config = EmailConfig(
        imap_host="imap.test",
        imap_username="user",
        imap_password="secret",
        agent_emails="foo@example.com, bar@example.com"
    )

    assert config.agent_emails == ["foo@example.com", "bar@example.com"]
    assert config.agent_email is None


def test_defaults_are_set() -> None:
    config = EmailConfig(
        imap_host="imap.test",
        imap_username="user",
        imap_password="secret"
    )

    assert config.delete_after_process is True
    assert config.email_process_interval == 30
    assert config.agent_emails == []
