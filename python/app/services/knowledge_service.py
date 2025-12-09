from typing import Optional, Dict, Any, List
from app.client.database_client import DatabaseClient
from app.client.redis_client import RedisClient
from app.client.oss_client import oss_client
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.config import settings
import re

class KnowledgeService:
    """知识库服务"""
    
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
        # 假设路径格式可能是：beiwen1/xxx/xxx.jpg 或 /beiwen1/xxx/xxx.jpg
        object_name = url_or_path.lstrip('/')
        # 移除bucket名称前缀（如果存在）
        if object_name.startswith('beiwen1/'):
            object_name = object_name[8:]
        
        try:
            return oss_client.get_file_url(object_name)
        except Exception:
            # 如果OSS转换失败，尝试构建基础URL
            return f"https://{settings.aliyun_oss_domain}/{object_name}"
    
    def _extract_excerpt(self, content: str, max_length: int = 200) -> str:
        """从内容中提取摘要"""
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
    
    def _format_article(self, article: Dict[str, Any], include_content: bool = False) -> Dict[str, Any]:
        """格式化文章数据"""
        if not article:
            return {}
        
        formatted = {
            "id": article.get("id"),
            "title": article.get("title", ""),
            "author": article.get("author"),
            "source_url": article.get("source_url"),
            "cover_image": self._convert_oss_url(article.get("cover_image_url")),
            "status": article.get("status", "draft"),
            "views": article.get("views", 0),
            "likes": article.get("likes", 0),
            "created_at": article.get("created_at"),
            "updated_at": article.get("updated_at"),
        }
        
        # 添加可选字段
        if "dynasty" in article:
            formatted["dynasty"] = article.get("dynasty")
        if "category" in article:
            formatted["category"] = article.get("category")
        if "year" in article:
            formatted["year"] = article.get("year")
        
        # 内容处理
        content = article.get("content", "")
        if include_content:
            formatted["content"] = content
        else:
            formatted["excerpt"] = self._extract_excerpt(content)
        
        return formatted
    
    async def get_list(
        self,
        page: int = 0,
        size: int = 10,
        keyword: Optional[str] = None,
        dynasty: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取知识库列表"""
        # 生成缓存键
        cache_key = f"knowledge:list:{page}:{size}:{keyword or ''}:{dynasty or ''}:{category or ''}:{tags or ''}"
        
        # 先查缓存
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            return cached_result
        
        # 查数据库
        result = await self.database_client.get_knowledge_list(
            page=page,
            size=size,
            keyword=keyword,
            dynasty=dynasty,
            category=category,
            tags=tags
        )
        
        if not result:
            return {
                "list": [],
                "total": 0,
                "page": page,
                "size": size,
                "totalPages": 0
            }
        
        # 格式化数据
        items = result.get("items", [])
        formatted_items = []
        for item in items:
            formatted = self._format_article(item, include_content=False)
            
            # 获取文章标签
            tags = await self.database_client.get_knowledge_tags(item.get("id", 0))
            # 添加标签到返回结果
            formatted["tags"] = [{"id": tag.get("id"), "name": tag.get("name"), "type": tag.get("type")} for tag in tags]
            
            # 从标签中提取朝代和年份信息
            dynasties = ["夏", "商", "周", "秦", "汉", "三国", "晋", "南北朝", "隋", "唐", "五代十国", "宋", "辽", "金", "元", "明", "清", "民国", "现代"]
            for tag in tags:
                tag_name = tag.get("name", "").strip()
                # 检查标签是否为朝代名称
                if tag_name in dynasties:
                    formatted["dynasty"] = tag_name
                # 检查标签是否为年份（4位数字）
                if re.match(r"^\d{4}$", tag_name):
                    formatted["year"] = tag_name
            
            formatted_items.append(formatted)
        
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
            timeout=settings.cache_knowledge_list_ttl
        )
        
        return formatted_result
    
    async def get_related_articles(
        self, 
        current_id: int, 
        dynasty: Optional[str] = None, 
        category: Optional[str] = None, 
        tags: Optional[List[str]] = None,
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        """获取相关文章"""
        # 从数据库获取文章列表
        related_result = await self.database_client.get_knowledge_list(
            page=0,
            size=limit + 3,  # 获取更多结果，以便过滤后仍有足够数量
            keyword=None,
            dynasty=None,  # 不按朝代筛选
            category=None  # 不按分类筛选
        )
        
        related_items = related_result.get("items", []) if related_result else []
        
        # 过滤掉当前文章，并格式化数据
        related = []
        for item in related_items:
            if item.get("id") != current_id:
                related.append(self._format_article(item, include_content=False))
        
        return related[:limit]
    
    async def get_by_id(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取知识库详情"""
        knowledge = await self.database_client.get_knowledge_by_id(knowledge_id)
        if not knowledge:
            raise BusinessException(ResultCode.KNOWLEDGE_NOT_FOUND)
        
        # 格式化数据
        formatted = self._format_article(knowledge, include_content=True)
        
        # 获取标签
        tags = await self.database_client.get_knowledge_tags(knowledge_id)
        formatted["tags"] = [{"id": tag.get("id"), "name": tag.get("name"), "type": tag.get("type")} for tag in tags]
        
        # 从标签中提取朝代和年份信息
        # 查找朝代标签（通常是中国朝代名称）
        dynasties = ["夏", "商", "周", "秦", "汉", "三国", "晋", "南北朝", "隋", "唐", "五代十国", "宋", "辽", "金", "元", "明", "清", "民国", "现代"]
        for tag in tags:
            tag_name = tag.get("name", "").strip()
            # 检查标签是否为朝代名称
            if tag_name in dynasties:
                formatted["dynasty"] = tag_name
            # 检查标签是否为年份（4位数字）
            if re.match(r"^\d{4}$", tag_name):
                formatted["year"] = tag_name
        
        # 构建元数据
        formatted["metadata"] = {
            "category": formatted.get("category"),
            "dynasty": formatted.get("dynasty"),
            "read_time": self._estimate_read_time(formatted.get("content", "")),
            "word_count": len(formatted.get("content", "")),
            "publish_date": formatted.get("created_at"),
            "last_updated": formatted.get("updated_at")
        }
        
        # 构建统计信息
        formatted["stats"] = {
            "views": formatted.get("views", 0),
            "likes": formatted.get("likes", 0),
            "comments": 0,  # 暂时没有评论功能
            "bookmarks": 0  # 可以通过favorites表查询
        }
        
        # 获取相关文章
        tag_names = [tag.get("name") for tag in tags]
        formatted["related_articles"] = await self.get_related_articles(
            knowledge_id,
            dynasty=formatted.get("dynasty"),
            category=formatted.get("category"),
            tags=tag_names,
            limit=6
        )
        
        return formatted
    
    def _estimate_read_time(self, content: str) -> int:
        """估算阅读时间（分钟）"""
        if not content:
            return 0
        # 假设每分钟阅读200字
        word_count = len(content)
        return max(1, (word_count + 199) // 200)
    
    async def search(
        self,
        keyword: str,
        dynasty: Optional[str] = None,
        tags: Optional[str] = None,
        page: int = 0,
        size: int = 20
    ) -> Dict[str, Any]:
        """搜索知识库"""
        # 生成缓存键
        cache_key = f"search:knowledge:{keyword}:{dynasty or ''}:{tags or ''}:{page}:{size}"
        
        # 先查缓存
        cached_result = await self.redis_client.get(cache_key)
        if cached_result:
            return cached_result
        
        # 查数据库
        result = await self.database_client.search_knowledge(keyword, dynasty, tags, page, size)
        if not result:
            result = {"items": [], "total": 0, "page": page, "size": size}
        
        # 格式化数据
        items = result.get("items", [])
        formatted_items = []
        for item in items:
            formatted = self._format_article(item, include_content=False)
            # 获取文章标签
            tags = await self.database_client.get_knowledge_tags(item.get("id", 0))
            formatted["tags"] = [{"id": tag.get("id"), "name": tag.get("name"), "type": tag.get("type")} for tag in tags]
            formatted_items.append(formatted)
        
        formatted_result = {
            "items": formatted_items,
            "total": result.get("total", 0),
            "page": page,
            "size": size
        }
        
        # 缓存结果
        await self.redis_client.set(
            cache_key,
            formatted_result,
            timeout=settings.cache_search_result_ttl
        )
        
        return formatted_result
    
    async def get_home(
        self,
        category: Optional[str] = None,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取知识库首页数据"""
        # 获取分类列表
        categories = await self.database_client.get_knowledge_categories()
        
        # 获取朝代列表
        dynasties = await self.database_client.get_knowledge_dynasties()
        
        # 获取推荐文章（按浏览量排序，取前6条）
        featured_result = await self.database_client.get_knowledge_list(
            page=0,
            size=6,
            keyword=None,
            dynasty=period,
            category=category
        )
        featured_items = featured_result.get("items", []) if featured_result else []
        featured = [self._format_article(item, include_content=False) for item in featured_items]
        
        # 获取最新文章（取前10条）
        recent_result = await self.database_client.get_knowledge_list(
            page=0,
            size=10,
            keyword=None,
            dynasty=None,
            category=None
        )
        recent_items = recent_result.get("items", []) if recent_result else []
        recent_articles = [self._format_article(item, include_content=False) for item in recent_items]
        
        return {
            "categories": [{"name": cat.get("category"), "count": cat.get("count", 0)} for cat in categories],
            "dynasties": [{"name": dyn.get("dynasty"), "count": dyn.get("count", 0)} for dyn in dynasties],
            "featured": featured,
            "recent_articles": recent_articles
        }
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """获取分类列表"""
        categories = await self.database_client.get_knowledge_categories()
        return [{"name": cat.get("category"), "count": cat.get("count", 0)} for cat in categories]
    
    async def get_dynasties(self) -> List[Dict[str, Any]]:
        """获取朝代列表"""
        dynasties = await self.database_client.get_knowledge_dynasties()
        return [{"name": dyn.get("dynasty"), "count": dyn.get("count", 0)} for dyn in dynasties]
    
    async def increment_views(self, article_id: int) -> bool:
        """增加文章查看次数"""
        affected_rows = await self.database_client.increment_knowledge_views(article_id)
        return affected_rows > 0
    
    async def close(self):
        """关闭客户端连接"""
        await self.database_client.close()
        await self.redis_client.close()

