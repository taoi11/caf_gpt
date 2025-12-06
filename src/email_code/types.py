"""
src/email_code/types.py

Pydantic models for email data structures and validation.

Top-level declarations:
- EmailRecipients: Model for email recipient lists (to, cc)
- ParsedEmailData: Model for parsed incoming email data
- ReplyData: Model for email reply data structure
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator, Field

class EmailRecipients(BaseModel):
    # Model for email recipient lists with to and cc fields
    to: List[EmailStr] = Field(default_factory=list)
    cc: List[EmailStr] = Field(default_factory=list)

class ParsedEmailData(BaseModel):
    # Model for parsed incoming email data with all required fields
    message_id: str
    from_addr: EmailStr
    recipients: EmailRecipients = Field(default_factory=EmailRecipients)
    subject: str
    body: str  # For prototype: prefer text_body, fallback to html_body stripped
    date: Optional[str] = None
    thread_id: Optional[str] = None

    @validator('body', pre=True)
    def extract_body(cls, v, values):
        # Ensure body is never None, fallback to empty string
        return v or ''

class ReplyData(BaseModel):
    # Model for email reply data structure with threading support
    to: List[EmailStr]
    cc: List[EmailStr] = Field(default_factory=list)
    subject: str
    body: str
    in_reply_to: Optional[str] = None
    references: Optional[str] = None
