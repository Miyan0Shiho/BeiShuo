"""
LLM缓存服务 - 基于现有llm_cache表结构

功能：
- 基于prompt和模型参数的LLM响应缓存
- 利用现有表结构实现高性能缓存
- 支持缓存命中统计和清理
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..client.mysql_client import mysql_client

logger = logging.getLogger(__name__)


class LLMCacheService:
    """LLM缓存服务类"""
    
    def __init__(self):
        self.db = mysql_client
    
    def generate_cache_key(self, prompt: str, model_params: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        Args:
            prompt: 用户输入的提示词
            model_params: 模型参数
            
        Returns:
            缓存键字符串
        """
        # 将prompt和模型参数组合生成唯一键
        key_data = f"{prompt}:{json.dumps(model_params, sort_keys=True)}"
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()
    
    async def get_cached_response(
        self, 
        prompt: str, 
        model_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的LLM响应
        
        Args:
            prompt: 用户输入的提示词
            model_params: 模型参数
            
        Returns:
            缓存的响应数据，如果未命中则返回None
        """
        try:
            cache_key = self.generate_cache_key(prompt, model_params)
            
            # 查询llm_cache表 - 根据实际的表结构调整
            query = """
                SELECT id, prompt_key, context_fingerprint, message_id, 
                       citations_fingerprint, model_key, model_provider, 
                       token_count, hit_count, expires_at, created_at
                FROM llm_cache
                WHERE prompt_key = %s
                LIMIT 1
            """
            
            result = await self.db.execute_query(query, (cache_key,))
            
            if result:
                # 更新命中次数
                await self.db.execute_update(
                    "UPDATE llm_cache SET hit_count = hit_count + 1, updated_at = %s WHERE id = %s",
                    (datetime.now(), result[0]['id'])
                )
                
                return {
                    'id': result[0]['id'],
                    'prompt_key': result[0]['prompt_key'],
                    'context_fingerprint': result[0]['context_fingerprint'],
                    'message_id': result[0]['message_id'],
                    'citations_fingerprint': result[0]['citations_fingerprint'],
                    'model_key': result[0]['model_key'],
                    'model_provider': result[0]['model_provider'],
                    'token_count': result[0]['token_count'],
                    'hit_count': result[0]['hit_count'] + 1,  # 返回更新后的命中次数
                    'expires_at': result[0]['expires_at'],
                    'created_at': result[0]['created_at']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取LLM缓存失败: {e}")
            return None
    
    async def cache_llm_response(
        self, 
        prompt: str, 
        response: str, 
        model_params: Dict[str, Any], 
        usage: Dict[str, Any],
        message_id: int = None
    ) -> bool:
        """
        缓存LLM响应到数据库
        
        Args:
            prompt: 用户输入的提示词
            response: LLM响应内容
            model_params: 模型参数
            usage: 使用量统计
            message_id: 关联的message_id（可选）
            
        Returns:
            缓存是否成功
        """
        try:
            cache_key = self.generate_cache_key(prompt, model_params)
            
            # 先检查是否已存在
            existing = await self.get_cached_response(prompt, model_params)
            if existing:
                logger.info(f"LLM响应已存在，跳过缓存: {cache_key}")
                return True
            
            # 插入llm_cache记录 - 根据实际的表结构调整
            query = """
                INSERT INTO llm_cache (
                    prompt_key, context_fingerprint, message_id, 
                    citations_fingerprint, model_key, model_provider,
                    token_count, hit_count, expires_at, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                cache_key,  # prompt_key
                hashlib.md5(prompt.encode('utf-8')).hexdigest(),  # context_fingerprint
                message_id,  # message_id (使用传入的message_id)
                hashlib.md5(response.encode('utf-8')).hexdigest(),  # citations_fingerprint
                model_params.get('model', 'unknown'),  # model_key
                model_params.get('provider', 'unknown'),  # model_provider
                usage.get('total_tokens', 0),  # token_count
                0,  # hit_count
                None,  # expires_at (暂时设为NULL)
                datetime.now(),  # created_at
                datetime.now()  # updated_at
            )
            
            await self.db.execute_insert(query, values)
            
            logger.info(f"LLM响应缓存成功: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"缓存LLM响应失败: {e}")
            return False
    
    async def cleanup_expired_llm(self, days: int = 30, min_hits: int = 5) -> int:
        """
        清理过期的LLM缓存
        
        Args:
            days: 保留天数
            min_hits: 最小命中次数阈值
            
        Returns:
            清理的记录数
        """
        try:
            # 删除超过指定天数且命中次数低于阈值的缓存
            query = """
                DELETE FROM llm_cache
                WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                AND hit_count < %s
            """
            
            result = await self.db.execute_delete(query, (days, min_hits))
            return result
            
        except Exception as e:
            logger.error(f"清理LLM缓存失败: {e}")
            return 0
    
    async def get_top_hit_cache(self, limit: int = 10) -> list:
        """
        获取高命中率的LLM缓存记录
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            高命中缓存记录列表
        """
        try:
            query = """
                SELECT id, prompt_key, model_key, hit_count, created_at, updated_at
                FROM llm_cache
                ORDER BY hit_count DESC
                LIMIT %s
            """
            
            result = await self.db.execute_query(query, (limit,))
            return result if result else []
            
        except Exception as e:
            logger.error(f"获取高命中LLM缓存失败: {e}")
            return []
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """获取LLM缓存统计信息"""
        try:
            # 统计总缓存数
            total_query = "SELECT COUNT(*) as total_count FROM llm_cache"
            
            # 统计命中率
            hit_query = """
                SELECT 
                    AVG(hit_count) as avg_hits, 
                    SUM(hit_count) as total_hits,
                    COUNT(*) as total_entries
                FROM llm_cache
            """
            
            # 统计最近7天的缓存使用情况
            recent_query = """
                SELECT 
                    COUNT(*) as recent_count,
                    SUM(hit_count) as recent_hits
                FROM llm_cache
                WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            """
            
            # 统计不同模型的缓存分布
            model_query = """
                SELECT 
                    model_provider, 
                    COUNT(*) as count,
                    AVG(hit_count) as avg_hits
                FROM llm_cache
                GROUP BY model_provider
            """
            
            total_result = await self.db.execute_query(total_query)
            hit_result = await self.db.execute_query(hit_query)
            recent_result = await self.db.execute_query(recent_query)
            model_result = await self.db.execute_query(model_query)
            
            model_distribution = {}
            if model_result:
                for row in model_result:
                    model_distribution[row['model_provider']] = {
                        'count': row['count'],
                        'avg_hits': float(row['avg_hits']) if row['avg_hits'] else 0.0
                    }
            
            return {
                'total_count': total_result[0]['total_count'] if total_result else 0,
                'avg_hits': float(hit_result[0]['avg_hits']) if hit_result and hit_result[0]['avg_hits'] else 0.0,
                'total_hits': hit_result[0]['total_hits'] if hit_result else 0,
                'total_entries': hit_result[0]['total_entries'] if hit_result else 0,
                'recent_count': recent_result[0]['recent_count'] if recent_result else 0,
                'recent_hits': recent_result[0]['recent_hits'] if recent_result else 0,
                'model_distribution': model_distribution
            }
            
        except Exception as e:
            logger.error(f"获取LLM缓存统计失败: {e}")
            return {
                'total_count': 0, 'avg_hits': 0.0, 'total_hits': 0, 
                'total_entries': 0, 'recent_count': 0, 'recent_hits': 0,
                'model_distribution': {}
            }
    
    async def get_top_hit_cache(self, limit: int = 10) -> list:
        """
        获取命中次数最高的缓存记录
        
        Args:
            limit: 返回记录数
            
        Returns:
            高命中缓存记录列表
        """
        try:
            query = """
                SELECT id, prompt_key, model_key, hit_count, created_at, updated_at
                FROM llm_cache
                ORDER BY hit_count DESC
                LIMIT %s
            """
            
            result = await self.db.execute_query(query, (limit,))
            return result if result else []
            
        except Exception as e:
            logger.error(f"获取高命中缓存失败: {e}")
            return []


# 全局LLM缓存服务实例
llm_cache_service = LLMCacheService()