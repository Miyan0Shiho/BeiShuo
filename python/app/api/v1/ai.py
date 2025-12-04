from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import datetime, timezone
from app.common.response import Result
from app.common.result_code import ResultCode
from app.core.dependencies import get_current_user_id
from app.services.interpretation_service import InterpretationService
from app.schemas.request.interpretation import InterpretationRequest, ChatRequest
from app.LLM.context import ContextManager
from app.LLM.models import Message, MessageStatus
from app.RAG.references import contexts_to_references
from app.LLM.streaming import llm_stream_generator, sse_response
from app.client.database_client import DatabaseClient
import uuid
import hashlib
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI功能"])

class InterpretationSectionsRequest(BaseModel):
    recognition_id: Optional[str] = None
    inscription_id: Optional[int] = None
    text: str
    conversation_id: Optional[str] = None

@router.post("/interpretation")
async def get_interpretation(
    request: InterpretationRequest,
    user_id: int = Depends(get_current_user_id)
):
    """获取AI阐释"""
    if not request.recognition_id:
        return Result.fail(ResultCode.BAD_REQUEST, "recognition_id不能为空")
    
    service = InterpretationService()
    try:
        # TODO: 调用服务层生成阐释
        results = {}
        
        aspects = request.aspects or ["history", "culture", "literature"]
        
        if "history" in aspects:
            results["history"] = {
                "title": "历史背景",
                "content": "",
                "key_points": []
            }
        
        if "culture" in aspects:
            results["culture"] = {
                "title": "文化意义",
                "content": "",
                "keywords": []
            }
        
        if "literature" in aspects:
            results["literature"] = {
                "title": "文学价值",
                "content": "",
                "style": "",
                "themes": []
            }
        
        result = {
            "interpretation_id": f"int_{int(datetime.now().timestamp() * 1000)}",
            "results": results,
            "related_inscriptions": []
        }
        
        return Result.ok(result)
    finally:
        await service.close()

@router.post("/interpretation/sections")
async def interpretation_sections(
    request: InterpretationSectionsRequest,
    user_id: int = Depends(get_current_user_id)
):
    if not request.text or not request.text.strip():
        return Result.fail(ResultCode.BAD_REQUEST, "text不能为空")
    service = InterpretationService()
    try:
        sections, refs = await service.generate_sections(request.text, request.inscription_id)
        conversation_id = request.conversation_id or f"conv_{int(datetime.now().timestamp() * 1000)}"
        
        # 保存AI阐释结果到数据库
        logger.debug(f"准备保存AI阐释结果: user_id={user_id}, recognition_id={request.recognition_id}, inscription_id={request.inscription_id}")
        save_result = await service.save_interpretation(
            user_id=user_id,
            recognition_id=request.recognition_id,
            inscription_id=request.inscription_id,
            sections=sections
        )
        
        if save_result:
            logger.info(f"AI阐释结果保存成功: conversation_id={conversation_id}")
        else:
            logger.warning(f"AI阐释结果保存失败: conversation_id={conversation_id}")
        
        return Result.ok({
            "conversation_id": conversation_id,
            "sections": sections,
            "sources": [r.model_dump() for r in refs]
        })
    except Exception as e:
        logger.exception(f"AI阐释生成失败: {e}")
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"生成失败: {str(e)}")
    finally:
        await service.close()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)
):
    """AI对话"""
    logger.debug(f"收到AI对话请求: user_id={user_id}, request={request}")
    
    if not request.message:
        logger.warning(f"AI对话请求失败: 缺少问题内容")
        return Result.fail(ResultCode.BAD_REQUEST, "问题不能为空")
    
    # 生成缓存键
    def generate_cache_key(message: str, context: Optional[str] = None) -> str:
        """生成LLM缓存键"""
        cache_input = f"{message}:{context or ''}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    cache_key = generate_cache_key(request.message, request.context)
    logger.debug(f"生成LLM缓存键: {cache_key}")
    
    # 检查数据库缓存
    db_client = DatabaseClient()
    cached_response = await db_client.get_llm_cache(cache_key)
    if cached_response:
        # 缓存命中，直接返回
        logger.info(f"LLM缓存命中: cache_key={cache_key}")
        logger.debug(f"缓存结果: {cached_response}")
        
        conversation_id = request.conversation_id or f"conv_{int(datetime.now().timestamp() * 1000)}"
        logger.debug(f"使用对话ID: {conversation_id}")
        
        ctx = ContextManager()
        
        # 添加用户消息
        user_msg = Message(id=str(uuid.uuid4()), role="user", content=request.message, status=MessageStatus.success)
        logger.debug(f"添加用户消息: msg_id={user_msg.id}, content={user_msg.content[:50]}...")
        await ctx.append_message(conversation_id, user_msg)
        
        # 添加助手消息（从缓存）
        assistant_msg = Message(
            id=str(uuid.uuid4()), 
            role="assistant", 
            content=cached_response["reply"]["content"], 
            status=MessageStatus.success
        )
        logger.debug(f"添加助手消息（缓存）: msg_id={assistant_msg.id}, content={assistant_msg.content[:50]}...")
        await ctx.append_message(conversation_id, assistant_msg)
        
        logger.info(f"LLM对话完成（缓存命中）: conversation_id={conversation_id}")
        return Result.ok(cached_response)
    
    # 缓存未命中，调用LLM
    logger.info(f"LLM缓存未命中: cache_key={cache_key}")
    service = InterpretationService()
    ctx = ContextManager()
    try:
        conversation_id = request.conversation_id or f"conv_{int(datetime.now().timestamp() * 1000)}"
        logger.debug(f"创建新对话: conversation_id={conversation_id}")
        
        user_msg = Message(id=str(uuid.uuid4()), role="user", content=request.message, status=MessageStatus.success)
        logger.debug(f"添加用户消息: msg_id={user_msg.id}, content={user_msg.content[:50]}...")
        await ctx.append_message(conversation_id, user_msg)

        # 调用LLM获取回答
        logger.info(f"调用LLM生成回答: conversation_id={conversation_id}")
        answer, contexts = await service.chat_with_references(request.message, None)
        logger.debug(f"LLM回答生成完成: answer_length={len(answer)}, contexts_count={len(contexts)}")
        
        # 处理引用
        logger.debug(f"处理RAG引用: contexts_count={len(contexts)}")
        refs = contexts_to_references(contexts)
        logger.debug(f"生成引用完成: references_count={len(refs)}")
        
        # 创建助手消息
        assistant_msg = Message(
            id=str(uuid.uuid4()), 
            role="assistant", 
            content=answer, 
            status=MessageStatus.success, 
            references=refs
        )
        logger.debug(f"添加助手消息: msg_id={assistant_msg.id}, content={assistant_msg.content[:50]}...")
        await ctx.append_message(conversation_id, assistant_msg)

        # 构建响应结果
        reply = {
            "content": answer,
            "type": "text",
            "sources": [r.model_dump() for r in refs],
            "suggestions": []
        }
        logger.debug(f"构建回复: content_length={len(answer)}, sources_count={len(reply['sources'])}")

        result = {
            "conversation_id": conversation_id,
            "reply": reply,
            "related_questions": []
        }
        
        # 缓存结果到数据库
        logger.info(f"保存LLM结果到缓存: cache_key={cache_key}")
        try:
            await db_client.set_llm_cache(cache_key, result)
            logger.debug(f"LLM结果缓存成功: cache_key={cache_key}")
        except Exception as e:
            logger.warning(f"LLM结果缓存失败: {e}")
        
        logger.info(f"LLM对话完成: conversation_id={conversation_id}, answer_length={len(answer)}")
        return Result.ok(result)
    except Exception as e:
        logger.exception(f"LLM对话失败: {e}")
        return Result.fail(ResultCode.INTERNAL_SERVER_ERROR, f"对话失败: {str(e)}")
    finally:
        await service.close()
        logger.debug(f"InterpretationService已关闭")

