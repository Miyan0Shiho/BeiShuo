from fastapi import APIRouter, Depends, Query, Path, Body, Request
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path
import urllib.parse
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.inscription_service import InscriptionService
from app.utils.logger import logger
from app.config import settings
from app.client.kandianguji_ocr_client import KandiangujiOCRClient
from app.cache.ocr_cache_service import ocr_cache_service
from app.cache.cache_manager import cache_manager
import base64
import os
import uuid
import hashlib

router = APIRouter(prefix="/recognition", tags=["识别"])


async def _download_from_oss(image_url: str) -> tuple:
    """从OSS下载图片的辅助函数"""
    try:
        # 处理URL编码问题：如果URL被编码了，先解码
        actual_url = image_url
        if image_url.startswith("https%3A//"):
            actual_url = urllib.parse.unquote(image_url)
            logger.info(f"检测到编码的OSS URL，解码后: {actual_url}")
        
        # 从OSS URL中提取object_key
        # OSS URL格式: https://bucket.region.aliyuncs.com/path/to/file
        # 或者: https://bucket.oss-cn-region.aliyuncs.com/path/to/file
        parsed = urllib.parse.urlparse(actual_url)
        fully_decoded_url = urllib.parse.unquote(actual_url)
        path = urllib.parse.urlparse(fully_decoded_url).path
        object_key = path.lstrip('/')
        
        try:
            from app.services.oss_service import oss_service as _oss
            bucket_name = _oss.config.oss_bucket_name
        except Exception:
            bucket_name = None
        
        host = parsed.netloc or ""
        if bucket_name and host.startswith("oss-") and object_key.startswith(f"{bucket_name}/"):
            object_key = object_key[len(bucket_name)+1:]
        
        if not object_key:
            return None, None, "无效的OSS URL格式"
        
        logger.info(f"从OSS URL提取object_key: {object_key}")
        
        # 使用OSS服务直接下载文件
        from app.services.oss_service import oss_service
        content = await oss_service.download_file(object_key)
        
        if content is None:
            logger.error(f"无法从OSS下载图片，object_key: {object_key}")
            return None, None, "无法从OSS下载图片"
        
        image_base64 = base64.b64encode(content).decode("utf-8")
        # 为OSS URL生成一个文件名（使用图片哈希值）
        image_hash = ocr_cache_service.generate_image_hash(content)
        filename = f"oss_{image_hash[:16]}.jpg"
        logger.info(f"从OSS下载图片成功: object_key={object_key}, 大小: {len(content)}字节")
        
        return image_base64, filename, None
        
    except Exception as e:
        logger.error(f"从OSS下载图片失败: {e}")
        return None, None, f"OSS图片下载失败: {e}"

