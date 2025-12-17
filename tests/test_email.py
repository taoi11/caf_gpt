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
from datetime import datetime

from src.email_code.components.email_composer import EmailComposer
from src.email_code.components.email_sender import EmailSender
from src.email_code.components.email_thread_manager import EmailThreadManager
from src.email_code.components.email_adapter import EmailAdapter
from src.email_code.simple_email_handler import SimpleEmailProcessor
from src.email_code.imap_connector import IMAPConnector
from src.email_code.types import ParsedEmailData, ReplyData, EmailRecipients
from src.config import EmailConfig


@pytest.fixture
def mock_config():
    """Mock EmailConfig with IMAP and SMTP settings."""
    config = Mock()
    # IMAP settings
    config.imap_host = "imap.example.com"
    config.imap_port = 993
    config.imap_username = "user"
    config.imap_password = "pass"
    config.email_process_interval = 30
    # SMTP settings (for completeness, even though we mock EmailSender)
    config.smtp_host = "smtp.example.com"
    config.smtp_port = 587
    config.smtp_username = "user"
    config.smtp_password = "pass"
    config.smtp_use_tls = True
    config.smtp_use_ssl = False
    return config


@pytest.fixture
def sample_mail_message():
    """Sample imap_tools MailMessage for testing."""
    msg = Mock(spec=MailMessage)
    msg.uid = "test123"
    msg.from_ = "test@forces.gc.ca"
    msg.to = ["agent@caf.com"]
    msg.cc = []
    msg.subject = "Test Subject"
    msg.text = "Hello, this is a test body."
    msg.html = "<p>Hello, this is a test body.</p>"
    return msg


# Deprecated: search_unseen_uids - test removed as method is deprecated


@patch("src.email_code.imap_connector.MailBox")
def test_imap_connector_fetch_unseen_sorted(mock_mailbox, mock_config):
    """Test IMAP connector batch fetches and sorts unseen emails using imap_tools."""
    # Mock MailBox context manager
    mock_mb = MagicMock()
    # MailBox().login() returns the context manager
    mock_mailbox.return_value.login.return_value.__enter__.return_value = mock_mb

    # Mock uids to return test UIDs
    mock_mb.uids.return_value = ["2", "1"]

    # Mock fetch to return test messages with dates
    mock_msg1 = MagicMock()
    mock_msg1.uid = "2"
    mock_msg1.date = datetime(2023, 1, 2)
    mock_msg2 = MagicMock()
    mock_msg2.uid = "1"
    mock_msg2.date = datetime(2023, 1, 1)  # Older

    # Mock fetch to return all messages in one batch call
    mock_mb.fetch.return_value = [mock_msg2, mock_msg1]

    connector = IMAPConnector(mock_config)
    msgs = connector.fetch_unseen_sorted()

    assert len(msgs) == 2
    assert msgs[0].uid == "1"  # Oldest first
    assert msgs[1].uid == "2"
    mock_mb.uids.assert_called_once_with("UNSEEN")


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
        thread_id="test123",
    )

    headers = EmailThreadManager.build_threading_headers(parsed)
    assert "In-Reply-To" in headers
    assert headers["In-Reply-To"] == "<test123@domain.com>"
    assert "References" in headers


def test_email_composer_composes_reply():
    """Test EmailComposer builds a professional HTML reply dict for Redmail."""
    parsed = ParsedEmailData(
        message_id="<test123@domain.com>",
        from_addr="test@example.com",
        recipients=EmailRecipients(to=["agent@caf.com"]),
        subject="Test Subject",
        body="Test body",
        date="2023-01-01",
        thread_id="test123",
    )

    reply_data = ReplyData(
        to=["test@example.com"],
        subject="Re: Test Subject",
        body="Reply body",
        in_reply_to="<test123@domain.com>",
        references="<test123@domain.com>",
    )

    composer = EmailComposer()
    composed = composer.compose_reply(reply_data, parsed, "agent@caf.com")
    assert isinstance(composed, dict)
    assert "subject" in composed
    assert "to" in composed
    assert "html_body" in composed
    assert composed["subject"].startswith("Re: Test Subject")
    assert "Reply body" in composed["html_body"]
    assert "From:" in composed["html_body"]  # From template
    assert "Calibri" in composed["html_body"]  # Outlook-style font
    assert composed["to"] == ["test@example.com"]
    assert composed["in_reply_to"] == "<test123@domain.com>"


