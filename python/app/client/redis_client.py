from typing import Optional, Any
from app.client.base_client import BaseHTTPClient
from app.config import settings

class RedisClient(BaseHTTPClient):
    """Redis服务客户端"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.redis_api_base_url,
            connect_timeout=settings.redis_api_connect_timeout,
            read_timeout=settings.redis_api_read_timeout,
            retry_times=settings.redis_api_retry_times
        )
    
    async def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """设置缓存"""
        data = {
            "key": key,
            "value": value,
            "timeout": timeout
        }
        try:
            result = await self.post("/cache/set", json=data)
            return result is not None
        except Exception:
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        return await self.get("/cache/get", params={"key": key})
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        return await self.delete("/cache/delete", params={"key": key})
    
    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        result = await self.get("/cache/exists", params={"key": key})
        return result if isinstance(result, bool) else False
    
    async def search_keys(self, pattern: str) -> list:
        """模糊搜索key"""
        result = await self.get("/cache/search", params={"pattern": pattern})
        return result if isinstance(result, list) else []

