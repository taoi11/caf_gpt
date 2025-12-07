"""
src/email_code/components/email_composer.py

Email composer that creates professional HTML replies using Jinja templates.
Builds properly formatted emails with threading headers and original message quoting.

Top-level declarations:
- EmailComposer: Class for composing email replies using Jinja templates
"""

from typing import Dict, Optional
import jinja2
from pathlib import Path

from src.app_logging import get_logger
from src.config import config
from src.email_code.types import ReplyData, ParsedEmailData

logger = get_logger(__name__)


class EmailComposer:
    # Class for composing email replies using Jinja templates

    def __init__(self):
        # Initialize Jinja environment with template directory from config
        template_dir = Path(config.email.template_dir)
        if not template_dir.exists():
            raise ValueError(f"Template directory not found: {template_dir}")
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def compose_reply(
        self, reply_data: ReplyData, original: ParsedEmailData, agent_email: str
    ) -> Dict:
        # Compose professional HTML reply using Jinja template with threading and validation
        # :param reply_data: Structured reply info (body, to, cc, subject, in_reply_to, references)
        # :param original: Original parsed email for quoting and threading
        # :param agent_email: Bot's email address (for From header)
        # :return: Dict with keys: subject, to, cc, html_body, in_reply_to, references
        try:
            # Validate inputs
            self._validate_reply_data(reply_data)

            # Format subject
            subject = self._format_subject(reply_data.subject, original.subject)

            # Prepare original data for template
            original_dict = {
                "from_addr": original.from_addr,
                "date": original.date or "Unknown date",
                "to": original.recipients.to,
                "subject": original.subject,
                "body": original.body,
            }

            # Render HTML template
            template = self.jinja_env.get_template("reply.html.jinja")
            html_body = template.render(
                reply_body=reply_data.body,
                original=original_dict,
            )

            # Prepare recipients
            to = reply_data.to
            cc = reply_data.cc or []

            # Threading headers
            in_reply_to = reply_data.in_reply_to or original.message_id
            references = reply_data.references or original.message_id

            reply_dict = {
                "subject": subject,
                "to": to,
                "cc": cc,
                "html_body": html_body,
                "in_reply_to": in_reply_to,
                "references": references,
            }

            to_str = ", ".join(to)
            body_preview = (
                reply_data.body[:100] + "..." if len(reply_data.body) > 100 else reply_data.body
            )
            logger.debug(
                f"Jinja-templated HTML reply composed subject={subject} to={to_str} cc_count={len(cc)} body_preview={body_preview}"
            )
            return reply_dict
        except jinja2.TemplateNotFound as e:
            logger.error(f"Jinja template not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to compose reply: {e} subject={reply_data.subject}")
            raise

    @staticmethod
    def _format_subject(reply_subject: Optional[str], original_subject: str) -> str:
        # Format subject with 'Re:' prefix if not present, preferring reply_subject
        try:
            if reply_subject:
                # Ensure 'Re:' if replying but not present
                if not reply_subject.startswith("Re:") and original_subject:
                    return f"Re: {reply_subject}"
                return reply_subject
            # Fallback to original with Re:
            if original_subject:
                if not original_subject.startswith("Re:"):
                    return f"Re: {original_subject}"
                return original_subject
            return "Re:"
        except Exception as e:
            logger.error(f"Failed to format subject: {e} original_subject={original_subject}")
            return "Re:"

    @staticmethod
    def _validate_reply_data(data: ReplyData) -> None:
        # Ensure required fields for reply are present
        if not data.to:
            logger.error("Reply data validation failed: no recipients")
            raise ValueError("Reply must have at least one recipient")
        if not data.body.strip():
            logger.error("Reply data validation failed: empty body")
            raise ValueError("Reply body cannot be empty")
