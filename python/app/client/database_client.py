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
        self._db_last_error_time = 0
        self._db_circuit_break_duration = 30  # 熔断时间30秒

    def _is_db_available(self):
        import time
        if time.time() - self._db_last_error_time < self._db_circuit_break_duration:
            return False
        return True

    def _mark_db_failed(self):
        import time
        self._db_last_error_time = time.time()
        logger.warning(f"Database marked as failed, circuit break for {self._db_circuit_break_duration}s")

    
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
        
        db_items = []
        db_total = 0
        
        try:
            if self._is_db_available():
                try:
                    result = await self.client.get_inscription_list(user_id, page, size, sort, keyword)
                    logger.debug(f"DatabaseClient.get_inscription_list result: {result}")
                    if result and "items" in result:
                        db_items = result.get("items", []) or []
                        db_total = int(result.get("total", 0) or 0)
                    elif isinstance(result, dict):
                        db_items = result.get("list", []) or []
                        db_total = int(result.get("total", 0) or 0)
                except Exception as e:
                    logger.error(f"MySQL get_inscription_list failed: {e}")
                    self._mark_db_failed()
            
            # 读取本地保存的数据并置顶合并
            local_items = await self._local_list(user_id)
            if keyword:
                kw = keyword.lower()
                local_items = [it for it in local_items if kw in (it.get("title","").lower() + it.get("content","").lower())]
            
            combined = (local_items or []) + (db_items or [])
            # 分页切片
            start = page * size
            end = start + size
            page_items = combined[start:end]
            total = len(combined) if local_items else db_total
            total_pages = (total + size - 1) // size if size > 0 else 0
            
            return {
                "list": page_items,
                "total": total,
                "page": page,
                "size": size,
                "totalPages": total_pages
            }
        except Exception as e:
            logger.error(f"get_inscription_list failed completely: {e}")
            return {"list": [], "total": 0, "page": page, "size": size, "totalPages": 0}
    
    async def get_inscription_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询碑文详情"""
        logger.info(f"DatabaseClient.get_inscription_by_id: inscription_id={inscription_id}")
        
        # 优化：如果是大整数ID（时间戳），优先查本地文件
        is_local_id = False
        try:
            if int(inscription_id) > 1000000000000:  # 毫秒级时间戳是13位，10^12
                is_local_id = True
                logger.info(f"get_inscription_by_id: inscription_id={inscription_id} 是本地ID")
        except Exception as e:
            logger.error(f"get_inscription_by_id: 解析inscription_id失败: {e}")
            pass
            
        if is_local_id:
            # 尝试从本地查找
            logger.info(f"get_inscription_by_id: 优先从本地查找")
            local = await self._find_local_by_id(inscription_id)
            if local:
                logger.info(f"get_inscription_by_id: 从本地找到结果: {local}")
                return local
            logger.info(f"get_inscription_by_id: 本地查找失败，尝试数据库查找")
        
        # 尝试查数据库
        try:
            if self._is_db_available():
                logger.info(f"get_inscription_by_id: 尝试从数据库查找")
                result = await self.client.get_inscription_by_id(inscription_id)
                logger.info(f"DatabaseClient.get_inscription_by_id MySQL result: {result}")
                if result:
                    return result
        except Exception as e:
            logger.error(f"MySQL get_inscription_by_id failed: {e}")
            self._mark_db_failed()
        
        # 如果不是本地ID（即数据库ID），且数据库失败了，再尝试本地找一下（防止误判）
        if not is_local_id:
            logger.info(f"get_inscription_by_id: 数据库查找失败，再次尝试本地查找")
            return await self._find_local_by_id(inscription_id)
        
        logger.warning(f"get_inscription_by_id: 未找到inscription_id={inscription_id} 的结果")
        return None

    async def _find_local_by_id(self, inscription_id):
        """从本地存储中查找碑文"""
        logger.info(f"DatabaseClient._find_local_by_id: inscription_id={inscription_id}")
        import os, json
        uploads = settings.file_upload_path
        logger.info(f"_find_local_by_id: uploads directory={uploads}")
        if os.path.isdir(uploads):
            logger.info(f"_find_local_by_id: uploads directory exists")
            files = os.listdir(uploads)
            logger.info(f"_find_local_by_id: found {len(files)} files in uploads")
            for name in files:
                if not name.startswith("inscriptions_") or not name.endswith(".json"):
                    logger.debug(f"_find_local_by_id: skipping file {name} (not inscription JSON)")
                    continue
                logger.info(f"_find_local_by_id: processing file {name}")
                try:
                    with open(os.path.join(uploads, name), "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    logger.info(f"_find_local_by_id: loaded {len(data)} items from {name}")
                    for it in data:
                        if str(it.get("id")) == str(inscription_id):
                            logger.info(f"_find_local_by_id found: {it}")
                            return it
                except Exception as e:
                    logger.error(f"Local storage read error in _find_local_by_id: {e}")
                    continue
        else:
            logger.warning(f"_find_local_by_id: uploads directory not found")
        logger.warning(f"_find_local_by_id: no result found for inscription_id={inscription_id}")
        return None
    
    async def create_inscription(self, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建碑文记录"""
        logger.info(f"DatabaseClient.create_inscription: inscription_data={inscription_data}")
        try:
            if self._is_db_available():
                logger.info(f"create_inscription: 尝试从数据库创建碑文")
                try:
                    result = await self.client.create_inscription(inscription_data)
                    logger.info(f"DatabaseClient.create_inscription MySQL result: {result}")
                    return result
                except Exception as e:
                    logger.error(f"MySQL create_inscription failed: {e}")
                    self._mark_db_failed()
            raise Exception("Database unavailable")
        except Exception as e:
            logger.error(f"create_inscription failed, fallback to local storage: {e}")
            import os, json, time
            user_id = inscription_data.get("userId") or inscription_data.get("creator_user_id") or 0
            logger.info(f"create_inscription: 开始创建本地碑文记录，user_id={user_id}")
            item = {
                "id": int(time.time() * 1000),
                "title": inscription_data.get("title",""),
                "content": inscription_data.get("text",""),
                "dynasty": inscription_data.get("dynasty",""),
                "status": inscription_data.get("status","pending"),
                "image_url": inscription_data.get("image_url") or inscription_data.get("imageUrl",""),
                "userId": user_id,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            logger.info(f"create_inscription: 本地碑文记录内容: {item}")
            await self._local_append(user_id, item)
            logger.info(f"create_inscription: 本地碑文记录创建成功")
            return item
    
    async def update_inscription(self, inscription_id: int, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新碑文"""
        logger.debug(f"DatabaseClient.update_inscription: inscription_id={inscription_id}, inscription_data={inscription_data}")
        try:
            raise Exception("not implemented")
        except Exception:
            # 本地更新
            import os, json
            uploads = settings.file_upload_path
            if not os.path.isdir(uploads):
                return None
            for name in os.listdir(uploads):
                if not name.startswith("inscriptions_") or not name.endswith(".json"):
                    continue
                path = os.path.join(uploads, name)
                try:
                    with open(path, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    changed = False
                    target = None
                    for it in data:
                        if str(it.get("id")) == str(inscription_id):
                            for k,v in inscription_data.items():
                                if k == "corrected_text":
                                    it["content"] = v or it.get("content","")
                                else:
                                    it[k] = v
                            target = it
                            changed = True
                            break
                    if changed:
                        with open(path, "w", encoding="utf-8") as fp:
                            json.dump(data, fp, ensure_ascii=False, indent=2)
                        return target
                except Exception:
                    continue
            return None
    
    async def delete_inscription(self, inscription_id: int) -> bool:
        """删除碑文"""
        logger.debug(f"DatabaseClient.delete_inscription: inscription_id={inscription_id}")
        try:
            raise Exception("not implemented")
        except Exception:
            import os, json
            uploads = settings.file_upload_path
            if not os.path.isdir(uploads):
                return False
            for name in os.listdir(uploads):
                if not name.startswith("inscriptions_") or not name.endswith(".json"):
                    continue
                path = os.path.join(uploads, name)
                try:
                    with open(path, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    next_data = [it for it in data if str(it.get("id")) != str(inscription_id)]
                    if len(next_data) != len(data):
                        with open(path, "w", encoding="utf-8") as fp:
                            json.dump(next_data, fp, ensure_ascii=False, indent=2)
                        return True
                except Exception:
                    continue
            return False
    
    async def search_inscriptions(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """模糊搜索碑文"""
        logger.debug(f"DatabaseClient.search_inscriptions: keyword={keyword}")
        try:
            raise Exception("not implemented")
        except Exception:
            # 本地搜索
            import os, json
            uploads = settings.file_upload_path
            results: List[Dict[str, Any]] = []
            if os.path.isdir(uploads):
                for name in os.listdir(uploads):
                    if not name.startswith("inscriptions_") or not name.endswith(".json"):
                        continue
                    try:
                        with open(os.path.join(uploads, name), "r", encoding="utf-8") as fp:
                            data = json.load(fp)
                        kw = keyword.lower()
                        for it in data:
                            if kw in (it.get("title","").lower() + it.get("content","").lower()):
                                results.append(it)
                    except Exception:
                        continue
            return results
    
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

    async def _local_list(self, user_id: int) -> List[Dict[str, Any]]:
        import os, json
        uploads = settings.file_upload_path
        os.makedirs(uploads, exist_ok=True)
        path = os.path.join(uploads, f"inscriptions_{user_id or 0}.json")
        if not os.path.isfile(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except Exception:
            return []

    async def _local_append(self, user_id: int, item: Dict[str, Any]) -> None:
        import os, json
        uploads = settings.file_upload_path
        os.makedirs(uploads, exist_ok=True)
        path = os.path.join(uploads, f"inscriptions_{user_id or 0}.json")
        data: List[Dict[str, Any]] = []
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
            except Exception:
                data = []
        data.insert(0, item)
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

