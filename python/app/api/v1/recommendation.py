from fastapi import APIRouter, Depends, Query, Body
from typing import Optional, List, Dict, Any
from app.common.response import Result
from app.common.result_code import ResultCode
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendation", tags=["推荐系统"])

@router.post("/inscriptions")
async def get_recommended_inscriptions(
    ocr_text: Optional[str] = Body(None, description="OCR识别结果文本"),
    limit: int = Body(5, description="推荐数量，默认5条")
):
    """
    获取相关碑文推荐
    
    1. 当提供OCR识别结果文本时，基于文本内容推荐相关碑文
    2. 当未提供OCR文本或识别失败时，随机推荐碑文
    3. 推荐结果包含碑文标题、作者、简介等信息
    """
    service = RecommendationService()
    try:
        result = await service.get_recommended_inscriptions(ocr_text=ocr_text, limit=limit)
        return Result.ok(result, "获取推荐碑文成功")
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"获取推荐碑文失败: {str(e)}")
    finally:
        await service.close()

@router.get("/recognition/history")
async def get_recognition_history(
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=50, description="每页数量，默认10条，最大50条")
):
    """
    获取最近识别记录
    
    1. 从阿里云数据库中查询用户最近的碑文识别记录
    2. 展示识别时间、识别结果摘要及相关操作选项
    3. 实现分页加载机制
    """
    service = RecommendationService()
    try:
        result = await service.get_recognition_history(page=page, size=size)
        return Result.ok(result, "获取识别历史成功")
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"获取识别历史失败: {str(e)}")
    finally:
        await service.close()
