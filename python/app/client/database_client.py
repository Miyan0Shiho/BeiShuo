import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import aiomysql
from app.config import settings
from app.client.mysql_client import MySQLClient

logger = logging.getLogger(__name__)


class DatabaseClient:
    """
    数据库客户端 - 仅处理MySQL数据库操作
    
    This client provides database operations for the application.
    It uses a connection pool for efficient database access.
    """
    
    def __init__(self):
        self.pool = None
        self.is_connected = False
    
    async def connect(self):
        """连接到MySQL数据库"""
        if self.is_connected and self.pool:
            return
        
        try:
            self.pool = await aiomysql.create_pool(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                db=settings.mysql_database,
                minsize=1,
                maxsize=settings.mysql_pool_size,
                autocommit=True
            )
            self.is_connected = True
            logger.info("MySQL数据库连接成功")
        except Exception as e:
            logger.error(f"MySQL数据库连接失败: {e}")
            raise
    
    async def _execute_query(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """执行查询并返回单条记录"""
        await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                result = await cur.fetchone()
                if result:
                    # 转换datetime字段为字符串
                    for key, value in result.items():
                        if hasattr(value, 'isoformat'):  # 检查是否为datetime对象
                            result[key] = value.isoformat()
                return result
    
    async def _execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        """执行插入操作并返回插入ID"""
        await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                last_id = cur.lastrowid
                return last_id
    
    async def _execute_update(self, query: str, params: tuple = None) -> bool:
        """执行更新操作"""
        await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur.rowcount > 0
    
    async def _execute_query_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回多条记录"""
        await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                result = await cur.fetchall()
                return result

    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            self.is_connected = False
            logger.info("MySQL数据库连接池已关闭")
    
    # ========== 用户相关 ==========
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱查询用户"""
        query = "SELECT * FROM users WHERE email = %s"
        params = (email,)
        
        try:
            return await self._execute_query(query, params)
        except Exception as e:
            logger.error(f"根据邮箱查询用户失败: {e}")
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询用户"""
        query = "SELECT * FROM users WHERE id = %s"
        params = (user_id,)
        
        try:
            return await self._execute_query(query, params)
        except Exception as e:
            logger.error(f"根据ID查询用户失败: {e}")
            return None

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建用户"""
        query = """
            INSERT INTO users (name, email, password_hash, role, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        params = (
            user_data.get("username"),  # 前端传username，数据库存为name
            user_data.get("email"),
            user_data.get("password_hash"),
            user_data.get("role", "user")
        )
        
        try:
            user_id = await self._execute_insert(query, params)
            if user_id:
                return await self.get_user_by_id(user_id)
            return None
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        set_clauses = []
        params = []
        
        for field, value in user_data.items():
            if field == 'username':
                # 前端传username，数据库字段为name
                set_clauses.append("name = %s")
                params.append(value)
            elif field in ['email', 'password_hash', 'role']:
                set_clauses.append(f"{field} = %s")
                params.append(value)
       
        if not set_clauses:
            return None
            
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(set_clauses)}, updated_at = NOW() WHERE id = %s"
        
        try:
            success = await self._execute_update(query, tuple(params))
            if success:
                return await self.get_user_by_id(user_id)
            return None
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return None

    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        query = "DELETE FROM users WHERE id = %s"
        params = (user_id,)
        
        try:
            return await self._execute_update(query, params)
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False
    
    # ========== 碑文相关 ==========
    
    async def get_inscription_list(
        self,
        user_id: int,
        page: int = 0,
        size: int = 10,
        sort: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """查询碑文列表 - 从数据库直接查询"""
        try:
            offset = page * size
            query = """
                SELECT * FROM inscriptions 
                WHERE creator_user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params = (user_id, size, offset)
            return await self._execute_query_all(query, params)
        except Exception as e:
            logger.error(f"查询碑文列表失败: {e}")
            return []
    
    async def get_inscription_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询碑文详情"""
        try:
            query = "SELECT * FROM inscriptions WHERE id = %s"
            params = (inscription_id,)
            return await self._execute_query(query, params)
        except Exception as e:
            logger.error(f"查询碑文详情失败: {e}")
            return None
    
    async def create_inscription(self, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建碑文记录"""
        try:
            query = """
                INSERT INTO inscriptions (creator_user_id, title, dynasty, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """
            params = (
                inscription_data.get("user_id"),
                inscription_data.get("title"),
                inscription_data.get("dynasty")
            )
            inscription_id = await self._execute_insert(query, params)
            if inscription_id:
                return await self.get_inscription_by_id(inscription_id)
            return None
        except Exception as e:
            logger.error(f"创建碑文失败: {e}")
            return None
    
    async def update_inscription(self, inscription_id: int, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新碑文"""
        try:
            set_clauses = []
            params = []
            
            for field, value in inscription_data.items():
                if field in ['title', 'content', 'dynasty', 'category']:
                    set_clauses.append(f"{field} = %s")
                    params.append(value)
            
            if not set_clauses:
                return None
                
            params.append(inscription_id)
            query = f"UPDATE inscriptions SET {', '.join(set_clauses)}, updated_at = NOW() WHERE id = %s"
            
            success = await self._execute_update(query, tuple(params))
            if success:
                return await self.get_inscription_by_id(inscription_id)
            return None
        except Exception as e:
            logger.error(f"更新碑文失败: {e}")
            return None
    
    async def delete_inscription(self, inscription_id: int) -> bool:
        """删除碑文"""
        try:
            query = "DELETE FROM inscriptions WHERE id = %s"
            params = (inscription_id,)
            return await self._execute_update(query, params)
        except Exception as e:
            logger.error(f"删除碑文失败: {e}")
            return False
    
    async def search_inscriptions(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """模糊搜索碑文"""
        try:
            query = """
                SELECT * FROM inscriptions 
                WHERE title LIKE %s OR content LIKE %s
                ORDER BY created_at DESC
            """
            search_pattern = f"%{keyword}%"
            params = (search_pattern, search_pattern)
            return await self._execute_query_all(query, params)
        except Exception as e:
            logger.error(f"搜索碑文失败: {e}")
            return []

