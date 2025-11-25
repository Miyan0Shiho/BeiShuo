**目标**
- 用 LLM+RAG 自动生成“历史背景、相关人物、相关时间线”等内容，替代前端模拟数据。
- 触发点：用户在识别结果页点击“查看AI阐释”或进入文章详情的阐释区域时，自动调用后端生成。

**后端接口**
- 新增接口：`POST /api/v1/ai/interpretation/sections`
  - 请求体：
    - `recognition_id`（可选，占位或未来绑定真实识别记录）
    - `inscription_id`（可选，用于上下文检索与关联）
    - `text`（必填，识别出的碑文原文/选段）
    - `conversation_id`（可选，用于会话关系与上下文保留）
  - 响应体：
    - `conversation_id`
    - `sections`：
      - `history_markdown`（字符串，Markdown）
      - `culture_markdown`（字符串，Markdown）
      - `figures`：`[{name, role, description}]`
      - `timeline`：`[{year,title,description}]`
      - `sources`：`ReferenceCard[]`（来自 RAG 命中片段）
    - `status`: `success|failed`
- 生成流程：`InterpretationService.generate_sections(text, inscription_id)`
  1. 本地 RAG 检索 TopK 片段（`RAG/search.py`）
  2. 构造系统提示与用户提示，要求严格 JSON 输出（如支持 `response_format: {type: "json_object"}` 则开启；否则按 JSON code fence 返回并解析）
  3. 调用 `LLMClient.chat`（模型 `qwen-flash`），解析 JSON → 映射到响应结构；解析失败时降级为最小可读 Markdown
  4. 返回 `sources` 与会话 `conversation_id`
- 提示词规范（示例要点）：
  - 输入：碑文原文与 RAG 上下文摘要
  - 输出约束：仅返回 JSON，键为 `history_markdown`, `culture_markdown`, `figures`, `timeline`
  - 篇幅限制：history/culture 各 ≤ 400–600 字；人物 3–5 条；时间线 3–5 条
  - 风格：客观、简洁、避免编造；引用用“据碑文/史料”表达

**前端改造**
- 识别结果页（`Recognition.vue`）：
  - 在点击“查看AI阐释”时触发 `POST /ai/interpretation/sections`，将返回内容填充到现有“历史背景/文化意义/相关人物/延伸阅读/时间线”区域（替换模拟数据）
  - 加载态与错误提示：顶部显示旋转指示；失败时显示重试按钮
  - 保留聊天对话功能（流式增量）
- 文章详情页（`Article.vue`）：
  - 页面初次进入或切换到阐释区域时触发同一接口，按返回数据替换模拟内容，保持与识别页一致体验
- 展示规则：
  - `history_markdown` 与 `culture_markdown` 直接以 Markdown 渲染
  - `figures` 渲染为人物卡片：`name/role/description`
  - `timeline` 渲染为时间线：`year/title/description`
  - `sources` 以标签展示片段摘要

**校验与容错**
- 若 LLM 返回解析失败：
  - 回退为非结构化 Markdown（拼接 RAG 段与简短总结）并提示“该版为自动生成摘要”
- 若 RAG 索引为空：
  - 使用 `text` 作为唯一上下文仍生成简版说明；`sources` 为空
- 性能：
  - 每次触发只生成一次；会话 `conversation_id` 保持连续提问上下文

**实现要点**
- 复用现有 `LLMClient` 与本地 RAG 模块，不新增依赖
- 不打印或持久化密钥；从环境读取 `LLM_API_KEY`
- 返回体与错误体保持统一 `Result` 封装（`Result.ok` / `Result.fail`）

**联调步骤**
- 后端完成接口后，前端在点击“查看AI阐释”或进入阐释区域时调用接口并渲染返回
- 用 `碑文.txt` 构建索引后，实测能产生合理的历史背景、人物与时间线

**测试**
- 后端：
  - Mock LLM 返回 JSON，验证解析与响应映射
  - RAG 空索引时的降级路径
- 前端：
  - 识别页与文章页均可触发生成并渲染；加载态与错误态显示正确

请确认该方案，我将据此在后端新增生成接口与前端接入，替换当前的模拟数据。