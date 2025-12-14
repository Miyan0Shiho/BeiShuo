from fastapi import APIRouter, Depends, Body, Path
from app.common.response import Result
from app.core.dependencies import get_current_user_id
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorite", tags=["收藏"])

@router.post("/add")
async def add_favorite(
    request: dict = Body(..., example={"itemId": 1}),
    user_id: int = Depends(get_current_user_id)
):
    """添加收藏"""
    service = FavoriteService()
    try:
        item_id = request.get("itemId")
        if not item_id:
            return Result.fail("Missing itemId")
        await service.add_favorite(user_id, item_id)
        return Result.ok()
    finally:
        await service.close()

@router.delete("/{itemId}")
async def remove_favorite(
    itemId: int = Path(...),
    user_id: int = Depends(get_current_user_id)
):
    """移除收藏"""
    service = FavoriteService()
    try:
        await service.remove_favorite(user_id, itemId)
        return Result.ok()
    finally:
        await service.close()

@router.get("/list")
async def get_favorites(
    user_id: int = Depends(get_current_user_id)
):
    """获取收藏列表"""
    service = FavoriteService()
    try:
        ids = await service.get_favorites(user_id)
        return Result.ok(ids)
    finally:
        await service.close()