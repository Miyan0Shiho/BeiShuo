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
from app.client.database_client import DatabaseClient
import base64
import os
import uuid
import hashlib

router = APIRouter(prefix="/recognition", tags=["识别"])

# 内存缓存，用于存储OCR结果
# 键：图片哈希值，值：OCR结果
memory_cache = {}
logger.info("OCR内存缓存已初始化")

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
    logger.debug(f"收到OCR识别请求: user_id={user_id}, request={request}")
    
    image_url = request.get("image_url")
    image_base64 = request.get("image_base64")
    options = request.get("options", {})
    
    logger.debug(f"OCR请求参数: image_url={image_url}, image_base64={'存在' if image_base64 else '不存在'}, options={options}")

    if not image_url and not image_base64:
        logger.warning(f"OCR请求失败: 缺少必要参数，image_url和image_base64至少提供一个")
        return Result.fail(ResultCode.BAD_REQUEST, "image_url或image_base64至少提供一个")

    try:
        content = None
        filename = ""
        
        if not image_base64:
            logger.debug(f"处理图片URL: {image_url}")
            if not isinstance(image_url, str) or not image_url.startswith(settings.file_upload_url_prefix):
                logger.warning(f"无效的image_url: {image_url}")
                return Result.fail(ResultCode.BAD_REQUEST, "无效的image_url")
            filename = image_url.replace(settings.file_upload_url_prefix + "/", "")
            file_path = os.path.join(settings.file_upload_path, filename)
            logger.debug(f"图片文件路径: {file_path}")
            
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在: {file_path}")
                return Result.fail(ResultCode.BAD_REQUEST, "文件不存在或未上传")
            
            with open(file_path, "rb") as f:
                content = f.read()
            logger.debug(f"读取图片文件成功，大小: {len(content)} bytes")
            
            image_base64 = base64.b64encode(content).decode("utf-8")
            logger.debug(f"图片转换为base64成功，长度: {len(image_base64)} chars")
        else:
            logger.debug(f"直接使用base64图片，长度: {len(image_base64)} chars")
            # 提取内容用于生成哈希
            content = base64.b64decode(image_base64)

        # 生成图片哈希值，用于缓存
        image_hash = hashlib.md5(content).hexdigest()
        logger.debug(f"生成图片哈希值: {image_hash}")
        
        # 检查内存缓存
        if image_hash in memory_cache:
            logger.info(f"OCR内存缓存命中: image_hash={image_hash}")
            logger.debug(f"缓存结果: {memory_cache[image_hash]}")
            return Result.ok(memory_cache[image_hash], "识别完成（缓存命中）")
        
        logger.debug(f"OCR内存缓存未命中: image_hash={image_hash}")
        
        # 检查数据库缓存作为备用
        db_client = DatabaseClient()
        existing_result = None
        try:
            logger.debug(f"检查OCR数据库缓存: image_hash={image_hash}")
            existing_result = await db_client.get_ocr_result_by_image_hash(image_hash)
            if existing_result and existing_result.get("result"):
                # 数据库缓存命中，更新内存缓存并返回结果
                logger.info(f"OCR数据库缓存命中: image_hash={image_hash}")
                logger.debug(f"数据库缓存结果: {existing_result.get('result')}")
                memory_cache[image_hash] = existing_result.get("result")
                return Result.ok(existing_result.get("result"), "识别完成（缓存命中）")
        except Exception as e:
            logger.warning(f"获取OCR数据库缓存失败: {e}")
        
        # 缓存未命中或数据库服务不可用，执行OCR识别
        logger.info(f"OCR缓存未命中，执行识别: image_hash={image_hash}")

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
        logger.debug(f"OCR识别选项: {default_options}")

        client = KandiangujiOCRClient()
        primary_options = {**default_options, "return_position": True}
        logger.debug(f"主识别选项: {primary_options}")
        
        # 尝试多种OCR模式，提高识别成功率
        norm = {}
        recognition_success = False
        attempt_count = 0
        
        # 定义识别模式列表
        recognition_modes = [
            ("自动模式", primary_options),
            ("竖排模式", {**primary_options, "det_mode": "sp", "sp_line_words_angel": primary_options.get("sp_line_words_angel", "top2bottom")}),
            ("横排模式", {**primary_options, "det_mode": "hp", "hp_line_words_angel": primary_options.get("hp_line_words_angel", "left2right")}),
            ("beta版本+竖排模式", {**primary_options, "version": "beta", "det_mode": "sp", "sp_line_words_angel": primary_options.get("sp_line_words_angel", "top2bottom")})
        ]
        
        for mode_name, mode_options in recognition_modes:
            attempt_count += 1
            logger.debug(f"OCR识别尝试 {attempt_count}/{len(recognition_modes)}: {mode_name}")
            try:
                ocr_resp = await client.recognize(image_base64, mode_options)
                logger.debug(f"{mode_name}识别响应: {ocr_resp}")
                
                data = ocr_resp.get("data") or {}
                norm = _normalize_ocr(data)
                logger.debug(f"{mode_name}识别结果归一化: {norm}")
                
                recognition_success = bool(norm["full_text"] or (norm["text_lines"] and norm["word_count"] > 0))
                if recognition_success:
                    logger.info(f"{mode_name}识别成功")
                    break
                else:
                    logger.debug(f"{mode_name}识别结果为空")
            except Exception as e:
                logger.warning(f"{mode_name}识别失败: {e}")
        
        logger.info(f"OCR识别完成，共尝试 {attempt_count} 种模式，成功: {recognition_success}")
        
        # 生成识别结果
        recognition_id = f"rec_{int(datetime.now().timestamp() * 1000)}"
        task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        logger.debug(f"生成识别ID: {recognition_id}, 任务ID: {task_id}")

        result = {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "estimated_time": 0,
            "result": {
                "recognition_id": recognition_id,
                "text": norm.get("full_text", ""),
                "word_count": norm.get("word_count", 0),
                "confidence": norm.get("confidence", 0.0),
                "width": norm.get("width", 0),
                "height": norm.get("height", 0),
                "text_angel": norm.get("text_angel"),
                "text_lines": norm.get("text_lines", []),
                "texts": norm.get("texts", []),
                "layout": norm.get("layout"),
            }
        }
        
        logger.debug(f"OCR最终结果: {result}")
        
        # 将识别结果保存到数据库，以便后续缓存使用
        try:
            # 首先检查是否已存在对应的资产记录
            asset_id = None
            try:
                # 查找对应的资产记录
                # 注意：实际应用中应该根据图片哈希找到对应的asset_id
                # 这里简化处理，将asset_id设为None
                asset_id = None
            except Exception as e:
                logger.warning(f"查找资产记录失败: {e}")
            
            ocr_job = {
                "asset_id": asset_id,
                "status": "success",
                "vendor": "kandianguji",
                "params": primary_options,
                "confidence": norm.get("confidence", 0.0),
                "duration_ms": None,
                "retries": attempt_count - 1
            }
            logger.debug(f"创建OCR任务数据: {ocr_job}")
            created_job = await db_client.create_ocr_job(ocr_job)
            logger.info(f"OCR任务已保存到数据库: job_id={created_job['id']}, image_hash={image_hash}")
            
            logger.debug(f"保存OCR结果: task_id={task_id}")
            saved_result = await db_client.save_ocr_result(task_id, result)
            logger.info(f"OCR结果已保存到数据库: task_id={task_id}, image_hash={image_hash}")
        except Exception as e:
            logger.warning(f"保存OCR结果到数据库失败: {e}")
            # 数据库服务不可用，继续返回OCR结果，不影响用户体验
            pass

        # 将识别结果保存到内存缓存
        memory_cache[image_hash] = result
        logger.info(f"OCR结果已保存到内存缓存: image_hash={image_hash}")
        
        logger.info(f"OCR识别完成，返回结果: task_id={task_id}, word_count={norm.get('word_count', 0)}, confidence={norm.get('confidence', 0.0)}")
        return Result.ok(result, "识别完成")
    except Exception as e:
        # 打印堆栈，便于定位
        logger.exception(f"识别失败: {e}")
        msg = str(e).strip() or repr(e)
        logger.error(f"OCR识别失败，返回错误: {msg}")
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

@router.post("/result/{image_hash}/dislike")
async def dislike_ocr_result(
    image_hash: str = Path(..., description="图片哈希值"),
    user_id: int = Depends(get_current_user_id)
):
    """用户不满意OCR结果，删除缓存"""
    try:
        db_client = DatabaseClient()
        
        # 删除OCR缓存
        delete_result = await db_client.delete_ocr_cache(image_hash)
        
        if delete_result:
            logger.info(f"OCR缓存已删除: image_hash={image_hash}")
            return Result.ok(None, "OCR缓存已删除，将重新执行识别")
        else:
            logger.warning(f"删除OCR缓存失败: image_hash={image_hash}")
            return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, "删除OCR缓存失败")
    except Exception as e:
        logger.exception(f"处理用户不满意OCR结果请求失败: {e}")
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"处理请求失败: {str(e)}")

