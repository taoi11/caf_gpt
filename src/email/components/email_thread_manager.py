

"""
src/email/components/email_thread_manager.py

Basic EmailThreadManager for prototype: Manage RFC 5322 compliant email threading.
Generates In-Reply-To and References headers for replies.
For prototype: Simple append/trim logic.
"""

import re
from typing import Optional, Dict, List

from src.app_logging import get_logger
from src.email.types import ParsedEmailData  # For message_id

logger = get_logger(__name__)

class EmailThreadManager:
    @staticmethod
    def build_threading_headers(original: ParsedEmailData) -> Dict[str, str]:
        """
        Build threading headers for reply.
        In-Reply-To: Original Message-ID
        References: Existing References + original Message-ID (trim if >998 chars)
        """
        try:
            message_id = original.message_id.strip('<>')
            if not message_id:
                logger.warning("No Message-ID found for threading", thread_id=original.thread_id)
                return {}

            in_reply_to = f"<{message_id}>"
            references = EmailThreadManager._build_references(original, message_id)

            headers = {
                "In-Reply-To": in_reply_to,
                "References": references
            }
            logger.debug("Threading headers built", message_id=message_id, references_len=len(references))
            return headers
        except Exception as e:
            logger.error("Failed to build threading headers", error=str(e), message_id=original.message_id)
            return {}

    @staticmethod
    def _build_references(original: ParsedEmailData, new_id: str) -> str:
        """Build References header: Append new ID to existing, trim if needed."""
        try:
            # For prototype, use message_id as proxy; in full impl, parse actual References header
            existing_refs = original.message_id
            refs_list = [ref.strip('<>') for ref in existing_refs.split() if ref.strip('<>')] if existing_refs else []
            refs_list.append(new_id)
            
            # Trim to keep under 998 chars (RFC limit)
            trimmed = EmailThreadManager._trim_references(refs_list)
            result = " ".join([f"<{ref}>" for ref in trimmed])
            return result
        except Exception as e:
            logger.error("Failed to build references", error=str(e))
            return f"<{new_id}>"

    @staticmethod
    def _trim_references(refs: List[str], max_length: int = 998) -> List[str]:
        """Trim references list to fit within header length limit."""
        try:
            trimmed = []
            current = ""
            for ref in refs:
                test = f"{current} <{ref}>".strip()
                if len(test) > max_length:
                    logger.debug("References trimmed due to length limit", original_len=len(refs), trimmed_len=len(trimmed))
                    break
                trimmed.append(ref)
                current = test
            return trimmed
        except Exception as e:
            logger.error("Failed to trim references", error=str(e))
            return refs[:5]  # Fallback: keep first 5

    @staticmethod
    def validate_message_id(message_id: str) -> bool:
        """Basic validation of Message-ID format (RFC 2822)."""
        try:
            # Should be <local-part@domain>, but simple check
            pattern = r'^<[^@]+@[^>]+>$'
            is_valid = bool(re.match(pattern, message_id))
            if not is_valid:
                logger.warning("Invalid Message-ID format", message_id=message_id)
            return is_valid
        except Exception as e:
            logger.error("Error validating Message-ID", message_id=message_id, error=str(e))
            return False