def _normalize_ocr(data: Any) -> Dict[str, Any]:
    if isinstance(data, list):
        texts = [str(x) for x in data]
        full_text = "\n".join(texts) if texts else ""
        return {
            "width": 0,
            "height": 0,
            "text_angel": None,
            "texts": texts,
            "text_lines": [],
            "full_text": full_text,
            "word_count": len(full_text) if full_text else 0,
            "confidence": 0.0,
            "layout": None,
        }
    if not isinstance(data, dict):
        return {
            "width": 0,
            "height": 0,
            "text_angel": None,
            "texts": [],
            "text_lines": [],
            "full_text": "",
            "word_count": 0,
            "confidence": 0.0,
            "layout": None,
        }
    width = data.get("width") or 0
    height = data.get("height") or 0
    text_angel = data.get("text_angel")
    texts: List[str] = data.get("texts") or []
    text_lines: List[Dict[str, Any]] = data.get("text_lines") or []
    full_text = "\n".join(texts) if texts else ("\n".join([str(tl.get("text") or "") for tl in text_lines]) if text_lines else (str(data.get("text") or "")))
    word_count = 0
    confidences: List[float] = []
    for tl in text_lines or []:
        # 检查是否有words字段（旧格式）或直接有text字段（新格式）
        words = tl.get("words") or []
        if words:
            # 旧格式：从words数组中提取
            word_count += len(words)
            for w in words:
                c = w.get("confidence")
                if c is None:
                    c = w.get("det_confidence")
                if isinstance(c, (int, float)):
                    confidences.append(float(c))
        else:
            # 新格式：直接统计text字段的字符数
            text = tl.get("text", "")
            if text:
                word_count += len(text)
                c = tl.get("confidence")
                if isinstance(c, (int, float)):
                    confidences.append(float(c))
    
    # 如果通过text_lines没有统计到字数，使用full_text的长度
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
        # 初始化缓存管理器
        if not cache_manager.is_initialized:
            await cache_manager.initialize()

        # 调试输出：接收到的参数
        logger.info(f"=== OCR识别开始 ===")
        logger.info(f"用户ID: {user_id}")
        logger.info(f"图片URL: {image_url}")
        logger.info(f"图片Base64长度: {len(image_base64) if image_base64 else 0}")
        logger.info(f"识别选项: {options}")

        if not image_base64:
            if not isinstance(image_url, str):
                return Result.fail(ResultCode.BAD_REQUEST, "无效的image_url")
            
            # 首先检查是否为本地临时文件路径（来自上传接口的temp_file_path）
            if image_url.startswith("temp_"):
                # 这是本地临时文件路径，直接读取文件
                temp_file_path = Path(settings.file_upload_path) / "temp" / image_url
                if not temp_file_path.exists():
                    logger.warning(f"本地临时文件不存在，回退到OSS下载: {temp_file_path}")
                    # 临时文件不存在，回退到OSS下载
                    return await _download_from_oss(image_url)
                
                try:
                    with open(temp_file_path, "rb") as f:
                        content = f.read()
                    image_base64 = base64.b64encode(content).decode("utf-8")
                    filename = image_url
                    logger.info(f"从本地临时文件读取图片: {temp_file_path}, 大小: {len(content)}字节")
                except Exception as e:
                    logger.error(f"读取本地临时文件失败: {e}")
                    # 读取失败，回退到OSS下载
                    return await _download_from_oss(image_url)
            
            # 检查是否为OSS URL
            elif image_url.startswith("https://") or image_url.startswith("https%3A//"):
                image_base64, filename, error = await _download_from_oss(image_url)
                if error:
                    return Result.fail(ResultCode.BAD_REQUEST, error)
                # 从base64解码得到content用于生成哈希
                try:
                    content = base64.b64decode(image_base64)
                except Exception as e:
                    logger.error(f"Base64解码失败: {e}")
                    return Result.fail(ResultCode.BAD_REQUEST, "无效的Base64图片数据")
            elif image_url.startswith(settings.file_upload_url_prefix):
                # 从本地文件系统读取图片（相对路径格式）
                filename = image_url.replace(settings.file_upload_url_prefix + "/", "")
                file_path = os.path.join(settings.file_upload_path, filename)
                if not os.path.exists(file_path):
                    return Result.fail(ResultCode.BAD_REQUEST, "文件不存在或未上传")
                with open(file_path, "rb") as f:
                    content = f.read()
                image_base64 = base64.b64encode(content).decode("utf-8")
                logger.info(f"从文件读取图片: {file_path}, 大小: {len(content)}字节")
            elif image_url.startswith("http://localhost:8080" + settings.file_upload_url_prefix):
                # 从本地文件系统读取图片（完整URL格式）
                filename = image_url.replace("http://localhost:8080" + settings.file_upload_url_prefix + "/", "")
                file_path = os.path.join(settings.file_upload_path, filename)
                if not os.path.exists(file_path):
                    return Result.fail(ResultCode.BAD_REQUEST, "文件不存在或未上传")
                with open(file_path, "rb") as f:
                    content = f.read()
                image_base64 = base64.b64encode(content).decode("utf-8")
                logger.info(f"从文件读取图片（完整URL）: {file_path}, 大小: {len(content)}字节")
            else:
                return Result.fail(ResultCode.BAD_REQUEST, "无效的image_url格式")

        # 生成图片哈希用于缓存 - 使用与缓存服务相同的方式
        # 注意：ocr_cache_service.generate_image_hash() 需要图片数据bytes，不是base64字符串
        # 确保content变量在所有分支中都已定义
        if 'content' not in locals():
            # 当使用base64图片数据时，需要从base64解码得到图片数据
            if image_base64 and not image_url:
                try:
                    content = base64.b64decode(image_base64)
                    filename = f"base64_{int(datetime.now().timestamp() * 1000)}.jpg"
                except Exception as e:
                    logger.error(f"Base64解码失败: {e}")
                    return Result.fail(ResultCode.BAD_REQUEST, "无效的Base64图片数据")
            else:
                # 如果既没有image_url也没有content，这是无效状态
                return Result.fail(ResultCode.BAD_REQUEST, "无法获取图片数据用于生成哈希")
        
        # 现在content变量已定义，生成图片哈希
        image_hash = ocr_cache_service.generate_image_hash(content)
        vendor = "kandianguji"
        
        # 检查缓存
        logger.info(f"检查缓存: 图片哈希={image_hash}, 供应商={vendor}")
        cached_result = await ocr_cache_service.get_cached_ocr(image_hash, vendor)
        
        if cached_result:
            logger.info(f"✅ 缓存命中! 缓存ID: {cached_result.get('id')}")
            logger.info(f"缓存置信度: {cached_result.get('confidence', 0)}")
            logger.info(f"缓存处理时间: {cached_result.get('duration_ms', 0)}ms")
            
            # 从缓存中获取OCR结果
            norm = {
                "full_text": cached_result.get('text', ''),
                "word_count": cached_result.get('word_count', 0),
                "confidence": cached_result.get('confidence', 0.0),
                "width": cached_result.get('width', 0),
                "height": cached_result.get('height', 0),
                "text_angel": cached_result.get('text_angel', 0),
                "text_lines": cached_result.get('text_lines', []),
                "texts": cached_result.get('texts', []),
                "layout": cached_result.get('layout', None)
            }
            cache_hit = True
        else:
            logger.info("❌ 缓存未命中，需要调用OCR服务")
            cache_hit = False
            
            # 获取用户指定的检测模式
            user_det_mode = options.get("det_mode", "auto")
            
            # 如果用户指定了sp或hp模式，直接使用指定模式
            if user_det_mode in ["sp", "hp"]:
                logger.info(f"用户指定使用{user_det_mode}模式，直接调用OCR服务")
                
                # 根据用户指定的模式设置det_mode参数
                det_mode = user_det_mode
                if user_det_mode == "sp":
                    # 竖排模式使用sp（single-page）模式
                    sp_line_words_angel = options.get("sp_line_words_angel", "top2bottom")
                else:  # hp
                    # 横排模式使用hp（horizontal-page）模式
                    hp_line_words_angel = options.get("hp_line_words_angel", "left2right")
                
                # 默认选项，使用用户指定的模式
                default_options = {
                    "version": options.get("version", "v2"),  # 数据库允许值：default, beta, v2
                    "det_mode": det_mode,
                    "return_position": options.get("return_position", True),
                    "return_choices": options.get("return_choices", False),
                    "det_layout": options.get("det_layout", False),
                    "only_plain_text": options.get("only_plain_text", False),
                    "return_layout": options.get("return_layout", False),
                    "auto_insert_space": options.get("auto_insert_space", False),
                    "hp_line_words_angel": options.get("hp_line_words_angel", hp_line_words_angel if user_det_mode == "horizontal" else "left2right"),
                    "sp_line_words_angel": options.get("sp_line_words_angel", sp_line_words_angel if user_det_mode == "vertical" else "top2bottom"),
                    "image_size": options.get("image_size", 2000),
                }

                client = KandiangujiOCRClient()
                primary_options = {**default_options, "return_position": True}
                logger.info(f"调用OCR服务，选项: {primary_options}")
                
                ocr_resp = await client.recognize(image_base64, primary_options)
                data = ocr_resp.get("data") or {}
                norm = _normalize_ocr(data)
                
                # 详细调试输出OCR结果（JSON格式）
                logger.info("=== OCR原始响应（JSON格式） ===")
                import json
                logger.info(json.dumps(ocr_resp, indent=2, ensure_ascii=False))
                
                logger.info("=== 归一化OCR结果（JSON格式） ===")
                logger.info(json.dumps(norm, indent=2, ensure_ascii=False))
                
                logger.info("=== OCR识别详情 ===")
                logger.info(f"{user_det_mode}模式结果 - 文字长度: {len(norm['full_text'])}, 置信度: {norm['confidence']}")
                
            else:
                # 用户未指定模式或使用auto模式，保持原有的自动检测逻辑
                logger.info("用户未指定模式或使用auto模式，使用自动检测逻辑")
                
                # 默认选项
                default_options = {
                    "version": options.get("version", "v2"),  # 数据库允许值：default, beta, v2
                    "det_mode": options.get("det_mode", "auto"),
                    "return_position": options.get("return_position", True),
                    "return_choices": options.get("return_choices", False),
                    "det_layout": options.get("det_layout", False),
                    "only_plain_text": options.get("only_plain_text", False),
                    "return_layout": options.get("return_layout", False),
                    "auto_insert_space": options.get("auto_insert_space", False),
                    "hp_line_words_angel": options.get("hp_line_words_angel", "left2right"),
                    "sp_line_words_angel": options.get("sp_line_words_angel", "top2bottom"),
                    "image_size": options.get("image_size", 2000),
                }

                client = KandiangujiOCRClient()
                primary_options = {**default_options, "return_position": True}
                logger.info(f"调用OCR服务，选项: {primary_options}")
                
                ocr_resp = await client.recognize(image_base64, primary_options)
                data = ocr_resp.get("data") or {}
                norm = _normalize_ocr(data)
                
                # 详细调试输出OCR结果（JSON格式）
                logger.info("=== OCR原始响应（JSON格式） ===")
                import json
                logger.info(json.dumps(ocr_resp, indent=2, ensure_ascii=False))
                
                logger.info("=== 归一化OCR结果（JSON格式） ===")
                logger.info(json.dumps(norm, indent=2, ensure_ascii=False))
                
                logger.info("=== OCR识别详情 ===")
                logger.info(f"主模式结果 - 文字长度: {len(norm['full_text'])}, 置信度: {norm['confidence']}")
                
                # 如果识别结果为空，尝试备用模式
                if not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0):
                    logger.warning("主模式识别失败，尝试SP模式")
                    fallback_sp = {**primary_options, "det_mode": "sp", "sp_line_words_angel": primary_options.get("sp_line_words_angel", "top2bottom")}
                    try:
                        ocr_resp = await client.recognize(image_base64, fallback_sp)
                        sp_norm = _normalize_ocr(ocr_resp.get("data") or {})
                        
                        logger.info("=== SP模式原始响应（JSON格式） ===")
                        logger.info(f"{ocr_resp}")
                        logger.info("=== SP模式归一化结果（JSON格式） ===")
                        logger.info(f"{sp_norm}")
                        logger.info(f"SP模式结果 - 文字长度: {len(sp_norm['full_text'])}, 置信度: {sp_norm['confidence']}")
                        
                        # 如果SP模式成功，更新主norm变量
                        if sp_norm["full_text"] or sp_norm["text_lines"]:
                            norm = sp_norm
                            logger.info("✅ SP模式识别成功，使用SP模式结果")
                    except Exception as e:
                        logger.error(f"SP模式失败: {e}")
                        pass
                
                if not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0):
                    logger.warning("SP模式识别失败，尝试HP模式")
                    fallback_hp = {**primary_options, "det_mode": "hp", "hp_line_words_angel": primary_options.get("hp_line_words_angel", "left2right")}
                    try:
                        ocr_resp = await client.recognize(image_base64, fallback_hp)
                        hp_norm = _normalize_ocr(ocr_resp.get("data") or {})
                        
                        logger.info("=== HP模式原始响应（JSON格式） ===")
                        logger.info(f"{ocr_resp}")
                        logger.info("=== HP模式归一化结果（JSON格式） ===")
                        logger.info(f"{hp_norm}")
                        logger.info(f"HP模式结果 - 文字长度: {len(hp_norm['full_text'])}, 置信度: {hp_norm['confidence']}")
                        
                        # 如果HP模式成功，更新主norm变量
                        if hp_norm["full_text"] or hp_norm["text_lines"]:
                            norm = hp_norm
                            logger.info("✅ HP模式识别成功，使用HP模式结果")
                    except Exception as e:
                        logger.error(f"HP模式失败: {e}")
                        pass
                
                # 尝试版本回退（beta + sp）
                if not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0):
                    logger.warning("HP模式识别失败，尝试Beta+SP模式")
                    fallback_beta_sp = {**primary_options, "version": "beta", "det_mode": "sp", "sp_line_words_angel": primary_options.get("sp_line_words_angel", "top2bottom")}
                    try:
                        ocr_resp = await client.recognize(image_base64, fallback_beta_sp)
                        beta_sp_norm = _normalize_ocr(ocr_resp.get("data") or {})
                        
                        logger.info("=== Beta+SP模式原始响应（JSON格式） ===")
                        logger.info(f"{ocr_resp}")
                        logger.info("=== Beta+SP模式归一化结果（JSON格式） ===")
                        logger.info(f"{beta_sp_norm}")
                        logger.info(f"Beta+SP模式结果 - 文字长度: {len(beta_sp_norm['full_text'])}, 置信度: {beta_sp_norm['confidence']}")
                        
                        # 如果Beta+SP模式成功，更新主norm变量
                        if beta_sp_norm["full_text"] or beta_sp_norm["text_lines"]:
                            norm = beta_sp_norm
                            logger.info("✅ Beta+SP模式识别成功，使用Beta+SP模式结果")
                    except Exception as e:
                        logger.error(f"Beta+SP模式失败: {e}")
                        pass

            # 缓存OCR结果
            if norm["full_text"] or norm["text_lines"]:
                logger.info("缓存OCR结果")
                # 构建完整的OCR结果用于缓存
                cache_result = {
                    'text': norm['full_text'],
                    'word_count': norm['word_count'],
                    'confidence': norm['confidence'],
                    'width': norm['width'],
                    'height': norm['height'],
                    'text_angel': norm['text_angel'],
                    'text_lines': norm['text_lines'],
                    'texts': norm['texts'],
                    'layout': norm['layout'],
                    'duration_ms': 0,  # 可以添加实际的处理时间
                    'version': 'v2'   # 使用数据库允许的枚举值：default, beta, v2
                }
                
                # 修复参数顺序：image_data, filename, ocr_result, vendor
                await ocr_cache_service.cache_ocr_result(
                    content, filename, cache_result, vendor
                )
                
                # 缓存插入后，重新检查缓存以确保后续请求能命中
                logger.info("缓存插入完成，重新检查缓存...")
                cached_result = await ocr_cache_service.get_cached_ocr(image_hash, vendor)
                if cached_result:
                    logger.info("✅ 缓存插入后重新检查：缓存命中!")
                    cache_hit = True
                    # 更新为缓存中的结果
                    norm = {
                        "full_text": cached_result.get('text', ''),
                        "word_count": cached_result.get('word_count', 0),
                        "confidence": cached_result.get('confidence', 0.0),
                        "width": cached_result.get('width', 0),
                        "height": cached_result.get('height', 0),
                        "text_angel": cached_result.get('text_angel', 0),
                        "text_lines": cached_result.get('text_lines', []),
                        "texts": cached_result.get('texts', []),
                        "layout": cached_result.get('layout', None)
                    }

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
                "cache_hit": cache_hit  # 添加缓存命中标识
            }
        }

        # 最终调试输出（JSON格式）
        logger.info("=== OCR识别完成（JSON格式） ===")
        final_debug_info = {
            "识别结果": {
                "文字长度": len(norm['full_text']),
                "置信度": norm['confidence'],
                "文字行数": len(norm['text_lines']),
                "文字块数": len(norm['texts']),
                "图片尺寸": f"{norm['width']}x{norm['height']}",
                "文字角度": norm['text_angel']
            },
            "缓存信息": {
                "缓存命中": cache_hit,
                "图片哈希": image_hash,
                "供应商": vendor
            },
            "任务信息": {
                "识别ID": recognition_id,
                "任务ID": task_id,
                "用户ID": user_id
            }
        }
        import json
        logger.info(json.dumps(final_debug_info, indent=2, ensure_ascii=False))

        return Result.ok(result, "识别完成")
    except Exception as e:
        # 打印堆栈，便于定位
        logger.exception(f"识别失败: {e}")
        msg = str(e).strip() or repr(e)
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"识别失败: {msg}")

