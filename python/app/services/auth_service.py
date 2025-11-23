from typing import Optional, Dict, Any
from app.client.database_client import DatabaseClient
from app.client.redis_client import RedisClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.config import settings
from app.utils.password import PasswordUtil
from app.utils.logger import logger

class AuthService:
    """认证服务"""
    
    def __init__(self):
        self.database_client = DatabaseClient()
        self.redis_client = RedisClient()
        self.password_util = PasswordUtil()
    
    async def register(self, email: str, password: str, username: str) -> Dict[str, Any]:
        """用户注册"""
        # 检查用户是否已存在
        existing_user = await self.database_client.get_user_by_email(email)
        if existing_user:
            raise BusinessException(ResultCode.USER_ALREADY_EXISTS)
        
        # 加密密码
        hashed_password = self.password_util.hash_password(password)
        
        # 创建用户
        user_data = {
            "email": email,
            "password": hashed_password,
            "username": username
        }
        
        user = await self.database_client.create_user(user_data)
        if not user:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "用户创建失败")
        
        logger.info(f"用户注册成功: email={email}, username={username}")
        return user
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        # 查询用户
        user = await self.database_client.get_user_by_email(email)
        if not user:
            raise BusinessException(ResultCode.INVALID_CREDENTIALS)
        
        # 验证密码
        stored_password = user.get("password")
        if not self.password_util.verify_password(password, stored_password):
            raise BusinessException(ResultCode.INVALID_CREDENTIALS)
        
        # 缓存用户信息
        await self.redis_client.set(
            f"user:{user['id']}",
            user,
            timeout=settings.cache_user_info_ttl
        )
        
        logger.info(f"用户登录成功: email={email}")
        return user
    
    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """根据ID获取用户信息"""
        # 先查缓存
        cached_user = await self.redis_client.get(f"user:{user_id}")
        if cached_user:
            return cached_user
        
        # 查数据库
        user = await self.database_client.get_user_by_id(user_id)
        if not user:
            raise BusinessException(ResultCode.USER_NOT_FOUND)
        
        # 缓存结果
        await self.redis_client.set(
            f"user:{user_id}",
            user,
            timeout=settings.cache_user_info_ttl
        )
        
        return user
    
    async def close(self):
        """关闭客户端连接"""
        await self.database_client.close()
        await self.redis_client.close()

