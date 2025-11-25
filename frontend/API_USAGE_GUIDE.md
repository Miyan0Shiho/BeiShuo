# API调用层与Mock数据系统使用指南

## 📋 概述

本项目已完整实现了前端的API调用层和Mock数据系统，为开发提供了统一的HTTP客户端和完善的测试数据支持。

## 🏗️ 架构组成

### 1. API调用层
- **HTTP客户端**: `src/utils/httpClient.js` - 基于axios的统一HTTP客户端
- **服务模块**: `src/services/` - 按功能模块封装的API服务
- **统一入口**: `src/services/apiService.js` - 导出所有API服务

### 2. Mock数据系统
- **数据生成器**: `src/mock/dataGenerator.js` - 生成符合API规范的测试数据
- **Mock API**: `src/mock/mockApi.js` - 模拟真实API响应行为
- **控制面板**: `src/components/MockControlPanel.vue` - 可视化控制Mock数据

## 🚀 快速开始

### 1. 使用API服务

```javascript
// 导入API服务
import { authService, recognitionService } from '@/services/apiService.js';

// 登录示例
const login = async (email, password) => {
  try {
    const response = await authService.login({ email, password });
    console.log('登录成功:', response.data);
    return response.data;
  } catch (error) {
    console.error('登录失败:', error.message);
  }
};

// 上传图片并识别
const uploadAndRecognize = async (file) => {
  try {
    // 1. 上传图片
    const uploadResult = await recognitionService.uploadImage(file);
    
    // 2. 开始识别
    const recognitionResult = await recognitionService.startRecognition(uploadResult.data.image_id);
    
    // 3. 查询进度
    const progress = await recognitionService.getRecognitionProgress(recognitionResult.data.task_id);
    
    return progress.data;
  } catch (error) {
    console.error('识别失败:', error.message);
  }
};
```

### 2. 使用Mock数据

```javascript
// 导入Mock API
import { 
  mockLogin, 
  mockGetRecognitionHistory, 
  mockGetAIInterpretation,
  setResponseScenario 
} from '@/mock/mockApi.js';

// 设置响应场景（normal/slow/error/network/offline）
setResponseScenario('normal');

// 测试API调用
const testAPI = async () => {
  try {
    // Mock登录
    const loginResult = await mockLogin({
      email: 'test@example.com',
      password: '123456'
    });
    
    // Mock获取识别历史
    const history = await mockGetRecognitionHistory({
      page: 1,
      perPage: 10
    });
    
    // Mock AI阐释
    const interpretation = await mockGetAIInterpretation('test_recognition_id');
    
    return { loginResult, history, interpretation };
  } catch (error) {
    console.error('Mock API测试失败:', error.message);
  }
};
```

### 3. 在Vue组件中使用

```vue
<template>
  <div>
    <!-- API调用按钮 -->
    <button @click="handleLogin" class="btn-primary">登录</button>
    <button @click="handleRecognition" class="btn-secondary">开始识别</button>
    
    <!-- Mock控制面板 -->
    <MockControlPanel v-if="isDevelopment" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { authService, recognitionService } from '@/services/apiService.js';
import { mockLogin } from '@/mock/mockApi.js';
import MockControlPanel from '@/components/MockControlPanel.vue';

const isDevelopment = import.meta.env.DEV;

// 登录处理
const handleLogin = async () => {
  if (isDevelopment) {
    // 开发环境使用Mock
    try {
      const result = await mockLogin({
        email: 'test@example.com',
        password: '123456'
      });
      console.log('Mock登录成功:', result.data);
    } catch (error) {
      console.error('Mock登录失败:', error.message);
    }
  } else {
    // 生产环境使用真实API
    try {
      const result = await authService.login({
        email: 'user@example.com',
        password: 'password123'
      });
      console.log('登录成功:', result.data);
    } catch (error) {
      console.error('登录失败:', error.message);
    }
  }
};

// 识别处理
const handleRecognition = async (file) => {
  if (isDevelopment) {
    // 开发环境使用Mock
    console.log('Mock识别功能');
  } else {
    // 生产环境使用真实API
    const result = await recognitionService.uploadImage(file);
    console.log('识别结果:', result.data);
  }
};
</script>
```

## 📚 API服务模块详解

### 统一API服务入口

```javascript
// 推荐的导入方式
import apiService from '@/services/apiService.js';

// 使用示例
const { auth, recognition, ai, knowledge, favorites, tools, stats } = apiService;

// 或单独导入特定服务
import { auth, recognition } from '@/services/apiService.js';
```

