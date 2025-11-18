"""
src/email_code/simple_email_handler.py

Simple email processing handler that polls IMAP for new emails, parses them, and logs incoming messages.

Top-level declarations:
- LoggedEmail: Dataclass for logging email metadata
- SimpleEmailProcessor: Class for polling and processing unseen emails via IMAP
"""

# Note: This directory is named 'email_code' to avoid shadowing Python's standard 'email' module.
from __future__ import annotations


import structlog
import threading
import time

from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from typing import Optional

from src.config import EmailConfig
from src.email_code.imap_connector import IMAPConnector, IMAPConnectorError
from src.email.components.email_parser import EmailParser
from src.email.types import ParsedEmailData


logger = structlog.get_logger()


@dataclass
class LoggedEmail:
    # Dataclass holding metadata for logged emails: UID, sender, subject, and content preview
    # Used for structured logging of incoming email details
    uid: str
    sender: str
    subject: str
    preview: str


class SimpleEmailProcessor:
    # Basic processor for polling IMAP inbox, parsing new emails with EmailParser, and logging them
    # Manages connection, threading for continuous operation, and error handling
    # Orchestrates the main email processing workflow without AI integration yet

    def __init__(self, config: EmailConfig) -> None:
        # Initialize processor with email config, IMAP connector, stop event, parser, and lock
        self._config = config
        self._connector = IMAPConnector(config)
        self._stop_event = threading.Event()
        self._parser = BytesParser(policy=policy.default)
        self._lock = threading.Lock()

    def run_loop(self) -> None:
        # Main loop that continuously polls the IMAP inbox at intervals, processes unseen emails, and handles graceful shutdown
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
        # Connect to IMAP, search for unseen UIDs, fetch and parse each email, log it, with error handling per email
        try:
            self._connector.connect()
            logger.info("connected to IMAP server")
        except IMAPConnectorError as error:
            logger.error("cannot connect to IMAP server", exc_info=error)
            return

        try:
            uids = self._connector.search_unseen_uids()
            logger.info("found unseen emails", count=len(uids))
        except IMAPConnectorError as error:
            logger.error("failed to search unseen emails", exc_info=error)
            return

        if not uids:
            logger.debug("no unseen emails to process")
            return

        for uid in uids:
            with logger.bind(uid=uid):
                try:
                    raw_message = self._connector.fetch_email_bytes(uid)
                    parsed_data = EmailParser.parse_email(raw_message)
                    logged_email = self._build_log_entry(uid, parsed_data)
                    self._log_email(logged_email)
                    logger.info("email processed successfully")
                    # TODO: Delete email after full processing (including AI response)
                except ValueError as error:  # From parser validation
                    logger.error("invalid email data", exc_info=error)
                except IMAPConnectorError as error:
                    logger.error("error fetching message", exc_info=error)
                except Exception as error:
                    logger.exception("unexpected error while parsing email", exc_info=error)

    def _build_log_entry(self, uid: str, data: ParsedEmailData) -> LoggedEmail:
        # Construct LoggedEmail instance from UID and parsed data, generating a 200-char preview from body content
        sender = data.from_addr
        subject = data.subject or "<no subject>"
        if data.text_body:
            preview = data.text_body.strip()[:200]
        elif data.html_body:
            import re
            text = re.sub(r'<[^>]+>', '', data.html_body)
            preview = text.strip()[:200]
        else:
            preview = ""
        return LoggedEmail(uid=uid, sender=sender, subject=subject, preview=preview)

    @staticmethod
    def _log_email(entry: LoggedEmail) -> None:
        logger.info(
            "received email",
            uid=entry.uid,
            from_addr=entry.sender,
            subject=entry.subject,
            preview=entry.preview[:50] + "..."
        )
