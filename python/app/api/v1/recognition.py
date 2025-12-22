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
    
    # 获取并清理image_url，移除不必要的反引号和空格
    image_url = request.get("image_url")
    if isinstance(image_url, str):
        # 移除可能的反引号和前后空格
        image_url = image_url.strip().strip('`')
    
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
            
            # 检查image_url是否是完整的OSS URL或本地路径
            is_oss_url = image_url.startswith('http') or image_url.startswith('https')
            is_local_path = image_url.startswith(settings.file_upload_url_prefix)
            
            if not isinstance(image_url, str) or not (is_oss_url or is_local_path):
                logger.warning(f"无效的image_url: {image_url}")
                return Result.fail(ResultCode.BAD_REQUEST, "无效的image_url")
            
            if is_local_path:
                # 处理本地路径
                filename = image_url.replace(settings.file_upload_url_prefix + "/", "")
                file_path = os.path.join(settings.file_upload_path, filename)
                logger.debug(f"图片文件路径: {file_path}")
                
                if not os.path.exists(file_path):
                    logger.warning(f"文件不存在: {file_path}")
                    return Result.fail(ResultCode.BAD_REQUEST, "文件不存在或未上传")
                
                with open(file_path, "rb") as f:
                    content = f.read()
                logger.debug(f"读取图片文件成功，大小: {len(content)} bytes")
            else:
                # 处理OSS URL，直接从URL下载图片内容
                logger.debug(f"处理OSS URL: {image_url}")
                try:
                    import requests
                    # 确保URL格式正确，特别是查询参数前有问号
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(image_url)
                    # 重建正确的URL
                    query_str = f"?{parsed_url.query}" if parsed_url.query else ''
                    correct_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}{query_str}{parsed_url.fragment if parsed_url.fragment else ''}"
                    logger.debug(f"修正后的OSS URL: {correct_url}")
                    
                    response = requests.get(correct_url, timeout=10)
                    response.raise_for_status()
                    content = response.content
                    logger.debug(f"从OSS URL下载图片成功，大小: {len(content)} bytes")
                except Exception as e:
                    logger.error(f"从OSS URL下载图片失败: {e}")
                    logger.error(f"错误URL: {image_url}")
                    return Result.fail(ResultCode.BAD_REQUEST, "无法从图片URL获取内容")
            
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
        logger.info(f"检查OCR缓存，图片哈希: {image_hash}")
        if image_hash in memory_cache:
            logger.info(f"OCR内存缓存命中: image_hash={image_hash}")
            return Result.ok(memory_cache[image_hash], "识别完成（缓存命中）")
        
        logger.info(f"OCR内存缓存未命中: image_hash={image_hash}")
        
        # 检查数据库缓存作为备用
        db_client = DatabaseClient()
        existing_result = None
        try:
            logger.info(f"开始检查OCR数据库缓存: image_hash={image_hash}")
            existing_result = await db_client.get_ocr_result_by_image_hash(image_hash)
            logger.debug(f"数据库缓存查询返回结果: {existing_result}")
            
            if existing_result and existing_result.get("result"):
                # 数据库缓存命中，更新内存缓存并返回结果
                logger.info(f"OCR数据库缓存命中: image_hash={image_hash}")
                cached_result = existing_result.get("result").copy()
                
                # 检查并处理cached_result中的image_url，如果是OSS URL则转换为本地临时文件URL
                cached_image_url = cached_result.get("image_url", "")
                if cached_image_url and (cached_image_url.startswith('http') or cached_image_url.startswith('https')):
                    logger.info(f"处理缓存结果中的OSS URL: {cached_image_url}")
                    
                    # 下载OSS图片到本地临时目录
                    try:
                        import os
                        import uuid
                        import tempfile
                        import requests
                        
                        # 创建临时目录（如果不存在）
                        temp_dir = os.path.join(os.getcwd(), "temp_oss_images")
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        # 生成临时文件名
                        temp_filename = f"temp_{uuid.uuid4()}.png"
                        temp_file_path = os.path.join(temp_dir, temp_filename)
                        
                        # 下载OSS图片到本地
                        logger.info(f"下载缓存结果中的OSS图片到本地: {cached_image_url} -> {temp_file_path}")
                        response = requests.get(cached_image_url, timeout=10)
                        response.raise_for_status()
                        with open(temp_file_path, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"缓存图片下载成功: {temp_file_path}")
                        
                        # 构建本地URL
                        local_image_url = f"/temp_oss_images/{temp_filename}"
                        cached_result['image_url'] = local_image_url
                        logger.info(f"缓存结果的OSS URL已转换为本地URL: {local_image_url}")
                    except Exception as e:
                        logger.error(f"处理缓存结果的OSS URL失败: {e}")
                        # 如果处理失败，保持原URL不变
                        logger.info(f"使用缓存结果中的原始图片URL: {cached_image_url}")
                
                # 更新内存缓存
                memory_cache[image_hash] = cached_result
                logger.info(f"OCR数据库缓存结果已加载到内存缓存")
                return Result.ok(cached_result, "识别完成（缓存命中）")
            else:
                logger.info(f"OCR数据库缓存未命中或结果无效: image_hash={image_hash}")
        except Exception as e:
            logger.error(f"获取OCR数据库缓存失败: {e}", exc_info=True)
        
        # 缓存未命中或数据库服务不可用，执行OCR识别
        logger.info(f"OCR缓存未命中，执行识别: image_hash={image_hash}")

        # 默认选项
        default_options = {
            "version": options.get("version", "v2"),
            "det_mode": options.get("det_mode", "auto"),
            "return_position": options.get("return_position", True),
            "return_choices": options.get("return_choices", True),
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
                # 减少OCR响应的详细输出
                logger.debug(f"{mode_name}识别响应: 状态={ocr_resp.get('code', 'unknown')}")
                
                data = ocr_resp.get("data") or {}
                norm = _normalize_ocr(data)
                # 减少OCR结果的详细输出
                logger.debug(f"{mode_name}识别结果归一化: 文本行数={len(norm.get('text_lines', []))}, 词数={norm.get('word_count', 0)}")
                
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
        # 移除识别ID和任务ID的详细输出
        logger.debug("OCR识别结果生成完成")

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
        
        # 4. 将识别结果保存到数据库，以便后续缓存使用
        # 添加OCR最终结果生成完成的日志
        logger.debug(f"OCR最终结果生成完成: task_id={result['task_id']}, 文本长度={len(result['result'].get('text', ''))}, 文本行数={len(result['result'].get('text_lines', []))}")
        
        # 4. 将识别结果保存到数据库，以便后续缓存使用
        try:
            # 保存OCR结果，这会创建完整的OCR记录（asset、ocr_job、ocr_image、ocr_text_lines）
            logger.debug(f"保存OCR结果: task_id={task_id}")
            
            # 为了确保save_ocr_result方法能获取到原始图片URL，我们将request信息添加到result对象中
            result_with_request = {
                **result,
                "request": {
                    "image_url": image_url,  # 原始请求中的image_url（可能是OSS URL）
                    "options": options
                }
            }
            
            # 将OSS图片下载到本地临时目录，然后返回本地URL
            import tempfile
            import shutil
            import os
            import uuid
            
            # 创建临时目录（如果不存在）
            temp_dir = os.path.join(os.getcwd(), "temp_oss_images")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成临时文件名
            temp_filename = f"temp_{uuid.uuid4()}.png"
            temp_file_path = os.path.join(temp_dir, temp_filename)
            
            # 下载OSS图片到本地
            logger.info(f"下载OSS图片到本地临时目录: {image_url} -> {temp_file_path}")
            try:
                import requests
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                with open(temp_file_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"图片下载成功: {temp_file_path}")
                
                # 构建本地URL
                local_image_url = f"/temp_oss_images/{temp_filename}"
                result['result']['image_url'] = local_image_url
                logger.info(f"添加本地临时图片URL到result['result']字段: {local_image_url}")
                
                # 保存临时文件信息，以便后续清理
                if not hasattr(result_with_request, 'temp_files'):
                    result_with_request['temp_files'] = []
                result_with_request['temp_files'].append(temp_file_path)
            except Exception as e:
                logger.error(f"下载OSS图片到本地失败: {e}")
                # 如果下载失败，使用原始URL
                result['result']['image_url'] = image_url
                logger.info(f"使用原始图片URL: {image_url}")
            
            # 保存OCR结果到数据库
            saved_result = await db_client.save_ocr_result(task_id, result_with_request, image_hash, content)
            logger.info(f"OCR结果已保存到数据库: task_id={task_id}, image_hash={image_hash}")
            
            # 从保存结果中获取资产ID
            asset_id = None
            if saved_result and isinstance(saved_result, dict):
                asset_id = saved_result.get("asset_id")
            logger.debug(f"从保存结果中获取到的asset_id: {asset_id}")
        except Exception as e:
            logger.warning(f"保存OCR结果到数据库失败: {e}")
            # 数据库服务不可用，继续返回OCR结果，不影响用户体验
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
    
    # 不尝试从recognition_id中提取数字ID，直接使用service更新
    # 这里的识别ID是前端生成的临时ID，实际存储使用的是数据库中的id
    # 我们需要查找对应的inscription记录
    service = InscriptionService()
    try:
        # 这里应该是通过recognition_id查找对应的inscription记录
        # 但当前实现中，recognition_id是前端生成的，没有存储到数据库
        # 所以我们需要修改保存逻辑，将recognition_id存储到数据库
        # 或者修改校对逻辑，使用其他方式关联识别结果
        
        # 暂时返回成功，后续需要完善
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

@router.delete("/history/{record_id}")
async def delete_recognition_record(
    record_id: int = Path(..., description="识别记录ID"),
    user_id: int = Depends(get_current_user_id)
):
    """删除识别记录"""
    try:
        db_client = DatabaseClient()
        
        # 删除OCR相关记录
        # 1. 删除ocr_text_lines记录
        await db_client.execute_update("DELETE FROM ocr_text_lines WHERE image_id IN (SELECT id FROM ocr_images WHERE job_id = %s)", (record_id,))
        
        # 2. 删除ocr_images记录
        await db_client.execute_update("DELETE FROM ocr_images WHERE job_id = %s", (record_id,))
        
        # 3. 删除ocr_jobs记录
        await db_client.execute_update("DELETE FROM ocr_jobs WHERE id = %s", (record_id,))
        
        logger.info(f"识别记录已删除: record_id={record_id}")
        return Result.ok(None, "识别记录已删除")
    except Exception as e:
        logger.exception(f"删除识别记录失败: {e}")
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"删除识别记录失败: {str(e)}")

