from fastapi import APIRouter, Depends, Header
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.security import jwt_util
from app.core.dependencies import get_current_user_id
from app.services.auth_service import AuthService
from app.schemas.request.auth import LoginRequest, RegisterRequest
from app.schemas.response.auth import LoginResponse, UserInfoResponse, RefreshResponse

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=Result[LoginResponse])
async def register(request: RegisterRequest):
    """用户注册"""
    service = AuthService()
    try:
        # 使用name作为username
        user = await service.register(request.email, request.password, request.name)
        
        # 生成Token
        user_id = user["id"]
        username = user.get("username") or request.name
        token = jwt_util.generate_token(user_id, username)
        
        # 计算过期时间（24小时后）
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        expires_at_str = expires_at.isoformat()
        
        response_data = {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at_str,
            "user": {
                "id": user_id,
                "name": username,
                "email": user["email"],
                "phone": request.phone,
                "avatar": request.avatar,
                "created_at": user.get("created_at", datetime.now(timezone.utc).isoformat())
            }
        }
        
        return Result.ok(response_data, "注册成功")
    finally:
        await service.close()

@router.post("/login", response_model=Result[LoginResponse])
async def login(request: LoginRequest):
    """用户登录"""
    service = AuthService()
    try:
        user = await service.login(request.email, request.password)
        
        # 生成Token
        user_id = user["id"]
        username = user.get("username") or user.get("name", "")
        token = jwt_util.generate_token(user_id, username)
        
        # 根据remember_me决定过期时间
        expiration_hours = 168 if request.remember_me else 24  # 7天或1天
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
        expires_at_str = expires_at.isoformat()
        
        response_data = {
            "token": token,
            "expires_at": expires_at_str,
            "user": {
                "id": user_id,
                "name": username,
                "email": user["email"],
                "phone": user.get("phone"),
                "avatar": user.get("avatar")
            }
        }
        
        return Result.ok(response_data, "登录成功")
    finally:
        await service.close()

@router.post("/logout", response_model=Result[dict])
async def logout():
    """用户登出"""
    # TODO: 实现登出逻辑（如将Token加入黑名单等）
    return Result.ok(None, "已成功登出")

@router.get("/profile", response_model=Result[UserInfoResponse])
async def get_current_user_info(user_id: int = Depends(get_current_user_id)):
    """获取当前用户信息"""
    service = AuthService()
    try:
        user = await service.get_user_by_id(user_id)
        
        # 添加统计信息（需要从服务层获取）
        stats = {
            "total_recognitions": 0,
            "total_favorites": 0,
            "total_questions": 0
        }
        
        user_info = {
            "id": user["id"],
            "name": user.get("username") or user.get("name", ""),
            "email": user["email"],
            "phone": user.get("phone"),
            "avatar": user.get("avatar"),
            "stats": stats,
            "created_at": user.get("created_at", datetime.now(timezone.utc).isoformat())
        }
        return Result.ok(user_info)
    finally:
        await service.close()

@router.post("/refresh", response_model=Result[RefreshResponse])
async def refresh_token(authorization: Optional[str] = Header(None)):
    """刷新Token"""
    if not authorization or not authorization.startswith("Bearer "):
        return Result.error(ResultCode.UNAUTHORIZED, "未授权，请先登录")
    
    token = authorization.replace("Bearer ", "")
    if not jwt_util.validate_token(token):
        return Result.error(ResultCode.TOKEN_INVALID)
    
    user_id = jwt_util.get_user_id_from_token(token)
    username = jwt_util.get_username_from_token(token)
    
    if not user_id or not username:
        return Result.error(ResultCode.TOKEN_INVALID)
    
    new_token = jwt_util.generate_token(user_id, username)
    
    # 计算过期时间（24小时后）
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    expires_at_str = expires_at.isoformat()
    
    return Result.ok({
        "token": new_token,
        "expires_at": expires_at_str
    })

