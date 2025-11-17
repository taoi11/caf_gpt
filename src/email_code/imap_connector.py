# Note: This directory is named 'email_code' to avoid shadowing Python's standard 'email' module.
from __future__ import annotations


import imaplib
from typing import Iterable, List, Optional

from src.config import EmailConfig


class IMAPConnectorError(Exception):
    """Raised when an IMAP operation fails."""


class IMAPConnector:
    """Simple helper for connecting to an IMAP server and fetching emails."""

    def __init__(self, config: EmailConfig) -> None:
        self._config = config
        self._client: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        if self._client:
            return

        try:
            self._client = imaplib.IMAP4_SSL(
                self._config.imap_host,
                self._config.imap_port
            )
            self._client.login(self._config.imap_username, self._config.imap_password)
        except imaplib.IMAP4.error as error:
            raise IMAPConnectorError("unable to authenticate with IMAP server") from error

        self._select_inbox()

    def _select_inbox(self) -> None:
        assert self._client is not None
        typ, _ = self._client.select("INBOX")
        if typ != "OK":
            raise IMAPConnectorError("failed to select INBOX")

    def search_unseen_uids(self) -> List[str]:
        assert self._client is not None
        typ, raw_data = self._client.search(None, "UNSEEN")
        if typ != "OK":
            raise IMAPConnectorError("failed to search for unseen emails")
        return self._extract_uids(raw_data)

    def fetch_email_bytes(self, uid: str) -> bytes:
        assert self._client is not None
        typ, data = self._client.fetch(uid, "(BODY.PEEK[])")
        if typ != "OK" or not data:
            raise IMAPConnectorError(f"failed to fetch email {uid}")

        message_bytes = self._extract_message_bytes(data)
        if not message_bytes:
            raise IMAPConnectorError(f"no message body returned for {uid}")

        return message_bytes

    def mark_seen(self, uid: str) -> None:
        assert self._client is not None
        typ, _ = self._client.store(uid, "+FLAGS", "\\Seen")
        if typ != "OK":
            raise IMAPConnectorError(f"failed to mark {uid} as seen")

    def disconnect(self) -> None:
        if not self._client:
            return
        try:
            self._client.close()
        except imaplib.IMAP4.error:
            pass
        finally:
            try:
                self._client.logout()
            except imaplib.IMAP4.error:
                pass
            finally:
                self._client = None

    def _extract_uids(self, data: List[bytes]) -> List[str]:
        if not data or not data[0]:
            return []
        raw_uids = data[0].split()
        return [uid.decode("utf-8") for uid in raw_uids if uid]

    def _extract_message_bytes(self, data: List[bytes | tuple[bytes, bytes]]) -> bytes:
        for item in data:
            if isinstance(item, tuple) and len(item) >= 2:
                return item[1]
        return b""
