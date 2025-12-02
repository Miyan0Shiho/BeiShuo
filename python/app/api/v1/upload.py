from fastapi import APIRouter, Depends, UploadFile, File, Header
from typing import Optional
from datetime import datetime, timezone
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.inscription_service import InscriptionService
from app.services.oss_service import oss_service
from app.config import settings
from app.utils.logger import logger
import os
import uuid
import shutil
from pathlib import Path

router = APIRouter(prefix="/upload", tags=["上传"])

@router.post("/image")
async def upload_image(
    image: UploadFile = File(..., description="图片文件"),
    filename: Optional[str] = None,
    inscription_id: Optional[int] = None,
    user_id: int = Depends(get_current_user_id)
):
    """上传图片到OSS并创建asset记录"""
    try:
        # 验证文件类型
        file_ext = image.filename.split('.')[-1].lower() if image.filename else ''
        if file_ext not in settings.file_upload_allowed_types:
            return Result.fail(
                ResultCode.BAD_REQUEST,
                f"不支持的文件类型，支持的类型: {', '.join(settings.file_upload_allowed_types)}"
            )
        
        # 验证文件大小
        content = await image.read()
        if len(content) > settings.file_upload_max_size:
            return Result.fail(
                ResultCode.BAD_REQUEST,
                f"文件大小超过限制，最大{settings.file_upload_max_size / 1024 / 1024}MB"
            )
        
        # 使用原始文件名或生成唯一文件名
        if not filename:
            filename = image.filename or f"{uuid.uuid4()}.{file_ext}"
        
        # 如果inscription_id为空，创建临时碑文记录
        final_inscription_id = inscription_id
        if final_inscription_id is None:
            inscription_service = InscriptionService()
            try:
                # 创建临时碑文记录
                inscription_data = {
                    "title": f"临时碑文-{filename}",
                    "dynasty": "未知"
                }
                
                # 调用创建碑文服务
                new_inscription = await inscription_service.create(user_id, inscription_data)
                if new_inscription and "id" in new_inscription:
                    final_inscription_id = new_inscription["id"]
                    logger.info(f"为上传图片创建临时碑文记录: inscription_id={final_inscription_id}, filename={filename}")
                else:
                    return Result.fail(
                        ResultCode.INTERNAL_SERVER_ERROR,
                        "创建临时碑文记录失败"
                    )
            except Exception as e:
                logger.error(f"创建临时碑文记录失败: {e}")
                return Result.fail(
                    ResultCode.INTERNAL_SERVER_ERROR,
                    f"创建临时碑文记录失败: {str(e)}"
                )
            finally:
                await inscription_service.close()
        
        # 上传到OSS并创建asset记录
        upload_result = await oss_service.upload_image(
            content, 
            filename, 
            final_inscription_id
        )
        
        if not upload_result or 'asset_id' not in upload_result:
            return Result.fail(
                ResultCode.INTERNAL_SERVER_ERROR,
                "图片上传到OSS失败"
            )
        
        # 同时保存本地临时文件
        temp_file_path = None
        try:
            # 创建临时文件目录
            temp_dir = Path(settings.file_upload_path) / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成临时文件名（使用asset_id确保唯一性）
            temp_filename = f"temp_{upload_result['asset_id']}_{filename}"
            temp_file_path = temp_dir / temp_filename
            
            # 保存本地临时文件
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(content)
            
            logger.info(f"本地临时文件保存成功: {temp_file_path}")
            
        except Exception as e:
            logger.error(f"保存本地临时文件失败: {e}")
            # 临时文件保存失败不影响主要流程，继续返回OSS上传结果
        
        # 返回前端期望的格式，包含临时文件路径信息
        result = {
            "image_id": upload_result['asset_id'],  # 使用asset_id作为image_id
            "image_url": upload_result['url'],      # OSS访问URL
            "asset_id": upload_result['asset_id'],  # 新增asset_id字段
            "object_key": upload_result['object_key'],  # OSS对象键
            "file_hash": upload_result['file_hash'],    # 文件哈希
            "temp_file_path": str(temp_file_path) if temp_file_path else None,  # 本地临时文件路径
            "image_size": {
                "width": 0,  # TODO: 从图片中获取实际尺寸
                "height": 0
            },
            "file_size": len(content),
            "upload_time": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"图片上传到OSS成功: asset_id={upload_result['asset_id']}, user_id={user_id}")
        
        return Result.ok(result, "图片上传成功")
        
    except Exception as e:
        logger.error(f"图片上传失败: {e}")
        return Result.fail(
            ResultCode.INTERNAL_SERVER_ERROR,
            f"图片上传失败: {str(e)}"
        )

