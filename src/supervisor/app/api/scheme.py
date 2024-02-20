from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    id: int
    source: str
    date: datetime
    from_user: str
    text: Optional[str] = None
    image: Optional[str] = None


class MessageDB(BaseModel):
    local_id: int
    source: str
    date: datetime
    from_user: str
    text: Optional[str] = None
    image: Optional[bytes] = None
