from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
import uuid
from datetime import datetime

from api.auth import get_current_user

router = APIRouter()

# 模拟收藏数据库
fake_favorites_db = {}

# 获取收藏列表
@router.get("")
async def get_favorites(
    type: Optional[str] = None,  # inscriptions|articles
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    user_favorites = []
    
    # 查找用户的所有收藏
    for favorite_id, favorite in fake_favorites_db.items():
        if favorite["user_id"] == current_user["id"]:
            # 如果指定了类型，则筛选
            if type and favorite["type"] != type:
                continue
            user_favorites.append({
                "id": favorite_id,
                "type": favorite["type"],
                "item": favorite["item"],
                "notes": favorite.get("notes", ""),
                "tags": favorite.get("tags", []),
                "created_at": favorite["created_at"]
            })
    
    # 按创建时间排序
    user_favorites.sort(key=lambda x: x["created_at"], reverse=True)
    
    # 分页
    start = (page - 1) * per_page
    end = start + per_page
    paginated_favorites = user_favorites[start:end]
    
    # 统计
    total_count = len(user_favorites)
    inscriptions_count = sum(1 for f in user_favorites if f["type"] == "inscription")
    articles_count = sum(1 for f in user_favorites if f["type"] == "article")
    
    return {
        "success": True,
        "data": {
            "favorites": paginated_favorites,
            "stats": {
                "total_count": total_count,
                "inscriptions_count": inscriptions_count,
                "articles_count": articles_count
            },
            "pagination": {
                "current_page": page,
                "total_pages": (total_count + per_page - 1) // per_page,
                "total_count": total_count
            }
        }
    }

# 添加收藏
@router.post("")
async def add_favorite(
    favorite_data: dict,
    current_user: dict = Depends(get_current_user)
):
    # 验证必需字段
    if "type" not in favorite_data or "item_id" not in favorite_data:
        raise HTTPException(
            status_code=400,
            detail="缺少必需字段：type 和 item_id"
        )
    
    # 生成收藏ID
    favorite_id = str(uuid.uuid4())
    
    # 模拟创建收藏
    fake_favorites_db[favorite_id] = {
        "user_id": current_user["id"],
        "type": favorite_data["type"],
        "item_id": favorite_data["item_id"],
        "item": {
            "id": favorite_data["item_id"],
            "title": f"{favorite_data['type']} 项目",
            "dynasty": "唐代" if favorite_data["type"] == "inscription" else None,
            "image_url": "https://example.com/image.jpg",
            "excerpt": "这是一个示例项目",
            "confidence": 98.7 if favorite_data["type"] == "inscription" else None
        },
        "notes": favorite_data.get("notes", ""),
        "tags": favorite_data.get("tags", []),
        "created_at": datetime.utcnow()
    }
    
    return {
        "success": True,
        "message": "已添加到收藏",
        "data": {
            "favorite_id": favorite_id
        }
    }

# 更新收藏
@router.put("/{favorite_id}")
async def update_favorite(
    favorite_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user)
):
    # 检查收藏是否存在
    if favorite_id not in fake_favorites_db:
        raise HTTPException(
            status_code=404,
            detail="收藏不存在"
        )
    
    favorite = fake_favorites_db[favorite_id]
    
    # 检查权限
    if favorite["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="无权修改此收藏"
        )
    
    # 更新字段
    if "notes" in update_data:
        favorite["notes"] = update_data["notes"]
    if "tags" in update_data:
        favorite["tags"] = update_data["tags"]
    
    return {
        "success": True,
        "message": "收藏已更新"
    }

# 删除收藏（同时支持deleteFavorite和removeFavorite，用于兼容前端）
@router.delete("/{favorite_id}")
async def delete_favorite(
    favorite_id: str,
    current_user: dict = Depends(get_current_user)
):
    # 检查收藏是否存在
    if favorite_id not in fake_favorites_db:
        raise HTTPException(
            status_code=404,
            detail="收藏不存在"
        )
    
    favorite = fake_favorites_db[favorite_id]
    
    # 检查权限
    if favorite["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="无权删除此收藏"
        )
    
    # 删除收藏
    del fake_favorites_db[favorite_id]
    
    return {
        "success": True,
        "message": "已从收藏中移除"
    }