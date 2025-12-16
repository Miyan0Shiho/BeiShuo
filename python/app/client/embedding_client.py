from typing import List, Optional, Dict, Any
from app.client.base_client import BaseHTTPClient
from app.config import settings


class EmbeddingClient(BaseHTTPClient):
    def __init__(self):
        super().__init__(
            base_url=settings.llm_api_base_url,
            connect_timeout=5000,
            read_timeout=settings.llm_timeout,
            retry_times=2
        )

    async def embed_texts(self, texts: List[str], dimensions: Optional[int] = None) -> List[List[float]]:
        headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
        data: Dict[str, Any] = {
            "model": "text-embedding-v4",
            "input": texts,
            "encoding_format": "float",
        }
        if dimensions:
            data["dimensions"] = dimensions
        result = await self.post("/embeddings", json=data, headers=headers)
        embeddings: List[List[float]] = []
        if result and "data" in result:
            for item in result["data"]:
                embeddings.append(item.get("embedding", []))
        return embeddings

    async def close(self):
        await super().close()