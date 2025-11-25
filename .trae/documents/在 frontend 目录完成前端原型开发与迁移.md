## 目标

* 在仓库根目录新增 `frontend/`，将现有静态原型完整迁移并作为前端开发目录。

* 保持“像素级复现”与现有交互框架（Vue 3 UMD + Tailwind CDN 本地化 + Font Awesome + Vditor + ECharts + iframe 组织）。

## 迁移与结构

* 新建目录结构：

  * `frontend/index.html`（来自 `文件资源/碑说 (1)/index.html`，维持预览与文档弹窗逻辑）

  * `frontend/assets/`（复制全部静态资源与脚本）

    * `css/`：`index.css`、`tailwindcss.css` 等

    * `font-awesome/`：本地图标资源

    * `javascript/`：`vue.global.js`、`index.js`、`initData.js`、`docModal.js`、`tool.js`、`reload.js`

    * `vditor/`：编辑器资源

    * `img/`：图片与图标资源

    * `page/`：各页面 HTML（如首页、历史记录、识别等）

* 路径与路由：

  * `initData.js` 中 `treeArr.url` 仍指向相对路径 `./assets/page/*.html`（assets/javascript/initData.js:212-216）。

  * `index.html` 中 iframe 加载逻辑保持（文件内 373-399、381-385），只调整资源相对路径到新目录。

## Tailwind 运行方式校准

* 保持本地化的 Tailwind CDN 运行时：

  * 继续通过 `<script src="./assets/css/tailwindcss.css"></script>` 方式引入，以支持 `<style type="text/tailwindcss">` 的 JIT 解析（首页文件 32-47 存在该块）。

* 如后续需要改为纯 CSS 构建：删去 `text/tailwindcss` 代码块，改为 `<link>` 引入已构建 CSS；当前阶段不切换，确保设计稿完美复现。

## 实施里程碑

1. 目录搭建与资源拷贝

* 创建 `frontend/` 与子目录，复制现有静态文件，修正所有资源相对路径。

* 验收：打开 `frontend/index.html`，页面加载正常、预览面板工作。

1. 首页像素级对齐

* 校准颜色/字体/间距（需求文档“4.界面设计规范”），检查导航、英雄区、功能卡片、流程、识别演示、阐释展示、推荐、注册引导模块（首页文件内容详见 assets/page/1988264127725830144.html）。

* 验收：桌面与移动断点下布局与样式一致。

1. 识别页/校对页/阐释页/历史记录页

* 保留交互占位与流程（上传→识别展示、左图右文校对、对话式阐释、时间线/列表检索），按文档规范完善 UI。

* 验收：关键交互路径可演示，样式与组件状态一致。

1. 预览与文档弹窗

* 保持 Vditor 需求弹窗与键盘预览（index.html:410-433、assets/javascript/index.js:456-474），确保跨页面通信正常。

* 验收：Esc/左右键交互有效，文档弹窗正常显示。

1. 响应式与动效收尾

* 覆盖需求文档断点（4.2），检查所有页面在常见尺寸表现；保留滚动、懒加载等动效（首页文件 1051-1112 等）。

## 提交及分支

* 所有改动在 `feature/techTest` 分支进行。

* 暂不引入构建工具；后续若需要再按文档演进规划迁移到 Vite。

## 执行说明

* 获批后：创建 `frontend/` 并拷贝/调整资源；修正 `index.html` 与脚本路径；本地预览验证并回传可视化结果与变更列表。

