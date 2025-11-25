**总体架构**
- 后端形态：Python FastAPI 为主（`/api/v1`），Java Spring Boot 并存；遵循统一响应 `Result` 封装、JWT 认证。
- 现有链路（Python）：路由 `app/api/v1/ai.py:13` → 服务 `app/services/interpretation_service.py:9` → 客户端 `LLMClient` 与 `RAGClient`。
- LLM 替换：沿用 OpenAI 兼容的聊天接口，切换 Base URL 与模型到阿里云百炼通义千问兼容端点（POST `.../chat/completions`），模型如 `qwen-plus`，鉴权用 `DASHSCOPE_API_KEY`。[1][2][3]
- RAG：继续通过外部 RAG 服务 `settings.rag_api_base_url` 的 `/retrieve` 聚合上下文（`python/app/client/rag_client.py:16`）。

**目录规划**
- `python/app/LLM/`：消息流与上下文组件（模型定义、服务编排、流式输出适配），内部引用现有 `client/llm_client.py`。
- `python/app/RAG/`：检索与引用卡片适配层（结构规范、消息关联、交互状态），内部引用现有 `client/rag_client.py`。
- 不新增外部依赖；使用 FastAPI 原生 `StreamingResponse` 实现服务端流。

**接口清单与规格**
- 统一规范：JWT 校验 `Depends(get_current_user_id)`、`Result.success/error` 包装、时间戳 `ISO8601`，分页 `page(>=1) / per_page(<=100)`。

1) BS-44 LLM 对话接口
- `POST /api/v1/ai/chat`（非流式）
  - 请求：`recognition_id`、`message`、`context?`、`conversation_id?`
  - 响应：`conversation_id`、`reply{content,type,text|markdown}`、`status: success|failed`、`sources[]`、`related_questions[]`（与现有文档保持一致，`PYTHON_API_DOCUMENTATION.md:398`）。
- `GET /api/v1/ai/chat/messages`（历史列表）
  - 查询：`conversation_id`、`page`、`per_page`、`order: asc|desc`
  - 响应：`messages[]`（见消息标准），`pagination{current_page,total_pages,total_count,per_page}`。
- 消息标准（Message）
  - 字段：`id`、`role: user|assistant|system`、`content`、`status: sending|success|failed`、`created_at`、`references[]?`（与 BS-46 关联）
  - 排序：默认按 `created_at desc`，可指定 `order`。
- 状态管理
  - 写入 Redis 会话键：`chat:{conversation_id}:messages`（列表）、`chat:{conversation_id}:status`（会话级）、TTL 与刷新策略由 `settings.cache_*` 控制。

2) BS-45 上下文保持接口
- `POST /api/v1/ai/context/reset`：重置会话上下文（清除 Redis 缓存）。
- `GET /api/v1/ai/context`：查询会话上下文摘要（最近 N 条用户与助手消息）。
- 设计规则
  - 上下文长度限制：基于 `settings.llm_max_tokens` 与 `business.interpretation.max-context-length`（`src/main/resources/application.yml:96`；`python/app/config.py:29`）。
  - 截断策略：优先保留最近消息，合并系统提示与 RAG 片段，超过限制时按消息时间倒序裁剪。
  - 多轮关联：使用 `conversation_id` 作为关联主键；消息入库前先写 `sending` → 完成后更新 `success|failed`。

3) BS-46 引用卡片渲染与定位接口
- 数据结构（ReferenceCard）
  - 字段：`id`、`title`、`type: inscription|article|knowledge|web`、`snippet`、`source_url?`、`source_id?`、`meta{dynasty,tags,relevance}`。
- 关联机制
  - 在对话响应中返回 `references[]` 并为消息打点：`message.references = [...]`；引用来源来自 RAG `contexts` 聚合（`python/app/client/rag_client.py:16`）。
- 交互规范
  - 支持“定位到来源”与“展开更多”行为；后端返回 `source_id/source_url` 与偏移近似定位标识（如 `meta.offset?`）。

