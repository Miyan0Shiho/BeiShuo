from typing import Optional, List
from app.client.base_client import BaseHTTPClient
from app.config import settings

class RAGClient(BaseHTTPClient):
    """RAG服务客户端"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.rag_api_base_url,
            connect_timeout=settings.rag_api_connect_timeout,
            read_timeout=settings.rag_api_read_timeout,
            retry_times=2
        )
    
    async def retrieve(
        self,
        query: str,
        inscription_id: Optional[int] = None,
        top_k: Optional[int] = None
    ) -> Optional[List[str]]:
        """检索相关上下文"""
        if top_k is None:
            top_k = settings.rag_api_top_k
        
        data = {
            "query": query,
            "topK": top_k
        }
        if inscription_id:
            data["inscriptionId"] = inscription_id
        
        try:
            result = await self.post("/retrieve", json=data)
            if result and "contexts" in result:
                return result["contexts"]
            return []
        except Exception:
            return []

