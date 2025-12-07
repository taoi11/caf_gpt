"""
src/email_code/components/email_adapter.py

Email adapter that converts imap_tools MailMessage objects to our internal ParsedEmailData format.
Handles the translation between external library objects and our domain models.

Top-level declarations:
- EmailAdapter: Static class for converting between MailMessage and ParsedEmailData formats
"""

from imap_tools import MailMessage

from src.email_code.types import ParsedEmailData, EmailRecipients


class EmailAdapter:
    # Static class for converting between MailMessage and ParsedEmailData formats

    @staticmethod
    def adapt_mail_message(msg: MailMessage) -> ParsedEmailData:
        # Convert imap_tools MailMessage to our ParsedEmailData domain model
        # Recipients
        recipients = EmailRecipients(
            to=list(msg.to) if msg.to else [], cc=list(msg.cc) if msg.cc else []
        )

        # Body: prefer text, fallback to HTML stripped
        body = msg.text or EmailAdapter._strip_html(msg.html) if msg.html else ""

        return ParsedEmailData(
            message_id=msg.uid or "",
            from_addr=msg.from_ or "",
            recipients=recipients,
            subject=msg.subject or "",
            body=body,
            thread_id=msg.uid,
        )

    @staticmethod
    def _strip_html(html: str) -> str:
        # Basic HTML stripping for fallback when text content is not available
        import re
        from html import unescape

        clean = re.sub(r"<[^>]+>", "", html)
        return unescape(clean).strip()
