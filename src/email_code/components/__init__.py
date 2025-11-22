"""
src/email_code/components/__init__.py

Email components for the CAF-GPT email agent.
"""

from .email_composer import EmailComposer
from .email_thread_manager import EmailThreadManager
from .email_adapter import EmailAdapter

__all__ = ["EmailComposer", "EmailThreadManager", "EmailAdapter"]
