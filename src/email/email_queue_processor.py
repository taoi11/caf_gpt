


"""
src/email/email_queue_processor.py

EmailQueueProcessor: Treats inbox as FIFO queue - processes oldest unseen email first, then deletes it.
Synchronous loop for prototype: Connect IMAP, search UNSEEN, sort by date, process via SimpleEmailHandler, delete.
"""

import imaplib
import time
from typing import Optional

from src.config import AppConfig
from src.email.simple_email_handler import SimpleEmailHandler
from src.app_logging import get_logger

logger = get_logger(__name__)

class EmailQueueProcessor:
    def __init__(self, config: AppConfig, handler: SimpleEmailHandler):
        self.config = config
        self.handler = handler
        self.logger = get_logger(__name__)
        self.imap_config = config.email.imap
        self.process_interval = config.email.process_interval or 30  # seconds
        self.delete_after_process = config.email.delete_after_process or True
        logger.info("EmailQueueProcessor initialized", interval=self.process_interval, delete_after=self.delete_after_process)

    def start_queue_processing(self) -> None:
        """
        Start synchronous processing loop: Poll inbox every interval, process oldest email.
        Runs indefinitely until interrupted.
        """
        self.logger.info("Starting email queue processor", interval=self.process_interval)
        while True:
            try:
                self.process_next_email()
                time.sleep(self.process_interval)
            except KeyboardInterrupt:
                self.logger.info("Queue processor interrupted")
                break
            except Exception as e:
                self.logger.error("Error in queue processing loop", error=str(e), exc_info=True)
                time.sleep(self.process_interval)  # Continue on error

    def process_next_email(self) -> None:
        """Find and process the oldest unseen email in the inbox."""
        try:
            email_id = self.get_oldest_email_id()
            if not email_id:
                self.logger.debug("No unseen emails found")
                return

            logger.info("Processing next email", email_id=email_id)
            self.fetch_and_process_email(email_id)
        except Exception as e:
            self.logger.error("Error in process_next_email", error=str(e), exc_info=True)

    def get_oldest_email_id(self) -> Optional[str]:
        """Search IMAP for oldest UNSEEN email ID."""
        try:
            logger.debug("Connecting to IMAP for unseen emails", host=self.imap_config.host)
            with imaplib.IMAP4_SSL(self.imap_config.host, self.imap_config.port) as mail:
                mail.login(self.imap_config.username, self.imap_config.password)
                mail.select("INBOX")
                status, messages = mail.search(None, "UNSEEN")
                if status != "OK" or not messages[0]:
                    logger.debug("No unseen emails in inbox")
                    return None

                # For prototype: Assume first UNSEEN is oldest; full sort by date later
                email_ids = messages[0].split()
                if email_ids:
                    oldest_id = email_ids[0].decode()
                    logger.debug("Found oldest unseen email", email_id=oldest_id, total_unseen=len(email_ids))
                    return oldest_id
                return None
        except Exception as e:
            self.logger.error("Failed to get oldest email ID", error=str(e), host=self.imap_config.host, exc_info=True)
            return None

    def fetch_and_process_email(self, email_id: str) -> None:
        """Fetch raw message, process via handler, delete if successful."""
        try:
            logger.debug("Fetching email", email_id=email_id)
            with imaplib.IMAP4_SSL(self.imap_config.host, self.imap_config.port) as mail:
                mail.login(self.imap_config.username, self.imap_config.password)
                mail.select("INBOX")
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK" or not msg_data[0]:
                    raise ValueError(f"Failed to fetch email {email_id}")

                raw_message = msg_data[0][1]  # Bytes of raw email
                logger.debug("Processing email with handler", email_id=email_id, message_size=len(raw_message))
                self.handler.process_email(raw_message)

                if self.delete_after_process:
                    self.delete_email(email_id, mail)
                    logger.info("Email processed and deleted", email_id=email_id)
                else:
                    logger.info("Email processed (deletion disabled)", email_id=email_id)
        except Exception as e:
            self.logger.error("Failed to process email", email_id=email_id, error=str(e), exc_info=True)
            # Don't delete on failure
            raise  # Re-raise to signal failure

    def delete_email(self, email_id: str, mail: imaplib.IMAP4_SSL) -> None:
        """Mark email as deleted and expunge from inbox."""
        try:
            mail.store(email_id, "+FLAGS", "\\Deleted")
            mail.expunge()
            self.logger.info("Email deleted after processing", email_id=email_id)
        except Exception as e:
            self.logger.error("Failed to delete email", email_id=email_id, error=str(e), exc_info=True)
            raise


