from typing import List, Dict, Any, Optional
from app.client.database_client import DatabaseClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.utils.logger import logger
import time
import os
import io

class ImportService:
    def __init__(self):
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
                        continue

                    try:
                        # 直接插入到inscriptions表中
                        inscription_data = {
                            "title": item.get("title") or "未命名",
                            "description": item.get("content") or "",
                            "dynasty": item.get("dynasty", "未知"),
                            "style": item.get("category", ""),
                            "cover_image_url": item.get("image_url", ""),
                            "status": "pending",
                            "userId": user_id
                        }
                        
                        # 使用inscription_service的create方法或者直接插入数据库
                        query = "INSERT INTO inscriptions (title, description, dynasty, style, cover_image_url, status, creator_user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        await self.database_client.execute_update(
                            query, 
                            (inscription_data["title"], 
                             inscription_data["description"], 
                             inscription_data["dynasty"], 
                             inscription_data["style"], 
                             inscription_data["cover_image_url"], 
                             inscription_data["status"], 
                             user_id)
                        )
                        file_success_count += 1
                        logger.info(f"导入记录成功: {inscription_data['title']}")
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
        # 直接查询inscriptions表中用户创建的碑文记录
        query = "SELECT id, title, description, dynasty, style, cover_image_url, status, created_at FROM inscriptions WHERE creator_user_id = %s ORDER BY created_at DESC"
        results = await self.database_client.execute_query(query, (user_id,))
        
        # 格式化结果
        formatted_results = []
        for row in results:
            formatted_results.append({
                "id": str(row["id"]),
                "userId": user_id,
                "title": row["title"],
                "content": row["description"],
                "dynasty": row["dynasty"],
                "category": row["style"],
                "image_url": row["cover_image_url"],
                "status": row["status"],
                "created_at": row["created_at"]
            })
        
        return formatted_results

    async def get_import(self, user_id: int, import_id: str) -> Optional[Dict[str, Any]]:
        # 直接查询inscriptions表，根据ID获取碑文记录
        query = "SELECT id, title, description, dynasty, style, cover_image_url, status, created_at FROM inscriptions WHERE id = %s AND creator_user_id = %s"
        results = await self.database_client.execute_query(query, (int(import_id), user_id))
        
        if not results:
            return None
        
        row = results[0]
        return {
            "id": str(row["id"]),
            "userId": user_id,
            "title": row["title"],
            "content": row["description"],
            "dynasty": row["dynasty"],
            "category": row["style"],
            "image_url": row["cover_image_url"],
            "status": row["status"],
            "created_at": row["created_at"]
        }



    def _extract_keywords(self, text: str) -> List[str]:
        import re
        words = re.findall(r"[\u4e00-\u9fa5]{2,}", text)
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w,_ in ranked[:8]]

    def _extract_excerpt(self, text: str) -> str:
        s = text.strip().replace("\r","").replace("\n"," ")
        return s[:200] + ("..." if len(s) > 200 else "")

    async def close(self):
        """关闭客户端连接"""
        await self.database_client.close()
