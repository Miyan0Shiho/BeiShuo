"""
OCR缓存服务 - 基于现有ocr_images和ocr_jobs表结构

功能：
- 基于图片哈希的OCR结果缓存
- 利用现有表结构实现高性能缓存
- 支持缓存状态管理和清理
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..client.mysql_client import mysql_client

logger = logging.getLogger(__name__)


class OCRCacheService:
    """OCR缓存服务类"""
    
    def __init__(self):
        self.db = mysql_client
    
    def generate_image_hash(self, image_data: bytes) -> str:
        """生成图片哈希值"""
        return hashlib.sha256(image_data).hexdigest()
    
    def generate_image_hash_from_str(self, image_str: str) -> str:
        """从字符串生成图片哈希值（用于测试）
        
        Args:
            image_str: 图片字符串
            
        Returns:
            图片哈希字符串
        """
        return hashlib.sha256(image_str.encode('utf-8')).hexdigest()
    
    async def get_cached_ocr(self, image_hash: str, vendor: str = "kandianguji") -> Optional[Dict[str, Any]]:
        """
        根据图片哈希获取缓存的OCR结果
        
        Args:
            image_hash: 图片哈希值
            vendor: OCR服务提供商
            
        Returns:
            OCR结果字典，如果未命中缓存则返回None
        """
        try:
            # 查询ocr_images表 - 根据实际的表结构调整
            query = """
                SELECT oi.id, oi.job_id, oi.width, oi.height, oi.text_angel, 
                       oi.text_angel_confidence, oi.version, oi.det_mode, 
                       oi.det_layout, oi.only_plain_text, oi.return_layout, 
                       oi.auto_insert_space, oi.hp_line_words_angel, 
                       oi.sp_line_words_angel, oi.char_ocr, oi.image_size,
                       oj.confidence, oj.duration_ms, oj.created_at, oj.params
                FROM ocr_images oi
                JOIN ocr_jobs oj ON oi.job_id = oj.id
                WHERE oj.vendor = %s AND oj.status = 'success' AND oj.params LIKE %s
                AND oi.id = (SELECT MAX(id) FROM ocr_images WHERE job_id = oj.id)
                LIMIT 1
            """
            
            # 在params中查找image_hash - 使用更精确的模式匹配
            hash_pattern = f'%"image_hash":"{image_hash}"%'
            result = await self.db.execute_query(query, (vendor, hash_pattern))
            
            if result:
                # 尝试从params中提取OCR文本数据
                params = json.loads(result[0]['params']) if result[0]['params'] else {}
                
                # 构建完整的OCR结果
                return {
                    'id': result[0]['id'],
                    'job_id': result[0]['job_id'],
                    'width': result[0]['width'],
                    'height': result[0]['height'],
                    'confidence': result[0]['confidence'],
                    'duration_ms': result[0]['duration_ms'],
                    'created_at': result[0]['created_at'],
                    # 添加OCR文本数据占位符
                    'text': params.get('text', ''),
                    'word_count': params.get('word_count', 0),
                    'text_lines': params.get('text_lines', []),
                    'texts': params.get('texts', []),
                    'layout': params.get('layout', None)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取OCR缓存失败: {e}")
            return None
    
    async def cache_ocr_result(
        self, 
        image_hash: str, 
        image_data: bytes, 
        ocr_result: Dict[str, Any],
        vendor: str = "kandianguji",
        asset_id: int = None
    ) -> bool:
        """
        缓存OCR结果到数据库
        
        Args:
            image_hash: 图片哈希值
            image_data: 图片原始数据
            ocr_result: OCR识别结果
            vendor: OCR服务提供商
            asset_id: 关联的asset_id（可选）
            
        Returns:
            缓存是否成功
        """
        try:
            # 先检查是否已存在
            existing = await self.get_cached_ocr(image_hash, vendor)
            if existing:
                logger.info(f"OCR结果已存在，跳过缓存: {image_hash}")
                return True
            
            # 插入ocr_jobs记录
            job_query = """
                INSERT INTO ocr_jobs (
                    asset_id, status, vendor, params, confidence, 
                    duration_ms, retries, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 这里asset_id使用传入的asset_id
            job_params = {
                'vendor': vendor,
                'image_size': len(image_data),
                'image_hash': image_hash,  # 添加image_hash用于查询
                # 添加完整的OCR文本数据，便于缓存查询
                'text': ocr_result.get('full_text', ''),
                'word_count': ocr_result.get('word_count', 0),
                'text_lines': ocr_result.get('text_lines', []),
                'texts': ocr_result.get('texts', []),
                'layout': ocr_result.get('layout', None)
            }
            
            job_values = (
                asset_id,  # asset_id
                'success',  # status
                vendor,  # vendor
                json.dumps(job_params),  # params
                ocr_result.get('confidence', 0.0),  # confidence
                ocr_result.get('duration_ms', 0),  # duration_ms
                0,  # retries
                datetime.now(),  # created_at
                datetime.now()  # updated_at
            )
            
            job_id = await self.db.execute_insert(job_query, job_values)
            
            # 插入ocr_images记录 - 根据实际的表结构调整
            image_query = """
                INSERT INTO ocr_images (
                    job_id, width, height, text_angel, text_angel_confidence, 
                    version, det_mode, det_layout, only_plain_text, return_layout,
                    auto_insert_space, hp_line_words_angel, sp_line_words_angel,
                    char_ocr, image_size, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            image_values = (
                job_id,  # job_id
                ocr_result.get('width', 0), ocr_result.get('height', 0),
                ocr_result.get('text_angel', 0), ocr_result.get('text_angel_confidence', 0),
                ocr_result.get('version', 'default'), ocr_result.get('det_mode', 'auto'),
                ocr_result.get('det_layout', 0), ocr_result.get('only_plain_text', 0),  # det_layout改为整数
                ocr_result.get('return_layout', 0), ocr_result.get('auto_insert_space', 0),
                ocr_result.get('hp_line_words_angel', 0), ocr_result.get('sp_line_words_angel', 0),
                ocr_result.get('char_ocr', 0), len(image_data)  # image_size, char_ocr改为整数
            )
            
            await self.db.execute_insert(image_query, image_values)
            
            logger.info(f"OCR结果缓存成功: {image_hash}")
            return True
            
        except Exception as e:
            logger.error(f"缓存OCR结果失败: {e}")
            return False
    
    async def cleanup_expired_ocr(self, max_age_days: int = 30) -> int:
        """
        清理过期的OCR缓存
        
        Args:
            max_age_days: 最大保留天数
            
        Returns:
            删除的记录数
        """
        try:
            # 删除超过指定天数的记录（由于没有hit_count字段，简化清理逻辑）
            delete_query = """
                DELETE oj FROM ocr_jobs oj
                WHERE oj.created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                AND oj.status = 'success'
            """
            
            result = await self.db.execute_delete(delete_query, (max_age_days,))
            logger.info(f"清理了 {result} 条过期OCR缓存记录")
            return result
            
        except Exception as e:
            logger.error(f"清理过期OCR缓存失败: {e}")
            return 0
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """获取OCR缓存统计信息
        
        Returns:
            缓存统计信息字典
        """
        try:
            # 总缓存数量
            total_query = "SELECT COUNT(*) as total FROM ocr_jobs WHERE status = 'success'"
            total_result = await self.db.execute_query(total_query)
            total_count = total_result[0]['total'] if total_result else 0
            
            # 今日新增缓存
            today_query = """
                SELECT COUNT(*) as today_count 
                FROM ocr_jobs 
                WHERE status = 'success' AND DATE(created_at) = CURDATE()
            """
            today_result = await self.db.execute_query(today_query)
            today_count = today_result[0]['today_count'] if today_result else 0
            
            # 不同供应商的缓存分布
            vendor_query = """
                SELECT vendor, COUNT(*) as count 
                FROM ocr_jobs 
                WHERE status = 'success' 
                GROUP BY vendor
            """
            vendor_result = await self.db.execute_query(vendor_query)
            vendor_distribution = {row['vendor']: row['count'] for row in vendor_result} if vendor_result else {}
            
            # 平均置信度
            confidence_query = """
                SELECT AVG(confidence) as avg_confidence 
                FROM ocr_jobs 
                WHERE status = 'success' AND confidence IS NOT NULL
            """
            confidence_result = await self.db.execute_query(confidence_query)
            avg_confidence = float(confidence_result[0]['avg_confidence']) if confidence_result and confidence_result[0]['avg_confidence'] else 0.0
            
            return {
                'total_count': total_count,
                'today_count': today_count,
                'vendor_distribution': vendor_distribution,
                'avg_confidence': avg_confidence,
                'cache_size_mb': 0,  # 需要额外计算
                'last_cleanup': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取OCR缓存统计信息失败: {e}")
            return {
                'total_count': 0,
                'today_count': 0,
                'vendor_distribution': {},
                'avg_confidence': 0.0,
                'cache_size_mb': 0,
                'last_cleanup': None
            }


# 全局OCR缓存服务实例
ocr_cache_service = OCRCacheService()