4) BS-47 流式对话输出接口
- `POST /api/v1/ai/chat/stream`：SSE/NDJSON 流式传输
  - 媒体类型：`text/event-stream` 或 `application/x-ndjson`
  - 事件：`status`（accepted/sending/success/failed）、`delta`（增量文本）、`usage`（可选）、`references`（首包提供）、`error`（中断原因）。
  - 传输协议
    - 首包：`{event:"status",data:{conversation_id,status:"accepted",timestamp}}`
    - 流包：`{event:"delta",data:{text:"..."}}`
    - 完结：`{event:"status",data:{status:"success"}}`
  - 错误与恢复：
    - 网络中断返回 `failed` 并记录最后 token 偏移；客户端可携带 `resume_token_index` 重试；后端从 Redis 最近上下文恢复。

**服务编排与实现要点**
- LLMClient 适配阿里云 DashScope 兼容接口
  - Base URL：北京 `https://dashscope.aliyuncs.com/compatible-mode/v1`；新加坡 `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
  - Endpoint：`POST /chat/completions`
  - 模型：`qwen-plus` 等；鉴权：`Authorization: Bearer {DASHSCOPE_API_KEY}`。[1][2][3]
  - 非流式：保持现有实现（`python/app/client/llm_client.py:16`）。
  - 流式：使用 `httpx.AsyncClient.stream` 读取分块，解析 `choices[].delta.content` 累加。
- RAGClient：维持 `/retrieve` 结构（`query, topK, inscriptionId`），统一到引用卡片结构。
- InterpretationService
  - 入参：`question/text` 与 `inscription_id`，先取 RAG 上下文，再组装 LLM 消息；失败走业务异常（`python/app/services/interpretation_service.py:35`）。
- RedisClient：用于会话上下文与消息流状态，键空间前缀 `chat:`，TTL 通过 `settings.cache_*`。

**API 请求/响应示例（与文档一致）**
- 非流式对话：复用 `PYTHON_API_DOCUMENTATION.md:398-436` 的结构与字段。
- 流式示例（SSE 首包与流包）
  - 首包：`{event:"status",data:{conversation_id:"conv_123",status:"accepted",timestamp:"2025-11-24T10:30:00Z"}}`
  - 流包：`{event:"delta",data:{text:"'维'在古文中是..."}}`

**测试用例规范**
- 框架：`pytest` + `pytest-asyncio`（`python/requirements.txt:29-30`）。
- 覆盖点：
  - LLM 非流式：模拟 `POST /chat/completions` 返回，断言消息解析与错误分支。
  - LLM 流式：模拟分块 `delta` 序列，断言增量合并与完结事件。
  - RAG 检索：`topK` 边界与空结果容错。
  - 上下文长度：构造超长历史，验证截断策略与顺序稳定性。
  - 状态机：`sending → success/failed`，中断恢复 `resume_token_index`。
  - API 套件：`/ai/chat`、`/ai/chat/messages`、`/ai/chat/stream`、`/ai/context/reset` 正常与异常路径。

**实施顺序**
- 第1步：新增 LLM 流式适配与消息标准模型（不引入新依赖）。
- 第2步：RAG 引用卡结构与服务编排接入。
- 第3步：上下文/消息持久与分页接口（Redis）。
- 第4步：流式 SSE 出口与恢复机制。
- 第5步：完善测试覆盖并对齐 API 文档示例。

**对现有代码的对齐点（代码参考）**
- 路由：`python/app/api/v1/ai.py:13-61`、`python/app/api/v1/router.py:6-12`
- 服务：`python/app/services/interpretation_service.py:17-52`
- 客户端：`python/app/client/llm_client.py:16-93`、`python/app/client/rag_client.py:16-39`
- 配置：`python/app/config.py:24-37`、Java `src/main/resources/application.yml:50-66`

**合规与安全**
- 不在代码中写入 API Key；仅通过环境变量或配置注入。
- 响应中不泄露内部检索原文，引用片段为摘要。

**参考**
- [1] 使用 OpenAI 兼容接口调用通义千问模型（北京/新加坡 Base URL 与 HTTP 端点）https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope 
- [2] OpenAI Chat 接口兼容（多语言示例与流式调用）https://www.alibabacloud.com/help/zh/model-studio/compatibility-of-openai-with-dashscope 
- [3] API 请求与响应参数详解（端点与协议细节）https://help.aliyun.com/zh/dashscope/developer-reference/api-details