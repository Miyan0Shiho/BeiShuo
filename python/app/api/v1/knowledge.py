from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["知识库"])

@router.get("/home")
async def get_knowledge_home(
    category: Optional[str] = Query(None, description="分类筛选"),
    period: Optional[str] = Query(None, description="时期筛选")
):
    """获取知识库首页"""
    service = KnowledgeService()
    try:
        result = await service.get_home(category=category, period=period)
        return Result.ok(result)
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"获取首页数据失败: {str(e)}")
    finally:
        await service.close()

@router.get("/articles/{article_id}")
async def get_article_detail(
    article_id: int = Path(..., description="文章ID")
):
    """获取文章详情"""
    service = KnowledgeService()
    try:
        result = await service.get_by_id(article_id)
        
        return Result.ok(result)
    except Exception as e:
        if "NOT_FOUND" in str(e) or "不存在" in str(e):
            return Result.fail(ResultCode.KNOWLEDGE_NOT_FOUND, "文章不存在")
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"获取文章详情失败: {str(e)}")
    finally:
        await service.close()

@router.get("/search")
async def search_knowledge(
    q: str = Query(..., description="搜索关键词"),
    type: Optional[str] = Query("all", description="搜索类型: all|articles|inscriptions"),
    category: Optional[str] = Query(None, description="分类筛选"),
    dynasty: Optional[str] = Query(None, description="朝代筛选"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量")
):
    """搜索知识库"""
    service = KnowledgeService()
    try:
        # 如果type不是articles，暂时只搜索文章（后续可以扩展搜索碑刻）
        if type != "all" and type != "articles":
            return Result.ok({
                "query": q,
                "total_results": 0,
                "results": [],
                "suggestions": [],
                "facets": {
                    "categories": [],
                    "dynasties": []
                }
            })
        
        # 转换分页参数（前端从1开始，后端从0开始）
        page_index = page - 1
        
        # 执行搜索
        search_result = await service.search(
            keyword=q,
            dynasty=dynasty,
            tags=None,  # 暂时不支持标签搜索
            page=page_index,
            size=per_page
        )
        
        # 获取分类和朝代列表用于facet
        categories = await service.get_categories()
        dynasties = await service.get_dynasties()
        
        # 构建响应
        result = {
            "query": q,
            "total_results": search_result.get("total", 0),
            "results": search_result.get("items", []),
            "suggestions": [],  # 暂时没有搜索建议功能
            "facets": {
                "categories": categories,
                "dynasties": dynasties
            },
            "pagination": {
                "current_page": page,
                "total_pages": (search_result.get("total", 0) + per_page - 1) // per_page if per_page > 0 else 0,
                "total_count": search_result.get("total", 0),
                "per_page": per_page
            }
        }
        
        return Result.ok(result)
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"搜索失败: {str(e)}")
    finally:
        await service.close()

@router.get("/list")
async def get_knowledge_list(
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    dynasty: Optional[str] = Query(None, description="朝代筛选"),
    category: Optional[str] = Query(None, description="分类筛选")
):
    """获取知识库列表"""
    service = KnowledgeService()
    try:
        result = await service.get_list(
            page=page,
            size=size,
            keyword=keyword,
            dynasty=dynasty,
            category=category
        )
        return Result.ok(result)
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"获取列表失败: {str(e)}")
    finally:
        await service.close()

@router.get("/categories")
async def get_categories():
    """获取分类列表"""
    service = KnowledgeService()
    try:
        result = await service.get_categories()
        return Result.ok(result)
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"获取分类列表失败: {str(e)}")
    finally:
        await service.close()

@router.get("/dynasties")
async def get_dynasties():
    """获取朝代列表"""
    service = KnowledgeService()
    try:
        result = await service.get_dynasties()
        return Result.ok(result)
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"获取朝代列表失败: {str(e)}")
    finally:
        await service.close()

@router.post("/articles/{article_id}/views")
async def increment_article_views(
    article_id: int = Path(..., description="文章ID")
):
    """增加文章查看次数"""
    service = KnowledgeService()
    try:
        result = await service.increment_views(article_id)
        if result:
            return Result.ok(None, "查看次数更新成功")
        else:
            return Result.fail(ResultCode.KNOWLEDGE_NOT_FOUND, "文章不存在或更新失败")
    except Exception as e:
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"更新查看次数失败: {str(e)}")
    finally:
        await service.close()

