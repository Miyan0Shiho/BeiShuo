import asyncio
from app.LLM.streaming import llm_stream_generator


class FakeLLM:
    async def chat_stream(self, question, context=None):
        for t in ["你好", "，这是", "流式输出"]:
            await asyncio.sleep(0)
            yield t


async def collect(generator):
    chunks = []
    async for b in generator:
        chunks.append(b.decode("utf-8"))
    return "".join(chunks)


def test_llm_stream_generator_event_sequence():
    gen = llm_stream_generator("问题", None, FakeLLM(), None)
    result = asyncio.get_event_loop().run_until_complete(collect(gen))
    assert "accepted" in result
    assert "delta" in result
    assert "success" in result