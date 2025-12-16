from fastapi import APIRouter, Depends, Query, Path, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from typing import Optional, List
from app.common.response import Result
from app.common.page_result import PageResult
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.inscription_service import InscriptionService
from app.schemas.request.inscription import InscriptionCreateRequest, InscriptionUpdateRequest
import os
from app.config import settings
from app.utils.logger import logger
from urllib.parse import quote

router = APIRouter(prefix="/inscription", tags=["碑文"])

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """上传碑文图片"""
    # 验证文件类型
    file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
    if file_ext not in settings.file_upload_allowed_types:
        return Result.fail(ResultCode.BAD_REQUEST, f"不支持的文件类型，支持的类型: {', '.join(settings.file_upload_allowed_types)}")
    
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.file_upload_max_size:
        return Result.fail(ResultCode.BAD_REQUEST, f"文件大小超过限制，最大{settings.file_upload_max_size / 1024 / 1024}MB")
    
    # 保存文件
    upload_dir = settings.file_upload_path
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # 返回文件URL
    file_url = f"{settings.file_upload_url_prefix}/{file.filename}"
    
    logger.info(f"文件上传成功: {file_url}, user_id={user_id}")
    return Result.ok({"url": file_url})

@router.post("/recognize")
async def recognize(
    request: dict,
    user_id: int = Depends(get_current_user_id)
):
    """提交识别任务"""
    # TODO: 实现识别任务提交
    return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, "识别功能待实现")

@router.get("/list", response_model=Result[PageResult])
async def get_inscription_list(
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    sort: Optional[str] = Query(None, description="排序方式，如 created:desc"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    user_id: int = Depends(get_current_user_id)
):
    """获取我的碑文列表"""
    service = InscriptionService()
    try:
        result = await service.get_list(user_id, page, size, sort, keyword)
        return Result.ok(result)
    finally:
        await service.close()

@router.get("/{id}/download")
async def download_inscription(
    id: int = Path(..., description="碑文ID"),
    format: str = Query("txt", description="下载格式：txt, pdf, image"),
    user_id: int = Depends(get_current_user_id)
):
    """下载碑文"""
    service = InscriptionService()
    try:
        stream, media_type, filename = await service.download(id, format)
        
        encoded_filename = quote(filename)
        
        return StreamingResponse(
            stream, 
            media_type=media_type, 
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
            }
        )
    finally:
        await service.close()

@router.get("/{id}")
async def get_inscription_by_id(
    id: int = Path(..., description="碑文ID"),
    user_id: int = Depends(get_current_user_id)
):
    """获取碑文详情"""
    service = InscriptionService()
    try:
        inscription = await service.get_by_id(id)
        if not inscription:
            return Result.fail(ResultCode.INSCRIPTION_NOT_FOUND)
        return Result.ok(inscription)
    finally:
        await service.close()

@router.post("")
async def create_inscription(
    request: InscriptionCreateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """创建碑文记录"""
    service = InscriptionService()
    try:
        inscription = await service.create(user_id, request.dict(exclude_unset=True))
        return Result.ok(inscription)
    finally:
        await service.close()

@router.put("/{id}")
async def update_inscription(
    id: int = Path(..., description="碑文ID"),
    request: InscriptionUpdateRequest = None,
    user_id: int = Depends(get_current_user_id)
):
    """更新碑文"""
    service = InscriptionService()
    try:
        inscription = await service.update(id, user_id, request.dict(exclude_unset=True) if request else {})
        return Result.success(inscription)
    finally:
        await service.close()

@router.delete("/{id}")
async def delete_inscription(
    id: int = Path(..., description="碑文ID"),
    user_id: int = Depends(get_current_user_id)
):
    """删除碑文"""
    service = InscriptionService()
    try:
        await service.delete(id, user_id)
        return Result.ok()
    finally:
        await service.close()

@router.post("/batch_import")
async def batch_import_inscriptions(
    files: List[UploadFile] = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """批量导入碑文"""
    service = InscriptionService()
    try:
        result = await service.batch_import(user_id, files)
        return Result.ok(result)
    finally:
        await service.close()

@router.post("/save")
async def save_inscription(
    request: dict = Body(..., example={"itemId": 1}),
    user_id: int = Depends(get_current_user_id)
):
    """保存碑文到我的列表 (从知识库)"""
    service = InscriptionService()
    try:
        item_id = request.get("itemId")
        if not item_id:
            return Result.fail("Missing itemId")
            
        # 检查是否已存在
        # 这里简化为：如果是"收藏"逻辑，应该用收藏接口。
        # 如果是"复制"逻辑，则创建新记录。
        # 根据需求 "碑文详情页保存功能...调用保存API：POST /api/saves" (这里映射为 /save)
        
        source_item = await service.get_by_id(item_id)
        if not source_item:
            # 可能是知识库的文章ID，需要跨服务查询(这里简化，假设只在inscription表查)
            # 如果是跨服务，通常前端直接传内容更方便，或者后端调用 KnowledgeService
            return Result.fail(ResultCode.DATA_NOT_FOUND, "源碑文不存在")
            
        # 复制一份
        new_data = {
            "title": source_item.get("title", "") + " (副本)",
            "content": source_item.get("content", "") or source_item.get("text", ""),
            "image_url": source_item.get("image_url"),
            "dynasty": source_item.get("dynasty"),
            "category": source_item.get("category"),
            "status": "active",
            "type": "save"
        }
        await service.create(user_id, new_data)
        return Result.ok(message="保存成功")
    finally:
        await service.close()

@router.post("/{id}/publish")
async def publish_inscription(
    id: int = Path(..., description="碑文ID"),
    request: dict = None,
    user_id: int = Depends(get_current_user_id)
):
    """发布碑文"""
    platforms = request.get("platforms", []) if request else []
    schedule_time = request.get("scheduleTime") if request else None
    
    service = InscriptionService()
    try:
        await service.publish(user_id, id, platforms, schedule_time)
        return Result.ok()
    finally:
        await service.close()

@router.get("/search")
async def search_inscriptions(
    keyword: str = Query(..., description="搜索关键词")
):
    """搜索碑文"""
    service = InscriptionService()
    try:
        results = await service.search(keyword)
        return Result.ok(results)
    finally:
        await service.close()

