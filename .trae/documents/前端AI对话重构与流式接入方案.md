**目标**

* 重构“AI阐释”对话区为标准一来一回的对话框，消息列表展示在输入框上方。

* 接入流式输出（SSE/NDJSON），实现实时增量渲染、引用卡片展示与会话上下文保持。

**UI重构**

* 在“识别 → AI阐释”区域新增消息列表容器，位于输入框上方。

* 消息气泡样式：

  * 用户消息右侧浅色气泡，助手消息左侧白色气泡，时间戳与状态（sending/success/failed）。

  * 助手消息下方显示“引用来源”标签（来自 RAG）。

* 输入区保留现有输入框与发送按钮，并在发送中显示 loading/typing 指示。

**状态管理**

* 页面内新增状态：`messages[]`、`conversationId`、`streaming`、`currentReplyBuffer`、`currentReferences[]`。

* 发送流程：

  1. 追加用户消息（status: success）
  2. 调用流式接口，追加占位的助手消息（status: sending）
  3. 流事件到达时累加到 `currentReplyBuffer` 并更新该助手气泡内容；首包“references”事件到达时设置引用标签
  4. 完结事件更新助手消息为 `success`

**接口接入（流式）**

* 新增前端 API 方法 `streamChatFetch`，使用 `fetch` POST 调用 `POST /api/v1/ai/chat/stream`：

  * 请求头：`Authorization: Bearer <token>`，`Content-Type: application/json`

  * 请求体：`{ recognition_id, message, conversation_id }`

  * 读取 `response.body` 的 ReadableStream，逐行解析 `text/event-stream`（`data: {...}`），事件类型：

    * `status`: accepted/sending/success/failed

    * `references`: 首包提供引用卡片数组

    * `delta`: 增量文本（累加）

* 保留非流式 `POST /api/v1/ai/chat` 作为降级路径（异常时回退）。

**引用卡片展示**

* 在助手气泡下渲染 `sources[]` 标签（每个显示片段摘要 `snippet` 的前 N 字符），点击可展开全文（后续支持）。

**错误处理与容错**

* 若流式连接异常（网络/401），将助手消息标记为 `failed` 并提示错误；回退调用非流式接口尝试一次。

* token 缺失时提示登录或自动加载开发令牌；保持与当前 JWT 依赖一致。

**实现范围与文件**

* 修改 `frontend/src/views/Recognition.vue`：引入消息列表与流式逻辑，替换现有一次性回答展示。

* 新增/修改 `frontend/src/api/ai.js`：添加 `streamChatFetch`（fetch+ReadableStream），保留 `postChat`。

* 不新增依赖；不改变项目路由与页面结构其余部分。

**联调与测试**

* 启动后端与前端，设置开发令牌（已自动注入）。

* 输入多轮问题，确认：

  * 消息按时间顺序渲染在输入框上方，用户/助手气泡交替

  * 助手消息实时增量更新

  * 引用来源标签展示正确

  * 异常时回退非流式并展示错误提示

**验收标准**

* 对话消息流的交互体验符合常规聊天应用：输入框下方无消息，消息列表在上方，支持连续多轮。

* 流式输出稳定，页面不阻塞；引用卡片随首包事件展示。

* 在本地未启 Redis/数据库情况下对话功能仍可用。

