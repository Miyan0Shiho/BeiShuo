from typing import Optional, Dict, Any, List
from app.client.database_client import DatabaseClient
from app.client.redis_client import RedisClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.config import settings

class KnowledgeService:
    """知识库服务"""
    
    def __init__(self):
        self.database_client = DatabaseClient()
        self.redis_client = RedisClient()
    
    async def get_list(
        self,
        page: int = 0,
        size: int = 10,
        keyword: Optional[str] = None,
        dynasty: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取知识库列表"""
        # 生成缓存键
        cache_key = f"knowledge:list:{page}:{size}:{keyword or ''}:{dynasty or ''}:{category or ''}"
        
        # 先查缓存
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            return cached_result
        
        # 查数据库
        result = await self.database_client.get_knowledge_list(
            page=page,
            size=size,
            keyword=keyword,
            dynasty=dynasty,
            category=category
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
            timeout=settings.cache_knowledge_list_ttl
        )
        
        return result
    
    async def get_by_id(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取知识库详情"""
        knowledge = await self.database_client.get_knowledge_by_id(knowledge_id)
        if not knowledge:
            raise BusinessException(ResultCode.KNOWLEDGE_NOT_FOUND)
        return knowledge
    
    async def search(
        self,
        keyword: str,
        dynasty: Optional[str] = None,
        tags: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索知识库"""
        # 生成缓存键
        cache_key = f"search:knowledge:{keyword}:{dynasty or ''}:{tags or ''}"
        
        # 先查缓存
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            return cached_result
        
        # 查数据库
        result = await self.database_client.search_knowledge(keyword, dynasty, tags)
        if not result:
            result = []
        
        # 缓存结果
        await self.redis_client.set(
            cache_key,
            result,
            timeout=settings.cache_search_result_ttl
        )
        
        return result
    
    async def close(self):
        """关闭客户端连接"""
        await self.database_client.close()
        await self.redis_client.close()

