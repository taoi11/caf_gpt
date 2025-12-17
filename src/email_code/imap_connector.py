"""
src/email_code/imap_connector.py

IMAP client wrapper using imap_tools for simplified email operations.
Optimized to exclude attachments from download to reduce bandwidth usage.
Supports session reuse to avoid multiple connection overhead.

Top-level declarations:
- IMAPConnectorError: Custom exception for IMAP operation failures
- IMAPConnector: Main class handling IMAP connections and email retrieval using imap_tools
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, List, Optional
from imap_tools import MailBox, BaseMailBox, MailMessage, MailMessageFlags
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
        with MailBox(self._config.imap_host, self._config.imap_port).login(
            self._config.imap_username, self._config.imap_password
        ) as mb:
            yield mb

    def mark_seen(self, uid: str, mb: Optional[BaseMailBox] = None) -> None:
        # Mark email as seen using direct UID flag (no fetch needed)
        # Accepts optional mailbox to reuse existing connection
        if mb is not None:
            self._mark_seen_impl(uid, mb)
        else:
            try:
                with self.mailbox() as new_mb:
                    self._mark_seen_impl(uid, new_mb)
            except Exception as error:
                logger.error(f"Failed to mark uid={uid} as seen: {error}")
                raise IMAPConnectorError(f"failed to mark {uid} as seen: {error}") from error

    def _mark_seen_impl(self, uid: str, mb: BaseMailBox) -> None:
        # Internal implementation for marking email as seen
        try:
            logger.info(f"Marking uid={uid} as SEEN")
            mb.flag([uid], [MailMessageFlags.SEEN], True)
            mb.client.noop()
            logger.info(f"Successfully marked uid={uid} as SEEN")
        except Exception as error:
            logger.error(f"Failed to mark uid={uid} as seen: {error}")
            raise IMAPConnectorError(f"failed to mark {uid} as seen: {error}") from error

    def fetch_unseen_sorted(self, mb: Optional[BaseMailBox] = None) -> List[MailMessage]:
        # Batch fetch unseen emails without attachments to reduce bandwidth, sort by date (oldest first)
        # Accepts optional mailbox to reuse existing connection
        if mb is not None:
            return self._fetch_unseen_sorted_impl(mb)
        else:
            try:
                with self.mailbox() as new_mb:
                    return self._fetch_unseen_sorted_impl(new_mb)
            except Exception as error:
                raise IMAPConnectorError(f"failed to fetch unseen emails: {error}") from error

    def _fetch_unseen_sorted_impl(self, mb: BaseMailBox) -> List[MailMessage]:
        # Internal implementation for fetching unseen emails
        try:
            uids = list(mb.uids("UNSEEN"))
            if not uids:
                return []

            logger.info(f"Fetching {len(uids)} unseen messages without attachments")

            # Batch fetch all messages in a single call to avoid N+1 query pattern
            uid_str = ",".join(uids)
            msgs = list(mb.fetch(f"UID {uid_str}", mark_seen=False))

            # Sort by date (oldest first)
            if msgs:
                msgs.sort(key=lambda msg: msg.date or datetime.min)
                logger.info(f"Successfully fetched and sorted {len(msgs)} messages")

            return msgs
        except Exception as error:
            logger.error(f"Failed to fetch unseen emails: {error}")
            raise IMAPConnectorError(f"failed to fetch unseen emails: {error}") from error

    def move_to_junk(self, uid: str, mb: Optional[BaseMailBox] = None) -> None:
        # Move email to Junk folder and mark as seen
        # Accepts optional mailbox to reuse existing connection
        if mb is not None:
            self._move_to_junk_impl(uid, mb)
        else:
            try:
                with self.mailbox() as new_mb:
                    self._move_to_junk_impl(uid, new_mb)
            except Exception as error:
                logger.error(f"Failed to move uid={uid} to Junk: {error}")
                raise IMAPConnectorError(f"failed to move {uid} to Junk: {error}") from error

    def _move_to_junk_impl(self, uid: str, mb: BaseMailBox) -> None:
        # Internal implementation for moving email to Junk folder
        try:
            logger.info(f"Moving uid={uid} to Junk folder")
            mb.move([uid], "Junk")
            logger.info(f"Successfully moved uid={uid} to Junk")
        except Exception as error:
            logger.error(f"Failed to move uid={uid} to Junk: {error}")
            raise IMAPConnectorError(f"failed to move {uid} to Junk: {error}") from error
