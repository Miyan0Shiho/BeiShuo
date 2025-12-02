"""
管理接口

功能：
- 临时文件清理服务管理
- 系统状态监控
"""

from fastapi import APIRouter, HTTPException
from app.common.response import Result
from app.services.temp_file_cleaner import temp_file_cleaner

router = APIRouter(prefix="/admin", tags=["管理接口"])


@router.get("/temp-cleaner/status")
async def get_temp_cleaner_status():
    """获取临时文件清理服务状态"""
    try:
        status = temp_file_cleaner.get_status()
        return Result.success(status)
    except Exception as e:
        return Result.fail(str(e))


@router.post("/temp-cleaner/cleanup")
async def trigger_temp_cleanup():
    """立即触发临时文件清理"""
    try:
        result = await temp_file_cleaner.cleanup_now()
        return Result.success(result)
    except Exception as e:
        return Result.fail(str(e))


@router.post("/temp-cleaner/start")
async def start_temp_cleaner():
    """启动临时文件清理服务"""
    try:
        await temp_file_cleaner.start()
        return Result.success("临时文件清理服务已启动")
    except Exception as e:
        return Result.fail(str(e))


@router.post("/temp-cleaner/stop")
async def stop_temp_cleaner():
    """停止临时文件清理服务"""
    try:
        await temp_file_cleaner.stop()
        return Result.success("临时文件清理服务已停止")
    except Exception as e:
        return Result.fail(str(e))