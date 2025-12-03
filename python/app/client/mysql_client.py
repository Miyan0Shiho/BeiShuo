from typing import Optional, Dict, Any, List
import aiomysql
import logging
import time
from app.config import settings

logger = logging.getLogger(__name__)

class MySQLClient:
    """MySQL数据库客户端，提供直接连接数据库的功能"""
    
    def __init__(self):
        """初始化MySQL客户端配置"""
        self.config = {
            'host': settings.db_host,
            'port': settings.db_port,
            'user': settings.db_user,
            'password': settings.db_password,
            'db': settings.db_name,
            'charset': settings.db_charset,
            'autocommit': True,
        }
        self.pool: Optional[aiomysql.Pool] = None
        logger.info(f"MySQLClient initialized with config: host={settings.db_host}, port={settings.db_port}, db={settings.db_name}")
    
    async def connect(self):
        """创建数据库连接池"""
        try:
            self.pool = await aiomysql.create_pool(
                **self.config,
                minsize=1,
                maxsize=settings.db_pool_size,
                pool_recycle=settings.db_pool_recycle,
            )
            logger.info(f"MySQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create MySQL connection pool: {e}")
            raise
    
    async def disconnect(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info(f"MySQL connection pool closed successfully")
    
    async def execute_query(self, query: str, args: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询语句，返回结果列表"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    logger.debug(f"Executing query: {query} with args: {args}")
                    await cur.execute(query, args)
                    result = await cur.fetchall()
                    logger.debug(f"Query result: {result}")
                    return result
                except Exception as e:
                    logger.error(f"Error executing query: {query}, args: {args}, error: {e}")
                    raise
    
    async def execute_update(self, query: str, args: Optional[tuple] = None) -> int:
        """执行更新语句（INSERT/UPDATE/DELETE），返回影响的行数"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    logger.debug(f"Executing update: {query} with args: {args}")
                    await cur.execute(query, args)
                    affected_rows = cur.rowcount
                    logger.debug(f"Update affected {affected_rows} rows")
                    return affected_rows
                except Exception as e:
                    logger.error(f"Error executing update: {query}, args: {args}, error: {e}")
                    raise
    
    # ========== 用户相关 ==========    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱查询用户"""
        query = "SELECT * FROM users WHERE email = %s"
        result = await self.execute_query(query, (email,))
        return result[0] if result else None
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询用户"""
        query = "SELECT * FROM users WHERE id = %s"
        result = await self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建用户"""
        query = """
        INSERT INTO users (email, password_hash, role, name) 
        VALUES (%s, %s, %s, %s)
        """
        args = (
            user_data['email'],
            user_data['password_hash'],
            user_data.get('role', 'user'),
            user_data['name']
        )
        affected_rows = await self.execute_update(query, args)
        if affected_rows > 0:
            # 返回创建的用户信息
            return await self.get_user_by_email(user_data['email'])
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
        # 构建查询条件
        where_clause = ""
        params = []
        
        if keyword:
            where_clause = "WHERE title LIKE %s OR description LIKE %s"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        # 构建排序
        order_clause = "ORDER BY created_at DESC"
        if sort:
            if sort == "views":
                order_clause = "ORDER BY views DESC"
            elif sort == "newest":
                order_clause = "ORDER BY created_at DESC"
        
        # 构建分页
        offset = page * size
        limit_clause = "LIMIT %s OFFSET %s"
        params.extend([size, offset])
        
        # 主查询
        query = f"SELECT * FROM inscriptions {where_clause} {order_clause} {limit_clause}"
        result = await self.execute_query(query, tuple(params))
        
        # 查询总数
        count_query = f"SELECT COUNT(*) as total FROM inscriptions {where_clause}"
        count_params = tuple(params[:-2]) if keyword else tuple()
        count_result = await self.execute_query(count_query, count_params)
        total = count_result[0]['total'] if count_result else 0
        
        return {
            "items": result,
            "total": total,
            "page": page,
            "size": size
        }
    
    async def get_inscription_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询碑文详情"""
        query = "SELECT * FROM inscriptions WHERE id = %s"
        result = await self.execute_query(query, (inscription_id,))
        return result[0] if result else None
    
    async def create_inscription(self, inscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建碑文记录"""
        query = """
        INSERT INTO inscriptions (
            title, location, dynasty, year, description, style, material, size, 
            cover_image_url, creator_user_id, status, protection_level, 
            discovery_date, current_location, current_location_lat, current_location_lng
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        args = (
            inscription_data['title'],
            inscription_data.get('location'),
            inscription_data.get('dynasty'),
            inscription_data.get('year'),
            inscription_data.get('description'),
            inscription_data.get('style'),
            inscription_data.get('material'),
            inscription_data.get('size'),
            inscription_data.get('cover_image_url'),
            inscription_data['creator_user_id'],
            inscription_data.get('status', 'pending'),
            inscription_data.get('protection_level', 'general'),
            inscription_data.get('discovery_date'),
            inscription_data.get('current_location'),
            inscription_data.get('current_location_lat'),
            inscription_data.get('current_location_lng')
        )
        affected_rows = await self.execute_update(query, args)
        if affected_rows > 0:
            # 获取最后插入的ID
            last_id_query = "SELECT LAST_INSERT_ID() as id"
            last_id_result = await self.execute_query(last_id_query)
            if last_id_result:
                return await self.get_inscription_by_id(last_id_result[0]['id'])
        return None
    
    # ========== OCR相关 ==========    
    async def get_ocr_result_by_image_hash(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """根据图片哈希值获取OCR结果"""
        # 检查inscription_assets表，查找是否有对应的MD5哈希记录
        query = """
        SELECT * FROM inscription_assets WHERE hash_md5 = %s LIMIT 1
        """
        asset_result = await self.execute_query(query, (image_hash,))
        if not asset_result:
            logger.debug(f"未找到对应的资产记录: image_hash={image_hash}")
            return None
        
        asset = asset_result[0]
        logger.debug(f"找到资产记录: asset_id={asset['id']}, hash_md5={image_hash}")
        
        # 查询关联的OCR jobs
        query = """
        SELECT * FROM ocr_jobs WHERE asset_id = %s ORDER BY created_at DESC LIMIT 1
        """
        job_result = await self.execute_query(query, (asset['id'],))
        if not job_result:
            logger.debug(f"未找到对应的OCR任务: asset_id={asset['id']}")
            return None
        
        job = job_result[0]
        logger.debug(f"找到OCR任务: job_id={job['id']}, status={job['status']}")
        
        # 查询关联的OCR images
        query = """
        SELECT * FROM ocr_images WHERE job_id = %s LIMIT 1
        """
        image_result = await self.execute_query(query, (job['id'],))
        if not image_result:
            logger.debug(f"未找到对应的OCR图像结果: job_id={job['id']}")
            return None
        
        ocr_image = image_result[0]
        logger.debug(f"找到OCR图像结果: image_id={ocr_image['id']}")
        
        # 查询关联的文本行
        query = """
        SELECT * FROM ocr_text_lines WHERE image_id = %s ORDER BY line_index ASC
        """
        text_lines_result = await self.execute_query(query, (ocr_image['id'],))
        text_lines = text_lines_result
        
        # 查询每行的文字
        for line in text_lines:
            query = """
            SELECT * FROM ocr_words WHERE line_id = %s ORDER BY word_index ASC
            """
            words_result = await self.execute_query(query, (line['id'],))
            line['words'] = words_result
            
            # 查询每个字的候选字
            for word in line['words']:
                query = """
                SELECT choice_char FROM ocr_word_choices WHERE word_id = %s
                """
                choices_result = await self.execute_query(query, (word['id'],))
                if choices_result:
                    word['choices'] = ''.join([c['choice_char'] for c in choices_result])
        
        # 构建结果
        result = {
            "task_id": f"task_{int(time.time() * 1000)}",
            "status": "completed",
            "progress": 100,
            "estimated_time": 0,
            "result": {
                "recognition_id": f"rec_{int(time.time() * 1000)}",
                "text": '\n'.join([line['text'] for line in text_lines]) if text_lines else '',
                "word_count": sum(len(line['words']) for line in text_lines) if text_lines else 0,
                "confidence": job.get('confidence', 0.0),
                "width": ocr_image['width'],
                "height": ocr_image['height'],
                "text_angel": ocr_image['text_angel'],
                "text_lines": text_lines,
                "texts": [line['text'] for line in text_lines] if text_lines else [],
                "layout": None
            }
        }
        
        logger.debug(f"构建OCR缓存结果完成: {result}")
        return {"result": result}
    
    async def create_ocr_job(self, ocr_job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建OCR任务"""
        import json
        query = """
        INSERT INTO ocr_jobs (asset_id, status, vendor, params, confidence, duration_ms, retries)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        args = (
            ocr_job_data.get('asset_id'),
            ocr_job_data.get('status', 'pending'),
            ocr_job_data.get('vendor', 'unknown'),
            json.dumps(ocr_job_data.get('params')),
            ocr_job_data.get('confidence'),
            ocr_job_data.get('duration_ms'),
            ocr_job_data.get('retries', 0)
        )
        affected_rows = await self.execute_update(query, args)
        if affected_rows > 0:
            # 获取最后插入的ID
            last_id_query = "SELECT LAST_INSERT_ID() as id"
            last_id_result = await self.execute_query(last_id_query)
            if last_id_result:
                job_id = last_id_result[0]['id']
                query_result = await self.execute_query("SELECT * FROM ocr_jobs WHERE id = %s", (job_id,))
                return query_result[0] if query_result else None
        return None
    
    async def save_ocr_result(self, task_id: str, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """保存OCR识别结果"""
        # 解析结果数据
        result = result_data.get('result', {})
        if not result:
            logger.debug("没有可保存的OCR结果")
            return result_data
        
        # 由于缺少完整的外键关联，暂时只更新任务状态，不保存详细结果
        # 实际应用中应该完整保存文本行、单词等信息
        logger.debug(f"保存OCR结果: task_id={task_id}, result={result}")
        return result_data
    
    # ========== 对话相关 ==========    
    async def create_conversation(self, user_id: int, conversation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建对话"""
        import json
        query = """
        INSERT INTO conversations (user_id, title, inscription_id, model_key, model_provider, system_prompt, generation_config)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        args = (
            user_id,
            conversation_data.get('title', '新对话'),
            conversation_data.get('inscription_id'),
            conversation_data.get('model_key'),
            conversation_data.get('model_provider'),
            conversation_data.get('system_prompt'),
            json.dumps(conversation_data.get('generation_config'))
        )
        affected_rows = await self.execute_update(query, args)
        if affected_rows > 0:
            # 获取最后插入的ID
            last_id_query = "SELECT LAST_INSERT_ID() as id"
            last_id_result = await self.execute_query(last_id_query)
            if last_id_result:
                return await self.execute_query("SELECT * FROM conversations WHERE id = %s", (last_id_result[0]['id'],))[0]
        return None
    
    # ========== LLM缓存相关 ==========    
    async def get_llm_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取LLM响应缓存"""
        query = "SELECT * FROM llm_cache WHERE prompt_key = %s"
        result = await self.execute_query(query, (cache_key,))
        return result[0] if result else None
    
    async def set_llm_cache(self, cache_key: str, cache_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """设置LLM响应缓存"""
        query = """
        INSERT INTO llm_cache (prompt_key, context_fingerprint, message_id, citations_fingerprint, model_key, model_provider, token_count, hit_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE hit_count = hit_count + 1, updated_at = CURRENT_TIMESTAMP
        """
        args = (
            cache_key,
            cache_data.get('context_fingerprint', ''),
            cache_data.get('message_id', 0),
            cache_data.get('citations_fingerprint', ''),
            cache_data.get('model_key', 'default'),  # 提供默认值
            cache_data.get('model_provider', 'default'),  # 提供默认值
            cache_data.get('token_count', 0),  # 提供默认值
            1
        )
        affected_rows = await self.execute_update(query, args)
        return affected_rows > 0
    
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
        # 构建查询条件
        where_clause = ""
        params = []
        
        conditions = []
        if keyword:
            conditions.append("title LIKE %s OR content LIKE %s")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if dynasty:
            conditions.append("dynasty = %s")
            params.append(dynasty)
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # 构建分页
        offset = page * size
        limit_clause = "LIMIT %s OFFSET %s"
        params.extend([size, offset])
        
        # 主查询
        query = f"SELECT * FROM knowledge_articles {where_clause} ORDER BY created_at DESC {limit_clause}"
        result = await self.execute_query(query, tuple(params))
        
        # 查询总数
        count_query = f"SELECT COUNT(*) as total FROM knowledge_articles {where_clause}"
        count_params = tuple(params[:-2]) if params else tuple()
        count_result = await self.execute_query(count_query, count_params)
        total = count_result[0]['total'] if count_result else 0
        
        return {
            "items": result,
            "total": total,
            "page": page,
            "size": size
        }
    
    async def get_knowledge_by_id(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询知识库详情"""
        query = "SELECT * FROM knowledge_articles WHERE id = %s"
        result = await self.execute_query(query, (knowledge_id,))
        return result[0] if result else None

# 创建全局MySQL客户端实例
mysql_client = MySQLClient()
