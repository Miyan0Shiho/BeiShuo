"""
MySQL数据库客户端 - 直接连接MySQL数据库

功能：
- 提供异步MySQL数据库连接池
- 支持SQL查询、插入、更新、删除操作
- 自动连接管理和错误处理
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List

import aiomysql
from app.config import settings

logger = logging.getLogger(__name__)


class MySQLClient:
    """MySQL数据库客户端类"""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self):
        """创建数据库连接池"""
        try:
            self.pool = await aiomysql.create_pool(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                db=settings.mysql_database,
                minsize=1,
                maxsize=settings.mysql_pool_size,
                autocommit=True,
                echo=False
            )
            logger.info("MySQL连接池创建成功")
        except Exception as e:
            logger.error(f"MySQL连接池创建失败: {e}")
            raise
    
    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("MySQL连接池已关闭")
    
    async def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        执行查询操作
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(query, params)
                    result = await cursor.fetchall()
                    logger.debug(f"查询执行成功: {query[:100]}...")
                    return result
                except Exception as e:
                    logger.error(f"查询执行失败: {e}, SQL: {query}")
                    raise
    
    async def execute_insert(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> int:
        """
        执行插入操作
        
        Args:
            query: SQL插入语句
            params: 插入参数
            
        Returns:
            插入记录的主键ID
        """
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(query, params)
                    last_id = cursor.lastrowid
                    logger.debug(f"插入执行成功: {query[:100]}..., ID: {last_id}")
                    return last_id
                except Exception as e:
                    logger.error(f"插入执行失败: {e}, SQL: {query}")
                    raise
    
    async def execute_update(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> int:
        """
        执行更新操作
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            影响的行数
        """
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(query, params)
                    affected_rows = cursor.rowcount
                    logger.debug(f"更新执行成功: {query[:100]}..., 影响行数: {affected_rows}")
                    return affected_rows
                except Exception as e:
                    logger.error(f"更新执行失败: {e}, SQL: {query}")
                    raise
    
    async def execute_delete(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> int:
        """
        执行删除操作
        
        Args:
            query: SQL删除语句
            params: 删除参数
            
        Returns:
            影响的行数
        """
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(query, params)
                    affected_rows = cursor.rowcount
                    logger.debug(f"删除执行成功: {query[:100]}..., 影响行数: {affected_rows}")
                    return affected_rows
                except Exception as e:
                    logger.error(f"删除执行失败: {e}, SQL: {query}")
                    raise
    
    async def execute_transaction(
        self, 
        queries: List[tuple], 
        params_list: List[tuple]
    ) -> bool:
        """
        执行事务操作
        
        Args:
            queries: SQL语句列表
            params_list: 参数列表
            
        Returns:
            事务是否成功
        """
        if not self.pool:
            await self.connect()
        
        if len(queries) != len(params_list):
            raise ValueError("查询语句和参数列表长度不一致")
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await conn.begin()
                    
                    for i, (query, params) in enumerate(zip(queries, params_list)):
                        await cursor.execute(query, params)
                    
                    await conn.commit()
                    logger.info("事务执行成功")
                    return True
                    
                except Exception as e:
                    await conn.rollback()
                    logger.error(f"事务执行失败: {e}")
                    return False
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            result = await self.execute_query("SELECT 1 as health")
            return len(result) > 0 and result[0].get('health') == 1
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    async def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构信息"""
        try:
            query = "DESCRIBE {}".format(table_name)
            return await self.execute_query(query)
        except Exception as e:
            logger.error(f"获取表结构失败: {e}")
            return []
    
    async def get_table_count(self, table_name: str) -> int:
        """获取表记录数"""
        try:
            query = "SELECT COUNT(*) as count FROM {}".format(table_name)
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"获取表记录数失败: {e}")
            return 0


# 全局MySQL客户端实例
mysql_client = MySQLClient()


async def init_mysql():
    """初始化MySQL连接"""
    await mysql_client.connect()


async def close_mysql():
    """关闭MySQL连接"""
    await mysql_client.close()