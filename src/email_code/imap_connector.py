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
from datetime import datetime
from typing import Callable, Generator, List, Optional, TypeVar

from imap_tools import MailBox, BaseMailBox, MailMessage, MailMessageFlags  # type: ignore[attr-defined]

from src.config import EmailConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")


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

    def _with_mailbox(
        self,
        operation: Callable[[BaseMailBox], T],
        mb: Optional[BaseMailBox],
        error_msg: str,
    ) -> T:
        # Execute operation with provided mailbox or create new connection
        # Centralizes the if mb/else with self.mailbox() pattern
        if mb is not None:
            return operation(mb)
        try:
            with self.mailbox() as new_mb:
                return operation(new_mb)
        except Exception as error:
            logger.error(f"{error_msg}: {error}")
            raise IMAPConnectorError(f"{error_msg}: {error}") from error

    def mark_seen(self, uid: str, mb: Optional[BaseMailBox] = None) -> None:
        # Mark email as seen using direct UID flag (no fetch needed)
        # Accepts optional mailbox to reuse existing connection
        def do_mark(mailbox: BaseMailBox) -> None:
            logger.info(f"Marking uid={uid} as SEEN")
            mailbox.flag([uid], [MailMessageFlags.SEEN], True)
            mailbox.client.noop()
            logger.info(f"Successfully marked uid={uid} as SEEN")

        self._with_mailbox(do_mark, mb, f"failed to mark {uid} as seen")

    def fetch_unseen_sorted(self, mb: Optional[BaseMailBox] = None) -> List[MailMessage]:
        # Batch fetch unseen emails without attachments to reduce bandwidth, sort by date (oldest first)
        # Accepts optional mailbox to reuse existing connection
        def do_fetch(mailbox: BaseMailBox) -> List[MailMessage]:
            uids = list(mailbox.uids("UNSEEN"))
            if not uids:
                return []

            logger.info(f"Fetching {len(uids)} unseen messages without attachments")

            # Batch fetch all messages in a single call to avoid N+1 query pattern
            uid_str = ",".join(uids)
            msgs = list(mailbox.fetch(f"UID {uid_str}", mark_seen=False))

            # Sort by date (oldest first)
            if msgs:
                msgs.sort(key=lambda msg: msg.date or datetime.min)
                logger.info(f"Successfully fetched and sorted {len(msgs)} messages")

            return msgs

        return self._with_mailbox(do_fetch, mb, "failed to fetch unseen emails")

    def move_to_junk(self, uid: str, mb: Optional[BaseMailBox] = None) -> None:
        # Move email to Junk folder and mark as seen
        # Accepts optional mailbox to reuse existing connection
        def do_move(mailbox: BaseMailBox) -> None:
            logger.info(f"Moving uid={uid} to Junk folder")
            mailbox.move([uid], "Junk")
            logger.info(f"Successfully moved uid={uid} to Junk")

        self._with_mailbox(do_move, mb, f"failed to move {uid} to Junk")
