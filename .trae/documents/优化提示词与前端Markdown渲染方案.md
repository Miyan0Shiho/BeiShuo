**目标**

* 提升 AI 生成内容的可读性与层次感：标题清晰、列表规范、段落有间距，避免“文本堆在一起”。

* 同步优化后端提示词与前端 Markdown 渲染，保证端到端效果稳定。

**后端提示词优化**

* 位置：`python/app/services/interpretation_service.py` 的 `system` 提示词。

* 调整点：

  * 明确使用简体中文、只依据输入碑文与上下文；不确定处标注“待考”。

  * 强制 JSON 输出，不使用代码块；键固定为 `history_markdown/culture_markdown/figures/timeline`。

  * Markdown 规范：

    * `history_markdown/culture_markdown`：使用“### 标题”开头，每段之间空行；列表条目前缀统一为 `- ` ；限制 400–600 字；允许 **加粗**。

    * `figures`：3–5 条；`name/role/description` 字段长度控制并客观。

    * `timeline`：3–5 条；按时间升序；`year/title/description` 简洁。

  * 明确“段落之间必须使用空行；列表统一使用 `- ` ；不要混用其他符号”。

**前端 Markdown 渲染升级**

* 位置：

  * `frontend/src/views/Recognition.vue` 的 `renderMarkdown`

  * `frontend/src/views/Article.vue` 的 `renderMarkdown`

* 改动点：

  * 替换简易正则渲染为逐行解析：支持 `###/##` 标题、`-`/`*` 无序列表、`1.` 有序列表、空行换段、三反引号代码块、粗体/斜体/行内代码。

  * 自动包裹列表为 `<ul>/<ol>`，段落为 `<p>`，在空行处插入 `<br/>`，避免堆叠。

  * 保留 `escapeHtml` 安全处理。

**视觉提示**

* 保持识别页与文章页的“生成中”提示与旋转图标（已接入）；当 Markdown 内容为空且 `sectionsLoading` 为 true，显示占位文本（已接入）。

**验证方式**

* 点击“查看AI阐释”，观察“历史背景/文化意义/相关人物/时间线”展示：

  * 标题以 `###` 开头

  * 列表项按 `- `  渲染为条目，段落有间距

  * 代码块与行内代码正常显示

**实施范围**

* 不引入新依赖；仅优化提示词与前端渲染函数。

