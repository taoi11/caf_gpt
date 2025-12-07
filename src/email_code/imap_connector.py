"""
src/email_code/imap_connector.py

IMAP client wrapper using imap_tools for simplified email operations.

Top-level declarations:
- IMAPConnectorError: Custom exception for IMAP operation failures
- IMAPConnector: Main class handling IMAP connections and email retrieval using imap_tools
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, List
from imap_tools import MailBox, BaseMailBox, MailMessage, MailMessageFlags
from datetime import datetime
from src.config import EmailConfig
from src.app_logging import get_logger

logger = get_logger(__name__)


class IMAPConnectorError(Exception):
    """Custom exception raised when IMAP operations fail"""

    pass


class IMAPConnector:
    # IMAP client wrapper using imap_tools for simplified operations

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

    def mark_seen(self, uid: str) -> None:
        # Mark email as seen using direct UID flag (no fetch needed)
        try:
            with self.mailbox() as mb:
                logger.info(f"Attempting to mark uid={uid} as SEEN")

                # Check current flags before marking
                try:
                    msgs_before = list(mb.fetch(f"UID {uid}", mark_seen=False))
                    if msgs_before:
                        logger.info(f"Flags before marking uid={uid}: {msgs_before[0].flags}")
                except Exception as e:
                    logger.warning(f"Could not fetch flags before marking: {e}")

                # Use flag() to set the SEEN flag
                mb.flag([uid], [MailMessageFlags.SEEN], True)
                logger.info(f"Mark seen operation completed for uid={uid}")

                # Force IMAP to persist the flag change
                mb.client.noop()

                # Verify the flag was set
                try:
                    msgs_after = list(mb.fetch(f"UID {uid}", mark_seen=False))
                    if msgs_after:
                        logger.info(f"Flags after marking uid={uid}: {msgs_after[0].flags}")
                        if MailMessageFlags.SEEN in msgs_after[0].flags:
                            logger.info(f"✓ Successfully verified uid={uid} is marked as SEEN")
                        else:
                            logger.error(f"✗ uid={uid} is NOT marked as SEEN after operation!")
                except Exception as e:
                    logger.warning(f"Could not verify flags after marking: {e}")

        except Exception as error:
            logger.error(f"Failed to mark uid={uid} as seen: {error}")
            raise IMAPConnectorError(f"failed to mark {uid} as seen: {error}") from error

    def fetch_unseen_sorted(self) -> List[MailMessage]:
        # Batch fetch unseen emails, sort by date (oldest first), don't mark seen yet
        try:
            with self.mailbox() as mb:
                msgs = list(mb.fetch("UNSEEN", mark_seen=False))
                if msgs:
                    msgs.sort(key=lambda msg: msg.date or datetime.min)
                return msgs
        except Exception as error:
            raise IMAPConnectorError(f"failed to fetch unseen emails: {error}") from error

    def disconnect(self) -> None:
        # No-op: All connections are handled by context managers that automatically cleanup
        pass
