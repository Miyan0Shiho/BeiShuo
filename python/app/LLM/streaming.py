import json
from typing import AsyncGenerator, List, Optional, Dict, Any
from fastapi.responses import StreamingResponse
from app.client.llm_client import LLMClient
from app.LLM.models import ReferenceCard


async def llm_stream_generator(
    question: str,
    context: Optional[List[str]],
    llm_client: LLMClient,
    references: Optional[List[ReferenceCard]] = None
) -> AsyncGenerator[bytes, None]:
    first_event = {
        "event": "status",
        "data": {"status": "accepted"}
    }
    yield f"data: {json.dumps(first_event, ensure_ascii=False)}\n\n".encode("utf-8")

    if references:
        ref_event = {
            "event": "references",
            "data": [r.model_dump() for r in references]
        }
        yield f"data: {json.dumps(ref_event, ensure_ascii=False)}\n\n".encode("utf-8")

    async for delta in llm_client.chat_stream(question, context):
        evt = {"event": "delta", "data": {"text": delta}}
        yield f"data: {json.dumps(evt, ensure_ascii=False)}\n\n".encode("utf-8")

    end_event = {"event": "status", "data": {"status": "success"}}
    yield f"data: {json.dumps(end_event, ensure_ascii=False)}\n\n".encode("utf-8")


def sse_response(generator: AsyncGenerator[bytes, None]) -> StreamingResponse:
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(generator, media_type="text/event-stream", headers=headers)