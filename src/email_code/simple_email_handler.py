"""
src/email_code/simple_email_handler.py

Simple email processing handler that polls IMAP for new emails using imap_tools, parses them, and logs them.
Uses imap_tools for automatic email parsing, eliminating manual parsing boilerplate.

Top-level declarations:
- LoggedEmail: Dataclass for logging email metadata
- SimpleEmailProcessor: Class for polling and processing unseen emails via IMAP with imap_tools
"""

from __future__ import annotations

import logging
import textwrap
import threading

from dataclasses import dataclass
from imap_tools import MailMessage  # type: ignore[attr-defined]

from src.config import EmailConfig, should_trigger_agent, POLICY_AGENT_EMAIL, PACENOTE_AGENT_EMAIL
from src.email_code.imap_connector import IMAPConnector, IMAPConnectorError
from src.email_code.types import ParsedEmailData, ReplyData
from src.email_code.components.email_adapter import EmailAdapter
from src.email_code.components.email_sender import EmailSender
from src.email_code.components.email_thread_manager import EmailThreadManager
from src.agents.prompt_manager import PromptManager
from src.agents.agent_coordinator import AgentCoordinator
from src.agents.types import AgentResponse
from src.utils.spam_filter import is_sender_allowed

logger = logging.getLogger(__name__)


@dataclass
class LoggedEmail:
    # Dataclass holding metadata for logged emails: UID, sender, subject, and content preview
    # Used for logging email metadata with truncated previews for readability

    uid: str
    sender: str
    subject: str
    preview: str