@router.get("/recommendations")
async def get_recommendations(
    user_id: int = Depends(get_current_user_id),
    type: Optional[str] = Query(None, description="推荐类型: inscriptions|articles|questions"),
    limit: int = Query(5, ge=1, le=20, description="推荐数量")
):
    """获取相关推荐"""
    # TODO: 实现推荐功能
    result = {
        "inscriptions": [],
        "articles": [],
        "questions": []
    }
    
    return Result.ok(result)


@router.get("/chat/messages")
async def get_chat_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    user_id: int = Depends(get_current_user_id)
):
    ctx = ContextManager()
    messages = await ctx.get_messages(conversation_id)
    items = sorted(messages, key=lambda m: m.created_at, reverse=(order == "desc"))
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]
    pagination = {
        "current_page": page,
        "total_pages": (total + per_page - 1) // per_page,
        "total_count": total,
        "per_page": per_page
    }
    return Result.ok({
        "messages": [m.model_dump() for m in page_items],
        "pagination": pagination
    })


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)
):
    if not request.message:
        return Result.fail(ResultCode.BAD_REQUEST, "问题不能为空")
    service = InterpretationService()
    ctx = ContextManager()
    conversation_id = request.conversation_id or f"conv_{int(datetime.now().timestamp() * 1000)}"
    user_msg = Message(id=str(uuid.uuid4()), role="user", content=request.message, status=MessageStatus.success)
    await ctx.append_message(conversation_id, user_msg)

    try:
        # 预先检索引用
        contexts = await service._get_rag_context(request.message, None)
        refs = contexts_to_references(contexts)

        async def generator():
            async for chunk in llm_stream_generator(request.message, contexts, service.llm_client, refs):
                yield chunk
            # 完成后写入助手消息
            # 为简单起见，此处不累加全文，前端可自行重组；也可在服务端聚合全文。
        return sse_response(generator())
    finally:
        await service.close()


@router.post("/context/reset")
async def reset_context(
    conversation_id: str,
    user_id: int = Depends(get_current_user_id)
):
    ctx = ContextManager()
    await ctx.reset_context(conversation_id)
    return Result.ok({"conversation_id": conversation_id, "status": "reset"})


@router.get("/context")
async def get_context(
    conversation_id: str,
    max_chars: int = Query(2000, ge=100, le=20000),
    user_id: int = Depends(get_current_user_id)
):
    ctx = ContextManager()
    snippet = await ctx.build_context_snippets(conversation_id, max_chars)
    return Result.ok({"conversation_id": conversation_id, "snippet": snippet or ""})

