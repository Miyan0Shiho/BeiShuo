from typing import Any, Dict, Optional
import httpx
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
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(self.base_url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        if not isinstance(data, dict):
            raise RuntimeError("OCR响应解析失败：返回非JSON对象")

        message = data.get("message")
        if message != "success":
            info = data.get("info")
            # 尽最大努力提供可读错误信息
            if not info or not str(info).strip():
                # 尝试拼接返回体摘要
                try:
                    info = json.dumps({k: data.get(k) for k in ("message", "id", "info") if k in data}, ensure_ascii=False)
                except Exception:
                    info = "服务返回错误"
            raise RuntimeError(f"OCR识别失败：{info}")

        return data