class SimpleEmailProcessor:
    # Basic processor for polling IMAP inbox, parsing new emails with imap_tools, and logging them
    # Uses threading.Lock to prevent IMAP race conditions and processes emails oldest-first

    def __init__(self, config: EmailConfig) -> None:
        # Initialize with email config, connector, and components
        self._config = config
        self._connector = IMAPConnector(config)
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.sender = EmailSender()
        self.prompt_manager = PromptManager()
        self.coordinator = AgentCoordinator(self.prompt_manager)

    def run_loop(self) -> None:
        # Main loop that continuously polls the IMAP inbox at intervals
        logger.info(f"Starting IMAP poll loop, interval={self._config.email_process_interval}")
        try:
            while not self._stop_event.is_set():
                with self._lock:
                    self.process_unseen_emails()
                self._stop_event.wait(self._config.email_process_interval)
        finally:
            logger.info("IMAP poll loop stopped")
            

    def stop(self) -> None:
        # Signal the processing loop to stop
        self._stop_event.set()

    def process_unseen_emails(self) -> None:
        # Fetch all unseen emails using connector, sort by date (oldest first), process sequentially
        try:
            unseen_msgs = self._connector.fetch_unseen_sorted()
            if not unseen_msgs:
                logger.debug("No unseen emails to process")
                return

            logger.info(f"Found {len(unseen_msgs)} unseen emails")

            for msg in unseen_msgs:
                self._process_single_email(msg)
        except IMAPConnectorError as error:
            logger.error(f"Failed to process unseen emails: {error}")

    def _process_single_email(self, msg: MailMessage) -> None:
        # Process a single email: parse, validate, route to agent, send reply
        uid = msg.uid
        if uid is None:
            logger.warning("Skipping email with None UID")
            return

        uid_str = str(uid)
        # Create logger adapter with UID context for this email
        email_logger: logging.LoggerAdapter[logging.Logger] = logging.LoggerAdapter(
            logger, {"uid": uid_str}
        )

        try:
            # Parse email without marking as seen
            parsed_data = self._adapt_mail_message(msg)
            logged_email = self._build_log_entry(uid_str, parsed_data)
            self._log_email(logged_email)

            # Check if sender is allowed
            if not is_sender_allowed(parsed_data.from_addr):
                email_logger.info(f"Blocked sender: {parsed_data.from_addr}")
                self._connector.move_to_junk(uid_str)
                return

            # Check which agent should process this email
            email_logger.debug(f"Email recipients TO: {parsed_data.recipients.to}, CC: {parsed_data.recipients.cc}")
            agent_type = should_trigger_agent(parsed_data.recipients.to)

            if agent_type:
                self._process_with_agent(parsed_data, agent_type, uid_str, email_logger)
            else:
                email_logger.debug("Email does not trigger agent workflow - marking as read")
                self._connector.mark_seen(uid_str)

        except Exception as error:
            email_logger.exception(f"Error processing email: {error}")
            # Leave email unread on error to allow retry
            email_logger.warning("Email left unread due to processing error")

    def _process_with_agent(
        self,
        parsed_data: ParsedEmailData,
        agent_type: str,
        uid_str: str,
        email_logger: logging.LoggerAdapter[logging.Logger],
    ) -> None:
        # Route email to appropriate agent and handle response
        email_context = self._build_email_context(parsed_data)

        # Process with appropriate agent coordinator
        email_logger.info(f"Processing email through {agent_type} agent pipeline")

        result = self._get_agent_response(agent_type, email_context, email_logger, uid_str)
        agent_response, agent_email = result

        # Type guard: if agent_email is None, both are None (from union type)
        if agent_email is None or agent_response is None:
            return

        if agent_response.reply:
            self._send_agent_reply(
                parsed_data, agent_response.reply, agent_email, uid_str, email_logger
            )
        else:
            email_logger.info("No reply generated by agent - marking as read")
            self._connector.mark_seen(uid_str)

    def _build_email_context(self, parsed_data: ParsedEmailData) -> str:
        # Build email context string for LLM processing
        return textwrap.dedent(f"""
            Subject: {parsed_data.subject or '<no subject>'}
            From: {parsed_data.from_addr}
            To: {', '.join(parsed_data.recipients.to)}
            Date: {parsed_data.date or 'Unknown'}

            Body:
            {parsed_data.body}
        """).strip()

    def _get_agent_response(
        self,
        agent_type: str,
        email_context: str,
        email_logger: logging.LoggerAdapter[logging.Logger],
        uid_str: str,
    ) -> tuple[AgentResponse, str] | tuple[None, None]:
        # Get response from appropriate agent based on type
        if agent_type == "policy":
            return (
                self.coordinator.process_email_with_prime_foo(email_context),
                POLICY_AGENT_EMAIL,
            )
        elif agent_type == "pacenote":
            return (
                self.coordinator.process_email_with_feedback_note(email_context),
                PACENOTE_AGENT_EMAIL,
            )
        else:
            email_logger.warning(f"Unknown agent type: {agent_type}")
            self._connector.mark_seen(uid_str)
            return None, None

    def _send_agent_reply(
        self,
        parsed_data: ParsedEmailData,
        reply_body: str,
        agent_email: str,
        uid_str: str,
        email_logger: logging.LoggerAdapter[logging.Logger],
    ) -> None:
        # Build and send agent reply with proper threading headers
        threading_headers = EmailThreadManager.build_threading_headers(parsed_data)

        # Calculate reply recipients (excluding self)
        reply_to = {parsed_data.from_addr}
        reply_to.update(addr for addr in parsed_data.recipients.to if addr != agent_email)

        # CC recipients (excluding self)
        reply_cc = [addr for addr in parsed_data.recipients.cc if addr != agent_email]

        # Prepare reply data
        reply_data = ReplyData(
            body=reply_body,
            to=list(reply_to),
            cc=reply_cc,
            subject="Re: " + (parsed_data.subject or ""),
            in_reply_to=threading_headers.get("In-Reply-To"),
            references=threading_headers.get("References"),
        )

        # Send reply
        email_logger.debug("Sending agent reply")
        sent = self.sender.send_reply(reply_data, parsed_data, agent_email)
        if sent:
            email_logger.info("Agent reply sent and email marked as read")
            self._connector.mark_seen(uid_str)
        else:
            email_logger.error("Failed to send agent reply - email left unread for retry")

    def _adapt_mail_message(self, msg: MailMessage) -> ParsedEmailData:
        # Adapt imap_tools MailMessage to our ParsedEmailData format
        return EmailAdapter.adapt_mail_message(msg)

    def _build_log_entry(self, uid: str, data: ParsedEmailData) -> LoggedEmail:
        # Construct LoggedEmail instance from parsed data with truncated preview
        sender = data.from_addr
        subject = data.subject or "<no subject>"
        body_preview = data.body.strip() if data.body else ""
        # Truncate preview to 50 chars for logging readability
        preview = body_preview[:50] + "..." if len(body_preview) > 50 else body_preview
        return LoggedEmail(uid=uid, sender=sender, subject=subject, preview=preview)

    def _log_email(self, entry: LoggedEmail) -> None:
        # Log email entry with already-truncated preview
        logger.info(
            f"Received email uid={entry.uid} from={entry.sender} subject={entry.subject} preview={entry.preview}"
        )
