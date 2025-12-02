"""
图片代理路由模块
处理前端发送的OSS图片访问请求，通过后端代理访问OSS图片
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import asyncio
from urllib.parse import unquote
from app.utils.logger import logger

router = APIRouter(prefix="/proxy", tags=["图片代理"])

@router.get("/{path:path}")
async def proxy_image(request: Request, path: str):
    """
    代理访问图片
    
    处理前端发送的编码URL，如：
    GET /proxy/https%3A//beiwen1.oss-cn-hangzhou.aliyuncs.com/inscriptions/2025/12/01/80199d33.jpg?OSSAccessKeyId=...
    
    Args:
        request: FastAPI请求对象
        path: URL编码的图片路径
    
    Returns:
        StreamingResponse: 图片流响应
    """
    try:
        # 解码URL路径
        decoded_path = unquote(path)
        logger.info(f"图片代理请求: {decoded_path}")
        
        # 验证URL格式
        if not decoded_path.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="无效的URL格式")
        
        # 设置超时时间
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        # 使用httpx异步客户端获取图片
        async with httpx.AsyncClient(timeout=timeout) as client:
            # 转发原始请求的查询参数
            query_params = dict(request.query_params)
            
            # 发送请求到目标URL
            response = await client.get(
                decoded_path,
                params=query_params,
                headers={
                    # 转发一些必要的头信息
                    'User-Agent': 'Mozilla/5.0 (compatible; BeiwenOCR/1.0)',
                }
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"图片代理失败: {decoded_path}, 状态码: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"图片获取失败: {response.status_code}"
                )
            
            # 获取内容类型
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            # 返回图片流
            return StreamingResponse(
                response.iter_bytes(),
                media_type=content_type,
                headers={
                    'Cache-Control': 'public, max-age=3600',  # 缓存1小时
                    'Access-Control-Allow-Origin': '*',
                }
            )
            
    except httpx.TimeoutException:
        logger.error(f"图片代理超时: {path}")
        raise HTTPException(status_code=504, detail="图片获取超时")
    except httpx.RequestError as e:
        logger.error(f"图片代理请求错误: {e}")
        raise HTTPException(status_code=502, detail=f"图片代理错误: {str(e)}")
    except Exception as e:
        logger.error(f"图片代理异常: {e}")
        raise HTTPException(status_code=500, detail="图片代理服务异常")

@router.get("/health")
async def proxy_health_check():
    """图片代理健康检查"""
    return {"status": "ok", "service": "image_proxy"}