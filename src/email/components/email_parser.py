"""
src/email/components/email_parser.py

Basic EmailParser for prototype: Parse raw email bytes to ParsedEmailData using stdlib email module.
Extracts essentials: message_id, from, recipients, subject, body (text preferred), thread_id.
For prototype: Focus on text/plain body; simple validation.
"""

import email
from typing import Optional, List
import re
from html import unescape

from src.app_logging import get_logger
from src.email.types import ParsedEmailData, EmailRecipients

logger = get_logger(__name__)

class EmailParser:
    @staticmethod
    def parse_email(raw_message: bytes) -> ParsedEmailData:
        """
        Parse raw email message into structured data.
        For prototype: Extract text body, basic headers. Validate sender email format.
        """
        try:
            msg = email.message_from_bytes(raw_message)
            logger.debug("Email parsed successfully", message_size=len(raw_message))

            # Extract headers
            message_id = msg.get("Message-ID", "") or ""
            from_addr = EmailParser._extract_email(msg.get("From", ""))
            to_header = msg.get("To", "")
            cc_header = msg.get("Cc", "")
            subject = msg.get("Subject", "")
            in_reply_to = msg.get("In-Reply-To", "")

            # Recipients
            to_addrs = EmailParser._extract_emails(to_header)
            cc_addrs = EmailParser._extract_emails(cc_header)
            recipients = EmailRecipients(to=to_addrs, cc=cc_addrs, bcc=[])

            # Body: Prefer text/plain, fallback to html stripped
            text_body = EmailParser._get_text_body(msg)
            body = text_body or EmailParser._strip_html(msg.get_payload(decode=True).decode('utf-8', errors='ignore') if msg.get_payload(decode=True) else "")

            # Thread ID: Use In-Reply-To or Message-ID
            thread_id = in_reply_to.strip('<>') if in_reply_to else message_id.strip('<>')

            parsed = ParsedEmailData(
                message_id=message_id,
                from_addr=from_addr,
                recipients=recipients,
                subject=subject,
                body=body,
                thread_id=thread_id
            )

            # Basic validation: Ensure from_addr is valid email (Pydantic handles, but check non-empty)
            if not from_addr:
                logger.warning("Invalid or missing From address", message_id=message_id)
                raise ValueError("Invalid or missing From address")

            logger.info("Email parsing completed", message_id=message_id, from_addr=from_addr, subject=subject[:50])
            return parsed
        except Exception as e:
            logger.error("Failed to parse email", error=str(e), message_size=len(raw_message))
            raise

    @staticmethod
    def _extract_email(address_header: str) -> str:
        """Extract email from header like 'Name <email@domain.com>'."""
        if not address_header:
            return ""
        parsed = email.utils.parseaddr(address_header)
        return parsed[1] or ""

    @staticmethod
    def _extract_emails(header: str) -> List[str]:
        """Extract list of emails from To/Cc header."""
        if not header:
            return []
        addrs = email.utils.getaddresses([header])
        return [addr[1] for addr in addrs if addr[1]]

    @staticmethod
    def _get_text_body(msg: email.Message) -> Optional[str]:
        """Extract text/plain body, handling multipart."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        return payload.decode(charset, errors="ignore")
        else:
            if msg.get_content_type() == "text/plain":
                payload = msg.get_payload(decode=True)
                if payload:
                    return payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
        return None

    @staticmethod
    def _strip_html(html: str) -> str:
        """Basic HTML stripping for fallback body."""
        # Simple regex to remove tags; unescape entities
        clean = re.sub(r'<[^>]+>', '', html)
        return unescape(clean).strip()
