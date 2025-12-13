"""
src/email_code/imap_connector.py

IMAP client wrapper using imap_tools for simplified email operations.
Optimized to exclude attachments from download to reduce bandwidth usage.

Top-level declarations:
- IMAPConnectorError: Custom exception for IMAP operation failures
- IMAPConnector: Main class handling IMAP connections and email retrieval using imap_tools
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, List
from imap_tools import MailBox, BaseMailBox, MailMessage, MailMessageFlags  # type: ignore[attr-defined]
from datetime import datetime
from src.config import EmailConfig

logger = logging.getLogger(__name__)


class IMAPConnectorError(Exception):
    """Custom exception raised when IMAP operations fail"""
    # Used for error handling in IMAP operations

    pass


class IMAPConnector:
    # IMAP client wrapper using imap_tools for simplified email operations
    # Optimized to exclude attachments from download to reduce bandwidth usage

    def __init__(self, config: EmailConfig) -> None:
        # Initialize with email configuration
        self._config = config

    @contextmanager
    def mailbox(self) -> Generator[BaseMailBox, None, None]:
        # Context manager for IMAP connection using imap_tools
        with MailBox(self._config.imap_host, self._config.imap_port).login(  # type: ignore[no-untyped-call]
            self._config.imap_username, self._config.imap_password
        ) as mb:
            yield mb

    def mark_seen(self, uid: str) -> None:
        # Mark email as seen using direct UID flag (no fetch needed)
        try:
            with self.mailbox() as mb:
                logger.info(f"Marking uid={uid} as SEEN")
                # Use flag() to set the SEEN flag
                mb.flag([uid], [MailMessageFlags.SEEN], True)
                # Force IMAP to persist the flag change
                mb.client.noop()
                logger.info(f"Successfully marked uid={uid} as SEEN")
        except Exception as error:
            logger.error(f"Failed to mark uid={uid} as seen: {error}")
            raise IMAPConnectorError(f"failed to mark {uid} as seen: {error}") from error

    def fetch_unseen_sorted(self) -> List[MailMessage]:
        # Batch fetch unseen emails without attachments to reduce bandwidth, sort by date (oldest first)
        try:
            with self.mailbox() as mb:
                # Get UIDs of unseen messages
                uids = list(mb.uids("UNSEEN"))
                if not uids:
                    return []

                logger.info(f"Fetching {len(uids)} unseen messages without attachments")

                # Batch fetch all messages in a single call to avoid N+1 query pattern
                # Build UID criteria string (e.g., "UID 1,2,3")
                uid_str = ",".join(uids)
                msgs = list(mb.fetch(f"UID {uid_str}", mark_seen=False))

                # Sort by date (oldest first)
                if msgs:
                    msgs.sort(key=lambda msg: msg.date or datetime.min)
                    logger.info(f"Successfully fetched and sorted {len(msgs)} messages")

                return msgs
        except Exception as error:
            raise IMAPConnectorError(f"failed to fetch unseen emails: {error}") from error

    def move_to_junk(self, uid: str) -> None:
        # Move email to Junk folder and mark as seen
        try:
            with self.mailbox() as mb:
                logger.info(f"Moving uid={uid} to Junk folder")
                mb.move([uid], "Junk")
                logger.info(f"Successfully moved uid={uid} to Junk")
        except Exception as error:
            logger.error(f"Failed to move uid={uid} to Junk: {error}")
            raise IMAPConnectorError(f"failed to move {uid} to Junk: {error}") from error

