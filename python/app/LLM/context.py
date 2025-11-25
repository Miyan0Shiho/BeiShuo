from typing import List, Optional
import json
from app.client.redis_client import RedisClient
from app.config import settings
from app.LLM.models import Message, MessageStatus


class ContextManager:
    def __init__(self):
        self.redis = RedisClient()

    def _key_messages(self, conversation_id: str) -> str:
        return f"chat:{conversation_id}:messages"

    async def append_message(self, conversation_id: str, message: Message) -> None:
        key = self._key_messages(conversation_id)
        ttl = settings.cache_user_info_ttl
        messages = await self.get_messages(conversation_id)
        messages.append(message)
        data = json.dumps([m.model_dump() for m in messages], ensure_ascii=False)
        await self.redis.set(key, data, ttl)

    async def update_message_status(self, conversation_id: str, message_id: str, status: MessageStatus) -> None:
        key = self._key_messages(conversation_id)
        messages = await self.get_messages(conversation_id)
        for m in messages:
            if m.id == message_id:
                m.status = status
        data = json.dumps([m.model_dump() for m in messages], ensure_ascii=False)
        await self.redis.set(key, data, settings.cache_user_info_ttl)

    async def get_messages(self, conversation_id: str) -> List[Message]:
        key = self._key_messages(conversation_id)
        raw = await self.redis.get_value(key)
        if raw:
            try:
                arr = json.loads(raw)
                return [Message(**item) for item in arr]
            except Exception:
                return []
        return []

    async def reset_context(self, conversation_id: str) -> None:
        key = self._key_messages(conversation_id)
        await self.redis.delete_key(key)

    async def build_context_snippets(self, conversation_id: str, max_chars: int) -> Optional[str]:
        messages = await self.get_messages(conversation_id)
        if not messages:
            return None
        buf: List[str] = []
        total = 0
        for m in reversed(messages):
            piece = f"[{m.role}] {m.content}"
            length = len(piece)
            if total + length > max_chars:
                break
            buf.append(piece)
            total += length
        buf.reverse()
        return "\n".join(buf)