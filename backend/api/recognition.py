from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List, Dict
import os
import uuid
from datetime import datetime

from api.auth import get_current_user
from core.config import settings

router = APIRouter()

# 模拟存储
fake_image_db = {}
fake_recognition_tasks = {}
fake_recognition_history = {}

# 上传图片
@router.post("/upload/image")
async def upload_image(
    image: UploadFile = File(...),
    filename: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    # 生成唯一的图片ID
    image_id = f"img_{uuid.uuid4().hex[:8]}"
    
    # 保存文件（实际应该保存到磁盘或对象存储）
    content = await image.read()
    file_size = len(content)
    
    # 检查文件大小
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"文件大小超过限制，最大允许 {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 模拟保存图片信息
    fake_image_db[image_id] = {
        "image_id": image_id,
        "filename": filename or image.filename,
        "content_type": image.content_type,
        "size": file_size,
        "user_id": current_user["id"],
        "upload_time": datetime.utcnow()
    }
    
    return {
        "success": True,
        "message": "图片上传成功",
        "data": {
            "image_id": image_id,
            "image_url": f"https://cdn.example.com/images/{image_id}.jpg",
            "image_size": {
                "width": 800,
                "height": 600
            },
            "file_size": file_size,
            "upload_time": fake_image_db[image_id]["upload_time"].isoformat()
        }
    }

# 开始碑文识别
@router.post("/start")
async def start_recognition(
    request_data: dict,
    current_user: dict = Depends(get_current_user)
):
    image_id = request_data.get("image_id")
    
    # 检查图片是否存在
    if image_id not in fake_image_db:
        raise HTTPException(
            status_code=404,
            detail="图片不存在"
        )
    
    # 生成任务ID
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    # 模拟创建识别任务
    fake_recognition_tasks[task_id] = {
        "task_id": task_id,
        "image_id": image_id,
        "user_id": current_user["id"],
        "status": "processing",
        "progress": 0,
        "language": request_data.get("language", "classical"),
        "options": request_data.get("options", {}),
        "created_at": datetime.utcnow()
    }
    
    return {
        "success": True,
        "message": "识别任务已开始",
        "data": {
            "task_id": task_id,
            "status": "processing",
            "estimated_time": 30,  # 秒
            "progress": 0
        }
    }

# 查询识别进度
@router.get("/progress/{task_id}")
async def check_progress(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    if task_id not in fake_recognition_tasks:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
    
    task = fake_recognition_tasks[task_id]
    
    # 模拟任务完成
    if task["status"] == "processing":
        task["status"] = "completed"
        task["progress"] = 100
        
        # 生成识别结果
        recognition_id = f"rec_{uuid.uuid4().hex[:8]}"
        
        # 保存到历史记录
        if current_user["id"] not in fake_recognition_history:
            fake_recognition_history[current_user["id"]] = []
        
        fake_recognition_history[current_user["id"]].append({
            "id": recognition_id,
            "title": "模拟碑文",
            "image_url": f"https://cdn.example.com/images/{task['image_id']}.jpg",
            "original_text": "维大唐开元二十有九年，岁在辛巳，二月辛酉朔七日丁卯，故交州都督、上柱国、越国公李公墓志铭并序。",
            "confidence": 98.7,
            "dynasty": "唐代",
            "created_at": datetime.utcnow(),
            "is_favorited": False,
            "tags": ["唐代", "墓志铭"]
        })
    
    result = {
        "task_id": task["task_id"],
        "status": task["status"],
        "progress": task["progress"]
    }
    
    if task["status"] == "completed":
        result["result"] = {
            "recognition_id": f"rec_{uuid.uuid4().hex[:8]}",
            "original_text": "维大唐开元二十有九年，岁在辛巳，二月辛酉朔七日丁卯，故交州都督、上柱国、越国公李公墓志铭并序。",
            "modern_text": "维大唐开元二十九年，岁在辛巳，二月辛酉初一七丁卯，故交州都督、上柱国、越国公李公墓志铭并序。",
            "confidence": 98.7,
            "word_count": 28,
            "dynasty": "唐代",
            "period": "开元年间",
            "location": "当涂",
            "person": "李公",
            "estimated_year": "公元741年",
            "processing_time": 25
        }
    
    return {
        "success": True,
        "data": result
    }

# 获取识别历史记录
@router.get("/history")
async def get_recognition_history(
    page: int = 1,
    per_page: int = 20,
    dynasty: Optional[str] = None,
    sort: str = "date_desc",
    current_user: dict = Depends(get_current_user)
):
    user_history = fake_recognition_history.get(current_user["id"], [])
    
    # 筛选
    if dynasty:
        user_history = [h for h in user_history if h.get("dynasty") == dynasty]
    
    # 排序
    if sort == "date_desc":
        user_history.sort(key=lambda x: x["created_at"], reverse=True)
    else:
        user_history.sort(key=lambda x: x["created_at"])
    
    # 分页
    start = (page - 1) * per_page
    end = start + per_page
    paginated_history = user_history[start:end]
    
    return {
        "success": True,
        "data": {
            "recognition_list": paginated_history,
            "pagination": {
                "current_page": page,
                "total_pages": (len(user_history) + per_page - 1) // per_page,
                "total_count": len(user_history),
                "per_page": per_page
            }
        }
    }