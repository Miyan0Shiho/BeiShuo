from typing import Optional, List, Dict, Any
import re
import logging
from app.services.knowledge_service import KnowledgeService
from app.client.database_client import DatabaseClient

# 配置日志记录器
logger = logging.getLogger(__name__)

class RecommendationService:
    """
    推荐服务类
    
    1. 实现相关碑文推荐功能
    2. 实现最近识别记录功能
    """
    
    def __init__(self):
        """初始化推荐服务"""
        self.database_client = DatabaseClient()
        self.knowledge_service = KnowledgeService()
    
    async def close(self):
        """关闭客户端连接"""
        await self.knowledge_service.close()
    
    async def get_recommended_inscriptions(
        self, 
        ocr_text: Optional[str] = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取推荐碑文
        
        Args:
            ocr_text: OCR识别结果文本
            limit: 推荐数量
            
        Returns:
            推荐的碑文列表
        """
        if ocr_text and len(ocr_text.strip()) > 0:
            # 基于OCR文本推荐相关碑文
            return await self._recommend_by_ocr_text(ocr_text, limit)
        else:
            # 随机推荐碑文
            return await self._recommend_randomly(limit)
    
    async def _recommend_by_ocr_text(self, ocr_text: str, limit: int) -> List[Dict[str, Any]]:
        """
        基于OCR文本推荐相关碑文
        
        实现思路：
        1. 从OCR文本中提取关键词
        2. 基于关键词从knowledge_articles表中查询相关碑文
        3. 返回匹配度最高的前limit条结果
        """
        # 简单实现：使用MySQL的全文搜索或LIKE匹配
        # 注意：knowledge_articles表目前没有全文索引，使用LIKE匹配
        
        # 提取关键词
        keywords = self._extract_keywords(ocr_text)
        
        if not keywords:
            # 如果没有提取到关键词，随机推荐
            return await self._recommend_randomly(limit)
        
        # 使用关键词匹配查询
        query = """
            SELECT id, title, author, content, views, created_at
            FROM knowledge_articles 
            WHERE 
        """
        
        # 构建WHERE条件
        conditions = []
        params = []
        
        for keyword in keywords[:5]:  # 最多使用前5个关键词
            conditions.append(f"(title LIKE %s OR content LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if not conditions:
            return await self._recommend_randomly(limit)
        
        # 拼接完整查询
        query += " OR ".join(conditions) + " ORDER BY views DESC LIMIT %s"
        params.append(limit)
        
        try:
            # 执行查询
            results = await self.database_client.execute_query(query, tuple(params))
            
            if not results:
                # 如果没有匹配结果，随机推荐
                return await self._recommend_randomly(limit)
            
            # 格式化结果
            return [self._format_article(item) for item in results]
        except Exception as e:
            logger.error(f"关键词推荐失败: {e}")
            # 查询失败时随机推荐
            return await self._recommend_randomly(limit)
    
    async def _recommend_randomly(self, limit: int) -> List[Dict[str, Any]]:
        """
        随机推荐碑文
        
        实现思路：
        1. 从knowledge_articles表中随机查询limit条记录
        2. 返回结果
        """
        query = """
            SELECT id, title, author, content, views, created_at
            FROM knowledge_articles 
            ORDER BY RAND() 
            LIMIT %s
        """
        
        # 执行查询
        results = await self.database_client.execute_query(query, (limit,))
        return [self._format_article(item) for item in results]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            关键词列表
        """
        if not text:
            return []
        
        # 移除特殊字符和标点符号
        text = re.sub(r'[^\u4e00-\u9fa5\w\s]', '', text)
        
        # 简单的关键词提取：使用jieba分词
        try:
            import jieba
            from jieba.analyse import extract_tags
            
            # 使用jieba提取关键词
            keywords = extract_tags(text, topK=10, withWeight=False)
            return keywords
        except ImportError:
            # 如果jieba未安装，使用简单的空格分割
            return list(set(text.split()))[:10]
    
    def _format_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化文章数据
        
        Args:
            article: 原始文章数据
            
        Returns:
            格式化后的文章数据
        """
        return {
            "id": article.get("id"),
            "title": article.get("title", ""),
            "author": article.get("author", "未知作者"),
            "excerpt": self._extract_excerpt(article.get("content", "")),
            "views": article.get("views", 0),
            "created_at": article.get("created_at"),
        }
    
    def _extract_excerpt(self, content: str, max_length: int = 150) -> str:
        """
        从内容中提取摘要
        
        Args:
            content: 文章内容
            max_length: 摘要最大长度
            
        Returns:
            提取的摘要
        """
        if not content:
            return ""
        
        # 移除Markdown标记
        text = re.sub(r'#+\s+', '', content)  # 移除标题标记
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # 移除加粗
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # 移除斜体
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # 移除链接
        
        # 截取前max_length个字符
        if len(text) > max_length:
            text = text[:max_length].rstrip() + "..."
        
        return text
    
    async def get_recognition_history(
        self,
        page: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        获取最近识别记录

        Args:
            page: 页码，从0开始
            size: 每页数量

        Returns:
            识别记录列表及分页信息
        """
        offset = page * size

        # 查询最近的OCR识别记录
        query = """
            SELECT 
                oj.id, 
                oj.status, 
                oj.created_at, 
                oj.confidence, 
                ia.object_path,
                i.title as inscription_title,
                COALESCE(GROUP_CONCAT(otl.text SEPARATOR '\n'), '') as recognition_text
            FROM ocr_jobs oj
            LEFT JOIN inscription_assets ia ON oj.asset_id = ia.id
            LEFT JOIN inscriptions i ON ia.inscription_id = i.id
            LEFT JOIN ocr_images oi ON oj.id = oi.job_id
            LEFT JOIN ocr_text_lines otl ON oi.id = otl.image_id
            WHERE oj.status = 'success'
            GROUP BY oj.id, oj.status, oj.created_at, oj.confidence, ia.object_path, i.title
            ORDER BY oj.created_at DESC
            LIMIT %s OFFSET %s
        """

        # 执行查询
        results = await self.database_client.execute_query(query, (size, offset))

        # 查询总记录数
        count_query = """
            SELECT COUNT(*) as total
            FROM ocr_jobs
            WHERE status = 'success'
        """
        count_result = await self.database_client.execute_query(count_query)
        total = count_result[0]['total'] if count_result else 0

        # 格式化结果
        history = []
        for record in results:
            # 确保object_path总是包含正确的URL格式
            object_path = record.get("object_path", "")
            image_path = ""
            if object_path:
                # 如果已经是完整URL，直接使用
                if object_path.startswith('http://') or object_path.startswith('https://'):
                    image_path = object_path
                else:
                    # 如果是本地路径，确保包含/uploads/前缀
                    if not object_path.startswith('/uploads/'):
                        if object_path.startswith('/'):
                            image_path = f'/uploads{object_path}'
                        else:
                            image_path = f'/uploads/{object_path}'
                    else:
                        image_path = object_path
            
            history.append({
                "id": record.get("id"),
                "status": record.get("status"),
                "created_at": record.get("created_at"),
                "confidence": round(float(record.get("confidence", 0)) * 100, 2) if record.get("confidence") else 0,
                "image_path": image_path,
                "inscription_title": record.get("inscription_title", "未知碑文"),
                "recognition_text": record.get("recognition_text", "")
            })

        return {
            "list": history,
            "total": total,
            "page": page,
            "size": size,
            "totalPages": (total + size - 1) // size if size > 0 else 0
        }
