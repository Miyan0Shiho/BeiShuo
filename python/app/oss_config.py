"""
OSS存储配置

功能：
- 阿里云OSS客户端配置
- 存储桶和路径配置
- 文件上传和下载配置
"""

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional


class OSSConfig(BaseSettings):
    """OSS配置类"""
    
    # 阿里云OSS配置
    oss_access_key_id: str = "LTAI5tQc1DW41aWNq68u2TWX"
    oss_access_key_secret: str = "ge9NjmCfitIq0VOM9LsiypeY31ghDn"
    oss_endpoint: str = "https://oss-cn-hangzhou.aliyuncs.com"
    oss_bucket_name: str = "beiwen1"
    oss_region: str = "oss-cn-hangzhou"
    
    # 存储路径配置
    oss_base_path: str = "inscription-images"
    oss_temp_path: str = "temp"
    
    # 上传配置
    oss_max_file_size: int = 10 * 1024 * 1024  # 10MB
    oss_allowed_extensions: list = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"]
    oss_timeout: int = 30
    
    class Config:
        env_file = ".env"
        env_prefix = "OSS_"


# 创建全局配置实例
oss_config = OSSConfig()