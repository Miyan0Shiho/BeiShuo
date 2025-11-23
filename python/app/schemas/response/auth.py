from pydantic import BaseModel
from typing import Optional, Dict, Any

class UserStats(BaseModel):
    """用户统计信息"""
    total_recognitions: int = 0
    total_favorites: int = 0
    total_questions: int = 0

class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    stats: Optional[UserStats] = None
    created_at: Optional[str] = None

class LoginResponse(BaseModel):
    """登录响应"""
    user_id: Optional[int] = None
    token: str
    expires_at: str
    user: UserInfoResponse

class RefreshResponse(BaseModel):
    """刷新Token响应"""
    token: str
    expires_at: str

