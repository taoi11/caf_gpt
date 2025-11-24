
"""
src/email_code/components/email_sender.py

EmailSender using Redmail for robust SMTP sending with retries.
Handles connection, authentication, and sending composed replies.
"""

from redmail import EmailSender as RedmailSender
import time

from src.app_logging import get_logger
from src.config import config
from src.email_code.types import ReplyData, ParsedEmailData
from .email_composer import EmailComposer

logger = get_logger(__name__)

class EmailSender:
    def __init__(self) -> None:
        """Initialize Redmail EmailSender with SMTP config from app settings."""
        email_config = config.email
        self.redmail = RedmailSender(
            host=email_config.smtp_host,
            port=email_config.smtp_port,
            username=email_config.smtp_username,
            password=email_config.smtp_password,
            use_tls=email_config.smtp_use_tls,
            use_ssl=email_config.smtp_use_ssl,
        )
        self.composer = EmailComposer()
        logger.info("EmailSender initialized with Redmail and Jinja composer")

    def send_reply(self, reply_data: ReplyData, original: ParsedEmailData, agent_email: str) -> bool:
        """
        Compose a professional reply using EmailComposer and send via Redmail with retries.
        
        :param reply_data: Structured reply info (body, to, cc, subject, etc.)
        :param original: Original parsed email for quoting and threading
        :param agent_email: Sender's email address (e.g., from config)
        :return: True if sent successfully, False otherwise
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Compose the reply structure
                composed = self.composer.compose_reply(reply_data, original, agent_email)
                
                # Prepare send parameters
                send_kwargs = {
                    "sender": agent_email,
                    "receivers": composed["to"],
                    "subject": composed["subject"],
                    "html": composed["html_body"],
                }
                
                # Add CC if present
                if composed["cc"]:
                    send_kwargs["cc"] = composed["cc"]
                
                # Add threading headers
                extra_headers = {}
                if composed.get("in_reply_to"):
                    extra_headers["In-Reply-To"] = composed["in_reply_to"]
                if composed.get("references"):
                    extra_headers["References"] = composed["references"]
                
                if extra_headers:
                    send_kwargs["extra_headers"] = extra_headers
                
                # Send the email
                self.redmail.send(**send_kwargs)
                
                logger.info(
                    "Reply sent successfully via Redmail",
                    subject=composed["subject"],
                    to=", ".join(composed["to"]),
                    cc_count=len(composed["cc"] or []),
                    attempt=attempt + 1,
                )
                return True
                
            except Exception as e:
                logger.warning(
                    f"Send attempt {attempt + 1} failed via Redmail",
                    error=str(e),
                    subject=reply_data.subject,
                    to=", ".join(reply_data.to),
                )
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Failed to send reply after all retries",
                        error=str(e),
                        subject=reply_data.subject,
                        to=", ".join(reply_data.to),
                    )
                    return False
