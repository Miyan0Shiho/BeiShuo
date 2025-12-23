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

# 坐标转换工具函数
def _convert_word_positions(ocr_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将OCR结果中的字符位置从四边形格式转换为前端期望的矩形格式
    四边形格式：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    矩形格式：[x1, y1, x2, y2]
    保留字符的所有其他信息，包括候选字
    """
    logger.debug(f"开始坐标转换，OCR结果基本信息: {'result' in ocr_result and isinstance(ocr_result['result'], dict) or '无result字段'}")
    
    # 处理不同格式的OCR结果
    if "result" in ocr_result and isinstance(ocr_result["result"], dict):
        # 处理包含result字段的完整OCR结果
        result = ocr_result.copy()
        inner_result = result["result"].copy()
        
        logger.info(f"坐标转换: 处理完整OCR结果，包含text_lines: {'text_lines' in inner_result and isinstance(inner_result['text_lines'], list) or '无text_lines'}")
        
        if "text_lines" in inner_result and isinstance(inner_result["text_lines"], list):
            logger.info(f"坐标转换: 共 {len(inner_result['text_lines'])} 行文本需要转换")
            
            for line_index, line in enumerate(inner_result["text_lines"]):
                if "words" in line and isinstance(line["words"], list):
                    line_text = line.get("text", "")
                    logger.info(f"坐标转换: 处理第 {line_index+1} 行: '{line_text[:30]}...', 包含 {len(line['words'])} 个字符")
                    
                    # 保留原始单词列表，仅转换坐标
                    converted_words = []
                    for word_index, word in enumerate(line["words"]):
                        # 完整复制原始word，保留所有字段（包括候选字）
                        converted_word = word.copy()
                        char_text = converted_word.get("text", "")
                        word_pos = converted_word.get("position", [])
                        logger.debug(f"坐标转换: 字符 {word_index+1} '{char_text}' 原始位置: {word_pos}")
                        logger.debug(f"坐标转换: 字符 {word_index+1} 包含候选字: {converted_word.get('choices', [])[:2]}...")
                        
                        if isinstance(word_pos, list):
                            if len(word_pos) >= 2 and all(isinstance(p, list) for p in word_pos):
                                # 将四边形坐标转换为矩形坐标 [x1, y1, x2, y2]
                                # 使用左上和右下坐标作为矩形的对角
                                rect_pos = [
                                    word_pos[0][0],  # x1
                                    word_pos[0][1],  # y1
                                    word_pos[2][0],  # x2 (右下点)
                                    word_pos[2][1]   # y2 (右下点)
                                ]
                                converted_word["position"] = rect_pos
                                logger.info(f"坐标转换: 字符 {word_index+1} '{char_text}' 成功: 四边形{word_pos} -> 矩形{rect_pos}")
                            elif len(word_pos) == 4 and all(isinstance(p, (int, float)) for p in word_pos):
                                # 已经是正确格式，无需转换
                                logger.debug(f"坐标转换: 字符 {word_index+1} '{char_text}' 位置已正确: {word_pos}")
                            else:
                                # 格式不正确，设置为空数组
                                converted_word["position"] = []
                                logger.warning(f"坐标转换: 字符 {word_index+1} '{char_text}' 位置格式不正确: {word_pos}，已重置为空")
                        else:
                            # 格式不正确，设置为空数组
                            converted_word["position"] = []
                            logger.warning(f"坐标转换: 字符 {word_index+1} '{char_text}' 位置不是数组: {type(word_pos).__name__}: {word_pos}，已重置为空")
                        
                        # 添加转换后的单词到列表
                        converted_words.append(converted_word)
                    
                    # 更新行的单词列表
                    line["words"] = converted_words
            
            result["result"] = inner_result
            logger.info(f"坐标转换完成，处理了 {len(inner_result['text_lines'])} 行文本")
        else:
            logger.warning("坐标转换: OCR结果中未找到text_lines或text_lines不是列表")
    else:
        # 处理直接包含text_lines的OCR结果
        result = ocr_result.copy()
        
        logger.info(f"坐标转换: 处理直接OCR结果，包含text_lines: {'text_lines' in result and isinstance(result['text_lines'], list) or '无text_lines'}")
        
        if "text_lines" in result and isinstance(result["text_lines"], list):
            logger.info(f"坐标转换: 共 {len(result['text_lines'])} 行文本需要转换")
            
            for line_index, line in enumerate(result["text_lines"]):
                if "words" in line and isinstance(line["words"], list):
                    line_text = line.get("text", "")
                    logger.info(f"坐标转换: 处理第 {line_index+1} 行: '{line_text[:30]}...', 包含 {len(line['words'])} 个字符")
                    
                    # 保留原始单词列表，仅转换坐标
                    converted_words = []
                    for word_index, word in enumerate(line["words"]):
                        # 完整复制原始word，保留所有字段（包括候选字）
                        converted_word = word.copy()
                        char_text = converted_word.get("text", "")
                        word_pos = converted_word.get("position", [])
                        logger.debug(f"坐标转换: 字符 {word_index+1} '{char_text}' 原始位置: {word_pos}")
                        logger.debug(f"坐标转换: 字符 {word_index+1} 包含候选字: {converted_word.get('choices', [])[:2]}...")
                        
                        if isinstance(word_pos, list):
                            if len(word_pos) >= 2 and all(isinstance(p, list) for p in word_pos):
                                # 将四边形坐标转换为矩形坐标 [x1, y1, x2, y2]
                                # 使用左上和右下坐标作为矩形的对角
                                rect_pos = [
                                    word_pos[0][0],  # x1
                                    word_pos[0][1],  # y1
                                    word_pos[2][0],  # x2 (右下点)
                                    word_pos[2][1]   # y2 (右下点)
                                ]
                                converted_word["position"] = rect_pos
                                logger.info(f"坐标转换: 字符 {word_index+1} '{char_text}' 成功: 四边形{word_pos} -> 矩形{rect_pos}")
                            elif len(word_pos) == 4 and all(isinstance(p, (int, float)) for p in word_pos):
                                # 已经是正确格式，无需转换
                                logger.debug(f"坐标转换: 字符 {word_index+1} '{char_text}' 位置已正确: {word_pos}")
                            else:
                                # 格式不正确，设置为空数组
                                converted_word["position"] = []
                                logger.warning(f"坐标转换: 字符 {word_index+1} '{char_text}' 位置格式不正确: {word_pos}，已重置为空")
                        else:
                            # 格式不正确，设置为空数组
                            converted_word["position"] = []
                            logger.warning(f"坐标转换: 字符 {word_index+1} '{char_text}' 位置不是数组: {type(word_pos).__name__}: {word_pos}，已重置为空")
                        
                        # 添加转换后的单词到列表
                        converted_words.append(converted_word)
                    
                    # 更新行的单词列表
                    line["words"] = converted_words
            
            logger.info(f"坐标转换完成，处理了 {len(result['text_lines'])} 行文本")
        else:
            logger.warning("坐标转换: OCR结果中未找到text_lines或text_lines不是列表")
    
    logger.debug(f"坐标转换完成，最终结果: {result.keys()}")
    return result

def _normalize_ocr(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    归一化OCR识别结果，保留所有字符级别的详细信息
    """
    logger.debug(f"开始归一化OCR结果，原始数据: {data.keys()}")
    
    # 提取基本信息
    width = data.get("width") or 0
    height = data.get("height") or 0
    text_angel = data.get("text_angel")
    logger.debug(f"归一化: 图片尺寸={width}x{height}, 文本角度={text_angel}")
    
    # 提取文本信息，保留所有原始字符信息
    texts: List[str] = data.get("texts") or []
    text_lines: List[Dict[str, Any]] = data.get("text_lines") or []
    logger.debug(f"归一化: 原始texts={len(texts)}行, 原始text_lines={len(text_lines)}行")
    
    # 构建完整文本
    full_text = "\n".join(texts) if texts else ("\n".join([tl.get("text") or "" for tl in text_lines]) if text_lines else (data.get("text") or ""))
    logger.debug(f"归一化: 构建的完整文本长度={len(full_text)}, 内容前50字符='{full_text[:50]}...'")
    
    # 计算字符数量和置信度
    word_count = 0
    confidences: List[float] = []
    
    logger.debug(f"归一化: 开始处理text_lines，共{len(text_lines)}行")
    normalized_text_lines = []
    
    for line_index, tl in enumerate(text_lines or []):
        line_text = tl.get("text", "")
        words = tl.get("words") or []
        word_count += len(words)
        
        # 保留原始的word信息，包括position和候选字
        normalized_words = []
        for word_index, w in enumerate(words):
            # 完整复制原始word字典，保留所有字段
            normalized_word = w.copy()
            
            # 确保word包含必要的字段
            normalized_word.setdefault("text", "")
            normalized_word.setdefault("position", [])
            normalized_word.setdefault("confidence", 0.0)
            normalized_word.setdefault("choices", [])
            normalized_word.setdefault("det_confidence", normalized_word.get("confidence", 0.0))
            
            # 处理候选字，如果是字符串，转换成数组
            choices = normalized_word["choices"]
            if isinstance(choices, str):
                # 将字符串拆分成单个字符的数组
                normalized_word["choices"] = list(choices)
                logger.debug(f"将候选字字符串 '{choices}' 转换为数组: {normalized_word['choices']}")
            elif not isinstance(choices, list):
                # 如果不是数组，转换为空数组
                normalized_word["choices"] = []
                logger.debug(f"候选字不是数组，重置为空数组: {type(choices).__name__}")
            
            # 确保候选字列表不为空，至少包含当前字符本身
            if not normalized_word["choices"]:
                current_text = normalized_word["text"]
                if current_text:
                    normalized_word["choices"] = [current_text]  # 至少包含当前字符
                    logger.debug(f"候选字列表为空，添加当前字符 '{current_text}' 到候选字列表")
            
            normalized_words.append(normalized_word)
            
            # 处理置信度
            c = w.get("confidence")
            if c is None:
                c = w.get("det_confidence")
            if isinstance(c, (int, float)):
                confidences.append(float(c))
                logger.debug(f"归一化: 行{line_index+1}字符{word_index+1}: '{normalized_word['text']}', 置信度={c}, 位置={normalized_word['position']}, 候选字={normalized_word.get('choices', [])[:2]}...")
        
        # 构建归一化的文本行，保留所有原始信息
        normalized_line = tl.copy()
        normalized_line['words'] = normalized_words
        normalized_line.setdefault("text", line_text)
        normalized_line.setdefault("position", [])
        normalized_text_lines.append(normalized_line)
        
        logger.debug(f"归一化: 行{line_index+1}: 文本='{line_text[:20]}...', 字符数={len(normalized_words)}")
    
    # 如果没有通过words计算出字符数，使用full_text的长度
    if word_count == 0 and full_text:
        word_count = len(full_text)
        logger.debug(f"归一化: 使用full_text计算字符数={word_count}")
    
    # 计算平均置信度
    avg_conf = 0.0
    if confidences:
        avg_conf = round(sum(confidences) / len(confidences), 2)
        logger.debug(f"归一化: 平均置信度={avg_conf} (基于{len(confidences)}个字符)")
    elif isinstance(data.get("text_angel_confidence"), (int, float)):
        avg_conf = float(data.get("text_angel_confidence"))
        logger.debug(f"归一化: 使用文本角度置信度={avg_conf}")
    
    # 构建归一化结果，保留所有字符级别的详细信息
    normalized_result = {
        "width": width,
        "height": height,
        "text_angel": text_angel,
        "texts": texts,
        "text_lines": normalized_text_lines,  # 使用归一化后的文本行，保留完整字符信息
        "full_text": full_text or "",
        "word_count": word_count,
        "confidence": avg_conf,
        "layout": data.get("layout") or None,
    }
    
    logger.info(f"OCR结果归一化完成: 文本长度={len(full_text)}, 文本行数={len(normalized_text_lines)}, 字符数={word_count}, 平均置信度={avg_conf}")
    
    # 验证字符信息完整性
    for i, line in enumerate(normalized_text_lines[:2]):
        words = line.get("words", [])
        if words:
            first_word = words[0]
            logger.info(f"归一化结果验证 - 行{i+1}首个字符: 文本='{first_word['text']}', 位置={first_word['position']}, 候选字={first_word.get('choices', [])[:2]}...")
    
    return normalized_result

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
            
            # 当直接使用base64图片时，将其保存到本地临时目录，然后使用本地URL
            # 创建临时目录（如果不存在）
            temp_dir = os.path.join(os.getcwd(), "temp_oss_images")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成临时文件名
            import uuid
            temp_filename = f"temp_{uuid.uuid4()}.png"
            temp_file_path = os.path.join(temp_dir, temp_filename)
            logger.debug(f"生成临时文件路径: {temp_file_path}")
            
            # 保存base64图片到本地
            with open(temp_file_path, 'wb') as f:
                f.write(content)
            logger.info(f"base64图片保存到本地成功: {temp_file_path}")
            
            # 构建本地URL
            local_image_url = f"/temp_oss_images/{temp_filename}"
            image_url = local_image_url
            logger.info(f"base64图片转换为本地URL: {local_image_url}")
            
            # 保存临时文件信息，以便后续清理
            if not hasattr(result_with_request, 'temp_files'):
                result_with_request['temp_files'] = []
            result_with_request['temp_files'].append(temp_file_path)
            logger.debug(f"临时文件信息已添加到结果对象")

        # 生成图片哈希值，用于缓存
        image_hash = hashlib.md5(content).hexdigest()
        logger.debug(f"生成图片哈希值: {image_hash}")
        
        # 检查内存缓存
        logger.info(f"检查OCR内存缓存，当前缓存大小: {len(memory_cache)}")
        logger.info(f"待查询的图片哈希: {image_hash}")
        
        if image_hash in memory_cache:
            logger.info(f"✓ OCR内存缓存命中: image_hash={image_hash}")
            cache_result = memory_cache[image_hash]
            
            # 记录缓存结果的详细信息
            logger.debug(f"缓存结果结构: {list(cache_result.keys())}")
            
            if 'result' in cache_result:
                result = cache_result['result']
                logger.info(f"缓存结果包含result字段，结构: {list(result.keys())}")
                
                # 记录基本信息
                text = result.get('text', '')
                word_count = result.get('word_count', 0)
                confidence = result.get('confidence', 0.0)
                text_lines = result.get('text_lines', [])
                
                logger.info(f"缓存结果详细信息: 文本长度={len(text)}, 字符数={word_count}, 置信度={confidence}, 文本行数={len(text_lines)}")
                
                if text_lines and isinstance(text_lines, list):
                    logger.info(f"缓存结果包含 {len(text_lines)} 行文本")
                    
                    # 记录每行的详细信息
                    for line_idx, line in enumerate(text_lines[:3]):  # 只记录前3行
                        line_text = line.get('text', '')
                        line_words = line.get('words', [])
                        logger.debug(f"缓存结果行 {line_idx+1}: 文本='{line_text[:50]}...', 字符数={len(line_words)}")
                        
                        # 记录每个字符的位置信息和候选字
                        for word_idx, word in enumerate(line_words[:5]):  # 只记录前5个字符
                            char_text = word.get('text', '')
                            char_pos = word.get('position', [])
                            char_choices = word.get('choices', [])
                            logger.info(f"缓存结果行 {line_idx+1}字符 {word_idx+1}: '{char_text}', 位置={char_pos}, 候选字={char_choices[:2]}...")
            
            return Result.ok(cache_result, "识别完成（缓存命中）")
        
        logger.info(f"✗ OCR内存缓存未命中: image_hash={image_hash}")
        logger.debug(f"当前内存缓存包含 {len(memory_cache)} 条记录，键列表: {list(memory_cache.keys())[:5]}")
        
        # 检查数据库缓存作为备用
        logger.info(f"开始检查OCR数据库缓存: image_hash={image_hash}")
        
        # 初始化数据库客户端
        db_client = DatabaseClient()
        logger.debug(f"数据库客户端已初始化")
        
        existing_result = None
        try:
            logger.info(f"执行数据库查询: get_ocr_result_by_image_hash({image_hash})")
            existing_result = await db_client.get_ocr_result_by_image_hash(image_hash)
            logger.debug(f"数据库查询返回结果类型: {type(existing_result).__name__}")
            
            if existing_result:
                logger.info(f"数据库查询成功返回结果")
                logger.debug(f"数据库结果结构: {existing_result.keys()}")
                
                if existing_result.get("result"):
                    # 数据库缓存命中，更新内存缓存并返回结果
                    logger.info(f"✓ OCR数据库缓存命中: image_hash={image_hash}")
                    
                    # 获取并复制结果
                    cached_result = existing_result.get("result").copy()
                    logger.debug(f"数据库缓存结果结构: {list(cached_result.keys())}")
                    
                    # 检查并处理cached_result中的image_url
                    if 'result' in cached_result:
                        inner_result = cached_result['result']
                        cached_image_url = inner_result.get("image_url", "")
                        logger.info(f"数据库缓存结果的image_url: {cached_image_url}")
                        
                        if cached_image_url and (cached_image_url.startswith('http') or cached_image_url.startswith('https')):
                            logger.info(f"处理缓存结果中的OSS URL: {cached_image_url}")
                            
                            # 下载OSS图片到本地临时目录
                            try:
                                import uuid
                                import tempfile
                                import requests
                                
                                # 创建临时目录（如果不存在）
                                temp_dir = os.path.join(os.getcwd(), "temp_oss_images")
                                logger.debug(f"创建临时目录: {temp_dir}")
                                os.makedirs(temp_dir, exist_ok=True)
                                
                                # 生成临时文件名
                                temp_filename = f"temp_{uuid.uuid4()}.png"
                                temp_file_path = os.path.join(temp_dir, temp_filename)
                                logger.debug(f"生成临时文件路径: {temp_file_path}")
                                
                                # 下载OSS图片到本地
                                logger.info(f"下载缓存结果中的OSS图片到本地: {cached_image_url} -> {temp_file_path}")
                                response = requests.get(cached_image_url, timeout=10)
                                response.raise_for_status()
                                with open(temp_file_path, 'wb') as f:
                                    f.write(response.content)
                                logger.info(f"缓存图片下载成功: {temp_file_path}")
                                
                                # 构建本地URL
                                local_image_url = f"/temp_oss_images/{temp_filename}"
                                inner_result['image_url'] = local_image_url
                                logger.info(f"缓存结果的OSS URL已转换为本地URL: {local_image_url}")
                            except Exception as e:
                                logger.error(f"处理缓存结果的OSS URL失败: {e}")
                                # 如果处理失败，保持原URL不变
                                logger.info(f"使用缓存结果中的原始图片URL: {cached_image_url}")
                        
                        # 确保从数据库加载的结果格式正确
                        logger.info(f"检查从数据库加载的OCR结果格式")
                        logger.debug(f"调用_convert_word_positions确保字符位置格式正确")
                        cached_result["result"] = _convert_word_positions(cached_result["result"])
                        logger.info(f"坐标转换完成")
                    
                    # 更新内存缓存
                    logger.info(f"将数据库缓存结果加载到内存缓存: image_hash={image_hash}")
                    memory_cache[image_hash] = cached_result
                    logger.info(f"内存缓存已更新，当前大小: {len(memory_cache)}")
                    
                    # 记录缓存结果的字符位置信息
                    if 'result' in cached_result:
                        result = cached_result['result']
                        text_lines = result.get('text_lines', [])
                        logger.debug(f"缓存结果包含 {len(text_lines)} 行文本")
                        if text_lines:
                            first_line_words = text_lines[0].get('words', [])
                            if first_line_words:
                                logger.info(f"缓存结果第一行首个字符位置: {first_line_words[0].get('position', '无位置')}")
                    
                    logger.info(f"数据库缓存结果处理完成，准备返回")
                    return Result.ok(cached_result, "识别完成（数据库缓存命中）")
                else:
                    logger.warning(f"数据库结果缺少result字段")
                    logger.info(f"✗ OCR数据库缓存未命中或结果无效: image_hash={image_hash}")
            else:
                logger.info(f"✗ OCR数据库缓存未命中: image_hash={image_hash}")
        except Exception as e:
            logger.error(f"获取OCR数据库缓存失败: {e}", exc_info=True)
        finally:
            # 关闭数据库连接（如果有需要）
            logger.debug(f"数据库查询操作完成")
        
        # 缓存未命中或数据库服务不可用，执行OCR识别
        logger.info(f"OCR缓存未命中，执行新的识别: image_hash={image_hash}")

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
        logger.info(f"OCR识别结果生成完成，task_id={task_id}, recognition_id={recognition_id}")

        # 构建原始识别结果
        raw_result = {
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
        
        # 记录原始识别结果信息
        full_text = norm.get('full_text', '')
        text_lines = norm.get('text_lines', [])
        word_count = norm.get('word_count', 0)
        logger.info(f"OCR识别完成，详细结果: 文本长度={len(full_text)}, 文本行数={len(text_lines)}, 总字符数={word_count}, 置信度={norm.get('confidence', 0.0)}")
        logger.debug(f"原始OCR结果: 文本内容='{full_text[:100]}...', 文本行数量={len(text_lines)}")
        
        # 记录文本行详细信息
        for i, line in enumerate(text_lines[:3]):  # 只记录前3行
            line_text = line.get('text', '')
            line_words = line.get('words', [])
            logger.debug(f"原始OCR结果行 {i+1}: 文本='{line_text[:50]}...', 字符数={len(line_words)}")
            if line_words:
                logger.debug(f"行 {i+1} 首个字符: '{line_words[0].get('text', '')}', 位置={line_words[0].get('position', [])}")
        
        # 使用原始结果作为当前结果
        result = raw_result
        
        # 4. 将识别结果保存到数据库，以便后续缓存使用
        logger.info(f"OCR最终结果生成完成，准备保存到数据库: task_id={result['task_id']}, image_hash={image_hash}")
        logger.debug(f"最终结果结构: task_id={result['task_id']}, 文本长度={len(result['result'].get('text', ''))}, 文本行数={len(result['result'].get('text_lines', []))}")
        
        try:
            # 保存OCR结果，这会创建完整的OCR记录（asset、ocr_job、ocr_image、ocr_text_lines）
            logger.debug(f"开始保存OCR结果到数据库: task_id={task_id}, image_hash={image_hash}")
            
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
            import uuid
            
            # 创建临时目录（如果不存在）
            temp_dir = os.path.join(os.getcwd(), "temp_oss_images")
            logger.debug(f"准备创建临时目录: {temp_dir}")
            os.makedirs(temp_dir, exist_ok=True)
            logger.debug(f"临时目录创建成功: {temp_dir}")
            
            # 生成临时文件名
            temp_filename = f"temp_{uuid.uuid4()}.png"
            temp_file_path = os.path.join(temp_dir, temp_filename)
            logger.debug(f"生成临时文件路径: {temp_file_path}")
            
            # 处理OSS图片到本地的逻辑
            logger.info(f"处理图片URL: {image_url} -> {temp_file_path}")
            try:
                import requests
                import urllib.parse
                
                # 检查image_url是否是本地路径
                is_local_path = image_url.startswith('/')
                
                if is_local_path:
                    # 如果是本地路径，直接使用本地文件
                    logger.info(f"使用本地文件路径: {image_url}")
                    # 构建完整的本地文件路径
                    # 提取图片文件名
                    image_filename = os.path.basename(image_url)
                    logger.debug(f"提取图片文件名: {image_filename}")
                    
                    # 构建完整的本地文件路径
                    local_file_path = os.path.join(os.getcwd(), settings.file_upload_path, image_filename)
                    logger.debug(f"构建完整的本地文件路径: {local_file_path}")
                    
                    # 检查本地文件是否存在
                    if os.path.exists(local_file_path):
                        # 复制本地文件到临时目录
                        import shutil
                        shutil.copy(local_file_path, temp_file_path)
                        logger.info(f"本地文件复制到临时目录成功: {temp_file_path}")
                    else:
                        # 本地文件不存在，使用原始URL
                        logger.warning(f"本地文件不存在: {local_file_path}")
                        # 直接使用原始URL，不进行下载
                        result['result']['image_url'] = image_url
                        logger.info(f"使用原始图片URL: {image_url}")
                        # 跳过后续处理
                        raise Exception(f"本地文件不存在: {local_file_path}")
                else:
                    # 处理远程URL
                    download_url = image_url
                    if isinstance(download_url, str):
                        # 清理URL，移除可能的反引号和空格
                        download_url = download_url.strip().strip('`')
                        logger.debug(f"清理后的URL: {download_url}")
                        
                        # 检查是否有scheme
                        parsed_url = urllib.parse.urlparse(download_url)
                        if not parsed_url.scheme:
                            # 没有scheme，添加默认的http://
                            download_url = f"http://{download_url}"
                            logger.debug(f"添加默认scheme到URL: {download_url}")
                            # 重新解析URL，确保格式正确
                            parsed_url = urllib.parse.urlparse(download_url)
                        
                        # 确保URL有正确的netloc
                        if not parsed_url.netloc:
                            # 如果没有netloc，直接使用原始URL，不进行下载
                            logger.warning(f"URL没有有效的netloc: {download_url}")
                            result['result']['image_url'] = image_url
                            logger.info(f"使用原始图片URL: {image_url}")
                            raise Exception(f"URL没有有效的netloc: {download_url}")
                        
                        # 确保URL格式正确，特别是查询参数前有问号
                        query_str = f"?{parsed_url.query}" if parsed_url.query else ''
                        download_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}{query_str}{parsed_url.fragment if parsed_url.fragment else ''}"
                        logger.debug(f"修正后的下载URL: {download_url}")
                    else:
                        # 如果image_url不是字符串，直接使用原始URL
                        logger.warning(f"image_url不是字符串: {image_url}")
                        result['result']['image_url'] = image_url
                        logger.info(f"使用原始图片URL: {image_url}")
                        raise Exception(f"image_url不是字符串: {image_url}")
                    
                    logger.debug(f"开始下载图片: {download_url}")
                    response = requests.get(download_url, timeout=10)
                    response.raise_for_status()
                    logger.debug(f"图片下载成功，状态码: {response.status_code}, 大小: {len(response.content)} bytes")
                    
                    with open(temp_file_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"图片保存到本地成功: {temp_file_path}")
                
                # 构建本地URL
                local_image_url = f"/temp_oss_images/{temp_filename}"
                result['result']['image_url'] = local_image_url
                logger.info(f"添加本地临时图片URL到结果: {local_image_url}")
                
                # 保存临时文件信息，以便后续清理
                if not hasattr(result_with_request, 'temp_files'):
                    result_with_request['temp_files'] = []
                result_with_request['temp_files'].append(temp_file_path)
                logger.debug(f"临时文件信息已添加到结果对象")
            except Exception as e:
                logger.error(f"处理图片URL失败: {e}")
                # 无论如何，确保结果中包含image_url
                result['result']['image_url'] = image_url
                logger.info(f"使用原始图片URL: {image_url}")
            
            # 保存OCR结果到数据库
            logger.info(f"调用db_client.save_ocr_result保存OCR结果")
            saved_result = await db_client.save_ocr_result(task_id, result_with_request, image_hash, content)
            logger.info(f"OCR结果已保存到数据库: task_id={task_id}, image_hash={image_hash}")
            
            # 从保存结果中获取资产ID
            asset_id = None
            if saved_result and isinstance(saved_result, dict):
                asset_id = saved_result.get("asset_id")
                logger.debug(f"从保存结果中获取到的asset_id: {asset_id}")
                logger.info(f"OCR结果数据库保存成功，asset_id={asset_id}")
            else:
                logger.warning(f"从保存结果中未获取到asset_id，saved_result={saved_result}")
        except Exception as e:
            logger.error(f"保存OCR结果到数据库失败: {e}", exc_info=True)
            # 数据库服务不可用，继续返回OCR结果，不影响用户体验
        except Exception as e:
            logger.error(f"保存OCR结果到数据库失败: {e}", exc_info=True)
            # 数据库服务不可用，继续返回OCR结果，不影响用户体验
            pass
        
        # 确保结果中包含image_url字段，用于前端构建拼接图
        if "result" in result:
            # 如果result中还没有image_url，添加它
            if "image_url" not in result["result"]:
                # 确保image_url是有效的URL
                final_image_url = image_url
                if isinstance(image_url, str):
                    # 如果image_url是字符串，检查它是否是有效的URL或本地路径
                    if image_url.startswith('data:'):
                        # 是data URL，直接使用
                        final_image_url = image_url
                        logger.info(f"使用data URL作为image_url")
                    elif image_url.startswith('/'):
                        # 本地路径，构建完整的URL
                        # 使用服务器的实际地址或相对路径
                        final_image_url = f"{settings.file_upload_url_prefix}{image_url}" if not image_url.startswith(settings.file_upload_url_prefix) else image_url
                        logger.info(f"构建本地图片URL: {final_image_url}")
                    elif image_url.startswith('http') or image_url.startswith('https'):
                        # 已经是有效的URL，直接使用
                        logger.info(f"使用有效的image_url: {final_image_url}")
                    else:
                        # 可能是相对路径，尝试构建完整的URL
                        final_image_url = f"{settings.file_upload_url_prefix}/{image_url}"
                        logger.info(f"构建完整URL: {final_image_url}")
                else:
                    # 如果image_url不是字符串，使用默认图片URL
                    final_image_url = f"{settings.file_upload_url_prefix}/default-image.png"
                    logger.warning(f"image_url不是字符串，使用默认本地URL: {final_image_url}")
                result["result"]["image_url"] = final_image_url
        
        # 转换OCR结果中的字符位置格式
        logger.info(f"开始转换OCR结果中的字符位置格式")
        result_with_converted_positions = result.copy()
        if "result" in result_with_converted_positions:
            logger.debug(f"调用_convert_word_positions进行坐标转换")
            result_with_converted_positions["result"] = _convert_word_positions(result_with_converted_positions["result"])
            logger.info(f"坐标转换完成")
        
        # 将转换后的结果保存到内存缓存
        logger.info(f"准备将转换后的OCR结果保存到内存缓存: image_hash={image_hash}")
        logger.debug(f"缓存结果: task_id={result_with_converted_positions['task_id']}, 文本长度={len(result_with_converted_positions['result'].get('text', ''))}")
        
        memory_cache[image_hash] = result_with_converted_positions
        logger.info(f"OCR结果已保存到内存缓存: image_hash={image_hash}, 当前缓存大小={len(memory_cache)}")
        
        # 记录缓存结果的字符位置格式和候选字
        cached_text_lines = result_with_converted_positions['result'].get('text_lines', [])
        logger.debug(f"内存缓存结果包含 {len(cached_text_lines)} 行文本")
        for i, line in enumerate(cached_text_lines[:2]):
            line_words = line.get('words', [])
            logger.debug(f"缓存结果行 {i+1} 包含 {len(line_words)} 个字符")
            if line_words:
                first_word = line_words[0]
                char_text = first_word.get('text', '')
                char_pos = first_word.get('position', [])
                char_choices = first_word.get('choices', [])
                logger.info(f"缓存结果行 {i+1} 首个字符: '{char_text}', 转换后位置={char_pos}, 候选字={char_choices[:2]}...")
        
        logger.info(f"OCR识别完成，返回结果: task_id={task_id}, word_count={word_count}, confidence={norm.get('confidence', 0.0)}")
        logger.debug(f"最终返回结果结构: {result_with_converted_positions.keys()}")
        return Result.ok(result_with_converted_positions, "识别完成")
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

@router.delete("/cache/clear")
async def clear_ocr_cache():
    """清除OCR内存缓存"""
    global memory_cache
    cache_size = len(memory_cache)
    memory_cache.clear()
    logger.info(f"OCR内存缓存已清除，共清除 {cache_size} 条记录")
    return Result.ok({"cleared_count": cache_size}, "OCR内存缓存已清除")

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

