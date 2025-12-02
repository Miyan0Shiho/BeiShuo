"""
OCR缓存服务 - 基于现有ocr_images和ocr_jobs表结构

功能：
- 基于图片哈希的OCR结果缓存
- 集成OSS存储，先上传图片再创建asset记录
- 利用现有表结构实现高性能缓存
- 支持缓存状态管理和清理
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..client.mysql_client import mysql_client
from ..services.oss_service import oss_service

logger = logging.getLogger(__name__)


class OCRCacheService:
    """OCR缓存服务类"""
    
    def __init__(self):
        self.db = mysql_client
        self.oss = oss_service
    
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
                WHERE oj.vendor = %s AND oj.status = 'success' 
                AND JSON_UNQUOTE(JSON_EXTRACT(oj.params, '$.image_hash')) = %s
                AND oi.id = (SELECT MAX(id) FROM ocr_images WHERE job_id = oj.id)
                LIMIT 1
            """
            
            # 使用JSON_UNQUOTE去掉JSON_EXTRACT返回的引号，精确匹配image_hash
            result = await self.db.execute_query(query, (vendor, image_hash))
            
            if result:
                # 尝试从params中提取OCR文本数据
                params = json.loads(result[0]['params']) if result[0]['params'] else {}
                
                # 确保confidence字段是JSON可序列化的类型（Decimal转换为float）
                confidence = result[0]['confidence']
                if hasattr(confidence, 'as_integer_ratio'):  # 检查是否为Decimal类型
                    confidence = float(confidence)
                
                # 构建完整的OCR结果
                return {
                    'id': result[0]['id'],
                    'job_id': result[0]['job_id'],
                    'width': result[0]['width'],
                    'height': result[0]['height'],
                    'confidence': confidence,
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
    
    async def upload_image_and_create_asset(self, image_data: bytes, filename: str, 
                                          inscription_id: Optional[int] = None) -> Optional[int]:
        """
        上传图片到OSS并创建asset记录
        
        Args:
            image_data: 图片数据
            filename: 原始文件名
            inscription_id: 关联的碑刻ID（可选）
            
        Returns:
            asset_id，如果失败则返回None
        """
        try:
            # 上传图片到OSS并创建asset记录
            upload_result = await self.oss.upload_image(image_data, filename, inscription_id)
            
            if upload_result and 'asset_id' in upload_result:
                logger.info(f"图片上传成功，asset_id={upload_result['asset_id']}")
                return upload_result['asset_id']
            else:
                logger.error("图片上传失败，无法获取asset_id")
                return None
                
        except Exception as e:
            logger.error(f"上传图片并创建asset记录失败: {e}")
            return None
    
    async def cache_ocr_result(self, image_data: bytes, filename: str, ocr_result: Dict[str, Any], 
                              vendor: str = "kandianguji", inscription_id: Optional[int] = None) -> bool:
        """
        缓存OCR识别结果（先上传图片到OSS，再创建asset记录）
        
        Args:
            image_data: 图片数据
            filename: 原始文件名
            ocr_result: OCR识别结果
            vendor: OCR服务提供商
            inscription_id: 关联的碑刻ID（可选）
            
        Returns:
            缓存是否成功
        """
        try:
            # 生成图片哈希
            image_hash = self.generate_image_hash(image_data)
            
            # 检查是否已存在缓存
            existing_cache = await self.get_cached_ocr(image_hash, vendor)
            if existing_cache:
                logger.info(f"OCR缓存已存在，跳过缓存: image_hash={image_hash}")
                return True
            
            # 上传图片到OSS并创建asset记录
            asset_id = await self.upload_image_and_create_asset(image_data, filename, inscription_id)
            
            if not asset_id:
                logger.error("创建asset记录失败，无法缓存OCR结果")
                return False
            
            # 插入ocr_jobs记录
            job_query = """
                INSERT INTO ocr_jobs (asset_id, status, vendor, params, confidence, duration_ms, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            # 构建params，确保包含image_hash
            params = {
                'image_hash': image_hash,
                'text': ocr_result.get('text', ''),
                'word_count': ocr_result.get('word_count', 0),
                'text_lines': ocr_result.get('text_lines', []),
                'texts': ocr_result.get('texts', []),
                'layout': ocr_result.get('layout', None),
                'filename': filename,
                'inscription_id': inscription_id
            }
            
            # 使用从OSS上传获得的asset_id
            
            # 确保params正确序列化为JSON
            job_id = await self.db.execute_insert(
                job_query, 
                (asset_id, 'success', vendor, json.dumps(params, ensure_ascii=False), 
                 ocr_result.get('confidence', 0.0), ocr_result.get('duration_ms', 0))
            )
            
            if not job_id:
                logger.error("插入ocr_jobs记录失败")
                return False
            
            # 插入ocr_images记录
            image_query = """
                INSERT INTO ocr_images (job_id, width, height, text_angel, text_angel_confidence, 
                                       version, det_mode, det_layout, only_plain_text, return_layout, 
                                       auto_insert_space, hp_line_words_angel, sp_line_words_angel, 
                                       char_ocr, image_size, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            # 处理version字段，确保使用数据库允许的枚举值
            version_value = ocr_result.get('version', 'default')
            # 数据库允许的枚举值：'default', 'beta', 'v2'
            allowed_versions = ['default', 'beta', 'v2']
            if version_value not in allowed_versions:
                version_value = 'default'  # 如果不允许，使用默认值
            
            # 处理det_mode字段，确保使用数据库允许的枚举值
            det_mode_value = ocr_result.get('det_mode', 'auto')
            # 数据库允许的枚举值：'auto', 'sp', 'hp'
            allowed_det_modes = ['auto', 'sp', 'hp']
            if det_mode_value not in allowed_det_modes:
                det_mode_value = 'auto'  # 如果不允许，使用默认值
            
            # 处理hp_line_words_angel字段，确保使用数据库允许的枚举值
            hp_line_words_angel_value = ocr_result.get('hp_line_words_angel', 'left2right')
            # 数据库允许的枚举值：'left2right', 'right2left'
            allowed_hp_line_words_angel = ['left2right', 'right2left']
            if hp_line_words_angel_value not in allowed_hp_line_words_angel:
                hp_line_words_angel_value = 'left2right'  # 如果不允许，使用默认值
            
            # 处理sp_line_words_angel字段，确保使用数据库允许的枚举值
            sp_line_words_angel_value = ocr_result.get('sp_line_words_angel', 'top2bottom')
            # 数据库允许的枚举值：'top2bottom', 'bottom2top'
            allowed_sp_line_words_angel = ['top2bottom', 'bottom2top']
            if sp_line_words_angel_value not in allowed_sp_line_words_angel:
                sp_line_words_angel_value = 'top2bottom'  # 如果不允许，使用默认值
            
            image_id = await self.db.execute_insert(
                image_query,
                (job_id, ocr_result.get('width', 0), ocr_result.get('height', 0),
                 ocr_result.get('text_angel', 0.0), ocr_result.get('text_angel_confidence', 0.0),
                 version_value, det_mode_value,
                 ocr_result.get('det_layout', False), ocr_result.get('only_plain_text', False),
                 ocr_result.get('return_layout', False), ocr_result.get('auto_insert_space', True),
                 hp_line_words_angel_value, sp_line_words_angel_value,
                 ocr_result.get('char_ocr', False), ocr_result.get('image_size', 0))
            )
            
            if image_id:
                logger.info(f"OCR缓存成功: image_hash={image_hash}, job_id={job_id}, image_id={image_id}")
                return True
            else:
                logger.error("插入ocr_images记录失败")
                return False
                
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