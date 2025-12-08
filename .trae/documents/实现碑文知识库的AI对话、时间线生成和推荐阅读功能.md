# 实现碑文知识库的AI对话、时间线生成和推荐阅读功能

## 1. 需求分析
- 查看碑文识别/AI阐释界面中的大模型对话和时间线生成代码
- 为碑文知识库生成相关时间线
- 为碑文知识库生成推荐阅读
- 在碑文知识库界面实现AI对话功能

## 2. 技术实现方案

### 2.1 碑文史实时间线生成
- **实现位置**：`frontend/src/views/Article.vue`
- **功能说明**：为单篇碑文生成相关的历史时间线
- **技术实现**：
  - 调用AI接口 `postInterpretationSections` 获取时间线数据
  - 在右侧信息栏显示时间线
  - 支持从Markdown内容中提取时间线数据作为备选

### 2.2 推荐阅读生成
- **实现位置**：`frontend/src/views/Article.vue`
- **功能说明**：为单篇碑文生成相关的推荐阅读内容
- **技术实现**：
  - 调用AI接口获取推荐阅读数据
  - 在右侧信息栏显示推荐阅读列表
  - 支持从Markdown内容中提取延伸阅读作为备选

### 2.3 碑文知识库AI对话功能
- **实现位置**：`frontend/src/views/Knowledge.vue` 和 `frontend/src/views/Article.vue`
- **功能说明**：在知识库首页和文章详情页实现AI对话功能
- **技术实现**：
  - 使用 `postChat` 和 `streamChatFetch` 函数实现大模型对话
  - 支持上下文对话（conversationId）
  - 显示消息来源引用
  - 实现消息流显示

## 3. 实现步骤

### 3.1 碑文史实时间线生成
1. 在 `Article.vue` 中添加时间线相关响应式数据
2. 实现 `fetchTimeline` 函数，调用AI接口获取时间线数据
3. 实现从Markdown内容中提取时间线的备用函数
4. 在模板中添加时间线显示组件

### 3.2 推荐阅读生成
1. 在 `Article.vue` 中添加推荐阅读相关响应式数据
2. 实现 `fetchRecommendedReading` 函数，调用AI接口获取推荐阅读
3. 实现从Markdown内容中提取延伸阅读的备用函数
4. 在模板中添加推荐阅读显示组件

### 3.3 碑文知识库AI对话功能
1. 在 `Article.vue` 中添加AI对话相关响应式数据
2. 实现 `sendChatQuestion` 函数，支持流式对话
3. 在模板中添加AI对话界面
4. 在 `Knowledge.vue` 中实现类似的AI对话功能

## 4. 代码复用
- 复用 `Recognition.vue` 中的AI对话实现
- 复用 `Recognition.vue` 中的时间线生成实现
- 复用 `Recognition.vue` 中的推荐阅读生成实现

## 5. 预期效果
- 碑文详情页显示相关历史时间线
- 碑文详情页显示推荐阅读内容
- 碑文知识库首页和详情页支持AI对话
- 所有功能都有备用方案，确保在AI接口不可用时仍能显示内容

## 6. 依赖关系
- 后端AI接口：`postChat`, `streamChatFetch`, `postInterpretationSections`
- 前端组件：Vue 3, Vue Router, 响应式API

## 7. 实现顺序
1. 实现碑文史实时间线生成
2. 实现推荐阅读生成
3. 实现碑文知识库AI对话功能

## 8. 测试计划
- 测试AI对话功能是否正常工作
- 测试时间线生成是否正确
- 测试推荐阅读生成是否相关
- 测试在AI接口不可用时的备用方案是否生效