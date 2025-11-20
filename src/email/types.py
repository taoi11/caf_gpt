"""
src/email/types.py

Pydantic models for representing parsed email data structures.

Top-level declarations:
- ParsedEmailData: Model holding extracted email fields like sender, recipients, subject, and body content
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, EmailStr


class ParsedEmailData(BaseModel):
    from_addr: EmailStr
    to_addrs: List[EmailStr]
    cc_addrs: List[EmailStr]
    subject: str
    text_body: Optional[str] = None
    html_body: Optional[str] = None
