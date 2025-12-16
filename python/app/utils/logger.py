import sys
from loguru import logger
from app.config import settings
import os

def setup_logger():
    """设置日志"""
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出 - 确保使用DEBUG级别
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",  # 明确设置为DEBUG级别
        colorize=True
    )
    
    # 文件输出
    log_file = settings.log_file
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("日志系统初始化完成")

