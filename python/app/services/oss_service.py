"""
OSS存储服务

功能：
- 图片上传到阿里云OSS
- 文件管理和下载
- 生成访问URL
- 文件哈希计算和去重
"""

import asyncio
import hashlib
import logging
import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, Dict, Any, Tuple

import oss2
from app.oss_config import oss_config
from app.client.mysql_client import mysql_client

logger = logging.getLogger(__name__)


class OSSService:
    """OSS存储服务类"""
    
    def __init__(self):
        self.config = oss_config
        self.auth = None
        self.bucket = None
        self.db = mysql_client
        self._initialize_oss()
    
    def _initialize_oss(self):
        """初始化OSS客户端"""
        try:
            # 创建认证对象
            self.auth = oss2.Auth(
                self.config.oss_access_key_id,
                self.config.oss_access_key_secret
            )
            
            # 创建Bucket对象
            self.bucket = oss2.Bucket(
                self.auth,
                self.config.oss_endpoint,
                self.config.oss_bucket_name
            )
            
            logger.info(f"OSS客户端初始化成功: bucket={self.config.oss_bucket_name}")
            
        except Exception as e:
            logger.error(f"OSS客户端初始化失败: {e}")
            raise
    
    def _generate_object_key(self, filename: str, file_hash: str = None) -> str:
        """
        生成OSS对象存储键
        
        Args:
            filename: 原始文件名
            file_hash: 文件哈希值（用于去重）
            
        Returns:
            OSS对象键
        """
        # 获取文件扩展名
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            ext = ".jpg"  # 默认扩展名
        
        # 使用文件哈希或UUID生成唯一文件名
        if file_hash:
            filename_part = file_hash[:16]  # 使用前16位哈希作为文件名
        else:
            filename_part = str(uuid.uuid4())[:8]  # 使用UUID前8位
        
        # 生成日期路径
        date_path = datetime.now().strftime("%Y/%m/%d")
        
        # 构建完整路径
        object_key = f"{self.config.oss_base_path}/{date_path}/{filename_part}{ext}"
        
        return object_key
    
    def calculate_file_hash(self, file_data: bytes) -> str:
        """计算文件SHA256哈希值"""
        return hashlib.sha256(file_data).hexdigest()
    
    async def upload_image(self, image_data: bytes, filename: str, 
                          inscription_id: Optional[int] = None) -> Dict[str, Any]:
        """
        上传图片到OSS并创建asset记录
        
        Args:
            image_data: 图片数据
            filename: 原始文件名
            inscription_id: 关联的碑刻ID（可选）
            
        Returns:
            包含asset_id和OSS信息的字典
        """
        try:
            # 计算文件哈希
            file_hash = self.calculate_file_hash(image_data)
            
            # 检查是否已存在相同文件
            existing_asset = await self._get_asset_by_hash(file_hash)
            if existing_asset:
                logger.info(f"文件已存在，复用asset记录: asset_id={existing_asset['id']}")
                return existing_asset
            
            # 生成OSS对象键
            object_key = self._generate_object_key(filename, file_hash)
            
            # 上传文件到OSS
            result = await self._upload_to_oss(object_key, image_data)
            
            if not result:
                raise Exception("OSS上传失败")
            
            # 创建asset记录
            asset_data = {
                'inscription_id': inscription_id,
                'type': 'image',
                'object_path': object_key,
                'mime_type': self._detect_mime_type(filename),
                'size_bytes': len(image_data),
                'hash_md5': hashlib.md5(image_data).hexdigest(),
                'sha256': file_hash,
                'storage_provider': 'oss'
            }
            
            asset_id = await self._create_asset_record(asset_data)
            
            if not asset_id:
                raise Exception("创建asset记录失败")
            
            logger.info(f"图片上传成功: asset_id={asset_id}, object_key={object_key}")
            
            return {
                'asset_id': asset_id,
                'object_key': object_key,
                'file_hash': file_hash,
                'url': self._generate_url(object_key)
            }
            
        except Exception as e:
            logger.error(f"图片上传失败: {e}")
            raise
    
    async def _get_asset_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """根据文件哈希查询已存在的asset记录"""
        try:
            query = """
                SELECT id, inscription_id, type, object_path, mime_type, size_bytes,
                       hash_md5, sha256, storage_provider, created_at
                FROM inscription_assets
                WHERE sha256 = %s
                LIMIT 1
            """
            
            result = await self.db.execute_query(query, (file_hash,))
            if result:
                return {
                    'id': result[0]['id'],
                    'asset_id': result[0]['id'],
                    'object_key': result[0]['object_path'],
                    'file_hash': result[0]['sha256'],
                    'url': self._generate_url(result[0]['object_path'])
                }
            return None
            
        except Exception as e:
            logger.error(f"查询asset记录失败: {e}")
            return None
    
    async def _upload_to_oss(self, object_key: str, file_data: bytes) -> bool:
        """异步上传文件到OSS"""
        try:
            # 使用线程池执行同步的OSS上传操作
            loop = asyncio.get_event_loop()
            
            def sync_upload():
                return self.bucket.put_object(object_key, file_data)
            
            result = await loop.run_in_executor(None, sync_upload)
            
            if result.status == 200:
                logger.info(f"OSS上传成功: {object_key}")
                return True
            else:
                logger.error(f"OSS上传失败: {result.status}")
                return False
                
        except Exception as e:
            logger.error(f"OSS上传异常: {e}")
            return False
    
    async def _create_asset_record(self, asset_data: Dict[str, Any]) -> Optional[int]:
        """创建asset记录"""
        try:
            query = """
                INSERT INTO inscription_assets 
                (inscription_id, type, object_path, mime_type, size_bytes, 
                 hash_md5, sha256, storage_provider, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            params = (
                asset_data['inscription_id'],
                asset_data['type'],
                asset_data['object_path'],
                asset_data['mime_type'],
                asset_data['size_bytes'],
                asset_data['hash_md5'],
                asset_data['sha256'],
                asset_data['storage_provider']
            )
            
            asset_id = await self.db.execute_insert(query, params)
            return asset_id
            
        except Exception as e:
            logger.error(f"创建asset记录异常: {e}")
            return None
    
    def _detect_mime_type(self, filename: str) -> str:
        """检测文件MIME类型"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.pdf': 'application/pdf'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _generate_url(self, object_key: str, expires: int = 3600) -> str:
        """生成文件访问URL"""
        try:
            # 生成带签名的URL
            url = self.bucket.sign_url('GET', object_key, expires)
            return url
        except Exception as e:
            logger.error(f"生成URL失败: {e}")
            return f"https://{self.config.oss_bucket_name}.{self.config.oss_region}.aliyuncs.com/{object_key}"
    
    async def download_file(self, object_key: str) -> Optional[bytes]:
        """从OSS下载文件"""
        try:
            loop = asyncio.get_event_loop()
            
            def sync_download():
                result = self.bucket.get_object(object_key)
                return result.read()
            
            file_data = await loop.run_in_executor(None, sync_download)
            return file_data
            
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            return None
    
    async def delete_file(self, object_key: str) -> bool:
        """删除OSS文件"""
        try:
            loop = asyncio.get_event_loop()
            
            def sync_delete():
                self.bucket.delete_object(object_key)
                return True
            
            result = await loop.run_in_executor(None, sync_delete)
            logger.info(f"文件删除成功: {object_key}")
            return result
            
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False


# 创建全局OSS服务实例
oss_service = OSSService()