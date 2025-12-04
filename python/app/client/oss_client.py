#!/usr/bin/env python3
"""
阿里云OSS客户端工具类，用于封装阿里云OSS的操作
"""

import os
import uuid
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


try:
    import oss2
except ImportError:
    logger.warning("aliyun oss2 library not found, please install it with: pip install oss2")
    oss2 = None


class OSSClient:
    """阿里云OSS客户端工具类"""
    
    def __init__(self):
        """初始化OSS客户端"""
        self.access_key_id = settings.aliyun_oss_access_key_id
        self.access_key_secret = settings.aliyun_oss_access_key_secret
        self.endpoint = settings.aliyun_oss_endpoint
        self.bucket_name = settings.aliyun_oss_bucket_name
        self.domain = settings.aliyun_oss_domain
        
        self.bucket = None
        self._init_client()
    
    def _init_client(self):
        """初始化OSS客户端"""
        if not oss2:
            logger.warning("OSS客户端未初始化：oss2库未安装")
            return
            
        if not all([self.access_key_id, self.access_key_secret, self.endpoint, self.bucket_name]):
            logger.warning("OSS客户端未初始化：缺少必要配置")
            return
        
        try:
            # 创建auth对象
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            # 创建bucket对象
            self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
            logger.info("OSS客户端初始化成功")
        except Exception as e:
            logger.error(f"OSS客户端初始化失败: {e}")
    
    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> Optional[str]:
        """
        上传本地文件到OSS
        
        Args:
            file_path: 本地文件路径
            object_name: OSS对象名称，若不提供则自动生成
            
        Returns:
            OSS文件URL
        """
        if not self.bucket:
            logger.error("OSS客户端未初始化，无法上传文件")
            return None
        
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None
        
        # 生成object_name
        if not object_name:
            file_ext = os.path.splitext(file_path)[1]
            object_name = f"uploads/{uuid.uuid4().hex}{file_ext}"
        
        try:
            # 上传文件
            self.bucket.put_object_from_file(object_name, file_path)
            logger.info(f"文件上传OSS成功: bucket={self.bucket_name}, object_name={object_name}")
            
            # 生成URL
            return self.get_file_url(object_name)
        except Exception as e:
            logger.error(f"文件上传OSS失败: bucket={self.bucket_name}, object_name={object_name}, error={e}")
            return None
    
    def upload_content(self, content: bytes, object_name: Optional[str] = None, content_type: str = "image/png") -> Optional[str]:
        """
        上传字节内容到OSS
        
        Args:
            content: 要上传的字节内容
            object_name: OSS对象名称，若不提供则自动生成
            content_type: 内容类型
            
        Returns:
            OSS文件URL
        """
        if not self.bucket:
            logger.error("OSS客户端未初始化，无法上传内容")
            return None
        
        # 生成object_name
        if not object_name:
            # 生成随机文件名
            object_name = f"uploads/{uuid.uuid4().hex}.png"
        
        try:
            # 上传内容
            self.bucket.put_object(object_name, content, headers={"Content-Type": content_type})
            logger.info(f"内容上传OSS成功: bucket={self.bucket_name}, object_name={object_name}")
            
            # 生成URL
            return self.get_file_url(object_name)
        except Exception as e:
            logger.error(f"内容上传OSS失败: bucket={self.bucket_name}, object_name={object_name}, error={e}")
            return None
    
    def get_file_url(self, object_name: str) -> Optional[str]:
        """
        获取OSS文件URL
        
        Args:
            object_name: OSS对象名称
            
        Returns:
            OSS文件URL
        """
        if not self.bucket:
            logger.error("OSS客户端未初始化，无法获取文件URL")
            return None
        
        try:
            # 生成签名URL，有效期365天
            url = self.bucket.sign_url('GET', object_name, 365 * 24 * 3600)
            
            # 如果配置了自定义域名，使用自定义域名
            if self.domain:
                # 替换URL中的endpoint为自定义域名
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                
                # 构建自定义域名的URL，直接使用domain作为主机名，保留路径和查询参数
                # 确保查询参数前有问号
                query_str = f"?{parsed_url.query}" if parsed_url.query else ''
                url = f"http://{self.domain}{parsed_url.path}{query_str}{parsed_url.fragment if parsed_url.fragment else ''}"
            
            logger.info(f"获取OSS文件URL成功: {url}")
            return url
        except Exception as e:
            logger.error(f"获取OSS文件URL失败: bucket={self.bucket_name}, object_name={object_name}, error={e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """
        删除OSS文件
        
        Args:
            object_name: OSS对象名称
            
        Returns:
            是否删除成功
        """
        if not self.bucket:
            logger.error("OSS客户端未初始化，无法删除文件")
            return False
        
        try:
            self.bucket.delete_object(object_name)
            logger.info(f"删除OSS文件成功: bucket={self.bucket_name}, object_name={object_name}")
            return True
        except Exception as e:
            logger.error(f"删除OSS文件失败: bucket={self.bucket_name}, object_name={object_name}, error={e}")
            return False
    
    def is_initialized(self) -> bool:
        """
        检查OSS客户端是否已初始化
        
        Returns:
            是否已初始化
        """
        return self.bucket is not None


# 创建全局OSS客户端实例
oss_client = OSSClient()