"""
临时文件清理服务

功能：
- 定期清理临时文件目录中的过期文件
- 支持配置清理间隔和文件保留时间
- 自动记录清理操作日志
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from app.config import settings

logger = logging.getLogger(__name__)


class TempFileCleaner:
    """临时文件清理服务"""
    
    def __init__(self, 
                 temp_dir: str = None,
                 cleanup_interval: int = 600,  # 清理间隔，默认10分钟
                 file_retention: int = 600):   # 文件保留时间，默认10分钟
        """初始化清理服务
        
        Args:
            temp_dir: 临时文件目录路径
            cleanup_interval: 清理间隔（秒）
            file_retention: 文件保留时间（秒）
        """
        self.temp_dir = Path(temp_dir or settings.file_upload_path) / "temp"
        self.cleanup_interval = cleanup_interval
        self.file_retention = file_retention
        self._running = False
        self._task = None
        
        # 确保临时目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"临时文件清理服务初始化完成")
        logger.info(f"临时目录: {self.temp_dir}")
        logger.info(f"清理间隔: {self.cleanup_interval}秒")
        logger.info(f"文件保留时间: {self.file_retention}秒")
    
    async def start(self):
        """启动清理服务"""
        if self._running:
            logger.warning("清理服务已经在运行中")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info("临时文件清理服务已启动")
    
    async def stop(self):
        """停止清理服务"""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("临时文件清理服务已停止")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            try:
                await self._cleanup_expired_files()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理过程中发生异常: {e}")
                await asyncio.sleep(60)  # 发生异常时等待1分钟再重试
    
    async def _cleanup_expired_files(self):
        """清理过期文件"""
        try:
            if not self.temp_dir.exists():
                logger.warning(f"临时文件目录不存在: {self.temp_dir}")
                return
            
            current_time = time.time()
            expired_files = []
            total_files = 0
            
            # 遍历临时目录中的所有文件
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    total_files += 1
                    
                    # 检查文件是否过期
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > self.file_retention:
                        expired_files.append(file_path)
            
            # 删除过期文件
            deleted_count = 0
            for file_path in expired_files:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"已删除过期临时文件: {file_path.name}")
                except Exception as e:
                    logger.error(f"删除文件失败 {file_path}: {e}")
            
            if expired_files:
                logger.info(f"清理完成: 总文件数={total_files}, 过期文件数={len(expired_files)}, 删除文件数={deleted_count}")
            else:
                logger.debug(f"无过期文件需要清理，当前临时文件数: {total_files}")
                
        except Exception as e:
            logger.error(f"清理过期文件时发生异常: {e}")
    
    async def cleanup_now(self) -> dict:
        """立即执行一次清理操作
        
        Returns:
            清理结果统计
        """
        try:
            if not self.temp_dir.exists():
                return {"status": "error", "message": "临时文件目录不存在"}
            
            current_time = time.time()
            expired_files = []
            total_files = 0
            
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    total_files += 1
                    
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > self.file_retention:
                        expired_files.append(file_path)
            
            deleted_count = 0
            for file_path in expired_files:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"删除文件失败 {file_path}: {e}")
            
            result = {
                "status": "success",
                "total_files": total_files,
                "expired_files": len(expired_files),
                "deleted_files": deleted_count,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"立即清理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"立即清理时发生异常: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_status(self) -> dict:
        """获取服务状态"""
        return {
            "running": self._running,
            "temp_dir": str(self.temp_dir),
            "cleanup_interval": self.cleanup_interval,
            "file_retention": self.file_retention,
            "temp_dir_exists": self.temp_dir.exists()
        }


# 全局清理服务实例
temp_file_cleaner = TempFileCleaner()