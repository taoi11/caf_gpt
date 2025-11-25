
"""
src/email_code/components/email_sender.py

EmailSender using Redmail for robust SMTP sending with retries.
Handles connection, authentication, and sending composed replies.
"""

import yagmail
import time

from src.app_logging import get_logger
from src.config import config
from src.email_code.types import ReplyData, ParsedEmailData
from .email_composer import EmailComposer

logger = get_logger(__name__)

class EmailSender:
    def __init__(self) -> None:
        """Initialize yagmail SMTP with config from app settings."""
        email_config = config.email
        self.yag = yagmail.SMTP(
            user=email_config.smtp_username,
            password=email_config.smtp_password,
            host=email_config.smtp_host,
            port=email_config.smtp_port,
            smtp_starttls=email_config.smtp_use_tls,
            smtp_ssl=email_config.smtp_use_ssl,
        )
        self.composer = EmailComposer()
        logger.info("EmailSender initialized with yagmail and Jinja composer")

    def send_reply(self, reply_data: ReplyData, original: ParsedEmailData, agent_email: str) -> bool:
        """
        Compose a professional reply using EmailComposer and send via yagmail with retries.
        
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
                
                # Prepare headers
                headers = {}
                if composed.get("in_reply_to"):
                    headers["In-Reply-To"] = composed["in_reply_to"]
                if composed.get("references"):
                    headers["References"] = composed["references"]
                
                # Send the email
                self.yag.send(
                    to=composed["to"],
                    subject=composed["subject"],
                    contents=composed["html_body"],
                    cc=composed["cc"] if composed["cc"] else None,
                    headers=headers if headers else None,
                )
                
                logger.info(
                    "Reply sent successfully via yagmail",
                    subject=composed["subject"],
                    to=", ".join(composed["to"]),
                    cc_count=len(composed["cc"] or []),
                    attempt=attempt + 1,
                )
                return True
                
            except Exception as e:
                logger.warning(
                    f"Send attempt {attempt + 1} failed via yagmail",
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
