from fastapi import APIRouter, Depends, Query, Path, Body
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.inscription_service import InscriptionService
from app.utils.logger import logger
import uuid

router = APIRouter(prefix="/recognition", tags=["识别"])

@router.post("/start")
async def start_recognition(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """开始碑文识别"""
    image_id = request.get("image_id")
    language = request.get("language", "classical")
    options = request.get("options", {})
    
    if not image_id:
        return Result.error(ResultCode.BAD_REQUEST, "image_id不能为空")
    
    # TODO: 实现识别任务提交
    task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
    
    result = {
        "task_id": task_id,
        "status": "processing",
        "estimated_time": 30,
        "progress": 0
    }
    
    return Result.success("识别任务已开始", result)

@router.get("/progress/{task_id}")
async def get_recognition_progress(
    task_id: str = Path(..., description="任务ID"),
    user_id: int = Depends(get_current_user_id)
):
    """查询识别进度"""
    # TODO: 实现识别状态查询
    result = {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "result": {
            "recognition_id": f"rec_{int(datetime.now().timestamp() * 1000)}",
            "original_text": "",
            "modern_text": "",
            "confidence": 0.0,
            "word_count": 0,
            "dynasty": "",
            "period": "",
            "location": "",
            "person": "",
            "estimated_year": "",
            "processing_time": 0
        }
    }
    
    return Result.success(result)

@router.get("/history")
async def get_recognition_history(
    user_id: int = Depends(get_current_user_id),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    dynasty: Optional[str] = Query(None, description="筛选朝代"),
    sort: Optional[str] = Query("date_desc", description="排序方式")
):
    """获取识别历史记录"""
    service = InscriptionService()
    try:
        # 转换为后端分页格式（从1开始转为从0开始）
        page_index = page - 1
        sort_param = sort or "date_desc"
        
        # 调用服务层获取列表
        page_result = await service.get_list(user_id, page_index, per_page, sort_param, None)
        
        # 转换为前端期望的格式
        recognition_list = []
        for item in page_result.list:
            recognition_item = {
                "id": item.get("id"),
                "title": item.get("title", ""),
                "image_url": item.get("imageUrl", ""),
                "original_text": item.get("text", ""),
                "confidence": item.get("confidence", 0.0),
                "dynasty": item.get("dynasty", ""),
                "created_at": item.get("createdAt", datetime.now(timezone.utc).isoformat()),
                "is_favorited": item.get("isFavorited", False),
                "tags": item.get("tags", [])
            }
            recognition_list.append(recognition_item)
        
        pagination = {
            "current_page": page,
            "total_pages": page_result.totalPages if hasattr(page_result, 'totalPages') else (page_result.total + per_page - 1) // per_page,
            "total_count": page_result.total,
            "per_page": per_page
        }
        
        result = {
            "recognition_list": recognition_list,
            "pagination": pagination
        }
        
        return Result.success(result)
    finally:
        await service.close()

@router.put("/{recognition_id}/correct")
async def correct_recognition(
    recognition_id: str = Path(..., description="识别ID"),
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """更新识别结果（校对）"""
    corrected_text = request.get("corrected_text")
    corrections = request.get("corrections", [])
    notes = request.get("notes")
    
    if not corrected_text:
        return Result.error(ResultCode.BAD_REQUEST, "corrected_text不能为空")
    
    # 尝试从recognition_id中提取数字ID
    try:
        id_str = recognition_id.replace("rec_", "")
        inscription_id = int(id_str)
    except (ValueError, AttributeError):
        return Result.error(ResultCode.BAD_REQUEST, "无效的识别ID")
    
    service = InscriptionService()
    try:
        # 更新碑文
        update_data = {
            "correctedText": corrected_text
        }
        await service.update(inscription_id, user_id, update_data)
        
        result = {
            "recognition_id": recognition_id,
            "version": 2,
            "correction_count": len(corrections) if corrections else 0
        }
        
        return Result.success("校对结果已保存", result)
    finally:
        await service.close()

@router.get("/{recognition_id}/suggestions")
async def get_suggestions(
    recognition_id: str = Path(..., description="识别ID"),
    user_id: int = Depends(get_current_user_id)
):
    """获取校对建议"""
    # TODO: 实现校对建议功能
    result = {
        "suggestions": []
    }
    
    return Result.success(result)

@router.post("/{recognition_id}/history")
async def save_correction_history(
    recognition_id: str = Path(..., description="识别ID"),
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """保存校对记录"""
    # TODO: 实现校对记录保存
    return Result.success("校对记录已保存", None)

