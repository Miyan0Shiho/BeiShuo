from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict
import uuid
from datetime import datetime

from api.auth import get_current_user

router = APIRouter()

# 模拟知识库数据
fake_knowledge_base = [
    {
        "id": "1",
        "title": "唐代墓志铭简介",
        "content": "唐代墓志铭是研究唐代历史、文化和书法的重要资料。墓志铭一般包括志文和铭辞两部分，记录墓主生平、家族背景等信息。",
        "category": "历史知识",
        "tags": ["唐代", "墓志铭", "历史"]
    },
    {
        "id": "2",
        "title": "楷书书法特点",
        "content": "楷书是汉字书法中常见的一种字体，其特点是笔画平直，结构方正。唐代是楷书发展的黄金时期，涌现出欧阳询、颜真卿、柳公权等大师。",
        "category": "书法知识",
        "tags": ["楷书", "书法", "唐代"]
    },
    {
        "id": "3",
        "title": "古代纪年方法",
        "content": "中国古代常用干支纪年法，以天干地支相配，六十年为一甲子。除此之外，还有年号纪年、王公即位年次纪年等方法。",
        "category": "历史知识",
        "tags": ["干支纪年", "古代历法", "历史"]
    },
    {
        "id": "4",
        "title": "金石学概述",
        "content": "金石学是中国古代以研究古代青铜器和石刻为主要对象的学问，萌芽于先秦，发展于两汉，兴盛于宋代。",
        "category": "学术研究",
        "tags": ["金石学", "考古", "学术"]
    }
]

# 搜索知识库
@router.get("/search")
async def search_knowledge(
    query: str,
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    page: int = 1,
    per_page: int = 10,
    current_user: dict = Depends(get_current_user)
):
    # 搜索逻辑
    results = []
    
    for item in fake_knowledge_base:
        # 全文搜索
        text_to_search = f"{item['title']} {item['content']}".lower()
        query_lower = query.lower()
        
        # 类别筛选
        category_match = not category or item['category'] == category
        
        # 标签筛选
        tag_match = not tags or any(tag in item['tags'] for tag in tags)
        
        # 关键词匹配
        keyword_match = query_lower in text_to_search
        
        if keyword_match and category_match and tag_match:
            results.append({
                "id": item["id"],
                "title": item["title"],
                "category": item["category"],
                "tags": item["tags"],
                "excerpt": item["content"][:100] + "..."
            })
    
    # 分页
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]
    
    return {
        "success": True,
        "data": {
            "results": paginated_results,
            "total_count": len(results),
            "pagination": {
                "current_page": page,
                "total_pages": (len(results) + per_page - 1) // per_page
            }
        }
    }

# 获取知识详情
@router.get("/{knowledge_id}")
async def get_knowledge_detail(
    knowledge_id: str,
    current_user: dict = Depends(get_current_user)
):
    # 查找知识条目
    for item in fake_knowledge_base:
        if item["id"] == knowledge_id:
            return {
                "success": True,
                "data": {
                    "id": item["id"],
                    "title": item["title"],
                    "content": item["content"],
                    "category": item["category"],
                    "tags": item["tags"],
                    "related_knowledge": [
                        {
                            "id": "2",  # 示例相关知识
                            "title": "楷书书法特点",
                            "category": "书法知识"
                        }
                    ]
                }
            }
    
    raise HTTPException(
        status_code=404,
        detail="知识条目不存在"
    )

# 获取知识分类列表
@router.get("/categories/list")
async def get_categories(
    current_user: dict = Depends(get_current_user)
):
    # 获取所有分类
    categories = set(item["category"] for item in fake_knowledge_base)
    
    # 统计每个分类的数量
    category_stats = []
    for cat in categories:
        count = sum(1 for item in fake_knowledge_base if item["category"] == cat)
        category_stats.append({
            "name": cat,
            "count": count
        })
    
    return {
        "success": True,
        "data": {
            "categories": category_stats
        }
    }

# 获取热门标签
@router.get("/tags/hot")
async def get_hot_tags(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    # 统计所有标签的频率
    tag_counts = {}
    for item in fake_knowledge_base:
        for tag in item["tags"]:
            if tag in tag_counts:
                tag_counts[tag] += 1
            else:
                tag_counts[tag] = 1
    
    # 排序并取前N个
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    hot_tags = [
        {
            "name": tag[0],
            "count": tag[1]
        }
        for tag in sorted_tags[:limit]
    ]
    
    return {
        "success": True,
        "data": {
            "hot_tags": hot_tags
        }
    }