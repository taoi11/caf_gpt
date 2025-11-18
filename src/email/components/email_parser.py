"""
src/email/components/email_parser.py

Utility for parsing raw email messages into structured ParsedEmailData objects, handling headers, bodies, and attachments.

Top-level declarations:
- EmailParser: Class providing static methods to parse email bytes and extract components
"""

from __future__ import annotations

import email
from typing import Optional, List
import html

from src.email.types import ParsedEmailData

class EmailParser:
    # Class for parsing raw email messages into structured data using standard email library

    @staticmethod
    def parse_email(raw_message: bytes) -> ParsedEmailData:
        # Parse a raw email message and extract key fields like sender, recipients, subject, and body content
        # Handles both single-part and multipart messages, prioritizing HTML over text
        msg = email.message_from_bytes(raw_message)

        from_addr = EmailParser._parse_address(msg.get("From"))
        to_addrs = EmailParser._extract_email_addresses(msg.get("To", ""))
        cc_addrs = EmailParser._extract_email_addresses(msg.get("Cc", ""))
        subject = msg.get("Subject", "")

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
        # Parse a single email address from the From header, extracting the email part
        if not address:
            return ""
        # Use email.utils.parseaddr to extract the email address reliably
        return email.utils.parseaddr(address)[1] or address

    @staticmethod
    def _extract_email_addresses(header: str) -> List[str]:
        # Extract list of email addresses from To or Cc header using email.utils.getaddresses for robust parsing
        if not header:
            return []
        return [addr for name, addr in email.utils.getaddresses([header])]

    @staticmethod
    def _extract_bodies(msg: email.message.Message) -> tuple[Optional[str], Optional[str]]:
        # Extract text and HTML body content from email message, handling multipart and single-part cases
        # Prioritizes HTML, falls back to escaped text in <pre> if no HTML
        text_body = None
        html_body = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    continue
                if content_type == "text/plain":
                    raw_payload = part.get_payload(decode=True)
                    text_body = raw_payload.decode(part.get_content_charset() or "utf-8") if raw_payload else ""
                elif content_type == "text/html":
                    raw_payload = part.get_payload(decode=True)
                    html_body = raw_payload.decode(part.get_content_charset() or "utf-8") if raw_payload else ""
            if not html_body and text_body:
                html_body = f"<pre>{html.escape(text_body)}</pre>"
        else:
            raw_payload = msg.get_payload(decode=True)
            text_body = raw_payload.decode(msg.get_content_charset() or "utf-8") if raw_payload else ""
            html_body = f"<pre>{html.escape(text_body)}</pre>" if text_body else None

        return text_body, html_body
