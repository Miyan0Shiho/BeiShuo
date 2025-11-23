from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.config import settings

class JWTUtil:
    """JWT工具类"""
    
    @staticmethod
    def generate_token(user_id: int, username: str, expiration: Optional[int] = None) -> str:
        """生成Token"""
        if expiration is None:
            expiration = settings.jwt_expiration
        
        payload = {
            "userId": user_id,
            "username": username,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(milliseconds=expiration)
        }
        
        return jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
    
    @staticmethod
    def generate_refresh_token(user_id: int, username: str) -> str:
        """生成刷新Token"""
        expiration = settings.jwt_refresh_expiration
        payload = {
            "userId": user_id,
            "username": username,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(milliseconds=expiration)
        }
        
        return jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """解码Token"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """验证Token是否有效"""
        payload = JWTUtil.decode_token(token)
        return payload is not None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """从Token中获取用户ID"""
        payload = JWTUtil.decode_token(token)
        if payload:
            user_id = payload.get("userId")
            if isinstance(user_id, (int, str)):
                return int(user_id)
        return None
    
    @staticmethod
    def get_username_from_token(token: str) -> Optional[str]:
        """从Token中获取用户名"""
        payload = JWTUtil.decode_token(token)
        if payload:
            return payload.get("username")
        return None
    
    @staticmethod
    def extract_token_from_header(auth_header: Optional[str]) -> Optional[str]:
        """从请求头中提取Token"""
        if not auth_header:
            return None
        
        prefix = settings.jwt_token_prefix
        if auth_header.startswith(prefix):
            return auth_header[len(prefix):].strip()
        return None

jwt_util = JWTUtil()

