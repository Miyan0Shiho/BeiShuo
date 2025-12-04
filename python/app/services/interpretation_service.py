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

    async def generate_sections(self, text: str, inscription_id: Optional[int] = None):
        contexts = await self._get_rag_context(text, inscription_id)
        # 构造提示，约束为严格 JSON 输出
        system = (
            "你是一名严格的碑文阐释助手，仅使用输入的碑文原文与提供的上下文进行分析，输出简体中文。"
            "请只返回一个 JSON 对象，不要输出任何非 JSON 的字符，不要使用代码块语法。"
            "JSON 键为：history_markdown、culture_markdown、figures、timeline。"
            "各字段要求如下："
            "history_markdown：400-600字，使用 Markdown 的三级标题（###）开头，并包含若干要点列表（- ），可使用**加粗**标注核心词，避免长段堆砌；仅描述该碑文的历史背景与语境，不得混入其他碑文信息；不确定之处标注‘待考’。"
            "culture_markdown：400-600字，使用 Markdown 的三级标题（###）与要点列表（- ），围绕书法风格、文化意义、学术价值等展开，保持客观与精炼。"
            "figures：数组，3-5条，每项包含 {name, role, description}；name 唯一且与碑文相关，role 简短（6-12字），description 40-80字，避免夸张与编造。"
            "timeline：数组，3-5条，按时间升序，每项包含 {year, title, description}；year 可近似或改用年代区间；title 简短，description 30-60字，聚焦与该碑文直接相关的事件；严禁跨碑文混入。"
            "若未提供上下文或无法充分判断，仍需给出结构化内容，但请更为保守并在必要处标注‘待考’。"
        )
        context_text = "\n".join(contexts) if contexts else ""
        user = (
            f"碑文原文：\n{text}\n\n相关上下文：\n{context_text}\n"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        data = await self.llm_client.chat(question=user, context=[system, context_text] if context_text else [system])
        sections = {
            "history_markdown": "",
            "culture_markdown": "",
            "figures": [],
            "timeline": []
        }
        if data:
            try:
                # 直接解析 JSON 或从 code fence 中提取
                cleaned = data.strip()
                if cleaned.startswith("{"):
                    obj = json.loads(cleaned)
                else:
                    start = cleaned.find("{")
                    end = cleaned.rfind("}")
                    obj = json.loads(cleaned[start:end+1]) if start != -1 and end != -1 else {}
                sections["history_markdown"] = obj.get("history_markdown") or ""
                sections["culture_markdown"] = obj.get("culture_markdown") or ""
                sections["figures"] = obj.get("figures") or []
                sections["timeline"] = obj.get("timeline") or []
            except Exception as e:
                # 解析失败，降级为简版摘要
                logger.error(f"AI阐释解析失败: {e}")
                summary = ("基于碑文与上下文的自动摘要：\n" + (context_text[:600] if context_text else text[:600]))
                sections["history_markdown"] = summary
        
        refs = contexts_to_references(contexts)
        logger.info(f"AI阐释章节生成成功: inscription_id={inscription_id}")
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

