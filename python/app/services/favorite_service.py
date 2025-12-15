from typing import List, Optional, Dict, Any
from app.client.database_client import DatabaseClient
from app.utils.logger import logger

class FavoriteService:
    """收藏服务 (基于 MySQL)"""
    
    def __init__(self):
        self.database_client = DatabaseClient()
        
    async def add_favorite(self, user_id: int, item_id: int, object_type: str = 'inscription') -> bool:
        """添加收藏"""
        try:
            # 检查是否已经收藏
            if await self.is_favorite(user_id, item_id):
                logger.info(f"User {user_id} already favorited item {item_id}")
                return True
            
            # 添加收藏
            query = "INSERT INTO favorites (user_id, object_type, object_id) VALUES (%s, %s, %s)"
            await self.database_client.execute_update(query, (user_id, object_type, item_id))
            logger.info(f"User {user_id} favorited item {item_id} ({object_type})")
            return True
        except Exception as e:
            logger.error(f"Failed to add favorite: {e}")
            return False
        
    async def remove_favorite(self, user_id: int, item_id: int, object_type: str = 'inscription') -> bool:
        """移除收藏"""
        try:
            # 移除收藏
            query = "DELETE FROM favorites WHERE user_id = %s AND object_type = %s AND object_id = %s"
            await self.database_client.execute_update(query, (user_id, object_type, item_id))
            logger.info(f"User {user_id} unfavorited item {item_id} ({object_type})")
            return True
        except Exception as e:
            logger.error(f"Failed to remove favorite: {e}")
            return False
        
    async def get_favorites(self, user_id: int, object_type: Optional[str] = None) -> List[int]:
        """获取收藏列表"""
        try:
            # 构建查询条件
            where_clause = "WHERE user_id = %s"
            params = [user_id]
            
            if object_type:
                where_clause += " AND object_type = %s"
                params.append(object_type)
            
            # 查询收藏列表
            query = f"SELECT object_id FROM favorites {where_clause} ORDER BY created_at DESC"
            results = await self.database_client.execute_query(query, tuple(params))
            
            # 提取object_id列表
            favorite_ids = [int(row['object_id']) for row in results]
            logger.info(f"User {user_id} favorites: {favorite_ids}")
            return favorite_ids
        except Exception as e:
            logger.error(f"Failed to get favorites: {e}")
            return []
        
    async def is_favorite(self, user_id: int, item_id: int, object_type: str = 'inscription') -> bool:
        """检查是否已收藏"""
        try:
            # 查询收藏状态
            query = "SELECT id FROM favorites WHERE user_id = %s AND object_type = %s AND object_id = %s LIMIT 1"
            result = await self.database_client.execute_query(query, (user_id, object_type, item_id))
            
            is_favorited = len(result) > 0
            logger.info(f"User {user_id} favorite status for item {item_id}: {is_favorited}")
            return is_favorited
        except Exception as e:
            logger.error(f"Failed to check favorite status: {e}")
            return False

    async def close(self):
        await self.database_client.close()