### 1. 用户认证服务 (authService)
- `login(credentials)` - 用户登录
  - `credentials.email`: 邮箱
  - `credentials.password`: 密码
- `register(userData)` - 用户注册
  - `userData.username`: 用户名
  - `userData.email`: 邮箱
  - `userData.password`: 密码
- `refreshToken()` - 刷新Token
- `logout()` - 用户登出
- `getUserInfo()` - 获取用户信息
- `updateUserInfo(userData)` - 更新用户信息
- `changePassword(passwordData)` - 修改密码
  - `passwordData.oldPassword`: 旧密码
  - `passwordData.newPassword`: 新密码
- `verifyEmail(token)` - 邮箱验证
- `forgotPassword(email)` - 忘记密码
- `resetPassword(resetData)` - 重置密码

### 2. 碑文识别服务 (recognitionService)
- `uploadImage(file)` - 上传图片进行识别
  - `file`: 文件对象
- `startRecognition(imageId)` - 开始识别任务
  - `imageId`: 图片ID
- `getRecognitionProgress(taskId)` - 查询识别进度
  - `taskId`: 任务ID
- `getRecognitionResult(taskId)` - 获取识别结果
  - `taskId`: 任务ID
- `getRecognitionHistory(params)` - 获取识别历史
  - `params.page`: 页码
  - `params.per_page`: 每页数量
  - `params.keyword`: 关键词搜索
- `getRecognitionDetail(recognitionId)` - 获取识别详情
  - `recognitionId`: 识别记录ID
- `deleteRecognition(recognitionId)` - 删除识别记录
  - `recognitionId`: 识别记录ID
- `batchDeleteRecognitions(ids)` - 批量删除识别记录
  - `ids`: ID数组
- `exportRecognitionResult(recognitionId)` - 导出识别结果

### 3. AI功能服务 (aiService)
- `getInterpretation(recognitionId, params)` - 获取AI阐释
  - `recognitionId`: 识别记录ID
  - `params.style`: 阐释风格
- `aiChat(messages, params)` - AI对话
  - `messages`: 对话消息数组
  - `params.model`: AI模型
- `getRecommendations(recognitionId)` - 获取相关推荐
- `batchInterpretations(recognitionIds)` - 批量阐释
  - `recognitionIds`: 识别ID数组
- `getChatHistory(chatId)` - 获取对话历史
  - `chatId`: 对话ID
- `saveChatSession(sessionData)` - 保存对话会话
- `getAIUsageStats()` - 获取AI使用统计
- `provideFeedback(feedbackData)` - 提供反馈

### 4. 知识库服务 (knowledgeService)
- `getKnowledgeHome(params)` - 获取知识库首页数据
  - `params.category`: 分类筛选
  - `params.period`: 时期筛选
- `getArticleDetail(articleId)` - 获取文章详情
  - `articleId`: 文章ID
- `searchKnowledge(searchParams)` - 搜索知识库
  - `searchParams.q`: 搜索关键词
  - `searchParams.type`: 搜索类型
  - `searchParams.category`: 分类筛选
  - `searchParams.dynasty`: 朝代筛选
  - `searchParams.page`: 页码
  - `searchParams.per_page`: 每页数量
- `getCategories()` - 获取知识库分类列表
- `getCategoryArticles(categoryId, params)` - 获取分类文章列表
- `getDynasties()` - 获取朝代信息列表
- `getDynastyDetail(dynastyId)` - 获取朝代详情
- `getDynastyInscriptions(dynastyId, params)` - 获取朝代相关碑文
- `getInscriptionDetail(inscriptionId)` - 获取碑文详细信息
- `getRelatedArticles(articleId, limit)` - 获取相关文章
- `likeArticle(articleId)` - 点赞文章
- `unlikeArticle(articleId)` - 取消点赞
- `bookmarkArticle(articleId)` - 收藏文章
- `unbookmarkArticle(articleId)` - 取消收藏
- `getReadingHistory(params)` - 获取阅读历史
- `recordReadingProgress(articleId, progressData)` - 记录阅读进度
- `getHotContent(params)` - 获取热门内容
- `getFeaturedContent(params)` - 获取精选内容
- `provideContentFeedback(feedbackData)` - 提供内容反馈

### 5. 收藏管理服务 (favoriteService)
- `getFavorites(params)` - 获取收藏列表
  - `params.type`: 收藏类型
  - `params.page`: 页码
  - `params.per_page`: 每页数量
  - `params.sort`: 排序方式
- `addFavorite(favoriteData)` - 添加收藏
  - `favoriteData.type`: 收藏类型
  - `favoriteData.item_id`: 项目ID
  - `favoriteData.notes`: 备注
  - `favoriteData.tags`: 标签数组
