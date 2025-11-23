from pydantic import BaseModel
from typing import Optional

class InscriptionCreateRequest(BaseModel):
    """创建碑文请求"""
    title: Optional[str] = None
    imageUrl: Optional[str] = None
    text: Optional[str] = None
    dynasty: Optional[str] = None
    status: str = "recognizing"

class InscriptionUpdateRequest(BaseModel):
    """更新碑文请求"""
    title: Optional[str] = None
    correctedText: Optional[str] = None
    status: Optional[str] = None

