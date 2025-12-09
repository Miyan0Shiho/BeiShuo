from typing import Optional, Dict, Any, List
from app.client.database_client import DatabaseClient
from app.client.redis_client import RedisClient
from app.client.oss_client import oss_client
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.config import settings
from app.utils.logger import logger

class InscriptionService:
    """碑文服务"""
    
    def __init__(self):
        self.database_client = DatabaseClient()
        self.redis_client = RedisClient()
    
    def _convert_oss_url(self, url_or_path: Optional[str]) -> Optional[str]:
        """将OSS路径转换为可访问的URL"""
        if not url_or_path:
            return None
        
        # 如果已经是完整URL，直接返回
        if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
            return url_or_path
        
        # 如果是OSS路径，转换为URL
        object_name = url_or_path.lstrip('/')
        # 移除bucket名称前缀（如果存在）
        if object_name.startswith('beiwen1/'):
            object_name = object_name[8:]
        
        try:
            return oss_client.get_file_url(object_name)
        except Exception:
            # 如果OSS转换失败，尝试构建基础URL
            return f"https://{settings.aliyun_oss_domain}/{object_name}"
    
    def _format_inscription(self, inscription: Dict[str, Any]) -> Dict[str, Any]:
        """格式化碑文数据，确保字段名为下划线格式"""
        if not inscription:
            return {}
        
        formatted = {
            "id": inscription.get("id"),
            "title": inscription.get("title", ""),
            "location": inscription.get("location"),
            "dynasty": inscription.get("dynasty"),
            "year": inscription.get("year"),
            "description": inscription.get("description"),
            "style": inscription.get("style"),
            "material": inscription.get("material"),
            "size": inscription.get("size"),
            "cover_image_url": self._convert_oss_url(inscription.get("cover_image_url")),
            "creator_user_id": inscription.get("creator_user_id"),
            "status": inscription.get("status"),
            "views": inscription.get("views", 0),
            "protection_level": inscription.get("protection_level"),
            "discovery_date": inscription.get("discovery_date"),
            "current_location": inscription.get("current_location"),
            "current_location_lat": inscription.get("current_location_lat"),
            "current_location_lng": inscription.get("current_location_lng"),
            "created_at": inscription.get("created_at"),
            "updated_at": inscription.get("updated_at"),
        }
        
        return formatted
    
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
        
        # 格式化数据，确保字段名为下划线格式
        items = result.get("items", [])
        formatted_items = [self._format_inscription(item) for item in items]
        
        total = result.get("total", 0)
        total_pages = (total + size - 1) // size if size > 0 else 0
        
        formatted_result = {
            "list": formatted_items,
            "total": total,
            "page": page,
            "size": size,
            "totalPages": total_pages
        }
        
        # 缓存结果
        await self.redis_client.set(
            cache_key,
            formatted_result,
            timeout=settings.cache_inscription_list_ttl
        )
        
        return formatted_result
    
    async def get_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取碑文详情"""
        inscription = await self.database_client.get_inscription_by_id(inscription_id)
        if inscription:
            return self._format_inscription(inscription)
        return None
    
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
        
        # 格式化数据
        formatted_result = [self._format_inscription(item) for item in result]
        
        # 缓存结果
        await self.redis_client.set(
            cache_key,
            formatted_result,
            timeout=settings.cache_search_result_ttl
        )
        
        return formatted_result
    
    async def _clear_inscription_cache(self, user_id: int):
        """清除碑文相关缓存"""
        pattern = f"inscription:list:{user_id}:*"
        keys = await self.redis_client.search_keys(pattern)
        for key in keys:
            await self.redis_client.delete(key)
        
        # 清除搜索缓存
        pattern = "search:inscription:*"
        keys = await self.redis_client.search_keys(pattern)
        for key in keys:
            await self.redis_client.delete(key)
    
    async def close(self):
        """关闭客户端连接"""
        await self.database_client.close()
        await self.redis_client.close()

