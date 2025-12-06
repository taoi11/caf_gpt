"""
src/agents/types.py

Pydantic models for agent responses and research requests.

Top-level declarations:
- AgentResponse: Final response from coordinator (reply, no_response, or error)
- PrimeFooResponse: Parsed prime_foo response structure
- ResearchRequest: Sub-agent research query with multiple queries and agent type
"""

from typing import List, Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    # Final response from coordinator (reply, no_response, or error)
    reply: Optional[str] = None
    no_response: bool = False
    error: Optional[str] = None


class PrimeFooResponse(BaseModel):
    # Parsed prime_foo response structure
    type: str  # 'no_response', 'research', 'reply'
    content: Optional[str] = None
    research: Optional["ResearchRequest"] = None


class ResearchRequest(BaseModel):
    # Sub-agent research query with multiple queries and agent type
    queries: List[str]
    agent_type: str  # e.g., 'leave_foo'


