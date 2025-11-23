from fastapi import APIRouter, Depends, UploadFile, File, Header
from typing import Optional
from datetime import datetime, timezone
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.inscription_service import InscriptionService
from app.config import settings
from app.utils.logger import logger
import os
import uuid

router = APIRouter(prefix="/upload", tags=["上传"])

@router.post("/image")
async def upload_image(
    image: UploadFile = File(..., description="图片文件"),
    filename: Optional[str] = None,
    user_id: int = Depends(get_current_user_id)
):
    """上传图片"""
    # 验证文件类型
    file_ext = image.filename.split('.')[-1].lower() if image.filename else ''
    if file_ext not in settings.file_upload_allowed_types:
        return Result.error(
            ResultCode.BAD_REQUEST, 
            f"不支持的文件类型，支持的类型: {', '.join(settings.file_upload_allowed_types)}"
        )
    
    # 验证文件大小
    content = await image.read()
    if len(content) > settings.file_upload_max_size:
        return Result.error(
            ResultCode.BAD_REQUEST, 
            f"文件大小超过限制，最大{settings.file_upload_max_size / 1024 / 1024}MB"
        )
    
    # 生成唯一文件名
    if not filename:
        filename = f"{uuid.uuid4()}.{file_ext}"
    
    # 保存文件
    upload_dir = settings.file_upload_path
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # 返回文件URL
    file_url = f"{settings.file_upload_url_prefix}/{filename}"
    
    # 生成image_id
    image_id = f"img_{int(datetime.now().timestamp() * 1000)}"
    
    logger.info(f"文件上传成功: {file_url}, user_id={user_id}")
    
    # 返回前端期望的格式
    result = {
        "image_id": image_id,
        "image_url": file_url,
        "image_size": {
            "width": 0,  # TODO: 从图片中获取实际尺寸
            "height": 0
        },
        "file_size": len(content),
        "upload_time": datetime.now(timezone.utc).isoformat()
    }
    
    return Result.success("图片上传成功", result)

