from typing import Optional, List
from app.client.base_client import BaseHTTPClient
from app.config import settings

class LLMClient(BaseHTTPClient):
    """LLM服务客户端"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.llm_api_base_url,
            connect_timeout=5000,
            read_timeout=settings.llm_timeout,
            retry_times=2
        )
    
    async def generate_interpretation(
        self,
        text: str,
        dynasty: Optional[str] = None,
        context: Optional[str] = None
    ) -> Optional[str]:
        """生成AI阐释"""
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的碑文研究专家，擅长解读古代碑文的历史背景和文化意义。"
            },
            {
                "role": "user",
                "content": self._build_interpretation_prompt(text, dynasty, context)
            }
        ]
        
        data = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}"
        }
        
        try:
            result = await self.post("/chat/completions", json=data, headers=headers)
            if result and "choices" in result:
                choices = result["choices"]
                if choices and len(choices) > 0:
                    message = choices[0].get("message", {})
                    return message.get("content")
            return None
        except Exception:
            return None
    
    async def chat(self, question: str, context: Optional[List[str]] = None) -> Optional[str]:
        """AI对话"""
        messages = []
        
        if context:
            context_text = "\n".join(context)
            messages.append({
                "role": "system",
                "content": f"相关背景知识：\n{context_text}"
            })
        
        messages.append({
            "role": "user",
            "content": question
        })
        
        data = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}"
        }
        
        try:
            result = await self.post("/chat/completions", json=data, headers=headers)
            if result and "choices" in result:
                choices = result["choices"]
                if choices and len(choices) > 0:
                    message = choices[0].get("message", {})
                    return message.get("content")
            return None
        except Exception:
            return None
    
    def _build_interpretation_prompt(self, text: str, dynasty: Optional[str], context: Optional[str]) -> str:
        """构建阐释提示词"""
        prompt = f"请为以下{dynasty or '古代'}时期的碑文内容提供详细的历史文化阐释：\n\n"
        prompt += f"碑文内容：{text}\n\n"
        if context:
            prompt += f"上下文：{context}"
        return prompt

