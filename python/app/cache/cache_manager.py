"""
缓存管理器 - 统一管理OCR和LLM缓存服务

功能：
- 提供统一的缓存服务接口
- 管理缓存服务的初始化和关闭
- 提供缓存统计和监控功能
"""

import logging
from typing import Dict, Any

from .ocr_cache_service import ocr_cache_service
from .llm_cache_service import llm_cache_service
from ..client.mysql_client import init_mysql, close_mysql

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器类"""
    
    def __init__(self):
        self.ocr_service = ocr_cache_service
        self.llm_service = llm_cache_service
        self.is_initialized = False
    
    async def initialize(self):
        """初始化缓存服务"""
        try:
            await init_mysql()
            self.is_initialized = True
            logger.info("缓存管理器初始化成功")
        except Exception as e:
            logger.error(f"缓存管理器初始化失败: {e}")
            raise
    
    async def close(self):
        """关闭缓存服务"""
        try:
            await close_mysql()
            self.is_initialized = False
            logger.info("缓存管理器已关闭")
        except Exception as e:
            logger.error(f"缓存管理器关闭失败: {e}")
    
    async def health_check(self) -> Dict[str, bool]:
        """缓存服务健康检查"""
        try:
            if not self.is_initialized:
                return {'mysql': False, 'ocr_cache': False, 'llm_cache': False}
            
            # 检查MySQL连接
            mysql_health = await self.ocr_service.db.health_check()
            
            # 检查OCR缓存表
            ocr_count = await self.ocr_service.get_cache_statistics()
            ocr_health = ocr_count['total_count'] >= 0  # 只要查询成功就认为健康
            
            # 检查LLM缓存表
            llm_count = await self.llm_service.get_cache_statistics()
            llm_health = llm_count['total_count'] >= 0  # 只要查询成功就认为健康
            
            return {
                'mysql': mysql_health,
                'ocr_cache': ocr_health,
                'llm_cache': llm_health
            }
            
        except Exception as e:
            logger.error(f"缓存服务健康检查失败: {e}")
            return {'mysql': False, 'ocr_cache': False, 'llm_cache': False}
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """获取所有缓存服务的统计信息"""
        try:
            ocr_stats = await self.ocr_service.get_cache_statistics()
            llm_stats = await self.llm_service.get_cache_statistics()
            
            return {
                'ocr_cache': ocr_stats,
                'llm_cache': llm_stats,
                'total_entries': ocr_stats.get('total_count', 0) + llm_stats.get('total_count', 0),
                'total_hits': llm_stats.get('total_hits', 0),  # OCR缓存没有hit_count字段
                'vendor_distribution': ocr_stats.get('vendor_distribution', {}),
                'model_distribution': llm_stats.get('model_distribution', {})
            }
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {
                'ocr_cache': {'total_count': 0, 'today_count': 0, 'vendor_distribution': {}, 'avg_confidence': 0.0},
                'llm_cache': {'total_count': 0, 'avg_hits': 0.0, 'total_hits': 0, 'model_distribution': {}},
                'total_entries': 0,
                'total_hits': 0,
                'vendor_distribution': {},
                'model_distribution': {}
            }
    
    async def cleanup_cache(self, days: int = 30) -> Dict[str, int]:
        """清理所有过期的缓存"""
        try:
            ocr_cleaned = await self.ocr_service.cleanup_expired_ocr(days)
            llm_cleaned = await self.llm_service.cleanup_expired_llm(days)
            
            return {
                'ocr_cache_cleaned': ocr_cleaned,
                'llm_cache_cleaned': llm_cleaned,
                'total_cleaned': ocr_cleaned + llm_cleaned
            }
            
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return {
                'ocr_cache_cleaned': 0,
                'llm_cache_cleaned': 0,
                'total_cleaned': 0
            }
    
    async def get_top_hit_cache(self, limit: int = 10) -> Dict[str, list]:
        """获取各缓存服务的高命中记录"""
        try:
            # OCR缓存目前没有hit_count字段，暂时返回空列表
            ocr_top_hits = []
            llm_top_hits = await self.llm_service.get_top_hit_cache(limit)
            
            return {
                'ocr_cache_top_hits': ocr_top_hits,
                'llm_cache_top_hits': llm_top_hits
            }
            
        except Exception as e:
            logger.error(f"获取高命中缓存失败: {e}")
            return {
                'ocr_cache_top_hits': [],
                'llm_cache_top_hits': []
            }


# 全局缓存管理器实例
cache_manager = CacheManager()