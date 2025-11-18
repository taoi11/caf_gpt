from __future__ import annotations

import email
from typing import Optional, List
import html

from src.email.types import ParsedEmailData
from src.email.types import ParsedEmailData

class EmailParser:
    """Parses raw email bytes into structured data."""

    @staticmethod
    def parse_email(raw_message: bytes) -> ParsedEmailData:
        """
        Parse a raw email message and extract key fields.

        Args:
            raw_message: Raw email bytes

        Returns:
            ParsedEmailData object with extracted fields
        """
        msg = email.message_from_bytes(raw_message)

        # Extract headers
        from_addr = EmailParser._parse_address(msg.get("From"))
        to_addrs = EmailParser._extract_email_addresses(msg.get("To", ""))
        cc_addrs = EmailParser._extract_email_addresses(msg.get("Cc", ""))
        subject = msg.get("Subject", "")

        # Extract body (text or html)
        text_body, html_body = EmailParser._extract_bodies(msg)

        return ParsedEmailData(
            from_addr=from_addr,
            to_addrs=to_addrs,
            cc_addrs=cc_addrs,
            subject=subject,
            text_body=text_body,
            html_body=html_body
        )

    @staticmethod
    def _parse_address(address: Optional[str]) -> str:
        """Parse a single email address."""
        if not address:
            return ""
        # Simple parsing, could be improved with regex or email.utils.parseaddr
        # Use email.utils.parseaddr to extract the email address
        return email.utils.parseaddr(address)[1] or address

    @staticmethod
    def _extract_email_addresses(header: str) -> List[str]:
        """Extract a list of email addresses from a header."""
        if not header:
            return []
        # Use email.utils.getaddresses for robust parsing of multiple addresses
        return [addr for name, addr in email.utils.getaddresses([header])]

    @staticmethod
    def _extract_bodies(msg: email.message.Message) -> tuple[Optional[str], Optional[str]]:
        """Extract text and HTML bodies from the message."""
        text_body = None
        html_body = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                if content_type == "text/plain":
                    raw_payload = part.get_payload(decode=True)
                    text_body = raw_payload.decode(part.get_content_charset() or "utf-8") if raw_payload else ""
                elif content_type == "text/html":
                    raw_payload = part.get_payload(decode=True)
                    html_body = raw_payload.decode(part.get_content_charset() or "utf-8") if raw_payload else ""
            # If no HTML body found, try to convert text/plain to HTML as a fallback
            if not html_body and text_body:
                html_body = f"<pre>{html.escape(text_body)}</pre>"
        else:
            # Single part message (likely plain text)
            raw_payload = msg.get_payload(decode=True)
            text_body = raw_payload.decode(msg.get_content_charset() or "utf-8") if raw_payload else ""
            html_body = f"<pre>{html.escape(text_body)}</pre>" if text_body else None

        return text_body, html_body
        return text_body, html_body
