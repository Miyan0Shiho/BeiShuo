from typing import Optional
from fastapi import Header, HTTPException
from app.core.security import jwt_util
from app.common.result_code import ResultCode

async def get_current_user_id(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> int:
    """获取当前用户ID（依赖注入）"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=ResultCode.UNAUTHORIZED.message
        )
    
    token = jwt_util.extract_token_from_header(authorization)
    if not token or not jwt_util.validate_token(token):
        raise HTTPException(
            status_code=401,
            detail=ResultCode.TOKEN_INVALID.message
        )
    
    user_id = jwt_util.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail=ResultCode.TOKEN_INVALID.message
        )
    
    return user_id

async def get_current_username(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> str:
    """获取当前用户名（依赖注入）"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=ResultCode.UNAUTHORIZED.message
        )
    
    token = jwt_util.extract_token_from_header(authorization)
    if not token or not jwt_util.validate_token(token):
        raise HTTPException(
            status_code=401,
            detail=ResultCode.TOKEN_INVALID.message
        )
    
    username = jwt_util.get_username_from_token(token)
    if not username:
        raise HTTPException(
            status_code=401,
            detail=ResultCode.TOKEN_INVALID.message
        )
    
    return username

