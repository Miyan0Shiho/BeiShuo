from typing import Optional, List
from app.client.llm_client import LLMClient
from app.client.rag_client import RAGClient
from app.client.database_client import DatabaseClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.utils.logger import logger

class InterpretationService:
    """阐释服务"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.rag_client = RAGClient()
        self.database_client = DatabaseClient()
    
    async def generate_interpretation(
        self,
        inscription_id: int,
        text: str,
        dynasty: Optional[str] = None
    ) -> str:
        """生成AI阐释"""
        # 获取RAG上下文
        context_list = await self._get_rag_context(text, inscription_id)
        context = "\n".join(context_list) if context_list else None
        
        # 调用LLM生成阐释
        interpretation = await self.llm_client.generate_interpretation(
            text=text,
            dynasty=dynasty,
            context=context
        )
        
        if not interpretation:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "AI阐释生成失败")
        
        logger.info(f"AI阐释生成成功: inscription_id={inscription_id}")
        return interpretation
    
    async def chat(self, question: str, inscription_id: Optional[int] = None) -> str:
        """AI对话"""
        # 获取RAG上下文
        context_list = await self._get_rag_context(question, inscription_id)
        
        # 调用LLM进行对话
        answer = await self.llm_client.chat(question, context_list)
        
        if not answer:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "AI对话失败")
        
        return answer
    
    async def _get_rag_context(self, query: str, inscription_id: Optional[int] = None) -> List[str]:
        """获取RAG上下文"""
        try:
            context_list = await self.rag_client.retrieve(
                query=query,
                inscription_id=inscription_id
            )
            return context_list if context_list else []
        except Exception as e:
            logger.warning(f"RAG检索失败: {e}")
            return []
    
    async def close(self):
        """关闭客户端连接"""
        await self.llm_client.close()
        await self.rag_client.close()
        await self.database_client.close()

