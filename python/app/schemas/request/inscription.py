from pydantic import BaseModel, Field
from typing import Optional, List

class InscriptionCreateRequest(BaseModel):
    """创建碑文请求"""
    title: Optional[str] = None
    imageUrl: Optional[str] = Field(None, alias="image_url")
    image_url: Optional[str] = None # Support both snake_case and camelCase
    text: Optional[str] = None
    dynasty: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str = "recognizing"
    
    class Config:
        populate_by_name = True

class InscriptionUpdateRequest(BaseModel):
    """更新碑文请求"""
    title: Optional[str] = None
    correctedText: Optional[str] = None
    status: Optional[str] = None
