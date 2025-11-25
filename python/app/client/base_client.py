from typing import Optional, Dict, Any, List
import httpx
from app.config import settings
from app.utils.logger import logger

class BaseHTTPClient:
    """基础HTTP客户端"""
    
    def __init__(
        self,
        base_url: str,
        connect_timeout: int = 5000,
        read_timeout: int = 10000,
        retry_times: int = 3
    ):
        self.base_url = base_url.rstrip('/')
        self.connect_timeout = connect_timeout / 1000  # 转换为秒
        self.read_timeout = read_timeout / 1000
        self.retry_times = retry_times
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout=self.read_timeout, connect=self.connect_timeout, read=self.read_timeout, write=self.read_timeout)
        )
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """GET请求"""
        for attempt in range(self.retry_times):
            try:
                response = await self.client.get(path, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
                if attempt == self.retry_times - 1:
                    return None
            except Exception as e:
                logger.error(f"请求失败: {e}")
                if attempt == self.retry_times - 1:
                    return None
        return None
    
    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """POST请求"""
        for attempt in range(self.retry_times):
            try:
                response = await self.client.post(path, data=data, json=json, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
                if attempt == self.retry_times - 1:
                    raise
            except Exception as e:
                logger.error(f"请求失败: {e}")
                if attempt == self.retry_times - 1:
                    raise
        return None
    
    async def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """PUT请求"""
        for attempt in range(self.retry_times):
            try:
                response = await self.client.put(path, data=data, json=json, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
                if attempt == self.retry_times - 1:
                    raise
            except Exception as e:
                logger.error(f"请求失败: {e}")
                if attempt == self.retry_times - 1:
                    raise
        return None
    
    async def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """DELETE请求"""
        for attempt in range(self.retry_times):
            try:
                response = await self.client.delete(path, params=params, headers=headers)
                response.raise_for_status()
                return True
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
                if attempt == self.retry_times - 1:
                    return False
            except Exception as e:
                logger.error(f"请求失败: {e}")
                if attempt == self.retry_times - 1:
                    return False
        return False
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

