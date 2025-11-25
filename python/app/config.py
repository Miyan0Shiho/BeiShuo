from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "碑说后端服务"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8080
    
    # 数据库服务配置
    database_api_base_url: str = "http://localhost:8081/api/database"
    database_api_connect_timeout: int = 5000
    database_api_read_timeout: int = 10000
    database_api_retry_times: int = 3
    
    # Redis服务配置
    redis_api_base_url: str = "http://localhost:8082/api/redis"
    redis_api_connect_timeout: int = 3000
    redis_api_read_timeout: int = 5000
    redis_api_retry_times: int = 3
    
    # LLM服务配置
    llm_api_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_api_key: str = ""
    llm_model: str = "qwen-flash"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    llm_timeout: int = 30000
    
    # RAG服务配置
    rag_api_base_url: str = "http://localhost:8083/api/rag"
    rag_api_connect_timeout: int = 5000
    rag_api_read_timeout: int = 15000
    rag_api_top_k: int = 5
    
    # JWT配置
    jwt_secret: str = "K8mN2pQ7vX4wZ9aB3cD5eF6gH1jL8nM0qR2sT4uV6wY8zA1bC3dE5fG7hI9jK0"
    jwt_expiration: int = 86400000  # 24小时
    jwt_refresh_expiration: int = 604800000  # 7天
    jwt_algorithm: str = "HS512"
    jwt_header: str = "Authorization"
    jwt_token_prefix: str = "Bearer "
    
    # 缓存配置
    cache_inscription_list_ttl: int = 300
    cache_knowledge_list_ttl: int = 600
    cache_search_result_ttl: int = 600
    cache_user_info_ttl: int = 1800
    
    # 文件上传配置
    file_upload_path: str = "./uploads"
    file_upload_max_size: int = 10485760  # 10MB
    file_upload_allowed_types: List[str] = ["jpg", "jpeg", "png", "webp"]
    file_upload_url_prefix: str = "/uploads"

    # 看典古籍OCR配置
    kandianguji_ocr_token: str = ""
    kandianguji_ocr_email: str = ""
    kandianguji_ocr_timeout: int = 15000
    
    # CORS配置
    cors_allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
    cors_allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allowed_headers: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_max_age: int = 3600
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/python-backend.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

