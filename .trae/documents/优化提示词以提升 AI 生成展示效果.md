**目标**

* 优化后端 `generate_sections` 的系统提示词，使 LLM 输出更贴合前端展示：内容更结构化、格式更稳定、长度更可控，且仅返回 JSON，避免“自动摘要”式杂糅与跨碑文混淆。

**改动点**

* 更新 `python/app/services/interpretation_service.py` 中 `system` 提示词：

  * 明确语言与准确性：使用简体中文；只依据输入碑文与 RAG 上下文；不确定则标注“待考”。

  * 严格 JSON 模式：禁止代码块与额外文字；仅输出 JSON；键固定为 `history_markdown`、`culture_markdown`、`figures`、`timeline`。

  * Markdown 规范：

    * `history_markdown`、`culture_markdown`：400–600 字；使用 `###` 标题、小段落、粗体与条目列表（`-`）；避免长段落与堆砌。

    * 人物（`figures`）：3–5 条；`name` 唯一，`role` 简短（6–12字），`description` 40–80字，避免夸大。

    * 时间线（`timeline`）：3–5 条；按时间升序；`year` 可近似；`title` 简短；`description` 30–60字；避免跨碑文混入。

  * 引用与保守策略：若 RAG 为空仍输出简版；避免编造；禁止混合不同碑文信息。

**示例规范（嵌入提示）**

* 明示只返回如下 JSON 结构，并强调不要输出除 JSON 外的任何字符；不要使用代码块语法。

**验证**

* 不改接口与前端逻辑；联调时内容表现将更贴合前端：

  * `history/culture` 以小标题+列表清晰展示

  * 人物与时间线更精炼易读

  * 无“自动摘要”前缀与杂糅文本

**实施**

* 仅更新提示词字符串，不改变方法签名与响应映射；保持安全与依赖不变。

