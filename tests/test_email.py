"""
tests/test_email.py

Basic unit tests for email components using imap_tools integration.
Tests the simplified email processing with automated parsing.

Focus on: IMAP connector with imap_tools, email components, and processor functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from email.message import EmailMessage
from imap_tools import MailMessage

from src.email_code.components.email_composer import EmailComposer
from src.email_code.components.email_thread_manager import EmailThreadManager
from src.email_code.components.email_adapter import EmailAdapter
from src.email_code.simple_email_handler import SimpleEmailProcessor
from src.email_code.imap_connector import IMAPConnector
from src.email_code.types import ParsedEmailData, ReplyData, EmailRecipients
from src.config import EmailConfig


@pytest.fixture
def mock_config():
    """Mock EmailConfig with IMAP settings."""
    config = Mock(spec=EmailConfig)
    config.imap_host = "imap.example.com"
    config.imap_port = 993
    config.imap_username = "user"
    config.imap_password = "pass"
    config.email_process_interval = 30
    return config


@pytest.fixture
def sample_mail_message():
    """Sample imap_tools MailMessage for testing."""
    msg = Mock(spec=MailMessage)
    msg.uid = "test123"
    msg.from_ = "test@example.com"
    msg.to = ["agent@caf.com"]
    msg.cc = []
    msg.subject = "Test Subject"
    msg.text = "Hello, this is a test body."
    msg.html = "<p>Hello, this is a test body.</p>"
    return msg


# Deprecated: search_unseen_uids - test removed as method is deprecated


@patch('src.email_code.imap_connector.MailBox')
def test_imap_connector_fetch_unseen_sorted(mock_mailbox, mock_config):
    """Test IMAP connector batch fetches and sorts unseen emails using imap_tools."""
    # Mock MailBox context manager
    mock_mb = MagicMock()
    mock_mailbox.return_value.__enter__.return_value = mock_mb
    
    # Mock fetch to return test messages with dates
    mock_msg1 = MagicMock()
    mock_msg1.uid = "2"
    mock_msg1.date = datetime(2023, 1, 2)
    mock_msg2 = MagicMock()
    mock_msg2.uid = "1"
    mock_msg2.date = datetime(2023, 1, 1)  # Older
    mock_mb.fetch.return_value = [mock_msg1, mock_msg2]
    
    connector = IMAPConnector(mock_config)
    msgs = connector.fetch_unseen_sorted()
    
    assert len(msgs) == 2
    assert msgs[0].uid == "1"  # Oldest first
    assert msgs[1].uid == "2"
    mock_mb.fetch.assert_called_once_with("UNSEEN", mark_seen=False)

# Deprecated: fetch_email_message - test removed as method is deprecated


# Removed duplicate test


def test_email_thread_manager_builds_headers():
    """Test EmailThreadManager builds threading headers."""
    # Create ParsedEmailData from sample message
    parsed = ParsedEmailData(
        message_id="<test123@domain.com>",
        from_addr="test@example.com",
        recipients=EmailRecipients(to=["agent@caf.com"]),
        subject="Test Subject",
        body="Test body",
        thread_id="test123"
    )
    
    headers = EmailThreadManager.build_threading_headers(parsed)
    assert "In-Reply-To" in headers
    assert headers["In-Reply-To"] == "<test123@domain.com>"
    assert "References" in headers


def test_email_composer_composes_reply():
    """Test EmailComposer builds a valid EmailMessage."""
    parsed = ParsedEmailData(
        message_id="<test123@domain.com>",
        from_addr="test@example.com",
        recipients=EmailRecipients(to=["agent@caf.com"]),
        subject="Test Subject",
        body="Test body",
        thread_id="test123"
    )
    
    reply_data = ReplyData(
        to=["test@example.com"],
        subject="Re: Test Subject",
        body="Reply body",
        in_reply_to="<test123@domain.com>",
        references="<test123@domain.com>"
    )
    
    msg = EmailComposer.compose_reply(reply_data, parsed, "agent@caf.com")
    assert isinstance(msg, EmailMessage)
    assert msg["From"] == "agent@caf.com"
    assert msg["To"] == "test@example.com"
    assert msg["Subject"].startswith("Re: Test Subject")
    assert "Reply body" in msg.get_content()
    assert "Original message" in msg.get_content()


@patch('src.email_code.simple_email_handler.IMAPConnector')
def test_simple_email_processor_process_unseen(mock_connector_class, mock_config):
    """Test SimpleEmailProcessor processes unseen emails using mocked IMAP connector."""
    # Mock connector and its methods
    mock_connector = MagicMock()
    mock_msg = MagicMock()
    mock_msg.uid = "1"
    mock_msg.from_ = "test@example.com"
    mock_msg.to = ["agent@caf.com"]
    mock_msg.cc = []
    mock_msg.subject = "Test"
    mock_msg.text = "Body"
    mock_connector.fetch_unseen_sorted.return_value = [mock_msg]
    
    mock_connector_class.return_value = mock_connector
    
    processor = SimpleEmailProcessor(mock_config)
    processor.process_unseen_emails()
    
    # Verify the connector was called correctly
    mock_connector.fetch_unseen_sorted.assert_called_once()
    mock_connector.mark_seen.assert_called_once_with("1")


def test_email_adapter_adapts_mail_message(sample_mail_message):
    """Test EmailAdapter converts MailMessage to ParsedEmailData."""
    parsed = EmailAdapter.adapt_mail_message(sample_mail_message)
    
    assert isinstance(parsed, ParsedEmailData)
    assert parsed.from_addr == "test@example.com"
    assert parsed.subject == "Test Subject"
    assert "test body" in parsed.body
    assert parsed.message_id == "test123"
    assert parsed.recipients.to == ["agent@caf.com"]
    assert parsed.recipients.cc == []
    assert parsed.thread_id == "test123"


def test_email_adapter_strips_html():
    """Test EmailAdapter HTML stripping functionality."""
    html = "<p>Hello <strong>World</strong>!</p><br>"
    clean = EmailAdapter._strip_html(html)
    
    assert "Hello World!" in clean
    assert "<p>" not in clean
    assert "<strong>" not in clean
    assert "<br>" not in clean


def test_simple_email_processor_uses_adapter(sample_mail_message):
    """Test SimpleEmailProcessor correctly uses EmailAdapter for conversion."""
    processor = SimpleEmailProcessor(Mock())
    # Verify that the processor uses the EmailAdapter
    parsed = processor._adapt_mail_message(sample_mail_message)
    
    # The adapter should be called, so this should work
    assert isinstance(parsed, ParsedEmailData)
    assert parsed.from_addr == "test@example.com"
    assert parsed.subject == "Test Subject"
    assert "test body" in parsed.body
    assert parsed.message_id == "test123"
    assert parsed.recipients.to == ["agent@caf.com"]