@router.get("/progress/{task_id}")
async def get_recognition_progress(
    task_id: str = Path(description="任务ID"),
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

@router.get("/recent")
async def get_recent_recognition_records(
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(10, ge=1, le=50)
):
    """获取最近识别记录列表"""
    try:
        # 查询最近识别记录
        query = """
            SELECT 
                oj.id as job_id,
                oj.asset_id,
                oj.status,
                oj.confidence,
                oj.duration_ms,
                oj.created_at,
                oj.updated_at,
                oi.width,
                oi.height,
                oi.text_angel,
                oi.text_angel_confidence,
                oi.version,
                oi.det_mode,
                oi.image_size
            FROM ocr_jobs oj
            LEFT JOIN ocr_images oi ON oj.id = oi.job_id
            WHERE oj.status = 'success'
            AND oj.asset_id IN (SELECT id FROM inscriptions WHERE creator_user_id = %s)
            ORDER BY oj.created_at DESC
            LIMIT %s
        """
        
        # 使用mysql_client执行查询
        from app.client.mysql_client import mysql_client
        results = await mysql_client.execute_query(query, (user_id, limit))
        
        # 转换为前端需要的格式
        recent_records = []
        for record in results:
            # 确保confidence字段是JSON可序列化的类型（Decimal转换为float）
            confidence = record.get("confidence")
            if confidence is not None and hasattr(confidence, 'as_integer_ratio'):  # 检查是否为Decimal类型
                confidence = float(confidence)
            
            recent_records.append({
                "job_id": record.get("job_id"),
                "asset_id": record.get("asset_id"),
                "status": record.get("status"),
                "confidence": confidence,
                "duration_ms": record.get("duration_ms"),
                "created_at": record.get("created_at"),
                "width": record.get("width"),
                "height": record.get("height"),
                "image_size": record.get("image_size"),
                "text_angel": record.get("text_angel"),
                "text_angel_confidence": record.get("text_angel_confidence")
            })
        
        return {
            "code": 200,
            "message": "获取最近识别记录成功",
            "data": {
                "list": recent_records,
                "total": len(recent_records),
                "limit": limit
            }
        }
    except Exception as e:
        logger.error(f"获取最近识别记录失败: {e}")
        return {
            "code": 500,
            "message": "获取最近识别记录失败",
            "data": None
        }

@router.get("/recent/{job_id}")
async def get_recognition_record_detail(
    job_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """获取单个识别记录的详细信息"""
    try:
        # 查询识别记录详情
        query = """
            SELECT 
                oj.id as job_id,
                oj.asset_id,
                oj.status,
                oj.vendor,
                oj.params,
                oj.confidence,
                oj.duration_ms,
                oj.created_at,
                oj.updated_at,
                oi.*,
                i.title as inscription_title,
                i.content as inscription_content
            FROM ocr_jobs oj
            LEFT JOIN ocr_images oi ON oj.id = oi.job_id
            LEFT JOIN inscriptions i ON oj.asset_id = i.id
            WHERE oj.id = %s
            AND oj.status = 'success'
            AND i.creator_user_id = %s
        """
        
        # 使用mysql_client执行查询
        from app.client.mysql_client import mysql_client
        import json
        results = await mysql_client.execute_query(query, (job_id, user_id))
        
        if not results:
            return {
                "code": 404,
                "message": "识别记录不存在",
                "data": None
            }
        
        record = results[0]
        
        # 解析params字段
        params = {}
        if record.get("params"):
            try:
                params = json.loads(record.get("params"))
            except:
                pass
        
        # 转换为前端需要的格式
        # 确保confidence字段是JSON可序列化的类型（Decimal转换为float）
        confidence = record.get("confidence")
        if confidence is not None and hasattr(confidence, 'as_integer_ratio'):  # 检查是否为Decimal类型
            confidence = float(confidence)
        
        detail = {
            "job_id": record.get("job_id"),
            "asset_id": record.get("asset_id"),
            "status": record.get("status"),
            "vendor": record.get("vendor"),
            "confidence": confidence,
            "duration_ms": record.get("duration_ms"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
            "params": params,
            "image_info": {
                "width": record.get("width"),
                "height": record.get("height"),
                "image_size": record.get("image_size"),
                "text_angel": record.get("text_angel"),
                "text_angel_confidence": record.get("text_angel_confidence"),
                "version": record.get("version"),
                "det_mode": record.get("det_mode"),
                "det_layout": record.get("det_layout"),
                "only_plain_text": record.get("only_plain_text"),
                "return_layout": record.get("return_layout"),
                "auto_insert_space": record.get("auto_insert_space"),
                "hp_line_words_angel": record.get("hp_line_words_angel"),
                "sp_line_words_angel": record.get("sp_line_words_angel"),
                "char_ocr": record.get("char_ocr")
            },
            "inscription_info": {
                "title": record.get("inscription_title"),
                "content": record.get("inscription_content")
            }
        }
        
        return {
            "code": 200,
            "message": "获取识别记录详情成功",
            "data": detail
        }
    except Exception as e:
        logger.error(f"获取识别记录详情失败: {e}")
        return {
            "code": 500,
            "message": "获取识别记录详情失败",
            "data": None
        }

@router.put("/{recognition_id}/correct")
async def correct_recognition(
    recognition_id: str = Path(description="识别ID"),
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
    recognition_id: str = Path(description="识别ID"),
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
    recognition_id: str = Path(description="识别ID"),
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    """保存校对记录"""
    # TODO: 实现校对记录保存
    return Result.ok(None, "校对记录已保存")
