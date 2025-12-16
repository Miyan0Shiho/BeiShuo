from typing import Optional, Dict, Any, List
from app.client.database_client import DatabaseClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.utils.logger import logger

class InscriptionService:
    """碑文服务"""
    
    def __init__(self):
        self.database_client = DatabaseClient()
    
    async def get_list(
        self,
        user_id: int,
        page: int = 0,
        size: int = 10,
        sort: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取碑文列表"""
        # 直接查数据库，不再使用Redis缓存
        result = await self.database_client.get_inscription_list(
            user_id=user_id,
            page=page,
            size=size,
            sort=sort,
            keyword=keyword
        )
        
        if not result:
            return {
                "list": [],
                "total": 0,
                "page": page,
                "size": size,
                "totalPages": 0
            }
        
        return result
    
    async def get_by_id(self, inscription_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取碑文详情"""
        logger.info(f"开始获取碑文详情: inscription_id={inscription_id}")
        inscription = await self.database_client.get_inscription_by_id(inscription_id)
        logger.info(f"获取碑文详情结果: inscription={inscription}")
        return inscription
    
    async def create(self, user_id: int, inscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建碑文"""
        logger.info(f"开始创建碑文: user_id={user_id}, inscription_data={inscription_data}")
        inscription_data["userId"] = user_id
        inscription = await self.database_client.create_inscription(inscription_data)
        logger.info(f"创建碑文结果: inscription={inscription}")
        
        if not inscription:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "碑文创建失败")
        
        logger.info(f"碑文创建成功: inscription_id={inscription.get('id')}, user_id={user_id}")
        return inscription
    
    async def update(self, inscription_id: int, user_id: int, inscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新碑文"""
        logger.info(f"开始更新碑文: inscription_id={inscription_id}, user_id={user_id}, inscription_data={inscription_data}")
        
        # 先检查碑文是否存在
        inscription = await self.database_client.get_inscription_by_id(inscription_id)
        logger.info(f"检查碑文是否存在结果: inscription={inscription}")
        
        if not inscription:
            raise BusinessException(ResultCode.INSCRIPTION_NOT_FOUND)
        
        # 检查权限
        if inscription.get("userId") != user_id:
            raise BusinessException(ResultCode.FORBIDDEN, "无权限修改此碑文")
        
        # 更新碑文
        result = await self.database_client.update_inscription(inscription_id, inscription_data)
        logger.info(f"更新碑文结果: result={result}")
        
        if not result:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "碑文更新失败")
        
        logger.info(f"碑文更新成功: inscription_id={inscription_id}")
        return result
    
    async def delete(self, inscription_id: int, user_id: int) -> bool:
        """删除碑文"""
        # 先检查碑文是否存在
        inscription = await self.database_client.get_inscription_by_id(inscription_id)
        if not inscription:
            raise BusinessException(ResultCode.INSCRIPTION_NOT_FOUND)
        
        # 检查权限
        if inscription.get("userId") != user_id:
            raise BusinessException(ResultCode.FORBIDDEN, "无权限删除此碑文")
        
        # 删除碑文
        success = await self.database_client.delete_inscription(inscription_id)
        if not success:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "碑文删除失败")
        
        logger.info(f"碑文删除成功: inscription_id={inscription_id}")
        return True
    
    async def search(self, keyword: str) -> List[Dict[str, Any]]:
        """模糊搜索碑文"""
        # 直接查数据库，不再使用Redis缓存
        result = await self.database_client.search_inscriptions(keyword)
        if not result:
            result = []
        
        return result

    async def download(self, inscription_id: int, file_format: str) -> tuple:
        """下载碑文文件
        
        Returns:
            tuple: (file_stream, media_type, filename)
        """
        import io
        import json
        
        inscription = await self.get_by_id(inscription_id)
        if not inscription:
            raise BusinessException(ResultCode.INSCRIPTION_NOT_FOUND)
            
        title = inscription.get("title", "未命名碑文")
        
        # 仅支持 JSON 格式
        if file_format == "json":
            data = {
                "id": inscription.get("id"),
                "title": title,
                "content": inscription.get("content", "") or inscription.get("text", ""),
                "timestamp": inscription.get("created_at"),
                "dynasty": inscription.get("dynasty"),
                "category": inscription.get("category"),
                "image_url": inscription.get("image_url")
            }
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            stream = io.BytesIO(json_str.encode("utf-8"))
            filename = f"{title}.json"
            return stream, "application/json", filename
        else:
            # 兼容旧逻辑，但推荐使用 JSON
            # 为满足"不需要其他格式，用JSON格式即可"的要求，这里强制转为 JSON 或抛错
            # 但为了系统健壮性，如果请求非 json，暂时抛错
            raise BusinessException(ResultCode.BAD_REQUEST, "仅支持 JSON 格式下载")

    async def batch_import(self, user_id: int, files: List[Any]) -> Dict[str, Any]:
        """批量导入碑文 (仅支持 JSON)"""
        import os
        import json
        count = 0
        failed = 0
        
        for file in files:
            try:
                filename = file.filename
                if not filename.lower().endswith(".json"):
                    logger.warning(f"跳过非 JSON 文件: {filename}")
                    failed += 1
                    continue
                    
                content = await file.read()
                try:
                    data = json.loads(content.decode("utf-8"))
                except json.JSONDecodeError:
                    logger.error(f"JSON 解析失败: {filename}")
                    failed += 1
                    continue
                
                # 内容校验
                if "title" not in data or "content" not in data:
                    logger.error(f"JSON 缺少必填字段: {filename}")
                    failed += 1
                    continue
                    
                # 创建记录
                inscription_data = {
                    "title": data.get("title"),
                    "content": data.get("content"),
                    "image_url": data.get("image_url", ""),
                    "dynasty": data.get("dynasty", "未知"),
                    "category": data.get("category", ""),
                    "status": "pending",
                    "type": "import"
                }
                await self.create(user_id, inscription_data)
                count += 1
            except Exception as e:
                logger.error(f"导入文件失败 {file.filename}: {e}")
                failed += 1
                
        return {"status": "success", "message": "上传成功", "count": count, "failed": failed}

    async def publish(self, user_id: int, inscription_id: int, platforms: List[str], schedule_time: Optional[str] = None) -> bool:
        """发布碑文"""
        inscription = await self.get_by_id(inscription_id)
        if not inscription:
            raise BusinessException(ResultCode.INSCRIPTION_NOT_FOUND)
            
        # 检查权限
        if inscription.get("userId") != user_id:
            raise BusinessException(ResultCode.FORBIDDEN)
            
        # 更新状态 - 使用inscriptions表中status字段的有效值
        status = "completed" if not schedule_time else "processing"
        await self.update(inscription_id, user_id, {"status": status})
        
        # 模拟推送到平台
        logger.info(f"碑文 {inscription_id} 发布至 {platforms}, 时间: {schedule_time or '立即'}")
        
        return True

    async def close(self):
        """关闭客户端连接"""
        await self.database_client.close()

