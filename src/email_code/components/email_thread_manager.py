"""
src/email_code/components/email_thread_manager.py

Email thread manager for RFC 5322 compliant email threading.
Generates In-Reply-To and References headers for proper email conversation tracking.

Top-level declarations:
- EmailThreadManager: Static class for building email threading headers
"""

from typing import Dict, List
import logging

from src.email_code.types import ParsedEmailData  # For message_id

logger = logging.getLogger(__name__)


class EmailThreadManager:
    # Static class for building email threading headers
    # Generates In-Reply-To and References headers for proper email conversation tracking

    @staticmethod
    def build_threading_headers(original: ParsedEmailData) -> Dict[str, str]:
        # Build threading headers for reply following RFC 5322 standards
        # In-Reply-To: Original Message-ID
        # References: Existing References + original Message-ID (trim if >998 chars)
        try:
            message_id = original.message_id.strip("<>")
            if not message_id:
                logger.warning(f"No Message-ID found for threading thread_id={original.thread_id}")
                return {}

            in_reply_to = f"<{message_id}>"
            references = EmailThreadManager._build_references(original, message_id)

            headers = {"In-Reply-To": in_reply_to, "References": references}
            logger.debug(
                f"Threading headers built message_id={message_id} references_len={len(references)}"
            )
            return headers
        except Exception as e:
            logger.error(f"Failed to build threading headers: {e} message_id={original.message_id}")
            return {}

    @staticmethod
    def _build_references(original: ParsedEmailData, new_id: str) -> str:
        # Build References header: Append new ID to existing, trim if needed
        try:
            # For prototype, use message_id as proxy; in full implementation, parse actual References header
            existing_refs = original.message_id
            refs_list = (
                [ref.strip("<>") for ref in existing_refs.split() if ref.strip("<>")]
                if existing_refs
                else []
            )
            refs_list.append(new_id)

            # Trim to keep under 998 chars (RFC limit)
            trimmed = EmailThreadManager._trim_references(refs_list)
            result = " ".join([f"<{ref}>" for ref in trimmed])
            return result
        except Exception as e:
            logger.error(f"Failed to build references: {e}")
            return f"<{new_id}>"

    @staticmethod
    def _trim_references(refs: List[str], max_length: int = 998) -> List[str]:
        # Trim references list to fit within RFC header length limit
        try:
            trimmed: list[str] = []
            current = ""
            for ref in refs:
                test = f"{current} <{ref}>".strip()
                if len(test) > max_length:
                    logger.debug(
                        f"References trimmed due to length limit original_len={len(refs)} trimmed_len={len(trimmed)}"
                    )
                    break
                trimmed.append(ref)
                current = test
            return trimmed
        except Exception as e:
            logger.error(f"Failed to trim references: {e}")
            return refs[:5]  # Fallback: keep first 5
