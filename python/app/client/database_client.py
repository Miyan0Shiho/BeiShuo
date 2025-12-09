from typing import Optional, Dict, Any, List
from app.client.mysql_client import mysql_client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseClient:
    """数据库服务客户端，现在使用直接连接MySQL的方式"""
    
    def __init__(self):
        """初始化数据库客户端，使用MySQLClient"""
        self.client = mysql_client
        logger.info("DatabaseClient initialized with MySQLClient")
    
    async def close(self):
        """关闭数据库连接，这里实际上是调用mysql_client的disconnect方法"""
        logger.debug("DatabaseClient.close() called")
        # 这里不需要实际断开连接，因为连接是在应用生命周期管理中统一处理的
        pass
    
    # ========== 用户相关 ==========
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱查询用户"""
        logger.debug(f"DatabaseClient.get_user_by_email: email={email}")
        result = await self.client.get_user_by_email(email)
        logger.debug(f"DatabaseClient.get_user_by_email result: {result}")
        return result
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询用户"""
        logger.debug(f"DatabaseClient.get_user_by_id: user_id={user_id}")
        result = await self.client.get_user_by_id(user_id)
        logger.debug(f"DatabaseClient.get_user_by_id result: {result}")
        return result
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建用户"""
        logger.debug(f"DatabaseClient.create_user: user_data={user_data}")
        result = await self.client.create_user(user_data)
        logger.debug(f"DatabaseClient.create_user result: {result}")
        return result
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        logger.debug(f"DatabaseClient.update_user: user_id={user_id}, user_data={user_data}")
        # 暂时使用模拟实现
        return None
    
    # ========== 碑文相关 ==========
    
    async def get_inscription_list(
        self,
        user_id: int,
        page: int = 0,
        size: int = 10,
        sort: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """查询碑文列表"""
        logger.debug(f"DatabaseClient.get_inscription_list: user_id={user_id}, page={page}, size={size}, sort={sort}, keyword={keyword}")
        result = await self.client.get_inscription_list(user_id, page, size, sort, keyword)
        logger.debug(f"DatabaseClient.get_inscription_list result: {result}")
        return result
    
    async def get_inscription_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询碑文详情"""
        logger.debug(f"DatabaseClient.get_inscription_by_id: inscription_id={inscription_id}")
        result = await self.client.get_inscription_by_id(inscription_id)
        logger.debug(f"DatabaseClient.get_inscription_by_id result: {result}")
        return result
    
    async def create_inscription(self, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建碑文记录"""
        logger.debug(f"DatabaseClient.create_inscription: inscription_data={inscription_data}")
        result = await self.client.create_inscription(inscription_data)
        logger.debug(f"DatabaseClient.create_inscription result: {result}")
        return result
    
    async def update_inscription(self, inscription_id: int, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新碑文"""
        logger.debug(f"DatabaseClient.update_inscription: inscription_id={inscription_id}, inscription_data={inscription_data}")
        # 暂时使用模拟实现
        return None
    
    async def delete_inscription(self, inscription_id: int) -> bool:
        """删除碑文"""
        logger.debug(f"DatabaseClient.delete_inscription: inscription_id={inscription_id}")
        # 暂时使用模拟实现
        return True
    
    async def search_inscriptions(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """模糊搜索碑文"""
        logger.debug(f"DatabaseClient.search_inscriptions: keyword={keyword}")
        # 暂时使用模拟实现
        return []
    
    # ========== 知识库相关 ==========
    
    async def get_knowledge_list(
        self,
        page: int = 0,
        size: int = 10,
        keyword: Optional[str] = None,
        dynasty: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """查询知识库列表"""
        logger.debug(f"DatabaseClient.get_knowledge_list: page={page}, size={size}, keyword={keyword}, dynasty={dynasty}, category={category}")
        result = await self.client.get_knowledge_list(page, size, keyword, dynasty, category)
        logger.debug(f"DatabaseClient.get_knowledge_list result: {result}")
        return result
    
    async def get_knowledge_by_id(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询知识库详情"""
        logger.debug(f"DatabaseClient.get_knowledge_by_id: knowledge_id={knowledge_id}")
        result = await self.client.get_knowledge_by_id(knowledge_id)
        logger.debug(f"DatabaseClient.get_knowledge_by_id result: {result}")
        return result
    
    async def search_knowledge(
        self,
        keyword: str,
        dynasty: Optional[str] = None,
        tags: Optional[str] = None,
        page: int = 0,
        size: int = 20
    ) -> Optional[Dict[str, Any]]:
        """搜索知识库"""
        logger.debug(f"DatabaseClient.search_knowledge: keyword={keyword}, dynasty={dynasty}, tags={tags}, page={page}, size={size}")
        result = await self.client.search_knowledge(keyword, dynasty, tags, page, size)
        logger.debug(f"DatabaseClient.search_knowledge result: {result}")
        return result
    
    async def get_knowledge_tags(self, article_id: int) -> List[Dict[str, Any]]:
        """获取文章标签"""
        logger.debug(f"DatabaseClient.get_knowledge_tags: article_id={article_id}")
        result = await self.client.get_knowledge_tags(article_id)
        logger.debug(f"DatabaseClient.get_knowledge_tags result: {result}")
        return result
    
    async def get_knowledge_categories(self) -> List[Dict[str, Any]]:
        """获取知识库分类列表"""
        logger.debug("DatabaseClient.get_knowledge_categories")
        result = await self.client.get_knowledge_categories()
        logger.debug(f"DatabaseClient.get_knowledge_categories result: {result}")
        return result
    
    async def get_knowledge_dynasties(self) -> List[Dict[str, Any]]:
        """获取知识库朝代列表"""
        logger.debug("DatabaseClient.get_knowledge_dynasties")
        result = await self.client.get_knowledge_dynasties()
        logger.debug(f"DatabaseClient.get_knowledge_dynasties result: {result}")
        return result
    
    async def execute_query(self, query: str, args: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询语句"""
        logger.debug(f"DatabaseClient.execute_query: query={query}, args={args}")
        result = await self.client.execute_query(query, args)
        logger.debug(f"DatabaseClient.execute_query result: {result}")
        return result
    
    async def execute_update(self, query: str, args: Optional[tuple] = None) -> int:
        """执行更新语句"""
        logger.debug(f"DatabaseClient.execute_update: query={query}, args={args}")
        result = await self.client.execute_update(query, args)
        logger.debug(f"DatabaseClient.execute_update result: {result}")
        return result
    
    async def increment_knowledge_views(self, article_id: int) -> int:
        """增加文章查看次数"""
        logger.debug(f"DatabaseClient.increment_knowledge_views: article_id={article_id}")
        result = await self.client.increment_knowledge_views(article_id)
        logger.debug(f"DatabaseClient.increment_knowledge_views result: {result}")
        return result
    
    # ========== 收藏相关 ==========
    
    async def add_favorite(self, user_id: int, favorite_type: str, target_id: int) -> bool:
        """添加收藏"""
        logger.debug(f"DatabaseClient.add_favorite: user_id={user_id}, favorite_type={favorite_type}, target_id={target_id}")
        # 暂时使用模拟实现
        return True
    
    async def remove_favorite(self, user_id: int, favorite_type: str, target_id: int) -> bool:
        """取消收藏"""
        logger.debug(f"DatabaseClient.remove_favorite: user_id={user_id}, favorite_type={favorite_type}, target_id={target_id}")
        # 暂时使用模拟实现
        return True
    
    async def get_favorite_list(self, user_id: int, favorite_type: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """查询收藏列表"""
        logger.debug(f"DatabaseClient.get_favorite_list: user_id={user_id}, favorite_type={favorite_type}")
        # 暂时使用模拟实现
        return []
    
    # ========== 对话相关 ==========
    
    async def create_conversation(self, user_id: int, conversation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建对话"""
        logger.debug(f"DatabaseClient.create_conversation: user_id={user_id}, conversation_data={conversation_data}")
        result = await self.client.create_conversation(user_id, conversation_data)
        logger.debug(f"DatabaseClient.create_conversation result: {result}")
        return result
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取对话"""
        logger.debug(f"DatabaseClient.get_conversation_by_id: conversation_id={conversation_id}")
        # 暂时使用模拟实现
        return None
    
    async def add_message(self, conversation_id: str, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """添加对话消息"""
        logger.debug(f"DatabaseClient.add_message: conversation_id={conversation_id}, message_data={message_data}")
        # 暂时使用模拟实现
        return None
    
    async def get_messages(self, conversation_id: str, page: int = 0, size: int = 20, order: str = "asc") -> Optional[List[Dict[str, Any]]]:
        """获取对话消息列表"""
        logger.debug(f"DatabaseClient.get_messages: conversation_id={conversation_id}, page={page}, size={size}, order={order}")
        # 暂时使用模拟实现
        return []
    
    async def update_message_status(self, message_id: str, status: str) -> bool:
        """更新对话消息状态"""
        logger.debug(f"DatabaseClient.update_message_status: message_id={message_id}, status={status}")
        # 暂时使用模拟实现
        return True
    
    async def reset_conversation(self, conversation_id: str) -> bool:
        """重置对话上下文"""
        logger.debug(f"DatabaseClient.reset_conversation: conversation_id={conversation_id}")
        # 暂时使用模拟实现
        return True
    
    # ========== OCR相关 ==========
    
    async def get_ocr_result_by_image_hash(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """根据图片哈希值获取OCR结果"""
        logger.debug(f"DatabaseClient.get_ocr_result_by_image_hash: image_hash={image_hash}")
        result = await self.client.get_ocr_result_by_image_hash(image_hash)
        logger.debug(f"DatabaseClient.get_ocr_result_by_image_hash result: {result}")
        return result
    
    async def create_ocr_job(self, ocr_job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建OCR任务"""
        logger.debug(f"DatabaseClient.create_ocr_job: ocr_job_data={ocr_job_data}")
        result = await self.client.create_ocr_job(ocr_job_data)
        logger.debug(f"DatabaseClient.create_ocr_job result: {result}")
        return result
    
    async def save_ocr_result(self, task_id: str, result_data: Dict[str, Any], image_hash: str = None, content: bytes = None) -> Optional[Dict[str, Any]]:
        """保存OCR识别结果"""
        logger.debug(f"DatabaseClient.save_ocr_result: task_id={task_id}, result_data={result_data}, image_hash={image_hash}")
        result = await self.client.save_ocr_result(task_id, result_data, image_hash, content)
        logger.debug(f"DatabaseClient.save_ocr_result result: {result}")
        return result
    
    async def delete_ocr_cache(self, image_hash: str) -> bool:
        """删除OCR缓存"""
        logger.debug(f"DatabaseClient.delete_ocr_cache: image_hash={image_hash}")
        # 暂时使用模拟实现
        return True
    
    # ========== LLM缓存相关 ==========
    
    async def get_llm_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取LLM响应缓存"""
        logger.debug(f"DatabaseClient.get_llm_cache: cache_key={cache_key}")
        result = await self.client.get_llm_cache(cache_key)
        logger.debug(f"DatabaseClient.get_llm_cache result: {result}")
        return result
    
    async def set_llm_cache(self, cache_key: str, cache_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """设置LLM响应缓存"""
        logger.debug(f"DatabaseClient.set_llm_cache: cache_key={cache_key}, cache_data={cache_data}, ttl={ttl}")
        result = await self.client.set_llm_cache(cache_key, cache_data, ttl)
        logger.debug(f"DatabaseClient.set_llm_cache result: {result}")
        return result