- `updateFavorite(favoriteId, updateData)` - 更新收藏
- `deleteFavorite(favoriteId)` - 删除收藏
- `batchDeleteFavorites(favoriteIds)` - 批量删除收藏
- `checkFavoriteStatus(itemId, itemType)` - 检查是否已收藏
- `moveFavoriteToFolder(favoriteId, folderId)` - 移动收藏到文件夹
- `getFavoriteStats()` - 获取收藏统计
- `exportFavorites(params)` - 导出收藏
- `importFavorites(formData)` - 导入收藏
- `getFavoriteFolders()` - 获取收藏文件夹
- `createFavoriteFolder(folderData)` - 创建收藏文件夹
- `updateFavoriteFolder(folderId, updateData)` - 更新收藏文件夹
- `deleteFavoriteFolder(folderId)` - 删除收藏文件夹

### 6. 工具类服务 (toolsService)
- `textConvert(convertData)` - 文本转换工具
  - `convertData.text`: 原文
  - `convertData.convert_type`: 转换类型
  - `convertData.options`: 转换选项
- `identifyFont(fontData)` - 字体识别工具
- `spellCheck(correctionData)` - 文本纠错
- `textSegmentation(segmentationData)` - 文字分割
- `characterConversion(conversionData)` - 繁简转换
- `addPinyin(pinyinData)` - 拼音标注
- `textStatistics(statsData)` - 文字统计
- `imageEnhancement(enhancementData)` - 图像增强
- `extractText(ocrData)` - 文本提取
- `speechToText(audioData)` - 语音转文本

### 7. 统计数据服务 (statsService)
- `getUserStats()` - 获取用户统计
- `getPlatformStats()` - 获取平台统计
- `getRecognitionStats(params)` - 获取识别统计
  - `params.time_range`: 时间范围
  - `params.group_by`: 分组方式
- `getAIUsageStats(params)` - 获取AI使用统计
- `getPopularContentStats(params)` - 获取热门内容统计
- `getDynastyDistribution()` - 获取朝代分布统计
- `getUserActivityStats(params)` - 获取用户活跃度统计
- `getErrorStats(params)` - 获取错误统计
- `getPerformanceStats()` - 获取系统性能统计
- `exportStats(params)` - 导出统计数据

## 🛠️ Mock控制面板使用

Mock控制面板提供可视化的测试界面：

### 功能特性
- **响应场景控制**: 切换不同的响应模式
- **响应延迟调节**: 模拟不同的网络环境
- **用户状态管理**: 生成/清除模拟用户
- **API测试工具**: 快速测试各种API调用
- **数据统计显示**: 查看Mock数据概览

### 使用方式
在Vue组件中引入并使用：
```vue
<template>
  <div>
    <!-- 主要内容 -->
    <main>...</main>
    
    <!-- 开发环境显示Mock控制面板 -->
    <MockControlPanel v-if="import.meta.env.DEV" />
  </div>
</template>
```

## 🔧 配置说明

### HTTP客户端配置 (httpClient.js)
- 支持Token自动管理
- 统一的错误处理
- 请求/响应拦截器
- 支持多种环境配置

### Mock数据配置 (mockApi.js)
- 可配置的响应延迟
- 多种响应场景模拟
- 智能的数据生成
- 会话状态管理

## 📝 开发最佳实践

### 1. 环境适配
```javascript
// 根据环境选择API或Mock
const isDev = import.meta.env.DEV;
const apiService = isDev ? mockApi : realApi;
```

### 2. 错误处理
```javascript
try {
  const result = await apiService.someMethod();
  // 处理成功响应
} catch (error) {
  // 统一错误处理
  console.error('API调用失败:', error.message);
}
```

### 3. 数据状态管理
```javascript
// 使用Vue的响应式状态
import { ref, reactive } from 'vue';

const loading = ref(false);
const data = reactive([]);
const error = ref(null);

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await apiService.getData();
    data.splice(0, data.length, ...result.data);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
```

## 🎯 下一步开发计划

1. **集成到现有组件**: 将API服务集成到Recognition.vue等现有组件
2. **状态管理**: 结合Pinia进行全局状态管理
3. **路由守卫**: 实现基于Token的路由保护
4. **缓存策略**: 实现API响应缓存机制
5. **实时功能**: 添加WebSocket支持实时更新

## 📞 技术支持

如有问题，请参考：
- API规范文档: `frontend/API_DESIGN.md`
- 组件源码: `src/services/` 和 `src/mock/`
- 测试用例: MockControlPanel组件