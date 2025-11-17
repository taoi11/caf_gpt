# Note: This directory is named 'email_code' to avoid shadowing Python's standard 'email' module.
from __future__ import annotations


import logging
import threading
import time

from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from typing import Optional

from src.config import EmailConfig
from src.email_code.imap_connector import IMAPConnector, IMAPConnectorError


logger = logging.getLogger(__name__)


@dataclass
class LoggedEmail:
    uid: str
    sender: str
    subject: str
    preview: str


class SimpleEmailProcessor:
    """Basic IMAP polling processor that logs incoming messages."""

    def __init__(self, config: EmailConfig) -> None:
        self._config = config
        self._connector = IMAPConnector(config)
        self._stop_event = threading.Event()
        self._parser = BytesParser(policy=policy.default)
        self._lock = threading.Lock()

    def run_loop(self) -> None:
        """Continuously poll the inbox, logging any unseen emails."""
        logger.info(f"starting IMAP poll loop, interval={self._config.email_process_interval}")
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
        try:
            self._connector.connect()
        except IMAPConnectorError as error:
            logger.error("cannot connect to IMAP server", exc_info=error)
            return

        try:
            uids = self._connector.search_unseen_uids()
        except IMAPConnectorError as error:
            logger.error("failed to search unseen emails", exc_info=error)
            return

        for uid in uids:
            try:
                raw_message = self._connector.fetch_email_bytes(uid)
                parsed = self._parser.parsebytes(raw_message)
                logged_email = self._build_log_entry(uid, parsed)
                self._log_email(logged_email)
            except IMAPConnectorError as error:
                logger.error("error processing message", uid=uid, exc_info=error)
            except Exception as error:
                logger.exception("unexpected error while parsing email", uid=uid, exc_info=error)

    def _build_log_entry(self, uid: str, message) -> LoggedEmail:
        sender = self._extract_header(message, "From") or "<unknown>"
        subject = self._extract_header(message, "Subject") or "<no subject>"
        preview = self._extract_body_preview(message)
        return LoggedEmail(uid=uid, sender=sender, subject=subject, preview=preview)

    @staticmethod
    def _extract_header(message, name: str) -> Optional[str]:
        header = message[name]
        if header is None:
            return None
        return str(header)

    @staticmethod
    def _extract_body_preview(message) -> str:
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain" and part.get_content_disposition() in (None, "inline"):
                    return SimpleEmailProcessor._truncate(part.get_content())
            return SimpleEmailProcessor._truncate(message.get_body(preferencelist=("plain",)) or "")
        return SimpleEmailProcessor._truncate(message.get_content())

    @staticmethod
    def _truncate(body: Optional[str]) -> str:
        if not body:
            return ""
        return body.strip()[:200]

    @staticmethod
    def _log_email(entry: LoggedEmail) -> None:
        logger.info(
            f"received email: uid={entry.uid}, from={entry.sender}, subject={entry.subject}, preview={entry.preview[:50]}..."
        )
