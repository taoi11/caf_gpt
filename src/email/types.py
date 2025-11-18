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
