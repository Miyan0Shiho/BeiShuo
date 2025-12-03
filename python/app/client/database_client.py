from typing import Optional, Dict, Any, List
from app.client.base_client import BaseHTTPClient
from app.config import settings

class DatabaseClient(BaseHTTPClient):
    """数据库服务客户端"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.database_api_base_url,
            connect_timeout=settings.database_api_connect_timeout,
            read_timeout=settings.database_api_read_timeout,
            retry_times=settings.database_api_retry_times
        )
    
    # ========== 用户相关 ==========
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱查询用户"""
        return await self.get(f"/user/email/{email}")
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询用户"""
        return await self.get(f"/user/{user_id}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建用户"""
        return await self.post("/user", json=user_data)
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        return await self.put(f"/user/{user_id}", json=user_data)
    
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
        params = {
            "userId": user_id,
            "page": page,
            "size": size
        }
        if sort:
            params["sort"] = sort
        if keyword:
            params["keyword"] = keyword
        
        return await self.get("/inscription/list", params=params)
    
    async def get_inscription_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询碑文详情"""
        return await self.get(f"/inscription/{inscription_id}")
    
    async def create_inscription(self, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建碑文记录"""
        return await self.post("/inscription", json=inscription_data)
    
    async def update_inscription(self, inscription_id: int, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新碑文"""
        return await self.put(f"/inscription/{inscription_id}", json=inscription_data)
    
    async def delete_inscription(self, inscription_id: int) -> bool:
        """删除碑文"""
        return await self.delete(f"/inscription/{inscription_id}")
    
    async def search_inscriptions(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """模糊搜索碑文"""
        result = await self.get("/inscription/search", params={"keyword": keyword})
        if isinstance(result, list):
            return result
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
        params = {"page": page, "size": size}
        if keyword:
            params["keyword"] = keyword
        if dynasty:
            params["dynasty"] = dynasty
        if category:
            params["category"] = category
        
        return await self.get("/knowledge/list", params=params)
    
    async def get_knowledge_by_id(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询知识库详情"""
        return await self.get(f"/knowledge/{knowledge_id}")
    
    async def search_knowledge(
        self,
        keyword: str,
        dynasty: Optional[str] = None,
        tags: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """搜索知识库"""
        params = {"keyword": keyword}
        if dynasty:
            params["dynasty"] = dynasty
        if tags:
            params["tags"] = tags
        
        result = await self.get("/knowledge/search", params=params)
        if isinstance(result, list):
            return result
        return []
    
    # ========== 收藏相关 ==========
    
    async def add_favorite(self, user_id: int, favorite_type: str, target_id: int) -> bool:
        """添加收藏"""
        data = {
            "userId": user_id,
            "type": favorite_type,
            "targetId": target_id
        }
        result = await self.post("/favorite", json=data)
        return result is not None
    
    async def remove_favorite(self, user_id: int, favorite_type: str, target_id: int) -> bool:
        """取消收藏"""
        params = {
            "userId": user_id,
            "type": favorite_type,
            "targetId": target_id
        }
        return await self.delete("/favorite", params=params)
    
    async def get_favorite_list(self, user_id: int, favorite_type: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """查询收藏列表"""
        params = {"userId": user_id}
        if favorite_type:
            params["type"] = favorite_type
        
        result = await self.get("/favorite/list", params=params)
        if isinstance(result, list):
            return result
        return []
    
    # ========== 对话相关 ==========
    
    async def create_conversation(self, user_id: int, conversation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建对话"""
        data = {
            "userId": user_id,
            **conversation_data
        }
        return await self.post("/conversation", json=data)
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取对话"""
        return await self.get(f"/conversation/{conversation_id}")
    
    async def add_message(self, conversation_id: str, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """添加对话消息"""
        data = {
            "conversationId": conversation_id,
            **message_data
        }
        return await self.post("/message", json=data)
    
    async def get_messages(self, conversation_id: str, page: int = 0, size: int = 20, order: str = "asc") -> Optional[List[Dict[str, Any]]]:
        """获取对话消息列表"""
        params = {
            "conversationId": conversation_id,
            "page": page,
            "size": size,
            "order": order
        }
        result = await self.get("/message/list", params=params)
        if isinstance(result, list):
            return result
        return []
    
    async def update_message_status(self, message_id: str, status: str) -> bool:
        """更新对话消息状态"""
        data = {"status": status}
        result = await self.put(f"/message/{message_id}/status", json=data)
        return result is not None
    
    async def reset_conversation(self, conversation_id: str) -> bool:
        """重置对话上下文"""
        return await self.delete(f"/conversation/{conversation_id}/messages")
    
    # ========== OCR相关 ==========
    
    async def get_ocr_result_by_image_hash(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """根据图片哈希值获取OCR结果"""
        result = await self.get(f"/ocr/result/hash/{image_hash}")
        # 检查success字段，只有当success为true时才返回OCR结果，否则返回None
        if result and isinstance(result, dict) and result.get("success", False):
            return result
        return None
    
    async def create_ocr_job(self, ocr_job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建OCR任务"""
        return await self.post("/ocr/job", json=ocr_job_data)
    
    async def save_ocr_result(self, task_id: str, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """保存OCR识别结果"""
        return await self.post(f"/ocr/result/{task_id}", json=result_data)
    
    async def delete_ocr_cache(self, image_hash: str) -> bool:
        """删除OCR缓存"""
        result = await self.delete(f"/ocr/result/hash/{image_hash}")
        return result is not None
    
    # ========== LLM缓存相关 ==========
    
    async def get_llm_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取LLM响应缓存"""
        return await self.get(f"/llm/cache/{cache_key}")
    
    async def set_llm_cache(self, cache_key: str, cache_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """设置LLM响应缓存"""
        data = {
            "cacheKey": cache_key,
            "cacheData": cache_data,
            "ttl": ttl
        }
        result = await self.post("/llm/cache", json=data)
        return result is not None

