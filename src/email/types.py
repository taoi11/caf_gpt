from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator, Field

class EmailRecipients(BaseModel):
    to: List[EmailStr] = Field(default_factory=list)
    cc: List[EmailStr] = Field(default_factory=list)
    bcc: List[EmailStr] = Field(default_factory=list)

class ParsedEmailData(BaseModel):
    message_id: str
    from_addr: EmailStr
    recipients: EmailRecipients = Field(default_factory=EmailRecipients)
    subject: str
    body: str  # For prototype: prefer text_body, fallback to html_body stripped
    thread_id: Optional[str] = None

    @validator('body', pre=True)
    def extract_body(cls, v, values):
        # This is a placeholder; actual extraction in parser
        return v or ''

class ReplyData(BaseModel):
    to: List[EmailStr]
    cc: List[EmailStr] = Field(default_factory=list)
    subject: str
    body: str
    in_reply_to: Optional[str] = None
    references: Optional[str] = None
