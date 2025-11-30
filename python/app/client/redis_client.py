from typing import Optional, Any
import asyncio
from app.config import settings
from app.utils.logger import logger

class RedisClient:
    """内存缓存客户端 - 临时替代Redis服务"""
    
    def __init__(self):
        self._cache = {}
        self._expire_times = {}
        self._lock = asyncio.Lock()
        logger.info("使用内存缓存替代Redis服务")
    
    async def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            async with self._lock:
                self._cache[key] = value
                if timeout is not None:
                    self._expire_times[key] = asyncio.get_event_loop().time() + timeout
                else:
                    self._expire_times.pop(key, None)
            logger.debug(f"缓存设置成功: {key}")
            return True
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            # 检查是否过期
            current_time = asyncio.get_event_loop().time()
            if key in self._expire_times and current_time > self._expire_times[key]:
                async with self._lock:
                    self._cache.pop(key, None)
                    self._expire_times.pop(key, None)
                return None
            
            value = self._cache.get(key)
            if value:
                logger.debug(f"缓存命中: {key}")
            return value
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            async with self._lock:
                self._cache.pop(key, None)
                self._expire_times.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        return await self.get(key) is not None
    
    async def close(self):
        """关闭缓存客户端"""
        async with self._lock:
            self._cache.clear()
            self._expire_times.clear()
        logger.info("内存缓存已清空")

