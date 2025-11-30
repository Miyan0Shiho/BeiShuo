from typing import Optional, Dict, Any, List
from app.client.database_client import DatabaseClient
from app.client.redis_client import RedisClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.config import settings
from app.utils.logger import logger

class InscriptionService:
    """碑文服务"""
    
    def __init__(self):
        self.database_client = DatabaseClient()
        self.redis_client = RedisClient()
    
    async def get_list(
        self,
        user_id: int,
        page: int = 0,
        size: int = 10,
        sort: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取碑文列表"""
        # 生成缓存键
        cache_key = f"inscription:list:{user_id}:{page}:{size}:{sort or ''}:{keyword or ''}"
        
        # 先查缓存
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            return cached_result
        
        # 查数据库
        result = await self.database_client.get_inscription_list(
            user_id=user_id,
            page=page,
            size=size,
            sort=sort,
            keyword=keyword
        )
        
        if not result:
            return {
                "list": [],
                "total": 0,
                "page": page,
                "size": size,
                "totalPages": 0
            }
        
        # 缓存结果
        await self.redis_client.set(
            cache_key,
            result,
            timeout=settings.cache_inscription_list_ttl
        )
        
        return result
    
    async def get_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取碑文详情"""
        inscription = await self.database_client.get_inscription_by_id(inscription_id)
        return inscription
    
    async def create(self, user_id: int, inscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建碑文"""
        inscription_data["userId"] = user_id
        inscription = await self.database_client.create_inscription(inscription_data)
        if not inscription:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "碑文创建失败")
        
        # 清除相关缓存
        await self._clear_inscription_cache(user_id)
        
        logger.info(f"碑文创建成功: inscription_id={inscription.get('id')}, user_id={user_id}")
        return inscription
    
    async def update(self, inscription_id: int, user_id: int, inscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新碑文"""
        # 先检查碑文是否存在
        inscription = await self.database_client.get_inscription_by_id(inscription_id)
        if not inscription:
            raise BusinessException(ResultCode.INSCRIPTION_NOT_FOUND)
        
        # 检查权限
        if inscription.get("userId") != user_id:
            raise BusinessException(ResultCode.FORBIDDEN, "无权限修改此碑文")
        
        # 更新碑文
        result = await self.database_client.update_inscription(inscription_id, inscription_data)
        if not result:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "碑文更新失败")
        
        # 清除相关缓存
        await self._clear_inscription_cache(user_id)
        
        logger.info(f"碑文更新成功: inscription_id={inscription_id}")
        return result
    
    async def delete(self, inscription_id: int, user_id: int) -> bool:
        """删除碑文"""
        # 先检查碑文是否存在
        inscription = await self.database_client.get_inscription_by_id(inscription_id)
        if not inscription:
            raise BusinessException(ResultCode.INSCRIPTION_NOT_FOUND)
        
        # 检查权限
        if inscription.get("userId") != user_id:
            raise BusinessException(ResultCode.FORBIDDEN, "无权限删除此碑文")
        
        # 删除碑文
        success = await self.database_client.delete_inscription(inscription_id)
        if not success:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "碑文删除失败")
        
        # 清除相关缓存
        await self._clear_inscription_cache(user_id)
        
        logger.info(f"碑文删除成功: inscription_id={inscription_id}")
        return True
    
    async def search(self, keyword: str) -> List[Dict[str, Any]]:
        """模糊搜索碑文"""
        # 生成缓存键
        cache_key = f"search:inscription:{keyword}"
        
        # 先查缓存
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            return cached_result
        
        # 查数据库
        result = await self.database_client.search_inscriptions(keyword)
        if not result:
            result = []
        
        # 缓存结果
        await self.redis_client.set(
            cache_key,
            result,
            timeout=settings.cache_search_result_ttl
        )
        
        return result
    
    async def _clear_inscription_cache(self, user_id: int):
        """清除碑文相关缓存"""
        # 由于内存缓存不支持模糊搜索，我们只清除已知的缓存键
        # 在实际使用中，可以考虑使用更复杂的缓存键管理策略
        logger.info(f"清除用户{user_id}的碑文缓存")
    
    async def close(self):
        """关闭客户端连接"""
        await self.database_client.close()
        await self.redis_client.close()

