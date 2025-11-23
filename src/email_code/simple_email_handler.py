"""
src/email_code/simple_email_handler.py

Simple email processing handler that polls IMAP for new emails using imap_tools, parses them, and logs them.
Uses imap_tools for automatic email parsing, eliminating manual parsing boilerplate.

Top-level declarations:
- LoggedEmail: Dataclass for logging email metadata
- SimpleEmailProcessor: Class for polling and processing unseen emails via IMAP with imap_tools
"""

from __future__ import annotations

import structlog
import threading
import time

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from imap_tools import MailMessage

from src.config import EmailConfig
from src.email_code.imap_connector import IMAPConnector, IMAPConnectorError
from src.email_code.types import ParsedEmailData
from src.email_code.components.email_adapter import EmailAdapter

logger = structlog.get_logger()

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

    def run_loop(self) -> None:
        """Main loop that continuously polls the IMAP inbox at intervals"""
        logger.info("starting IMAP poll loop", interval=self._config.email_process_interval)
        try:
            while not self._stop_event.is_set():
                with self._lock:
                    self.process_unseen_emails()
                self._stop_event.wait(self._config.email_process_interval)
        finally:
            self._connector.disconnect()
            logger.info("imap poll loop stopped")

    def stop(self) -> None:
        self._stop_event.set()

    def process_unseen_emails(self) -> None:
        """Fetch all unseen emails using connector, sort by date (oldest first), process sequentially"""
        try:
            unseen_msgs = self._connector.fetch_unseen_sorted()
            if not unseen_msgs:
                logger.debug("no unseen emails to process")
                return

            logger.info("found unseen emails", count=len(unseen_msgs))

            for msg in unseen_msgs:
                uid = msg.uid
                with logger.bind(uid=uid):
                    try:
                        # Parse and log
                        parsed_data = self._adapt_mail_message(msg)
                        logged_email = self._build_log_entry(uid, parsed_data)
                        self._log_email(logged_email)
                        logger.info("email processed successfully")

                        # Mark as seen immediately after processing (prevents re-processing)
                        self._connector.mark_seen(uid)
                        # TODO: If full processing (e.g., AI reply) succeeds, optionally: self._connector.delete_email(uid)

                    except Exception as error:
                        logger.exception("error processing email", exc_info=error)
                        # Optionally mark as seen even on error to avoid infinite loops, or leave unseen for retry
        except IMAPConnectorError as error:
            logger.error("failed to process unseen emails", exc_info=error)

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
        logger.info(
            "received email",
            uid=entry.uid,
            from_addr=entry.sender,
            subject=entry.subject,
            preview=entry.preview[:50] + "...",
        )
