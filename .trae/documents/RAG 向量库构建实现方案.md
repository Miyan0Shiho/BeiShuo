**目标**

* 取消在线检索协议，改为本地向量库（文件/文件夹）构建与检索。

* LLM 对话模型切换为通义千问 `qwen-flash`，遵循 OpenAI 兼容接口。

* 保持既有 API 文档与原型的结构，更新实现细节，不新增不必要的需求。

**总体变更**

* LLM：`settings.llm_model` 改为 `qwen-flash`，`llm_api_base_url` 改为阿里云百炼兼容端点（北京：`https://dashscope.aliyuncs.com/compatible-mode/v1`；新加坡：`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`），鉴权 `Authorization: Bearer {DASHSCOPE_API_KEY}`。

* RAG：移除外部 HTTP `/retrieve` 依赖，新增本地索引构建与检索模块；`InterpretationService` 优先走本地 RAG，空库时返回空上下文安全降级。

**LLM 接入细节（通义千问）**

* Chat（非流/流式）：调用 `POST /chat/completions`，模型名使用 `qwen-flash`；消息格式沿用现有实现（system+user+上下文）。

* 流式：在请求体中添加 `"stream": true`，服务端以 SSE 推送 `status → references → delta → success` 事件。

* 参考文档（OpenAI兼容 Chat）：

  * 使用 OpenAI 兼容接口调用通义千问模型（Base URL 与端点）：<https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope>

  * API 请求与响应参数详解（多语言与流式示例）：<https://help.aliyun.com/zh/dashscope/developer-reference/api-details>

**本地 RAG 向量库设计**

* 目录：`python/app/RAG/`

  * `ingest.py`：向量库构建脚本（读取文本/目录→分块→向量化→落盘）

  * `store.py`：本地索引读写（JSON 存储与内存加载）

  * `search.py`：相似度检索（余弦相似度 TopK）

  * `references.py`：上下文转引用卡片（已存在，复用）

* 索引文件：`python/app/RAG/index/rag_index.json`

  * 结构：`[{id, text, meta:{source_path, start_offset, end_offset, dynasty?, author?}, embedding:[...]}]`

* 分块策略：

  * 优先按章节/标签（如“原文：”“翻译：”“故事：”“知识点：”）切分；无法识别时按定长字符分块（如 800–1500 字）。

  * 过滤空白与重复段；保留来源元数据用于前端定位。

* 向量化模型：

  * 阿里云百炼 Embeddings，OpenAI 兼容 `/embeddings`；推荐 `text-embedding-v4`，支持自定义维度与低成本批量模式。

  * 请求示例：`{"model":"text-embedding-v4","input":"段文本","encoding_format":"float","dimensions":1024?}`

  * 参考文档：

    * 使用 OpenAI 兼容模式调用百炼 Embedding：<https://help.aliyun.com/zh/model-studio/embedding-interfaces-compatible-with-openai>

    * 文本与多模态向量化概述：<https://help.aliyun.com/zh/model-studio/embedding>

**检索流程**

* 查询向量：对用户问题生成向量（同模型/维度）。

* 相似度：与索引向量计算余弦相似度，取 `top_k`（默认 5）。

* 返回：将命中段落作为上下文传入 LLM（system 中合并），同时生成引用卡片 `ReferenceCard[]` 返回至 `reply.sources` 与消息 `references[]`。

**服务编排与接口对齐**

* `InterpretationService`

  * `chat_with_references(question, inscription_id?)`：改为本地检索（`search.py`），返回 `answer, contexts[]`。

  * `_get_rag_context()`：读取本地索引，若不存在索引则返回 `[]`。

* 路由（保持既有）

  * `POST /api/v1/ai/chat`：非流式对话，结果含 `reply.sources`（引用卡片）。

  * `POST /api/v1/ai/chat/stream`：流式对话，首包发送 `references`，随后 `delta`。

  * `GET /api/v1/ai/chat/messages`、`POST /api/v1/ai/context/reset`、`GET /api/v1/ai/context` 原样保留。

* 不新增外部 `/rag` HTTP 协议；索引构建通过本地脚本触发即可。

**安全与密钥**

* 不在仓库中写入或打印密钥；通过环境变量 `DASHSCOPE_API_KEY` 或 `settings.llm_api_key` 注入，不触达日志与响应体。

* 对明确提供的密钥不做硬编码或持久化，仅在运行时注入。

**构建流程示意**

1. 读取输入源：支持单文件 `碑文.txt` 或目录。
2. 识别章节标签并分块；保留元数据 `{source_path, section, offset}`。
3. 批量调用 `/embeddings` 获取向量（必要时分批），落盘至 `rag_index.json`。
4. 检索时加载索引到内存，计算余弦相似度并返回 TopK 段落。

**测试规范**

* 单测：

  * 切分器：对示例 `碑文.txt` 验证章节识别与分块长度。

  * Embedding 调用：mock `/embeddings` 返回与异常路径。

  * 检索：构造小索引，验证 TopK 正确与相似度排序稳定性。

  * 路由端到端：`/ai/chat` 与 `/ai/chat/stream` 验证引用卡片挂载与流式事件序列。

* 运行：`PYTHONPATH=. pytest -q`（沿用现有测试框架）。

**实施步骤**

* 第1步：新增 RAG 本地索引构建三件套（`ingest.py / store.py / search.py`），不引入新三方库。

* 第2步：更新 `InterpretationService` 从本地检索获取上下文，移除外部 HTTP 依赖。

* 第3步：在 `LLMClient` 中将模型改为 `qwen-flash`，保持兼容流式与非流式调用。

* 第4步：补充测试与使用指南（如何从 `碑文.txt` 构建索引）。

**说明**

* 你提供的 API Key 不会被写入代码或索引文件；使用环境变量传入。部署时设置 `DASHSCOPE_API_KEY` 即可。

* 不需要在线检索协议：本方案完全基于本地索引，前后端接口不变，体验对齐设计稿。

