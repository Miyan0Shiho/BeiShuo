**目标**

* 在识别页与文章页的右侧“相关人物”区，改为展示后端接口返回的 `sectionsFigures`（AI+RAG 自动生成），替换现有前端模拟数据。

**改动点**

* 识别页（Recognition.vue）：

  * 右侧“相关人物”列表由 `relatedFigures` → `sectionsFigures`

  * 展示字段：`name/role/description`；为空时显示提示文案

  * 触发逻辑沿用已实现的 `showInterpretation()`，接口返回后填充 `sectionsFigures`

* 文章页（Article.vue）：

  * 右侧“相关人物”列表由静态示例 → `sectionsFigures`

  * 确保已导入 `postInterpretationSections` 并在 `fetchArticleInterpretation()` 后填充 `sectionsFigures`

**后端**

* 无额外改动；当前 `/api/v1/ai/interpretation/sections` 已返回 `figures[]`

**容错**

* 当 `sectionsFigures` 为空时显示“暂无人物信息，稍后重试/编辑添加”等提示；不影响其他区块展示

**联调**

* 点击“查看AI阐释”或进入文章阐释区域后，右侧“相关人物”应实时更新为 AI 生成内容；刷新页面保留体验一致性