@patch("src.email_code.simple_email_handler.EmailSender")
@patch("src.email_code.simple_email_handler.PromptManager")
@patch("src.email_code.simple_email_handler.IMAPConnector")
def test_simple_email_processor_process_unseen(
    mock_connector_class, mock_prompt_manager, mock_email_sender, mock_config
):
    """Test SimpleEmailProcessor processes unseen emails using mocked IMAP connector."""
    # Mock connector and its methods
    mock_connector = MagicMock()
    mock_mailbox = MagicMock()
    mock_connector.mailbox.return_value.__enter__.return_value = mock_mailbox

    mock_msg = MagicMock()
    mock_msg.uid = "1"
    mock_msg.from_ = "test@forces.gc.ca"
    mock_msg.to = ["agent@caf.com"]
    mock_msg.cc = []
    mock_msg.subject = "Test"
    mock_msg.text = "Body"
    mock_connector.fetch_unseen_sorted.return_value = [mock_msg]

    mock_connector_class.return_value = mock_connector

    processor = SimpleEmailProcessor(mock_config)
    processor.process_unseen_emails()

    # Verify the connector was called with shared mailbox session
    mock_connector.fetch_unseen_sorted.assert_called_once_with(mock_mailbox)
    mock_connector.mark_seen.assert_called_once_with("1", mock_mailbox)


def test_email_adapter_adapts_mail_message(sample_mail_message):
    """Test EmailAdapter converts MailMessage to ParsedEmailData."""
    parsed = EmailAdapter.adapt_mail_message(sample_mail_message)

    assert isinstance(parsed, ParsedEmailData)
    assert parsed.from_addr == "test@forces.gc.ca"
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


@patch("src.email_code.simple_email_handler.EmailSender")
@patch("src.email_code.simple_email_handler.PromptManager")
def test_simple_email_processor_uses_adapter(
    mock_prompt_manager, mock_email_sender, sample_mail_message
):
    """Test SimpleEmailProcessor correctly uses EmailAdapter for conversion."""
    processor = SimpleEmailProcessor(Mock())
    # Verify that the processor uses the EmailAdapter
    parsed = processor._adapt_mail_message(sample_mail_message)

    # The adapter should be called, so this should work
    assert isinstance(parsed, ParsedEmailData)
    assert parsed.from_addr == "test@forces.gc.ca"
    assert parsed.subject == "Test Subject"
    assert "test body" in parsed.body
    assert parsed.message_id == "test123"
    assert parsed.recipients.to == ["agent@caf.com"]


def test_email_sender_sends_reply(mock_yagmail, mock_composed_reply, sample_parsed_data):
    """Test EmailSender composes and sends a reply using yagmail mock."""
    sender = EmailSender()
    reply_data = ReplyData(
        to=["test@example.com"],
        body="Test reply body",
        cc=["cc@example.com"],
        subject="Re: Test Subject",
        in_reply_to="<test123@domain.com>",
        references="<test123@domain.com>",
    )

    # Mock compose_reply to return our composed dict
    with patch.object(EmailComposer, "compose_reply", return_value=mock_composed_reply):
        sent = sender.send_reply(reply_data, sample_parsed_data, "agent@caf.com")

    assert sent is True
    mock_yagmail.send.assert_called_once()
    call_args = mock_yagmail.send.call_args[1]
    # yagmail arguments
    assert call_args["to"] == ["test@example.com"]
    assert call_args["cc"] == ["cc@example.com"]
    assert call_args["subject"] == "Re: Test Subject"
    # contents is a list with HTML body
    assert len(call_args["contents"]) == 1
    assert "Test reply body" in call_args["contents"][0]
    assert "In-Reply-To" in call_args.get("headers", {})


@pytest.fixture
def mock_yagmail():
    """Mock yagmail SMTP instance."""
    with patch("src.email_code.components.email_sender.yagmail.SMTP") as mock_smtp:
        instance = mock_smtp.return_value
        instance.send.return_value = None  # Simulate successful send
        yield instance


@pytest.fixture
def mock_composed_reply():
    """Mock composed reply dict from EmailComposer."""
    return {
        "subject": "Re: Test Subject",
        "to": ["test@example.com"],
        "cc": ["cc@example.com"],
        "html_body": "<html><body>Test reply body<br><blockquote>Original</blockquote></body></html>",
        "in_reply_to": "<test123@domain.com>",
        "references": "<test123@domain.com>",
    }


@pytest.fixture
def sample_parsed_data():
    """Sample ParsedEmailData for testing."""
    return ParsedEmailData(
        message_id="<test123@domain.com>",
        from_addr="test@example.com",
        recipients=EmailRecipients(to=["agent@caf.com"], cc=[]),
        subject="Test Subject",
        body="Test body",
        date="2023-01-01",
        thread_id="test123",
    )
