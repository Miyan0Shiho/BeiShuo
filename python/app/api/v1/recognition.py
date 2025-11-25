from fastapi import APIRouter, Depends, Query, Path, Body
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.inscription_service import InscriptionService
from app.utils.logger import logger
from app.config import settings
from app.client.kandianguji_ocr_client import KandiangujiOCRClient
import base64
import os
import uuid

router = APIRouter(prefix="/recognition", tags=["识别"])

def _normalize_ocr(data: Dict[str, Any]) -> Dict[str, Any]:
    width = data.get("width") or 0
    height = data.get("height") or 0
    text_angel = data.get("text_angel")
    texts: List[str] = data.get("texts") or []
    text_lines: List[Dict[str, Any]] = data.get("text_lines") or []
    full_text = "\n".join(texts) if texts else ("\n".join([tl.get("text") or "" for tl in text_lines]) if text_lines else (data.get("text") or ""))
    word_count = 0
    confidences: List[float] = []
    for tl in text_lines or []:
        words = tl.get("words") or []
        word_count += len(words)
        for w in words:
            c = w.get("confidence")
            if c is None:
                c = w.get("det_confidence")
            if isinstance(c, (int, float)):
                confidences.append(float(c))
    if word_count == 0 and full_text:
        word_count = len(full_text)
    avg_conf = 0.0
    if confidences:
        avg_conf = round(sum(confidences) / len(confidences), 2)
    elif isinstance(data.get("text_angel_confidence"), (int, float)):
        avg_conf = float(data.get("text_angel_confidence"))
    return {
        "width": width,
        "height": height,
        "text_angel": text_angel,
        "texts": texts,
        "text_lines": text_lines,
        "full_text": full_text or "",
        "word_count": word_count,
        "confidence": avg_conf,
        "layout": data.get("layout") or None,
    }

@router.post("/start")
async def start_recognition(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """开始碑文识别（接入看典古籍OCR）"""
    image_url = request.get("image_url")
    image_base64 = request.get("image_base64")
    options = request.get("options", {})

    if not image_url and not image_base64:
        return Result.fail(ResultCode.BAD_REQUEST, "image_url或image_base64至少提供一个")

    try:
        if not image_base64:
            if not isinstance(image_url, str) or not image_url.startswith(settings.file_upload_url_prefix):
                return Result.fail(ResultCode.BAD_REQUEST, "无效的image_url")
            filename = image_url.replace(settings.file_upload_url_prefix + "/", "")
            file_path = os.path.join(settings.file_upload_path, filename)
            if not os.path.exists(file_path):
                return Result.fail(ResultCode.BAD_REQUEST, "文件不存在或未上传")
            with open(file_path, "rb") as f:
                content = f.read()
            image_base64 = base64.b64encode(content).decode("utf-8")

        # 默认选项
        default_options = {
            "version": options.get("version", "v2"),
            "det_mode": options.get("det_mode", "auto"),
            "return_position": options.get("return_position", True),
            "return_choices": options.get("return_choices", False),
            "det_layout": options.get("det_layout", False),
            "only_plain_text": options.get("only_plain_text", False),
            "return_layout": options.get("return_layout", False),
            "auto_insert_space": options.get("auto_insert_space", False),
            "hp_line_words_angel": options.get("hp_line_words_angel", "left2right"),
            "sp_line_words_angel": options.get("sp_line_words_angel", "top2bottom"),
        }

        client = KandiangujiOCRClient()
        primary_options = {**default_options, "return_position": True}
        ocr_resp = await client.recognize(image_base64, primary_options)
        data = ocr_resp.get("data") or {}
        norm = _normalize_ocr(data)
        if not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0):
            fallback_sp = {**primary_options, "det_mode": "sp", "sp_line_words_angel": primary_options.get("sp_line_words_angel", "top2bottom")}
            try:
                ocr_resp = await client.recognize(image_base64, fallback_sp)
                norm = _normalize_ocr(ocr_resp.get("data") or {})
            except Exception:
                pass
        if not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0):
            fallback_hp = {**primary_options, "det_mode": "hp", "hp_line_words_angel": primary_options.get("hp_line_words_angel", "left2right")}
            try:
                ocr_resp = await client.recognize(image_base64, fallback_hp)
                norm = _normalize_ocr(ocr_resp.get("data") or {})
            except Exception:
                pass
        # 尝试版本回退（beta + sp）
        if not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0):
            fallback_beta_sp = {**primary_options, "version": "beta", "det_mode": "sp", "sp_line_words_angel": primary_options.get("sp_line_words_angel", "top2bottom")}
            try:
                ocr_resp = await client.recognize(image_base64, fallback_beta_sp)
                norm = _normalize_ocr(ocr_resp.get("data") or {})
            except Exception:
                pass

        recognition_id = f"rec_{int(datetime.now().timestamp() * 1000)}"
        task_id = f"task_{int(datetime.now().timestamp() * 1000)}"

        result = {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "estimated_time": 0,
            "result": {
                "recognition_id": recognition_id,
                "text": norm["full_text"],
                "word_count": norm["word_count"],
                "confidence": norm["confidence"],
                "width": norm["width"],
                "height": norm["height"],
                "text_angel": norm["text_angel"],
                "text_lines": norm["text_lines"],
                "texts": norm["texts"],
                "layout": norm["layout"],
            }
        }

        return Result.ok(result, "识别完成")
    except Exception as e:
        # 打印堆栈，便于定位
        logger.exception(f"识别失败: {e}")
        msg = str(e).strip() or repr(e)
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"识别失败: {msg}")

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
    
    return Result.ok(result)

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
        return Result.fail(ResultCode.BAD_REQUEST, "corrected_text不能为空")
    
    # 尝试从recognition_id中提取数字ID
    try:
        id_str = recognition_id.replace("rec_", "")
        inscription_id = int(id_str)
    except (ValueError, AttributeError):
        return Result.fail(ResultCode.BAD_REQUEST, "无效的识别ID")
    
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
        
        return Result.ok(result, "校对结果已保存")
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
    
    return Result.ok(result)

@router.post("/{recognition_id}/history")
async def save_correction_history(
    recognition_id: str = Path(..., description="识别ID"),
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """保存校对记录"""
    # TODO: 实现校对记录保存
    return Result.ok(None, "校对记录已保存")

