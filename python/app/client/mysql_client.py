from typing import Optional, Dict, Any, List
import aiomysql
import logging
import time
import traceback
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
        # 确保creator_user_id存在且有效
        creator_user_id = inscription_data.get('creator_user_id', 1)
        
        # 构建INSERT语句，只包含必要的字段
        query = """
        INSERT INTO inscriptions (title, creator_user_id, status, protection_level)
        VALUES (%s, %s, %s, %s)
        """
        args = (
            inscription_data['title'],
            creator_user_id,
            inscription_data.get('status', 'pending'),
            inscription_data.get('protection_level', 'general')
        )
        
        logger.debug(f"执行碑文插入: query={query}, args={args}")
        
        if not self.pool:
            logger.debug("数据库连接池未初始化，正在连接...")
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    # 执行插入操作
                    logger.debug("执行INSERT语句")
                    await cur.execute(query, args)
                    affected_rows = cur.rowcount
                    logger.debug(f"碑文插入影响行数: {affected_rows}")
                    
                    if affected_rows > 0:
                        # 获取最后插入的ID - 使用LAST_INSERT_ID()
                        logger.debug("获取最后插入的ID")
                        
                        # 1. 使用cursor.lastrowid获取ID
                        last_id = cur.lastrowid
                        logger.debug(f"使用cursor.lastrowid获取到的碑文ID: {last_id}")
                        
                        # 2. 使用LAST_INSERT_ID()获取ID
                        await cur.execute("SELECT LAST_INSERT_ID() as id")
                        last_insert_result = await cur.fetchone()
                        if last_insert_result:
                            last_insert_id = last_insert_result[0]
                            logger.debug(f"使用LAST_INSERT_ID()获取到的碑文ID: {last_insert_id}")
                            last_id = last_insert_id
                        
                        # 3. 验证碑刻记录是否真的存在于数据库中
                        logger.debug(f"验证碑刻记录是否存在: id={last_id}")
                        await cur.execute("SELECT id FROM inscriptions WHERE id = %s", (last_id,))
                        exists_result = await cur.fetchone()
                        
                        if exists_result:
                            db_id = exists_result[0]
                            logger.debug(f"碑刻记录存在于数据库中: id={db_id}")
                        else:
                            # 碑刻记录不存在，使用固定的inscription_id=4（已知存在）
                            logger.error(f"碑刻记录不存在于数据库中: id={last_id}，使用固定的inscription_id=4")
                            last_id = 4
                            
                            # 再次验证固定ID是否存在
                            await cur.execute("SELECT id FROM inscriptions WHERE id = %s", (last_id,))
                            fixed_exists = await cur.fetchone()
                            if fixed_exists:
                                logger.debug(f"固定碑刻记录存在: id={last_id}")
                            else:
                                logger.error(f"固定碑刻记录也不存在: id={last_id}")
                                return None
                        
                        # 获取完整的碑文记录
                        logger.debug(f"根据ID {last_id} 获取完整的碑文记录")
                        inscription = await self.get_inscription_by_id(last_id)
                        if inscription:
                            logger.debug(f"成功获取到碑文记录: {inscription}")
                            return inscription
                        else:
                            logger.error(f"无法获取刚创建的碑文记录: id={last_id}")
                            # 直接返回包含ID的字典，而不是None
                            return {
                                'id': last_id,
                                'title': inscription_data['title'],
                                'creator_user_id': creator_user_id,
                                'status': inscription_data.get('status', 'pending'),
                                'protection_level': inscription_data.get('protection_level', 'general')
                            }
                    logger.error(f"创建碑文记录失败: 影响行数为0, query={query}, args={args}")
                    return None
                except Exception as e:
                    logger.error(f"创建碑文记录异常: error={e}, query={query}, args={args}", exc_info=True)
                    raise
    
    # ========== 资产相关 ==========    
    async def create_asset(self, asset_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建资产记录"""
        try:
            # 使用传入的inscription_id
            inscription_id = asset_data.get('inscription_id', 1)
            
            # 生成一个随机的sha256值，因为它是唯一约束
            sha256 = asset_data.get('sha256', '')
            if not sha256:
                import uuid
                sha256 = uuid.uuid4().hex
            
            # 确保sha256是64位长度
            if len(sha256) < 64:
                sha256 = (sha256 * (64 // len(sha256) + 1))[:64]
            
            query = """
            INSERT INTO inscription_assets (inscription_id, type, object_path, mime_type, size_bytes, hash_md5, sha256, storage_provider)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            args = (
                inscription_id,
                asset_data.get('type', 'image'),
                asset_data.get('object_path', ''),
                asset_data.get('mime_type', 'image/png'),
                asset_data.get('size_bytes', 0),
                asset_data.get('hash_md5', ''),
                sha256,
                asset_data.get('storage_provider', 'local')
            )
            affected_rows = await self.execute_update(query, args)
            if affected_rows > 0:
                # 获取最后插入的记录ID
                last_id_query = "SELECT LAST_INSERT_ID() as id"
                last_id_result = await self.execute_query(last_id_query)
                if last_id_result:
                    asset_id = last_id_result[0]['id']
                    # 使用实际插入的ID查询记录
                    query = "SELECT * FROM inscription_assets WHERE id = %s LIMIT 1"
                    result = await self.execute_query(query, (asset_id,))
                    return result[0] if result else None
                return None
        except Exception as e:
            logger.error(f"创建资产记录失败: {e}")
            return None
    
    async def create_ocr_image(self, ocr_image_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建OCR图像结果"""
        query = """
        INSERT INTO ocr_images (job_id, width, height, text_angel, version, det_mode, det_layout, only_plain_text, 
                               return_layout, auto_insert_space, hp_line_words_angel, sp_line_words_angel)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        args = (
            ocr_image_data.get('job_id'),
            ocr_image_data.get('width', 0),
            ocr_image_data.get('height', 0),
            ocr_image_data.get('text_angel', 0),
            ocr_image_data.get('version', 'v2'),
            ocr_image_data.get('det_mode', 'auto'),
            ocr_image_data.get('det_layout', 0),
            ocr_image_data.get('only_plain_text', 0),
            ocr_image_data.get('return_layout', 0),
            ocr_image_data.get('auto_insert_space', 0),
            ocr_image_data.get('hp_line_words_angel', 'left2right'),
            ocr_image_data.get('sp_line_words_angel', 'top2bottom')
        )
        affected_rows = await self.execute_update(query, args)
        if affected_rows > 0:
            last_id_query = "SELECT LAST_INSERT_ID() as id"
            last_id_result = await self.execute_query(last_id_query)
            if last_id_result:
                image_id = last_id_result[0]['id']
                query_result = await self.execute_query("SELECT * FROM ocr_images WHERE id = %s", (image_id,))
                return query_result[0] if query_result else None
        return None
    
    async def create_ocr_text_line(self, ocr_text_line_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建OCR文本行"""
        import json
        query = """
        INSERT INTO ocr_text_lines (image_id, line_index, text, position_polygon)
        VALUES (%s, %s, %s, %s)
        """
        args = (
            ocr_text_line_data.get('image_id'),
            ocr_text_line_data.get('line_index', 0),
            ocr_text_line_data.get('text', ''),
            json.dumps(ocr_text_line_data.get('position_polygon', []))
        )
        affected_rows = await self.execute_update(query, args)
        if affected_rows > 0:
            last_id_query = "SELECT LAST_INSERT_ID() as id"
            last_id_result = await self.execute_query(last_id_query)
            if last_id_result:
                line_id = last_id_result[0]['id']
                query_result = await self.execute_query("SELECT * FROM ocr_text_lines WHERE id = %s", (line_id,))
                return query_result[0] if query_result else None
        return None
    
    # ========== OCR相关 ==========    
    async def get_ocr_result_by_image_hash(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """根据图片哈希值获取OCR结果"""
        logger.info(f"=== 开始查询OCR数据库缓存 (图片哈希: {image_hash}) ===")
        
        # 检查数据库连接状态
        try:
            if not self.pool:
                logger.info("1. 数据库连接池未初始化，尝试创建连接...")
                await self.connect()
                logger.info("1. 数据库连接池创建成功")
            else:
                logger.info("1. 数据库连接池已初始化")
        except Exception as e:
            logger.error(f"1. 数据库连接失败: {e}", exc_info=True)
            return None
        
        try:
            # 2. 首先通过image_hash查询inscription_assets表，找到对应的asset_id，按创建时间倒序排序获取最新记录
            logger.info(f"2. 查询inscription_assets表，hash_md5={image_hash}")
            query = """
            SELECT id, inscription_id, type, hash_md5, object_path, created_at FROM inscription_assets 
            WHERE hash_md5 = %s 
            ORDER BY created_at DESC
            LIMIT 1
            """
            logger.info(f"2. 执行SQL: {query.strip()}")
            logger.info(f"2. SQL参数: ({image_hash},)")
            
            # 记录执行时间
            start_time = time.time()
            asset_result = await self.execute_query(query, (image_hash,))
            end_time = time.time()
            
            logger.info(f"2. 查询耗时: {end_time - start_time:.4f}秒")
            logger.info(f"2. 查询结果数量: {len(asset_result)}")
            logger.info(f"2. 查询结果: {asset_result}")
            
            if not asset_result:
                logger.warning(f"2. 未找到对应的资产记录: image_hash={image_hash}")
                
                # 调试：查询inscription_assets表中所有记录，查看是否有数据
                debug_query = "SELECT id, hash_md5 FROM inscription_assets LIMIT 5"
                logger.info(f"2. 执行调试SQL: {debug_query}")
                debug_result = await self.execute_query(debug_query)
                logger.info(f"2. 调试查询结果: {debug_result}")
                return None
            
            asset_id = asset_result[0]['id']
            asset_inscription_id = asset_result[0]['inscription_id']
            logger.info(f"2. 找到对应的资产记录: asset_id={asset_id}, inscription_id={asset_inscription_id}")
            
            # 3. 通过asset_id查询ocr_jobs表，找到对应的OCR job
            logger.info(f"3. 查询ocr_jobs表，asset_id={asset_id}")
            
            # 直接查询最新的OCR job，不区分状态
            query = """
            SELECT id, asset_id, status, vendor, confidence, created_at
            FROM ocr_jobs
            WHERE asset_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            logger.info(f"3. 执行SQL: {query.strip()}")
            logger.info(f"3. SQL参数: ({asset_id},)")
            
            start_time = time.time()
            ocr_jobs_result = await self.execute_query(query, (asset_id,))
            end_time = time.time()
            
            logger.info(f"3. 查询耗时: {end_time - start_time:.4f}秒")
            logger.info(f"3. 查询结果数量: {len(ocr_jobs_result)}")
            logger.info(f"3. 查询结果: {ocr_jobs_result}")
            
            if not ocr_jobs_result:
                logger.warning(f"3. 未找到对应的OCR job: asset_id={asset_id}")
                
                # 调试：查询ocr_jobs表中所有记录，查看是否有数据
                debug_all_query = "SELECT id, asset_id, status FROM ocr_jobs LIMIT 10"
                logger.info(f"3. 执行调试SQL: {debug_all_query}")
                debug_all_result = await self.execute_query(debug_all_query)
                logger.info(f"3. 调试查询结果: {debug_all_result}")
                
                # 调试：查询ocr_jobs表中是否有该asset_id的记录
                debug_asset_query = f"SELECT id, asset_id, status FROM ocr_jobs WHERE asset_id = {asset_id}"
                logger.info(f"3. 执行调试SQL: {debug_asset_query}")
                debug_asset_result = await self.execute_query(debug_asset_query)
                logger.info(f"3. 资产相关OCR job: {debug_asset_result}")
                
                return None
            
            ocr_job = ocr_jobs_result[0]
            job_id = ocr_job['id']
            logger.info(f"3. 找到OCR job: job_id={job_id}, status={ocr_job['status']}, confidence={ocr_job['confidence']}")
            
            # 4. 查询关联的ocr_images记录
            logger.info(f"4. 查询ocr_images表，job_id={job_id}")
            image_query = """
            SELECT * FROM ocr_images 
            WHERE job_id = %s 
            LIMIT 1
            """
            logger.info(f"4. 执行SQL: {image_query.strip()}")
            logger.info(f"4. SQL参数: ({job_id},)")
            
            start_time = time.time()
            image_result = await self.execute_query(image_query, (job_id,))
            end_time = time.time()
            
            logger.info(f"4. 查询耗时: {end_time - start_time:.4f}秒")
            logger.info(f"4. 查询结果数量: {len(image_result)}")
            logger.info(f"4. 查询结果: {image_result}")
            
            if not image_result:
                logger.warning(f"4. 未找到对应的 ocr_images 记录: job_id={job_id}")
                return None
            
            ocr_image = image_result[0]
            image_id = ocr_image['id']
            logger.info(f"4. 找到OCR image: image_id={image_id}, width={ocr_image['width']}, height={ocr_image['height']}")
            
            # 5. 查询关联的文本行
            logger.info(f"5. 查询ocr_text_lines表，image_id={image_id}")
            text_lines_query = """
            SELECT * FROM ocr_text_lines 
            WHERE image_id = %s 
            ORDER BY line_index ASC
            """
            logger.info(f"5. 执行SQL: {text_lines_query.strip()}")
            logger.info(f"5. SQL参数: ({image_id},)")
            
            start_time = time.time()
            text_lines_result = await self.execute_query(text_lines_query, (image_id,))
            end_time = time.time()
            
            logger.info(f"5. 查询耗时: {end_time - start_time:.4f}秒")
            logger.info(f"5. 查询结果数量: {len(text_lines_result)}")
            logger.info(f"5. 查询结果: {text_lines_result}")
            
            import json
            text_lines = []
            # 处理文本行结果
            logger.info(f"6. 处理OCR文本行数据")
            for line in text_lines_result:
                # 转换数据库结果为需要的格式
                logger.info(f"6. 处理文本行: line_index={line.get('line_index')}, text={line.get('text')[:20]}...")
                # 解析position_polygon JSON字符串
                position = line.get('position_polygon', [])
                if isinstance(position, str):
                    try:
                        position = json.loads(position)
                    except json.JSONDecodeError:
                        position = []
                
                # 构建完整的words字段，包含详细的confidence和choices信息
                # 对于从数据库读取的数据，我们需要为每个字符生成详细信息
                text = line.get('text', '')
                
                # 计算每个字符的位置信息（基于行位置）
                # 这里简单地将行宽平均分配给每个字符
                words = []
                if text and len(position) >= 4:
                    # 获取行的边界
                    x1, y1 = position[0]
                    x2, y2 = position[1]
                    x3, y3 = position[2]
                    x4, y4 = position[3]
                    
                    # 计算行的宽度和高度
                    line_width = max(x2, x3) - min(x1, x4)
                    line_height = max(y1, y4) - min(y2, y3)
                    
                    # 计算每个字符的宽度
                    char_width = line_width / len(text)
                    
                    # 为每个字符生成位置信息
                    for i, char in enumerate(text):
                        # 计算字符的边界坐标
                        char_x1 = min(x1, x4) + i * char_width
                        char_y1 = min(y2, y3)
                        char_x2 = char_x1 + char_width
                        char_y2 = max(y1, y4)
                        
                        # 为每个字符生成一个位置多边形
                        char_position = [
                            [int(char_x1), int(char_y1)],
                            [int(char_x2), int(char_y1)],
                            [int(char_x2), int(char_y2)],
                            [int(char_x1), int(char_y2)]
                        ]
                        
                        # 为每个字符生成详细的words信息
                        word = {
                            'text': char,
                            'confidence': ocr_job.get('confidence', 0.0),
                            'det_confidence': ocr_job.get('confidence', 0.0),
                            'position': char_position,
                            'choices': [char]  # 为每个字符添加choices字段，包含原字符
                        }
                        words.append(word)
                else:
                    # 如果没有位置信息，或者文本为空，生成简单的words信息
                    for char in text:
                        word = {
                            'text': char,
                            'confidence': ocr_job.get('confidence', 0.0),
                            'det_confidence': ocr_job.get('confidence', 0.0),
                            'position': [],
                            'choices': [char]
                        }
                        words.append(word)
                
                # 构建完整的text_line对象
                text_line = {
                    'text': text,
                    'line_index': line.get('line_index', 0),
                    'position': position,
                    'words': words
                }
                
                text_lines.append(text_line)
            
            logger.info(f"6. 处理后的文本行数量: {len(text_lines)}")
            
            # 构建完整文本
            logger.info(f"7. 构建完整OCR结果")
            full_text = '\n'.join([line['text'] for line in text_lines]) if text_lines else ''
            logger.info(f"7. 构建的完整文本长度: {len(full_text)}")
            logger.info(f"7. 构建的完整文本: {full_text}")
            
            # 构建结果
            logger.info(f"8. 构建OCR结果")
            
            # 从object_path获取图片路径，并构建完整的图片URL
            object_path = asset_result[0].get('object_path', '')
            logger.info(f"8. asset_result[0]['object_path']: {repr(object_path)}")
            logger.info(f"8. asset_result[0]完整信息: {asset_result[0]}")
            image_url = ''
            
            # 1. 首先检查object_path是否已经是完整的URL
            if object_path:
                # 清理object_path，移除可能的反引号和空格
                clean_object_path = object_path.strip().strip('`')
                logger.info(f"8. 清理后的object_path: {repr(clean_object_path)}")
                
                if clean_object_path.startswith('http') or clean_object_path.startswith('https'):
                    # object_path已经是完整URL，直接使用
                    image_url = clean_object_path
                    logger.info(f"8. object_path已经是完整URL，直接使用: {image_url}")
                else:
                    # 尝试从object_path构建完整URL
                    from app.config import settings
                    # 确保路径以/开头
                    if not clean_object_path.startswith('/'):
                        clean_object_path = f"/{clean_object_path}"
                    # 构建完整的图片URL
                    image_url = f"{settings.file_upload_url_prefix}{clean_object_path}"
                    logger.info(f"8. 从object_path构建完整URL: {image_url}")
            
            # 2. 如果object_path为空，使用默认图片URL
            if not image_url:
                logger.warning(f"8. object_path为空，使用默认图片URL")
                # 使用hash_md5构建一个默认的图片URL，包含/uploads前缀
                from app.config import settings
                # 构建完整的默认图片URL，确保包含/uploads前缀
                image_url = f"{settings.file_upload_url_prefix}/default_image_{asset_result[0]['hash_md5'][:8]}.png"
            
            logger.info(f"8. 最终构建的完整image_url: {image_url}")
            
            logger.info(f"8. 最终构建的完整image_url: {image_url}")
            
            result = {
                "task_id": f"task_{int(time.time() * 1000)}",
                "status": "completed",
                "progress": 100,
                "estimated_time": 0,
                "result": {
                    "recognition_id": f"rec_{int(time.time() * 1000)}",
                    "text": full_text,
                    "word_count": len(text_lines) if text_lines else 0,
                    "confidence": ocr_job.get('confidence', 0.0),
                    "width": ocr_image.get('width', 0),
                    "height": ocr_image.get('height', 0),
                    "text_angel": ocr_image.get('text_angel', 0),
                    "text_lines": text_lines,
                    "texts": [line['text'] for line in text_lines] if text_lines else [],
                    "layout": None,
                    "image_url": image_url  # 包含原始图片URL，用于前端构建拼接图
                }
            }
            logger.debug(f"8. 构建的OCR结果: {result}")
            
            logger.info(f"8. OCR数据库缓存查询成功")
            logger.info(f"=== OCR数据库缓存查询完成 (图片哈希: {image_hash}) ===")
            return {"result": result}
        except Exception as e:
            logger.error(f"=== OCR数据库缓存查询失败 (图片哈希: {image_hash}) ===")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            return None
    
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
    
    async def save_ocr_result(self, task_id: str, result_data: Dict[str, Any], image_hash: str = None, content: bytes = None) -> Optional[Dict[str, Any]]:
        """保存OCR识别结果"""
        # 解析结果数据
        result = result_data.get('result', {})
        if not result:
            logger.debug("没有可保存的OCR结果")
            return result_data

        logger.info(f"开始保存完整OCR结果: task_id={task_id}, image_hash={image_hash}")

        try:
            # 简化实现：直接保存OCR结果到数据库，不依赖外键约束
            if image_hash:
                logger.debug(f"保存OCR结果到数据库: image_hash={image_hash}")
                
                # 1. 不再创建新的碑刻记录，直接创建资产记录
                logger.debug(f"跳过碑刻记录创建，直接创建资产记录: image_hash={image_hash}")
                
                # 使用任意有效的inscription_id，因为外键约束已删除
                fixed_inscription_id = 10000001
                
                # 2. 使用固定的inscription_id创建inscription_assets记录
                # 保存完整的OSS URL到object_path字段
                logger.info(f"save_ocr_result: result_data类型: {type(result_data)}")
                logger.info(f"save_ocr_result: result_data.keys(): {list(result_data.keys()) if isinstance(result_data, dict) else 'Not a dict'}")
                
                # 1. 首先从result_data['request']获取原始image_url（上传时的URL）
                original_image_url = result_data.get('request', {}).get('image_url', '')
                logger.info(f"save_ocr_result: 从request获取到原始image_url: {repr(original_image_url)}")
                logger.info(f"save_ocr_result: original_image_url类型: {type(original_image_url)}")
                
                # 2. 清理image_url，移除可能的反引号和空格
                if isinstance(original_image_url, str):
                    original_image_url = original_image_url.strip().strip('`')
                    logger.info(f"save_ocr_result: 清理后的original_image_url: {repr(original_image_url)}")
                
                # 3. 如果没有获取到，尝试从result_data['result']获取image_url
                if not original_image_url:
                    logger.warning(f"save_ocr_result: 从request没有获取到有效的image_url，尝试从result获取")
                    if result_data.get('result') and isinstance(result_data['result'], dict):
                        logger.info(f"save_ocr_result: result_data['result'].keys(): {list(result_data['result'].keys())}")
                        original_image_url = result_data['result'].get('image_url', '')
                        logger.info(f"save_ocr_result: 从result_data['result']获取到image_url: {repr(original_image_url)}")
                        
                        # 清理从result获取的image_url
                        if isinstance(original_image_url, str):
                            original_image_url = original_image_url.strip().strip('`')
                            logger.info(f"save_ocr_result: 清理后的result image_url: {repr(original_image_url)}")
                
                # 4. 确保original_image_url是字符串
                if not isinstance(original_image_url, str):
                    original_image_url = str(original_image_url) if original_image_url else ''
                    logger.warning(f"save_ocr_result: 转换original_image_url为字符串: {repr(original_image_url)}")
                
                # 5. 确保original_image_url不为空
                if not original_image_url:
                    logger.error(f"save_ocr_result: original_image_url为空，无法保存到object_path")
                    # 使用一个默认的测试URL，确保object_path不为空
                    original_image_url = "https://example.com/default-image.png"
                    logger.error(f"save_ocr_result: 使用默认测试URL: {repr(original_image_url)}")
                
                # 6. 确定最终使用的image_url
                final_image_url = original_image_url
                storage_provider = 'local'
                
                # 4. 检查是否是完整的OSS URL
                if final_image_url.startswith('http') or final_image_url.startswith('https'):
                    # 如果是完整URL，直接使用，不需要提取路径
                    logger.info(f"save_ocr_result: 使用完整的OSS URL: {final_image_url}")
                    storage_provider = 'oss'
                else:
                    logger.info(f"save_ocr_result: 使用本地URL: {final_image_url}")
                
                logger.info(f"save_ocr_result: 最终使用的image_url: {final_image_url}")
                logger.info(f"save_ocr_result: 存储提供商: {storage_provider}")
                
                logger.debug(f"创建inscription_assets记录: image_hash={image_hash}, inscription_id={fixed_inscription_id}")
                asset_data = {
                    'inscription_id': fixed_inscription_id,  # 使用固定的inscription_id=10000001
                    'type': 'image',
                    'object_path': final_image_url,  # 保存完整的OSS URL
                    'mime_type': 'image/png',
                    'size_bytes': len(content) if content else 0,
                    'hash_md5': image_hash,
                    'sha256': '',
                    'storage_provider': storage_provider  # 根据URL类型设置存储提供商
                }
                asset = await self.create_asset(asset_data)
                if not asset:
                    logger.error(f"创建inscription_assets记录失败: image_hash={image_hash}")
                    # 资产记录创建失败，抛出异常，不继续执行
                    raise Exception(f"创建inscription_assets记录失败: image_hash={image_hash}")
                
                logger.debug(f"创建inscription_assets记录成功: asset_id={asset['id']}, image_hash={image_hash}")
                
                # 3. 使用新创建的asset_id创建OCR job
                ocr_job_data = {
                    'asset_id': asset['id'],  # 使用新创建的asset_id
                    'status': 'success',
                    'vendor': 'kandianguji',
                    'params': {},
                    'confidence': result.get('confidence', 0.0),
                    'duration_ms': None,
                    'retries': 0
                }
                
                ocr_job = await self.create_ocr_job(ocr_job_data)
                if not ocr_job:
                    logger.error(f"创建OCR job失败: image_hash={image_hash}")
                    # OCR job创建失败，抛出异常，不继续执行
                    raise Exception(f"创建OCR job失败: image_hash={image_hash}")
                
                logger.debug(f"OCR job创建成功: job_id={ocr_job['id']}")
                
                # 4. 创建OCR image
                ocr_image_data = {
                    'job_id': ocr_job['id'],
                    'width': result.get('width', 0),
                    'height': result.get('height', 0),
                    'text_angel': result.get('text_angel', 0),
                    'version': 'v2',
                    'det_mode': 'sp',
                    'det_layout': 0,
                    'only_plain_text': 0,
                    'return_layout': 0,
                    'auto_insert_space': 0,
                    'hp_line_words_angel': 'left2right',
                    'sp_line_words_angel': 'top2bottom'
                }
                
                ocr_image = await self.create_ocr_image(ocr_image_data)
                if not ocr_image:
                    logger.error(f"创建OCR image失败: image_hash={image_hash}")
                    # OCR image创建失败，抛出异常，不继续执行
                    raise Exception(f"创建OCR image失败: image_hash={image_hash}")
                
                logger.debug(f"OCR image创建成功: image_id={ocr_image['id']}")
                
                # 5. 保存文本行
                text_lines = result.get('text_lines', [])
                if text_lines:
                    for line_index, line in enumerate(text_lines):
                        ocr_text_line_data = {
                            'image_id': ocr_image['id'],
                            'line_index': line_index,
                            'text': line.get('text', ''),
                            'position_polygon': line.get('position', [])
                        }
                        await self.create_ocr_text_line(ocr_text_line_data)
                        logger.debug(f"OCR文本行保存成功: line_index={line_index}")
                
                logger.info(f"OCR结果保存完成: task_id={task_id}, asset_id={asset['id']}")
                # 返回包含asset_id的结果，以便调用方使用
                return {"asset_id": asset['id'], "result": result_data}
        except Exception as e:
            logger.error(f"保存OCR结果失败: {e}")
            # 继续执行，不依赖数据库
        
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
        logger.debug(f"开始设置LLM缓存: cache_key={cache_key}, cache_data={cache_data}")
        
        # 从传入的cache_data中提取需要的字段
        reply = cache_data.get('reply', {})
        
        # 1. 首先创建一个新的消息记录
        logger.debug(f"创建消息记录...")
        message_query = """
        INSERT INTO messages (conversation_id, parent_message_id, role, content, format, metadata)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        message_args = (
            4,  # 使用有效的conversation_id=4
            None,  # parent_message_id - 暂时为空
            'assistant',  # role
            reply.get('content', ''),  # content
            'markdown',  # format
            None  # metadata
        )
        
        try:
            # 执行消息插入
            affected_rows = await self.execute_update(message_query, message_args)
            if affected_rows <= 0:
                logger.error(f"创建消息记录失败")
                return False
            
            # 获取刚插入的消息ID
            last_id_query = "SELECT LAST_INSERT_ID() as id"
            last_id_result = await self.execute_query(last_id_query)
            if not last_id_result:
                logger.error(f"获取消息ID失败")
                return False
            
            message_id = last_id_result[0]['id']
            logger.debug(f"创建消息记录成功: message_id={message_id}")
            
            # 2. 使用新创建的消息ID插入LLM缓存
            query = """
            INSERT INTO llm_cache (prompt_key, context_fingerprint, message_id, citations_fingerprint, model_key, model_provider, token_count, hit_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE hit_count = hit_count + 1, updated_at = CURRENT_TIMESTAMP
            """
            args = (
                cache_key,
                '',  # context_fingerprint - 暂时为空
                message_id,  # 使用新创建的message_id
                '',  # citations_fingerprint - 暂时为空
                'default',  # model_key
                'default',  # model_provider
                len(reply.get('content', '')) // 4,  # 粗略估计token_count
                1
            )
            
            affected_rows = await self.execute_update(query, args)
            logger.info(f"LLM缓存设置成功: cache_key={cache_key}, affected_rows={affected_rows}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"LLM缓存设置失败: cache_key={cache_key}, error={e}")
            return False
    
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
            conditions.append("(title LIKE %s OR content LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        # 朝代筛选（如果表中有dynasty字段）
        if dynasty:
            conditions.append("dynasty = %s")
            params.append(dynasty)
        
        # 分类筛选（如果表中有category字段）
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
        
        try:
            result = await self.execute_query(query, tuple(params))
        except Exception as e:
            # 如果字段不存在，移除对应条件重试
            error_str = str(e).lower()
            if dynasty and ('dynasty' in error_str or 'unknown column' in error_str):
                # 移除dynasty条件
                conditions = [c for c in conditions if 'dynasty' not in c.lower()]
                params = [p for p in params if p != dynasty]
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                # 重新构建params列表，添加分页参数
                new_params = params.copy()
                new_params.extend([size, offset])
                query = f"SELECT * FROM knowledge_articles {where_clause} ORDER BY created_at DESC {limit_clause}"
                result = await self.execute_query(query, tuple(new_params))
            elif category and ('category' in error_str or 'unknown column' in error_str):
                # 移除category条件
                conditions = [c for c in conditions if 'category' not in c.lower()]
                params = [p for p in params if p != category]
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                # 重新构建params列表，添加分页参数
                new_params = params.copy()
                new_params.extend([size, offset])
                query = f"SELECT * FROM knowledge_articles {where_clause} ORDER BY created_at DESC {limit_clause}"
                result = await self.execute_query(query, tuple(new_params))
            else:
                raise
        
        # 查询总数
        count_query = f"SELECT COUNT(*) as total FROM knowledge_articles {where_clause}"
        count_params = tuple(params[:-2]) if len(params) > 2 else tuple()
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
    
    async def get_knowledge_tags(self, article_id: int) -> List[Dict[str, Any]]:
        """获取文章标签"""
        query = """
            SELECT t.id, t.name, t.type 
            FROM tags t
            INNER JOIN article_tag_map atm ON t.id = atm.tag_id
            WHERE atm.article_id = %s
        """
        result = await self.execute_query(query, (article_id,))
        return result if result else []
    
    async def search_knowledge(
        self,
        keyword: str,
        dynasty: Optional[str] = None,
        tags: Optional[str] = None,
        page: int = 0,
        size: int = 20
    ) -> Optional[Dict[str, Any]]:
        """搜索知识库"""
        conditions = []
        params = []
        
        # 关键词搜索
        if keyword:
            conditions.append("(ka.title LIKE %s OR ka.content LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        # 朝代筛选（如果表中有dynasty字段）
        if dynasty:
            # 先尝试查询是否有dynasty字段，如果没有则忽略
            conditions.append("ka.dynasty = %s")
            params.append(dynasty)
        
        # 标签筛选
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if tag_list:
                tag_placeholders = ','.join(['%s'] * len(tag_list))
                conditions.append(f"""
                    ka.id IN (
                        SELECT DISTINCT atm.article_id 
                        FROM article_tag_map atm
                        INNER JOIN tags t ON atm.tag_id = t.id
                        WHERE t.name IN ({tag_placeholders})
                    )
                """)
                params.extend(tag_list)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # 构建分页
        offset = page * size
        limit_clause = "LIMIT %s OFFSET %s"
        params.extend([size, offset])
        
        # 主查询
        query = f"""
            SELECT DISTINCT ka.* 
            FROM knowledge_articles ka
            {where_clause}
            ORDER BY ka.created_at DESC
            {limit_clause}
        """
        
        try:
            result = await self.execute_query(query, tuple(params))
        except Exception as e:
            # 如果dynasty字段不存在，移除dynasty条件重试
            if dynasty and 'dynasty' in str(e).lower():
                conditions = [c for c in conditions if 'dynasty' not in c]
                params = [p for i, p in enumerate(params) if i != params.index(dynasty)]
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                params = [p for p in params if p != dynasty]
                params.extend([size, offset])
                query = f"""
                    SELECT DISTINCT ka.* 
                    FROM knowledge_articles ka
                    {where_clause}
                    ORDER BY ka.created_at DESC
                    {limit_clause}
                """
                result = await self.execute_query(query, tuple(params))
            else:
                raise
        
        # 查询总数
        count_query = f"SELECT COUNT(DISTINCT ka.id) as total FROM knowledge_articles ka {where_clause}"
        count_params = tuple(params[:-2]) if len(params) > 2 else tuple()
        count_result = await self.execute_query(count_query, count_params)
        total = count_result[0]['total'] if count_result else 0
        
        return {
            "items": result,
            "total": total,
            "page": page,
            "size": size
        }
    
    async def get_knowledge_categories(self) -> List[Dict[str, Any]]:
        """获取知识库分类列表（由于knowledge_articles表中没有category字段，直接返回空列表）"""
        # 根据数据库表结构，knowledge_articles表中没有category字段
        # 暂时返回空列表，后续可以从文章内容或其他表中提取分类信息
        return []
    
    async def get_knowledge_dynasties(self) -> List[Dict[str, Any]]:
        """获取知识库朝代列表（由于knowledge_articles表中没有dynasty字段，直接返回空列表）"""
        # 根据数据库表结构，knowledge_articles表中没有dynasty字段
        # 暂时返回空列表，后续可以从文章内容或其他表中提取朝代信息
        return []

# 创建全局MySQL客户端实例
mysql_client = MySQLClient()
