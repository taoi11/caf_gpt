"""
src/utils/spam_filter.py

Email sender validation and spam filtering.
Validates email senders against allowed domains and email addresses.

Top-level declarations:
- ALLOWED_DOMAINS: Hardcoded list of allowed email domains
- ALLOWED_EMAILS: Hardcoded list of allowed specific email addresses
- is_sender_allowed: Function to check if sender email is in allow list
"""

import logging

logger = logging.getLogger(__name__)

ALLOWED_DOMAINS = [
    "forces.gc.ca",
    "ecn.forces.gc.ca",
]

ALLOWED_EMAILS: list[str] = [
    "luffy@luffy.email",
    "luffy1749@gmail.com",
]


def is_sender_allowed(sender_email: str) -> bool:
    # Check if sender email is allowed based on domain or explicit email match
    # Validates against hardcoded allowlists for domains and specific email addresses
    if not sender_email:
        return False

    sender_email = sender_email.lower().strip()

    # Check explicit email allowlist
    if sender_email in ALLOWED_EMAILS:
        return True

    # Check domain allowlist
    for domain in ALLOWED_DOMAINS:
        if sender_email.endswith(f"@{domain}"):
            return True

    return False
