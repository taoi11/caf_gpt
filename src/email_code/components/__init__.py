"""
src/email_code/components/__init__.py

Email components for the CAF-GPT email agent.

Top-level declarations:
- EmailComposer: Class for composing email replies using Jinja templates
- EmailThreadManager: Static class for building email threading headers
- EmailAdapter: Static class for converting between MailMessage and ParsedEmailData formats
"""

from .email_composer import EmailComposer
from .email_thread_manager import EmailThreadManager
from .email_adapter import EmailAdapter

__all__ = ["EmailComposer", "EmailThreadManager", "EmailAdapter"]
