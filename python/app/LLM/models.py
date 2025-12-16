from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timezone


class MessageStatus(str, Enum):
    sending = "sending"
    success = "success"
    failed = "failed"


class ReferenceCard(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    snippet: Optional[str] = None
    source_url: Optional[str] = None
    source_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    id: str
    role: str
    content: str
    status: MessageStatus = MessageStatus.success
    created_at: str = datetime.now(timezone.utc).isoformat()
    references: Optional[List[ReferenceCard]] = None


class Pagination(BaseModel):
    current_page: int
    total_pages: int
    total_count: int
    per_page: int