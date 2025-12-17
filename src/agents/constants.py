"""
src/agents/constants.py

Shared constants and enums for agent system to eliminate magic strings and improve type safety.

Top-level declarations:
- ResponseType: Enum for prime_foo response types (no_response, reply, research, feedback_note)
"""

from enum import Enum


class ResponseType(str, Enum):
    # Enum for prime_foo LLM response types parsed from XML
    # Used in agent_coordinator.py for response handling
    NO_RESPONSE = "no_response"
    REPLY = "reply"
    RESEARCH = "research"
    FEEDBACK_NOTE = "feedback_note"
