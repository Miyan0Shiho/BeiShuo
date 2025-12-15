from typing import Optional, List, Dict, Any
from app.client.llm_client import LLMClient
from app.client.rag_client import RAGClient
from app.client.embedding_client import EmbeddingClient
from app.RAG.search import retrieve_local
from app.RAG.references import contexts_to_references
import json
from app.client.database_client import DatabaseClient
from app.core.exceptions import BusinessException
from app.common.result_code import ResultCode
from app.utils.logger import logger

class InterpretationService:
    """阐释服务"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.rag_client = RAGClient()
        self.database_client = DatabaseClient()
        self.embedding_client = EmbeddingClient()
    
    async def generate_interpretation(
        self,
        inscription_id: int,
        text: str,
        dynasty: Optional[str] = None
    ) -> str:
        """生成AI阐释"""
        # 获取RAG上下文
        context_list = await self._get_rag_context(text, inscription_id)
        context = "\n".join(context_list) if context_list else None
        
        # 调用LLM生成阐释
        interpretation = await self.llm_client.generate_interpretation(
            text=text,
            dynasty=dynasty,
            context=context
        )
        
        if not interpretation:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "AI阐释生成失败")
        
        logger.info(f"AI阐释生成成功: inscription_id={inscription_id}")
        return interpretation
    
    async def chat(self, question: str, inscription_id: Optional[int] = None) -> str:
        """AI对话"""
        context_list = await self._get_rag_context(question, inscription_id)
        answer = await self.llm_client.chat(question, context_list)
        
        if not answer:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "AI对话失败")
        
        return answer

    async def chat_with_references(self, question: str, inscription_id: Optional[int] = None):
        context_list = await self._get_rag_context(question, inscription_id)
        answer = await self.llm_client.chat(question, context_list)
        if not answer:
            raise BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "AI对话失败")
        return answer, (context_list or [])
    
    async def _get_rag_context(self, query: str, inscription_id: Optional[int] = None) -> List[str]:
        """获取RAG上下文（本地索引优先）"""
        try:
            emb = await self.embedding_client.embed_texts([query])
            if emb and len(emb) > 0:
                contexts = retrieve_local(emb[0], top_k=5)
                return contexts
            return []
        except Exception as e:
            logger.warning(f"本地RAG检索失败: {e}")
            return []
    
    async def generate_interpretation_cache_key(self, text: str, inscription_id: Optional[int]) -> str:
        """生成AI阐释缓存键"""
        import hashlib
        cache_input = f"interpretation:{text}:{inscription_id}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    async def generate_sections(self, text: str, inscription_id: Optional[int] = None):
        # 生成缓存键
        cache_key = await self.generate_interpretation_cache_key(text, inscription_id)
        
        # 检查数据库缓存
        cached_response = await self.database_client.get_llm_cache(cache_key)
        if cached_response:
            logger.info(f"AI阐释缓存命中: cache_key={cache_key}, inscription_id={inscription_id}")
            # 解析缓存内容
            try:
                cache_data = cached_response.get('reply', {}).get('content', '')
                if cache_data:
                    sections = json.loads(cache_data)
                    # 构造空的refs，因为缓存中没有保存refs
                    refs = []
                    return sections, refs
            except Exception as e:
                logger.error(f"解析AI阐释缓存失败: {e}")
        
        # 缓存未命中，生成阐释
        contexts = await self._get_rag_context(text, inscription_id)
        # 构造提示，约束为严格 JSON 输出
        system = (
            "你是一名严格的碑文阐释助手，仅使用输入的碑文原文与提供的上下文进行分析，输出简体中文。"
            "请只返回一个 JSON 对象，不要输出任何非 JSON 的字符，不要使用代码块语法。"
            "JSON 键为：history_markdown、culture_markdown、figures、timeline、recommended_reading。"
            "各字段要求如下："
            "history_markdown：400-600字，使用 Markdown 的三级标题（###）开头，并包含若干要点列表（- ），可使用**加粗**标注核心词，避免长段堆砌；仅描述该碑文的历史背景与语境，不得混入其他碑文信息；不确定之处标注‘待考’。"
            "culture_markdown：400-600字，使用 Markdown 的三级标题（###）与要点列表（- ），围绕书法风格、文化意义、学术价值等展开，保持客观与精炼。"
            "figures：数组，3-5条，每项包含 {name, role, description}；name 唯一且与碑文相关，role 简短（6-12字），description 40-80字，避免夸张与编造。"
            "timeline：数组，3-5条，按时间升序，每项包含 {year, title, description}；year 可近似或改用年代区间；title 简短，description 30-60字，聚焦与该碑文直接相关的事件；严禁跨碑文混入。"
            "recommended_reading：数组，3-5条，每项包含 {title, author, description}；title 为推荐书籍或文章的名称，author 为作者或来源，description 为简短推荐理由（30-50字）；推荐内容需与当前碑文主题相关。"
            "若未提供上下文或无法充分判断，仍需给出结构化内容，但请更为保守并在必要处标注‘待考’。"
        )
        context_text = "\n".join(contexts) if contexts else ""
        user = (
            f"碑文原文：\n{text}\n\n相关上下文：\n{context_text}\n"
        )
        
        # 直接构建完整的消息列表，调用LLM生成JSON格式的阐释
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        
        # 直接调用LLM的聊天接口，传递完整的消息列表
        try:
            # 使用自定义的HTTP请求，确保正确传递消息格式
            import httpx
            from app.config import settings
            
            data = {
                "model": settings.llm_model,
                "messages": messages,
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens
            }
            
            headers = {
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                response = await client.post(
                    f"{settings.llm_api_base_url}/chat/completions",
                    json=data,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                if result and "choices" in result:
                    choices = result["choices"]
                    if choices and len(choices) > 0:
                        message = choices[0].get("message", {})
                        data = message.get("content", "")
        except Exception as e:
            logger.error(f"直接LLM调用失败: {e}")
            # 降级使用llm_client.chat方法
            data = await self.llm_client.chat(user, contexts)
        
        sections = {
            "history_markdown": "",
            "culture_markdown": "",
            "figures": [],
            "timeline": [],
            "recommended_reading": []
        }
        
        if data:
            try:
                # 直接解析 JSON 或从 code fence 中提取
                cleaned = data.strip()
                if cleaned.startswith("{"):
                    obj = json.loads(cleaned)
                else:
                    # 查找第一个{和最后一个}之间的内容
                    start = cleaned.find("{")
                    end = cleaned.rfind("}")
                    if start != -1 and end != -1:
                        json_str = cleaned[start:end+1]
                        obj = json.loads(json_str)
                    else:
                        # 如果没有找到完整的JSON，尝试使用更灵活的解析方式
                        # 提取各个字段
                        import re
                        
                        # 初始化默认值
                        obj = {
                            "history_markdown": "",
                            "culture_markdown": "",
                            "figures": [],
                            "timeline": []
                        }
                        
                        # 尝试提取history_markdown
                        history_match = re.search(r'"history_markdown"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned, re.DOTALL)
                        if history_match:
                            obj["history_markdown"] = history_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                        
                        # 尝试提取culture_markdown
                        culture_match = re.search(r'"culture_markdown"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned, re.DOTALL)
                        if culture_match:
                            obj["culture_markdown"] = culture_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                        
                        # 提取timeline
                        timeline_match = re.search(r'"timeline"\s*:\s*\[([^\]]*)\]', cleaned, re.DOTALL)
                        if timeline_match:
                            timeline_str = timeline_match.group(1)
                            # 尝试匹配每个timeline条目
                            timeline_items = []
                            item_pattern = re.compile(r'\{[^}]*"year"\s*:\s*"?([^",}]+)"?[^}]*"title"\s*:\s*"([^"]+)"[^}]*"description"\s*:\s*"([^"]+)"[^}]*\}', re.DOTALL)
                            for match in item_pattern.finditer(timeline_str):
                                year = match.group(1).strip('"')
                                title = match.group(2)
                                description = match.group(3)
                                timeline_items.append({"year": year, "title": title, "description": description})
                            obj["timeline"] = timeline_items
                        
                        # 提取figures
                        figures_match = re.search(r'"figures"\s*:\s*\[([^\]]*)\]', cleaned, re.DOTALL)
                        if figures_match:
                            figures_str = figures_match.group(1)
                            # 尝试匹配每个figure条目
                            figure_items = []
                            item_pattern = re.compile(r'\{[^}]*"name"\s*:\s*"([^"]+)"[^}]*"role"\s*:\s*"([^"]+)"[^}]*"description"\s*:\s*"([^"]+)"[^}]*\}', re.DOTALL)
                            for match in item_pattern.finditer(figures_str):
                                name = match.group(1)
                                role = match.group(2)
                                description = match.group(3)
                                figure_items.append({"name": name, "role": role, "description": description})
                            obj["figures"] = figure_items
                        
                        # 提取recommended_reading
                        recommended_reading_match = re.search(r'"recommended_reading"\s*:\s*\[([^\]]*)\]', cleaned, re.DOTALL)
                        if recommended_reading_match:
                            recommended_reading_str = recommended_reading_match.group(1)
                            # 尝试匹配每个recommended_reading条目
                            recommended_reading_items = []
                            item_pattern = re.compile(r'\{[^}]*"title"\s*:\s*"([^"]+)"[^}]*"author"\s*:\s*"([^"]+)"[^}]*"description"\s*:\s*"([^"]+)"[^}]*\}', re.DOTALL)
                            for match in item_pattern.finditer(recommended_reading_str):
                                title = match.group(1)
                                author = match.group(2)
                                description = match.group(3)
                                recommended_reading_items.append({"title": title, "author": author, "description": description})
                            obj["recommended_reading"] = recommended_reading_items
            except Exception as e:
                # 解析失败，降级为简版摘要
                logger.error(f"AI阐释解析失败: {e}")
                summary = ("基于碑文与上下文的自动摘要：\n" + (context_text[:600] if context_text else text[:600]))
                sections["history_markdown"] = summary
            else:
                # 解析成功，更新sections
                sections["history_markdown"] = obj.get("history_markdown") or ""
                sections["culture_markdown"] = obj.get("culture_markdown") or ""
                sections["figures"] = obj.get("figures") or []
                sections["timeline"] = obj.get("timeline") or []
                sections["recommended_reading"] = obj.get("recommended_reading") or []
        
        # 将结果存入数据库缓存
        cache_data = {
            "reply": {
                "content": json.dumps(sections),
                "type": "interpretation",
                "sources": [],
                "suggestions": []
            }
        }
        await self.database_client.set_llm_cache(cache_key, cache_data)
        
        refs = contexts_to_references(contexts)
        logger.info(f"AI阐释章节生成成功: inscription_id={inscription_id}, timeline_count={len(sections['timeline'])}")
        return sections, refs
    
    async def save_interpretation(self, user_id: int, recognition_id: Optional[str], inscription_id: Optional[int], sections: Dict[str, Any]) -> bool:
        """保存AI阐释结果到数据库"""
        try:
            logger.debug(f"开始保存AI阐释结果: user_id={user_id}, recognition_id={recognition_id}, inscription_id={inscription_id}")
            
            # 这里我们将AI阐释结果保存到llm_cache表中，作为一种临时解决方案
            # 在实际应用中，应该创建专门的表来保存AI阐释结果
            import hashlib
            
            # 生成唯一的缓存键
            cache_input = f"{user_id}:{recognition_id}:{inscription_id}:{json.dumps(sections)}"
            cache_key = hashlib.md5(cache_input.encode()).hexdigest()
            
            # 保存到LLM缓存
            cache_data = {
                "reply": {
                    "content": json.dumps(sections),
                    "type": "interpretation",
                    "sources": [],
                    "suggestions": []
                }
            }
            
            await self.database_client.set_llm_cache(cache_key, cache_data)
            logger.info(f"AI阐释结果保存成功: cache_key={cache_key}")
            return True
        except Exception as e:
            logger.error(f"AI阐释结果保存失败: {e}")
            return False
    
    async def close(self):
        """关闭客户端连接"""
        await self.llm_client.close()
        await self.rag_client.close()
        await self.database_client.close()
        await self.embedding_client.close()

