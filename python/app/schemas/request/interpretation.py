from pydantic import BaseModel
from typing import Optional, List

class InterpretationRequest(BaseModel):
    """生成阐释请求"""
    recognition_id: str
    aspects: Optional[List[str]] = None  # ["history", "culture", "literature"]
    depth: Optional[str] = "detailed"  # brief, detailed, academic

class ChatRequest(BaseModel):
    """AI对话请求"""
    recognition_id: str
    message: str
    context: Optional[str] = None
    conversation_id: Optional[str] = None

