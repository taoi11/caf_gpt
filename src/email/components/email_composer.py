

"""
src/email/components/email_composer.py

Basic EmailComposer for prototype: Compose properly formatted reply emails using stdlib.
Builds EmailMessage with headers, quoted original content.
For prototype: Plain text only, simple "Re:" subject, "> " quoting.
"""

import email.message
from typing import Optional
from email.message import EmailMessage

from src.app_logging import get_logger
from src.email.types import ReplyData, ParsedEmailData

logger = get_logger(__name__)

class EmailComposer:
    @staticmethod
    def compose_reply(reply_data: ReplyData, original: ParsedEmailData, agent_email: str) -> EmailMessage:
        """
        Compose complete reply email with threading headers and quoted content.
        :param reply_data: Structured reply info
        :param original: Original parsed email for quoting
        :param agent_email: Bot's email address (from config)
        :return: Ready-to-send EmailMessage
        """
        try:
            # Validate inputs
            EmailComposer._validate_reply_data(reply_data)

            # Create message
            msg = EmailMessage()
            msg["From"] = agent_email
            msg["To"] = ", ".join(reply_data.to)
            if reply_data.cc:
                msg["Cc"] = ", ".join(reply_data.cc)
            msg["Subject"] = EmailComposer._format_subject(reply_data.subject, original.subject)
            
            # Threading headers
            if reply_data.in_reply_to:
                msg["In-Reply-To"] = reply_data.in_reply_to
            if reply_data.references:
                msg["References"] = reply_data.references

            # Body: Reply + quoted original
            quoted = EmailComposer._format_quoted_content(original.body, original.from_addr, original.subject)
            full_body = f"{reply_data.body}\n\n{quoted}"
            msg.set_content(full_body)

            logger.debug("Reply composed successfully", subject=msg["Subject"], to=", ".join(reply_data.to), cc_count=len(reply_data.cc or []))
            return msg
        except Exception as e:
            logger.error("Failed to compose reply", error=str(e), subject=reply_data.subject)
            raise

    @staticmethod
    def _format_subject(reply_subject: str, original_subject: str) -> str:
        """Add 'Re:' prefix if not present."""
        try:
            if reply_subject:
                return reply_subject
            if original_subject and not original_subject.startswith("Re:"):
                return f"Re: {original_subject}"
            return original_subject or "Re:"
        except Exception as e:
            logger.error("Failed to format subject", error=str(e), original_subject=original_subject)
            return "Re:"

    @staticmethod
    def _format_quoted_content(body: str, from_addr: str, subject: str) -> str:
        """Create simple quoted original: Attribution + '> ' prefixed body."""
        try:
            attribution = f"\n--- Original message ---\nFrom: {from_addr}\nSubject: {subject}\n\n"
            quoted_body = "\n".join([f"> {line}" for line in body.splitlines()])
            return f"{attribution}{quoted_body}"
        except Exception as e:
            logger.error("Failed to format quoted content", error=str(e), from_addr=from_addr)
            return body  # Fallback to original body

    @staticmethod
    def _validate_reply_data(data: ReplyData) -> None:
        """Ensure required fields for reply are present."""
        try:
            if not data.to:
                raise ValueError("Reply must have at least one recipient")
            if not data.body.strip():
                raise ValueError("Reply body cannot be empty")
        except Exception as e:
            logger.error("Reply data validation failed", error=str(e))
            raise


