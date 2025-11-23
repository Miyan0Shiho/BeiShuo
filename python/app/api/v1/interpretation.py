from fastapi import APIRouter, Depends
from app.common.response import Result
from app.core.dependencies import get_current_user_id
from app.services.interpretation_service import InterpretationService
from app.schemas.request.interpretation import InterpretationRequest, ChatRequest

router = APIRouter(prefix="/interpretation", tags=["AI阐释"])

@router.post("/generate")
async def generate_interpretation(
    request: InterpretationRequest,
    user_id: int = Depends(get_current_user_id)
):
    """生成AI阐释"""
    service = InterpretationService()
    try:
        interpretation = await service.generate_interpretation(
            inscription_id=request.inscriptionId,
            text=request.text,
            dynasty=request.dynasty
        )
        return Result.success({"interpretation": interpretation})
    finally:
        await service.close()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)
):
    """AI对话"""
    service = InterpretationService()
    try:
        answer = await service.chat(
            question=request.question,
            inscription_id=request.inscriptionId
        )
        return Result.success({"answer": answer})
    finally:
        await service.close()

