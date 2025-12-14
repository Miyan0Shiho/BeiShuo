from fastapi import APIRouter, Depends, UploadFile, File, Path, Body
from typing import List, Optional
from app.common.response import Result
from app.core.dependencies import get_current_user_id
from app.services.import_service import ImportService

router = APIRouter(prefix="/imports", tags=["我的导入"])

@router.post("/upload")
async def upload_imports(
    files: List[UploadFile] = File(...),
    user_id: int = Depends(get_current_user_id)
):
    service = ImportService()
    try:
        result = await service.upload_files(user_id, files)
        return Result.ok(result)
    finally:
        await service.close()

@router.get("/list")
async def list_imports(
    user_id: int = Depends(get_current_user_id)
):
    service = ImportService()
    try:
        result = await service.list_imports(user_id)
        return Result.ok(result)
    finally:
        await service.close()

@router.get("/{import_id}")
async def get_import(
    import_id: str = Path(...),
    user_id: int = Depends(get_current_user_id)
):
    service = ImportService()
    try:
        data = await service.get_import(user_id, import_id)
        if not data:
            return Result.ok({})
        return Result.ok(data)
    finally:
        await service.close()

@router.post("/{import_id}/publish")
async def publish_import(
    import_id: str = Path(...),
    body: dict = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    category = body.get("category")
    tags = body.get("tags", [])
    service = ImportService()
    try:
        result = await service.publish(user_id, import_id, category, tags)
        return Result.ok(result)
    finally:
        await service.close()
