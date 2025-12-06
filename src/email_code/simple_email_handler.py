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
import threading

from dataclasses import dataclass
from typing import Optional
from imap_tools import MailMessage

from src.config import EmailConfig, should_trigger_agent, POLICY_AGENT_EMAIL
from src.email_code.imap_connector import IMAPConnector, IMAPConnectorError
from src.email_code.types import ParsedEmailData, ReplyData
from src.email_code.components.email_adapter import EmailAdapter
from src.email_code.components.email_sender import EmailSender
from src.email_code.components.email_thread_manager import EmailThreadManager
from src.agents.prompt_manager import PromptManager
from src.agents.agent_coordinator import AgentCoordinator

logger = logging.getLogger(__name__)

@dataclass
class LoggedEmail:
    """Dataclass holding metadata for logged emails: UID, sender, subject, and content preview"""
    uid: str
    sender: str
    subject: str
    preview: str

class SimpleEmailProcessor:
    """Basic processor for polling IMAP inbox, parsing new emails with imap_tools, and logging them"""
    
    def __init__(self, config: EmailConfig) -> None:
        self._config = config
        self._connector = IMAPConnector(config)
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.sender = EmailSender()
        self.prompt_manager = PromptManager()
        self.coordinator = AgentCoordinator(self.prompt_manager)

    def run_loop(self) -> None:
        """Main loop that continuously polls the IMAP inbox at intervals"""
        logger.info(f"Starting IMAP poll loop, interval={self._config.email_process_interval}")
        try:
            while not self._stop_event.is_set():
                with self._lock:
                    self.process_unseen_emails()
                self._stop_event.wait(self._config.email_process_interval)
        finally:
            logger.info("IMAP poll loop stopped")

    def stop(self) -> None:
        self._stop_event.set()

    def process_unseen_emails(self) -> None:
        """Fetch all unseen emails using connector, sort by date (oldest first), process sequentially"""
        try:
            unseen_msgs = self._connector.fetch_unseen_sorted()
            if not unseen_msgs:
                logger.debug("No unseen emails to process")
                return

            logger.info(f"Found {len(unseen_msgs)} unseen emails")

            for msg in unseen_msgs:
                uid = msg.uid
                try:
                    # Step 1: PEEK - Parse email without marking as seen
                    parsed_data = self._adapt_mail_message(msg)
                    logged_email = self._build_log_entry(uid, parsed_data)
                    self._log_email(logged_email)

                    # Check if should trigger agent
                    if should_trigger_agent(parsed_data.recipients.to):
                        # Step 2: FULL AI PIPELINE - Build email context for agent
                        email_context = f"""
                        Subject: {parsed_data.subject or '<no subject>'}
                        From: {parsed_data.from_addr}
                        To: {', '.join(parsed_data.recipients.to)}
                        Date: {parsed_data.date or 'Unknown'}

                        Body:
                        {parsed_data.body}
                        """

                        # Process with agent coordinator
                        logger.info(f"[uid={uid}] Processing email through AI pipeline")
                        agent_response = self.coordinator.process_email_with_prime_foo(email_context)

                        if agent_response.reply:
                            # Connect Thread Manager for Headers
                            threading_headers = EmailThreadManager.build_threading_headers(parsed_data)

                            # Calculate "Reply All" recipients (excluding self)
                            # TO: Original Sender + (Original TO - Me)
                            reply_to = {parsed_data.from_addr}
                            reply_to.update(addr for addr in parsed_data.recipients.to if addr != POLICY_AGENT_EMAIL)

                            # CC: Original CC - Me
                            reply_cc = [addr for addr in parsed_data.recipients.cc if addr != POLICY_AGENT_EMAIL]

                            # Prepare reply data
                            reply_data = ReplyData(
                                body=agent_response.reply,
                                to=list(reply_to),
                                cc=reply_cc,
                                subject="Re: " + (parsed_data.subject or ""),  # Will auto-format
                                in_reply_to=threading_headers.get("In-Reply-To"),
                                references=threading_headers.get("References"),
                            )

                            # Send reply
                            logger.info(f"[uid={uid}] Sending agent reply")
                            sent = self.sender.send_reply(reply_data, parsed_data, POLICY_AGENT_EMAIL)
                            if sent:
                                logger.info(f"[uid={uid}] Agent reply sent successfully")
                                # Step 3: MARK AS READ after successful processing
                                self._connector.mark_seen(uid)
                                logger.info(f"[uid={uid}] Email marked as read")
                            else:
                                logger.error(f"[uid={uid}] Failed to send agent reply - email left unread for retry")
                        else:
                            logger.info(f"[uid={uid}] No reply generated by agent - marking as read")
                            # Step 3: MARK AS READ after AI processing completed
                            self._connector.mark_seen(uid)
                    else:
                        logger.debug(f"[uid={uid}] Email does not trigger agent workflow - marking as read")
                        # Step 3: MARK AS READ (non-agent emails)
                        self._connector.mark_seen(uid)

                except Exception as error:
                    logger.exception(f"[uid={uid}] Error processing email: {error}")
                    # Leave email unread on error to allow retry
                    logger.warning(f"[uid={uid}] Email left unread due to processing error")
        except IMAPConnectorError as error:
            logger.error(f"Failed to process unseen emails: {error}")

    def _adapt_mail_message(self, msg: MailMessage) -> ParsedEmailData:
        """Adapt imap_tools MailMessage to our ParsedEmailData format"""
        return EmailAdapter.adapt_mail_message(msg)

    def _build_log_entry(self, uid: str, data: ParsedEmailData) -> LoggedEmail:
        """Construct LoggedEmail instance from parsed data"""
        sender = data.from_addr
        subject = data.subject or "<no subject>"
        preview = data.body.strip()[:200] if data.body else ""
        return LoggedEmail(uid=uid, sender=sender, subject=subject, preview=preview)

    # HTML stripping is now handled by EmailAdapter

    @staticmethod
    def _log_email(entry: LoggedEmail) -> None:
        preview = entry.preview[:50] + "..." if len(entry.preview) > 50 else entry.preview
        logger.info(f"Received email uid={entry.uid} from={entry.sender} subject={entry.subject} preview={preview}")
