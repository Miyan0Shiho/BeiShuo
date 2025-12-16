from typing import List, Optional
import json
from app.client.database_client import DatabaseClient
from app.config import settings
from app.LLM.models import Message, MessageStatus


class ContextManager:
    def __init__(self):
        self.db_client = DatabaseClient()
        self.mem = {}

    async def append_message(self, conversation_id: str, message: Message) -> None:
        # 先更新内存缓存
        mem_key = f"chat:{conversation_id}:messages"
        messages = await self.get_messages(conversation_id)
        messages.append(message)
        data = json.dumps([m.model_dump() for m in messages], ensure_ascii=False)
        self.mem[mem_key] = data
        
        # 持久化到数据库
        message_data = message.model_dump()
        try:
            await self.db_client.add_message(conversation_id, message_data)
        except Exception as e:
            print(f"Error saving message to database: {e}")

    async def update_message_status(self, conversation_id: str, message_id: str, status: MessageStatus) -> None:
        # 先更新内存缓存
        mem_key = f"chat:{conversation_id}:messages"
        messages = await self.get_messages(conversation_id)
        for m in messages:
            if m.id == message_id:
                m.status = status
        data = json.dumps([m.model_dump() for m in messages], ensure_ascii=False)
        self.mem[mem_key] = data
        
        # 更新数据库
        try:
            await self.db_client.update_message_status(message_id, status.value)
        except Exception as e:
            print(f"Error updating message status in database: {e}")

    async def get_messages(self, conversation_id: str) -> List[Message]:
        # 先从内存缓存获取
        mem_key = f"chat:{conversation_id}:messages"
        raw = self.mem.get(mem_key)
        
        if raw:
            try:
                arr = json.loads(raw)
                return [Message(**item) for item in arr]
            except Exception:
                pass
        
        # 从数据库获取
        try:
            db_messages = await self.db_client.get_messages(conversation_id)
            if db_messages:
                messages = [Message(**msg) for msg in db_messages]
                # 更新内存缓存
                data = json.dumps([m.model_dump() for m in messages], ensure_ascii=False)
                self.mem[mem_key] = data
                return messages
        except Exception as e:
            print(f"Error getting messages from database: {e}")
        
        return []

    async def reset_context(self, conversation_id: str) -> None:
        # 清除内存缓存
        mem_key = f"chat:{conversation_id}:messages"
        self.mem.pop(mem_key, None)
        
        # 清除数据库中的对话消息
        try:
            await self.db_client.reset_conversation(conversation_id)
        except Exception as e:
            print(f"Error resetting conversation in database: {e}")

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