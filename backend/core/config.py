from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "碑说API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./beishuo.db"
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建上传目录
settings = Settings()
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)

# CORS配置
CORS_ORIGINS = ["*"]  # 生产环境应该设置具体的域名