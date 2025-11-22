"""
src/email_code/imap_connector.py

IMAP client wrapper using imap_tools for simplified email operations.

Top-level declarations:
- IMAPConnectorError: Custom exception for IMAP operation failures
- IMAPConnector: Main class handling IMAP connections and email retrieval using imap_tools
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, List, Optional
from imap_tools import MailBox, BaseMailBox, MailMessage
from src.config import EmailConfig

class IMAPConnectorError(Exception):
    """Custom exception raised when IMAP operations fail"""

    pass

class IMAPConnector:
    """IMAP client wrapper using imap_tools for simplified operations"""
    
    def __init__(self, config: EmailConfig) -> None:
        self._config = config

    @contextmanager
    def mailbox(self) -> Generator[BaseMailBox, None, None]:
        """Context manager for IMAP connection using imap_tools"""
        with MailBox(self._config.imap_host, self._config.imap_port).login(
            self._config.imap_username,
            self._config.imap_password
        ) as mb:
            yield mb

    def search_unseen_uids(self) -> List[str]:
        """Search for unseen email UIDs"""
        try:
            with self.mailbox() as mb:
                uids = [msg.uid for msg in mb.fetch("UNSEEN")]
                return uids
        except Exception as error:
            raise IMAPConnectorError(f"failed to search for unseen emails: {error}") from error

    def fetch_email_message(self, uid: str) -> MailMessage:
        """Fetch and parse email message"""
        try:
            with self.mailbox() as mb:
                msgs = list(mb.fetch(f"UID {uid}"))
                if not msgs:
                    raise IMAPConnectorError(f"email {uid} not found")
                return msgs[0]
        except Exception as error:
            raise IMAPConnectorError(f"failed to fetch email {uid}: {error}") from error

    def mark_seen(self, uid: str) -> None:
        """Mark email as seen using imap_tools"""
        try:
            with self.mailbox() as mb:
                # Use A(uid=uid) for advanced search
                from imap_tools import A
                for msg in mb.fetch(A(uid=uid)):
                    mb.seen(msg.uid)
                    return
        except Exception as error:
            raise IMAPConnectorError(f"failed to mark {uid} as seen: {error}") from error

    def delete_email(self, uid: str) -> None:
        """Delete email using imap_tools"""
        try:
            with self.mailbox() as mb:
                from imap_tools import A
                for msg in mb.fetch(A(uid=uid)):
                    mb.delete(msg.uid)
                    return
        except Exception as error:
            raise IMAPConnectorError(f"failed to delete {uid}: {error}") from error

    def disconnect(self) -> None:
        """Disconnect is handled automatically by context manager"""
        pass
