from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, List
import uuid
from datetime import datetime

from api.auth import get_current_user

router = APIRouter()

# 翻译古典文本
@router.post("/translate")
async def translate_text(
    request_data: dict,
    current_user: dict = Depends(get_current_user)
):
    # 验证必需字段
    if "text" not in request_data:
        raise HTTPException(
            status_code=400,
            detail="缺少必需字段：text"
        )
    
    text = request_data["text"]
    target_language = request_data.get("target_language", "modern_chinese")
    options = request_data.get("options", {})
    
    # 模拟翻译结果
    translations = {
        "维大唐开元二十有九年，岁在辛巳，二月辛酉朔七日丁卯，故交州都督、上柱国、越国公李公墓志铭并序。": {
            "modern_chinese": "维大唐开元二十九年，岁在辛巳，二月辛酉初一七日丁卯，故交州都督、上柱国、越国公李公墓志铭并序。",
            "english": "In the 29th year of Kaiyuan era of the Tang Dynasty, during the Xin Si year, on the 7th day of the second lunar month, the epitaph of Li Gong, the late Governor of Jiaozhou, the Shang Zhuguo, and Duke of Yue, with its preface.",
            "simplified_explanation": "这是唐代开元二十九年的墓志铭开篇，记录了墓主人的身份。"
        },
        "故吏陈郡袁州刺史王仲回撰。": {
            "modern_chinese": "故吏陈郡袁州刺史王仲回撰写。",
            "english": "Written by Wang Zhonghui, the former official from Chen Commandery and governor of Yuanzhou.",
            "simplified_explanation": "说明此墓志铭的作者信息。"
        }
    }
    
    # 如果有匹配的翻译
    if text in translations and target_language in translations[text]:
        translation_result = translations[text][target_language]
    else:
        # 默认翻译
        translation_result = f"[{target_language}翻译] {text}"
    
    return {
        "success": True,
        "data": {
            "original_text": text,
            "translated_text": translation_result,
            "target_language": target_language,
            "confidence": 0.95,
            "translation_id": str(uuid.uuid4()),
            "word_count": len(text),
            "translation_time": 1.2
        }
    }

# 解释古典文本
@router.post("/explain")
async def explain_text(
    request_data: dict,
    current_user: dict = Depends(get_current_user)
):
    # 验证必需字段
    if "text" not in request_data:
        raise HTTPException(
            status_code=400,
            detail="缺少必需字段：text"
        )
    
    text = request_data["text"]
    detailed_level = request_data.get("detailed_level", "standard")  # basic, standard, detailed
    
    # 模拟解释结果
    explanations = {
        "开元二十有九年": {
            "basic": "开元二十九年，即公元741年。",
            "standard": "开元是唐玄宗李隆基的年号，开元二十九年对应公元741年，是唐代的强盛时期。",
            "detailed": "开元二十九年（741年）是唐玄宗李隆基统治的后期，此时唐朝国力达到鼎盛，史称'开元盛世'。这一年也是佛教、道教文化繁荣的时期，长安成为国际文化交流中心。"
        },
        "上柱国": {
            "basic": "上柱国是唐代的一种勋官称号。",
            "standard": "上柱国是唐代最高级别的勋官称号，正二品，授予有大功之臣，是一种荣誉性官职。",
            "detailed": "上柱国是唐代勋官体系中的最高等级，正二品。勋官是表示官员功劳的荣誉称号，不负责具体事务。上柱国这一称号始于战国时期的楚国，唐代沿用，授予在战场上立有大功的将领或对国家有重大贡献的官员。"
        }
    }
    
    # 查找最匹配的解释
    best_match = None
    for key, value in explanations.items():
        if key in text:
            best_match = value
            break
    
    if best_match and detailed_level in best_match:
        explanation_result = best_match[detailed_level]
    else:
        # 默认解释
        explanation_result = f"这是古典文献中的表述，需要进一步研究上下文以提供准确解释。"
    
    # 提取关键词
    keywords = ["唐代", "开元", "墓志铭", "官职"] if "开元" in text else ["古代", "文献"]
    
    return {
        "success": True,
        "data": {
            "original_text": text,
            "explanation": explanation_result,
            "detailed_level": detailed_level,
            "keywords": keywords,
            "difficulty": "medium",
            "related_references": [
                {
                    "title": "唐代官制研究",
                    "author": "陈寅恪",
                    "relevance": 0.85
                }
            ]
        }
    }

# 获取历史翻译记录
@router.get("/history/translate")
async def get_translation_history(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    # 模拟历史记录
    history = [
        {
            "id": str(uuid.uuid4()),
            "original_text": "维大唐开元二十有九年，岁在辛巳。",
            "translated_text": "维大唐开元二十九年，岁在辛巳。",
            "target_language": "modern_chinese",
            "created_at": datetime.utcnow(),
            "word_count": 10
        },
        {
            "id": str(uuid.uuid4()),
            "original_text": "故交州都督、上柱国、越国公李公墓志铭。",
            "translated_text": "The epitaph of Li Gong, the late Governor of Jiaozhou, the Shang Zhuguo, and Duke of Yue.",
            "target_language": "english",
            "created_at": datetime.utcnow().replace(minute=datetime.utcnow().minute - 10),
            "word_count": 12
        }
    ]
    
    return {
        "success": True,
        "data": {
            "history": history,
            "pagination": {
                "current_page": page,
                "total_pages": 1,
                "total_count": len(history)
            }
        }
    }

# 批量翻译术语
@router.post("/translate/terms")
async def translate_terms(
    request_data: dict,
    current_user: dict = Depends(get_current_user)
):
    terms = request_data.get("terms", [])
    
    if not terms:
        raise HTTPException(
            status_code=400,
            detail="缺少必需字段：terms"
        )
    
    # 模拟术语翻译
    term_translations = {
        "上柱国": "高级勋官称号，正二品",
        "交州": "古代地名，今越南北部及中国广西一部分",
        "墓志铭": "刻在墓碑上的文字，记录墓主生平",
        "开元": "唐玄宗年号，公元713-741年"
    }
    
    results = []
    for term in terms:
        results.append({
            "term": term,
            "translation": term_translations.get(term, "未找到该术语的解释"),
            "related_terms": ["唐代官制"] if term in ["上柱国"] else []
        })
    
    return {
        "success": True,
        "data": {
            "translations": results
        }
    }