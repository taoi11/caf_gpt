"""
tests/test_config.py

Unit tests for configuration validation, focusing on EmailConfig parsing and default behaviors.

Top-level declarations:
- test_policy_agent_email_constant: Verify POLICY_AGENT_EMAIL constant is set correctly
- test_defaults_are_set: Confirm default values for processing options
"""

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

from src.config import EmailConfig, POLICY_AGENT_EMAIL, should_trigger_agent


def test_policy_agent_email_constant() -> None:
    # Verify that POLICY_AGENT_EMAIL constant is set to the correct email address
    assert POLICY_AGENT_EMAIL == "policy@caf-gpt.com"


def test_should_trigger_agent_with_policy_email() -> None:
    # Verify that should_trigger_agent returns True when policy email is in recipient list
    assert should_trigger_agent(["policy@caf-gpt.com"]) is True
    assert should_trigger_agent(["other@example.com", "policy@caf-gpt.com"]) is True


def test_should_trigger_agent_without_policy_email() -> None:
    # Verify that should_trigger_agent returns False when policy email is not in recipient list
    assert should_trigger_agent(["other@example.com"]) is False
    assert should_trigger_agent(["pacenote@caf-gpt.com"]) is False
    assert should_trigger_agent([]) is False


def test_defaults_are_set() -> None:
    # Confirm that default values are applied correctly for processing flags
    config = EmailConfig(imap_host="imap.test", imap_username="user", imap_password="secret")

    assert config.delete_after_process is True
    assert config.email_process_interval == 30
