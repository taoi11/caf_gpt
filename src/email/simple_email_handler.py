

"""
src/email/simple_email_handler.py

SimpleEmailHandler: Main orchestrator for processing emails - parse, AI via AgentCoordinator, compose reply, send.
For prototype: Synchronous, basic validation, plain text focus.
"""

import smtplib
from email.message import EmailMessage
from typing import Optional

from src.config import AppConfig
from src.email.components.email_parser import EmailParser
from src.email.components.email_thread_manager import EmailThreadManager
from src.email.components.email_composer import EmailComposer
from src.email.types import ParsedEmailData, ReplyData
from src.agents.agent_coordinator import AgentCoordinator
from src.app_logging import get_logger

logger = get_logger(__name__)

class SimpleEmailHandler:
    def __init__(self, config: AppConfig, coordinator: AgentCoordinator):
        self.config = config
        self.coordinator = coordinator
        self.agent_email = config.email.agent_email
        self.logger = get_logger(__name__)
        self.smtp_config = config.email.smtp

    def process_email(self, raw_message: bytes) -> None:
        """
        Main entry point: Parse email, validate, process with AI, send reply if needed.
        """
        try:
            logger.debug("Starting email processing", message_size=len(raw_message))
            parsed = EmailParser.parse_email(raw_message)
            self._validate_sender(parsed)
            context = self._build_context(parsed)
            logger.info("Sending email context to agent coordinator", message_id=parsed.message_id, from_addr=parsed.from_addr)
            response = self.coordinator.process_email_with_prime_foo(context)
            if response and hasattr(response, 'reply_text') and response.reply_text:
                self._send_reply_for_parsed(parsed, response.reply_text)
            else:
                self.logger.info("No reply generated for email", message_id=parsed.message_id)
        except Exception as e:
            self.logger.error("Error processing email", error=str(e), exc_info=True, message_size=len(raw_message))
            # For prototype: Don't send error reply yet
            raise  # Re-raise to prevent deletion on failure

    def _validate_sender(self, parsed: ParsedEmailData) -> None:
        """Prevent self-loops."""
        try:
            if parsed.from_addr == self.agent_email:
                self.logger.warning("Self-loop detected: ignoring email from agent", message_id=parsed.message_id, from_addr=parsed.from_addr)
                raise ValueError("Self-loop detected: ignoring email from agent")
            logger.debug("Sender validated", from_addr=parsed.from_addr)
        except Exception as e:
            self.logger.error("Sender validation failed", error=str(e), from_addr=parsed.from_addr)
            raise

    def _build_context(self, parsed: ParsedEmailData) -> str:
        """Build string context for AgentCoordinator."""
        try:
            context = f"Subject: {parsed.subject}\nFrom: {parsed.from_addr}\nTo: {', '.join(parsed.recipients.to)}\n\nBody:\n{parsed.body}"
            logger.debug("Context built for AI", context_length=len(context), message_id=parsed.message_id)
            return context
        except Exception as e:
            self.logger.error("Failed to build context", error=str(e), message_id=parsed.message_id)
            raise

    def _send_reply_for_parsed(self, parsed: ParsedEmailData, reply_text: str) -> None:
        """Build and send reply for parsed email."""
        try:
            # Threading headers
            threading_headers = EmailThreadManager.build_threading_headers(parsed)

            # Reply data
            reply_subject = f"Re: {parsed.subject}" if parsed.subject else "Re:"
            reply_data = ReplyData(
                to=[parsed.from_addr],
                subject=reply_subject,
                body=reply_text,
                in_reply_to=threading_headers.get("In-Reply-To"),
                references=threading_headers.get("References")
            )

            # Compose
            msg = EmailComposer.compose_reply(reply_data, parsed, self.agent_email)

            # Send
            self._send_smtp(msg)
            self.logger.info("Reply sent successfully", message_id=parsed.message_id, to=parsed.from_addr, reply_length=len(reply_text))
        except Exception as e:
            self.logger.error("Failed to send reply", error=str(e), message_id=parsed.message_id, to=parsed.from_addr)
            raise

    def _send_smtp(self, msg: EmailMessage) -> None:
        """Send email via SMTP."""
        try:
            with smtplib.SMTP(self.smtp_config.host, self.smtp_config.port) as server:
                server.starttls()
                server.login(self.smtp_config.username, self.smtp_config.password)
                server.send_message(msg)
            logger.debug("SMTP send completed", to=msg["To"], subject=msg["Subject"])
        except Exception as e:
            self.logger.error("SMTP send failed", error=str(e), host=self.smtp_config.host, to=msg["To"] if 'msg' in locals() else "unknown")
            raise

