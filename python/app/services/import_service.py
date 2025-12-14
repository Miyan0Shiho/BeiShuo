from typing import List, Dict, Any, Optional
from app.client.redis_client import RedisClient
from app.client.database_client import DatabaseClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.utils.logger import logger
import time
import os
import io

class ImportService:
    def __init__(self):
        self.redis_client = RedisClient()
        self.database_client = DatabaseClient()

    async def upload_files(self, user_id: int, files: List[Any]) -> Dict[str, Any]:
        items = []
        for f in files:
            filename = f.filename or ""
            ext = os.path.splitext(filename)[1].lower()
            if ext != ".json":
                items.append({"filename": filename, "status": "failed", "reason": "仅支持 JSON 文件"})
                continue
            try:
                content_bytes = await f.read()
                if len(content_bytes) > 2 * 1024 * 1024:
                    items.append({"filename": filename, "status": "failed", "reason": "文件过大"})
                    continue
                import json
                try:
                    payload = json.loads(content_bytes.decode("utf-8"))
                except Exception as e:
                    logger.error(f"JSON decode failed: {e}")
                    items.append({"filename": filename, "status": "failed", "reason": "JSON解析失败"})
                    continue

                payload_list = []
                if isinstance(payload, list):
                    payload_list = payload
                elif isinstance(payload, dict):
                    payload_list = [payload]
                else:
                    items.append({"filename": filename, "status": "failed", "reason": "JSON格式必须为对象或数组"})
                    continue

                file_success_count = 0
                for idx, item in enumerate(payload_list):
                    # 映射字段
                    if "content" not in item and "text" in item:
                        item["content"] = item.get("text")
                    if "title" not in item and "name" in item:
                        item["title"] = item.get("name")
                    
                    # 必填校验
                    required = ["title", "content"]
                    missing = [k for k in required if k not in item]
                    if missing:
                        # 如果是多条记录，记录哪一条失败
                        msg = f"第{idx+1}条记录缺少字段: {', '.join(missing)}"
                        if len(payload_list) == 1:
                            items.append({"filename": filename, "status": "failed", "reason": msg})
                        # 对于列表导入，这里简化处理：如果部分失败，记录警告日志，不中断整个文件处理
                        # 或者我们可以将每条记录视为独立的导入项？
                        # 当前逻辑是 items 对应 files，如果一个 file 含多条，我们需要决定如何报告
                        # 方案：将每个 item 作为一个独立的导入结果？
                        # 这样会导致 items 数量 > files 数量，前端可能困惑
                        # 简单方案：如果文件中任何一条成功，则视为文件成功，但可以在 reason 中备注
                        continue

                    try:
                        import_id = f"imp:{user_id}:{int(time.time()*1000)}:{os.urandom(4).hex()}"
                        data = {
                            "id": import_id,
                            "userId": user_id,
                            "filename": filename, # 仍关联原文件名
                            "title": item.get("title") or "未命名",
                            "content": item.get("content") or "",
                            "source_id": item.get("id"),
                            "timestamp": item.get("timestamp"),
                            "dynasty": item.get("dynasty"),
                            "category": item.get("category"),
                            "image_url": item.get("image_url"),
                            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        if await self.redis_client.set(import_id, data, timeout=24*3600):
                            file_success_count += 1
                        else:
                            logger.error(f"Save import item failed: Redis set returned False for {import_id}")
                    except Exception as e:
                        logger.error(f"Save import item failed: {e}")
                
                if file_success_count > 0:
                    items.append({
                        "filename": filename, 
                        "status": "success", 
                        "id": "batch", 
                        "title": f"{filename} ({file_success_count}条)", 
                        "preview": "批量导入成功"
                    })
                else:
                    # 如果之前没有添加过失败记录（因为在循环里 continue 了），这里补充
                    # 如果 payload_list 为空
                    if not payload_list:
                        items.append({"filename": filename, "status": "failed", "reason": "JSON数组为空"})
                    elif len([it for it in items if it["filename"] == filename]) == 0:
                         items.append({"filename": filename, "status": "failed", "reason": "所有记录均缺少必填字段或保存失败"})

            except Exception as e:
                logger.error(f"upload failed {filename}: {e}")
                items.append({"filename": filename, "status": "failed", "reason": "服务处理失败"})
        summary = {
            "status": "success",
            "message": "上传完成",
            "count": sum(1 for it in items if it.get("status") == "success"),
            "failed": sum(1 for it in items if it.get("status") == "failed"),
            "items": items
        }
        return summary

    async def list_imports(self, user_id: int) -> List[Dict[str, Any]]:
        # Use search_keys instead of lrange
        pattern = f"imp:{user_id}:*"
        keys = await self.redis_client.search_keys(pattern)
        
        results = []
        for imp_id in keys:
            data = await self.redis_client.get(imp_id)
            if data:
                results.append(data)
        
        # Sort by created_at desc
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results

    async def get_import(self, user_id: int, import_id: str) -> Optional[Dict[str, Any]]:
        data = await self.redis_client.get(import_id)
        if not data or data.get("userId") != user_id:
            return None
        return data

    async def publish(self, user_id: int, import_id: str, category: Optional[str], tags: Optional[List[str]]) -> Dict[str, Any]:
        data = await self.get_import(user_id, import_id)
        if not data:
            raise BusinessException(ResultCode.DATA_NOT_FOUND, "导入记录不存在")
        title = data.get("title","").strip()
        content = data.get("content","").strip()
        if not title or not content:
            raise BusinessException(ResultCode.BAD_REQUEST, "标题或内容为空")
        try:
            keywords = self._extract_keywords(content)
            excerpt = self._extract_excerpt(content)
            sql = "INSERT INTO knowledge_articles(title, content, category, created_at) VALUES (%s, %s, %s, NOW())"
            await self.database_client.execute_update(sql, (title, content, category or None))
        except Exception as e:
            logger.error(f"publish insert failed: {e}")
        try:
            await self._clear_knowledge_cache()
        except Exception:
            pass
        await self.redis_client.delete(import_id)
        return {"status": "success", "message": "发布成功", "keywords": keywords, "summary": excerpt}

    def _extract_keywords(self, text: str) -> List[str]:
        import re
        words = re.findall(r"[\u4e00-\u9fa5]{2,}", text)
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w,_ in ranked[:8]]

    def _extract_excerpt(self, text: str) -> str:
        s = text.strip().replace("\r","")
        return s[:200] + ("..." if len(s) > 200 else "")

    async def _clear_knowledge_cache(self):
        keys = await self.redis_client.search_keys("knowledge:list:*")
        for k in keys:
            await self.redis_client.delete(k)
        keys = await self.redis_client.search_keys("search:knowledge:*")
        for k in keys:
            await self.redis_client.delete(k)

    async def close(self):
        await self.redis_client.close()
        await self.database_client.close()
