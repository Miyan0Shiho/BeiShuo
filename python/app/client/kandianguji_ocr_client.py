from typing import Any, Dict, Optional
import httpx
import asyncio
import json
from app.config import settings


class KandiangujiOCRClient:
    def __init__(self,
                 token: Optional[str] = None,
                 email: Optional[str] = None,
                 base_url: str = "https://ocr.kandianguji.com/ocr_api",
                 timeout_ms: Optional[int] = None):
        self.base_url = base_url
        self.token = token or settings.kandianguji_ocr_token
        self.email = email or settings.kandianguji_ocr_email
        self.timeout_ms = timeout_ms or settings.kandianguji_ocr_timeout

    async def recognize(self, image_base64: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.token or not self.email:
            raise ValueError("OCR配置缺失：请设置 KANDIANGUJI_OCR_TOKEN 与 KANDIANGUJI_OCR_EMAIL 环境变量")

        payload: Dict[str, Any] = {
            "token": self.token,
            "email": self.email,
            "image": image_base64,
        }
        if options:
            payload.update(options)

        timeout = httpx.Timeout(self.timeout_ms / 1000.0)
        attempt_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(self.base_url, json=payload)
                    if resp.status_code == 405:
                        # 尝试使用表单方式重试
                        resp = await client.post(self.base_url, data=payload)
                    resp.raise_for_status()
                    data = resp.json()
                break
            except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                attempt_error = e
                await asyncio.sleep(0.8 * (attempt + 1))
                continue
            except Exception as e:
                attempt_error = e
                break
        else:
            raise attempt_error or RuntimeError("OCR请求失败：网络超时")

        if not isinstance(data, dict):
            raise RuntimeError("OCR响应解析失败：返回非JSON对象")

        message = data.get("message")
        if message != "success":
            info = data.get("info")
            if not info or not str(info).strip():
                try:
                    info = json.dumps({k: data.get(k) for k in ("message", "id", "info") if k in data}, ensure_ascii=False)
                except Exception:
                    info = "服务返回错误"
            
            # 返回完整的响应数据，而不是抛出异常
            print(f"⚠️ OCR服务返回非成功状态: {message}, info: {info}")
            print(f"📋 完整响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 返回响应数据，让调用方处理
            return data

        return data