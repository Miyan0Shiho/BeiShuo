from typing import List, Optional
from app.client.redis_client import RedisClient
from app.config import settings
from app.utils.logger import logger

class FavoriteService:
    """收藏服务 (基于 Redis)"""
    
    def __init__(self):
        self.redis_client = RedisClient()
        
    async def add_favorite(self, user_id: int, item_id: int) -> bool:
        """添加收藏"""
        key = f"user:favorites:{user_id}"
        # 使用 Set 存储，自动去重
        await self.redis_client.sadd(key, str(item_id))
        logger.info(f"User {user_id} favorited item {item_id}")
        return True
        
    async def remove_favorite(self, user_id: int, item_id: int) -> bool:
        """移除收藏"""
        key = f"user:favorites:{user_id}"
        await self.redis_client.srem(key, str(item_id))
        logger.info(f"User {user_id} unfavorited item {item_id}")
        return True
        
    async def get_favorites(self, user_id: int) -> List[int]:
        """获取收藏列表"""
        key = f"user:favorites:{user_id}"
        members = await self.redis_client.smembers(key)
        # members 是 bytes 或 str 集合
        return [int(m) for m in members] if members else []
        
    async def is_favorite(self, user_id: int, item_id: int) -> bool:
        """检查是否已收藏"""
        key = f"user:favorites:{user_id}"
        return await self.redis_client.sismember(key, str(item_id))

    async def close(self):
        await self.redis_client.close()