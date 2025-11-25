/**
 * Mock API响应管理器
 * 控制不同场景下的响应行为和错误情况
 */
import dataGenerator from './dataGenerator.js';

// 响应延迟模拟
const DELAY = {
  fast: 200,     // 快速响应（缓存数据）
  normal: 500,   // 正常响应
  slow: 1500,    // 慢响应（复杂查询）
  upload: 3000   // 上传处理
};

// 响应场景配置
const RESPONSE_SCENARIOS = {
  normal: { success: true, delay: DELAY.normal },
  slow: { success: true, delay: DELAY.slow },
  error: { success: false, delay: DELAY.normal },
  network: { success: false, delay: 0, simulateNetworkError: true },
  offline: { success: false, delay: 0, simulateOffline: true }
};

// 当前激活的响应场景
let activeScenario = RESPONSE_SCENARIOS.normal;

// 当前模拟的用户状态
let mockUser = null;
let mockTokens = null;
let mockSession = {
  recognitionRecords: [],
  articles: [],
  favorites: [],
  notifications: [],
  chatHistory: []
};

// ==================== 响应延迟控制 ====================
export const setResponseDelay = (delay) => {
  activeScenario.delay = delay;
  return true;
};

// ==================== 响应场景控制 ====================
export const setResponseScenario = (scenario = 'normal') => {
  if (RESPONSE_SCENARIOS[scenario]) {
    activeScenario = RESPONSE_SCENARIOS[scenario];
    return true;
  }
  return false;
};

export const getActiveScenario = () => activeScenario;

// ==================== 用户状态管理 ====================
export const setMockUser = (userData) => {
  mockUser = userData || dataGenerator.generateUser();
  return mockUser;
};

export const getMockUser = () => mockUser;

export const setMockTokens = (tokens) => {
  mockTokens = tokens;
  return tokens;
};

// ==================== 会话数据管理 ====================
export const initializeMockSession = () => {
  mockSession = {
    recognitionRecords: dataGenerator.generateRecognitionList(25),
    articles: dataGenerator.generateArticleList(15),
    favorites: dataGenerator.generateFavoriteList(18),
    notifications: dataGenerator.generateNotificationList(12),
    chatHistory: []
  };
  
  setMockUser();
  setMockTokens({
    access_token: 'mock_access_token_' + Date.now(),
    refresh_token: 'mock_refresh_token_' + Date.now(),
    expires_in: 3600
  });
  
  return mockSession;
};

// ==================== 响应生成器 ====================
const createResponse = (data = null, message = '操作成功') => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // 网络错误模拟
      if (activeScenario.simulateNetworkError) {
        reject(new Error('网络连接失败，请检查网络设置'));
        return;
      }
      
      // 离线模拟
      if (activeScenario.simulateOffline) {
        reject(new Error('当前离线，无法连接服务器'));
        return;
      }
      
      // 错误响应
      if (!activeScenario.success) {
        reject(new Error(dataGenerator.generateError(500, '服务器内部错误').error.message));
        return;
      }
      
      // 正常响应
      resolve({
        success: true,
        data,
        message,
        timestamp: new Date().toISOString()
      });
    }, activeScenario.delay);
  });
};

// 错误响应生成器
const createErrorResponse = (code = 400, message = '请求失败', details = null) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (activeScenario.simulateNetworkError) {
        reject(new Error('网络连接失败'));
        return;
      }
      
      reject(new Error(dataGenerator.generateError(code, message).error.message));
    }, activeScenario.delay);
  });
};

// ==================== Mock API 方法 ====================

// 用户认证相关
export const mockLogin = async (credentials) => {
  // 模拟登录验证
  if (!credentials.email || !credentials.password) {
    return createErrorResponse(400, '邮箱和密码不能为空');
  }
  
  if (credentials.password.length < 6) {
    return createErrorResponse(400, '密码长度不能少于6位');
  }
  
  const user = dataGenerator.generateUser();
  const tokens = {
    access_token: 'mock_access_token_' + Date.now(),
    refresh_token: 'mock_refresh_token_' + Date.now(),
    expires_in: 3600
  };
  
  setMockUser(user);
  setMockTokens(tokens);
  
  return createResponse({
    user,
    tokens
  }, '登录成功');
};

export const mockRegister = async (userData) => {
  if (!userData.name || !userData.email || !userData.password) {
    return createErrorResponse(400, '请填写完整信息');
  }
  
  const user = dataGenerator.generateUser();
  user.name = userData.name;
  user.email = userData.email;
  
  return createResponse({
    user,
    message: '注册成功'
  }, '注册成功');
};

export const mockRefreshToken = async () => {
  const tokens = {
    access_token: 'mock_access_token_' + Date.now(),
    refresh_token: mockTokens?.refresh_token || 'mock_refresh_token_' + Date.now(),
    expires_in: 3600
  };
  
  setMockTokens(tokens);
  return createResponse(tokens);
};

// 碑文识别相关
export const mockUploadImage = async (file) => {
  if (!file) {
    return createErrorResponse(400, '请选择要上传的图片');
  }
  
  // 模拟文件验证
  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
  if (!allowedTypes.includes(file.type)) {
    return createErrorResponse(400, '仅支持JPG、PNG格式的图片');
  }
  
  if (file.size > 5 * 1024 * 1024) { // 5MB
    return createErrorResponse(400, '图片大小不能超过5MB');
  }
  
  const imageId = dataGenerator.generateId('img_');
  return createResponse({
    image_id: imageId,
    image_url: `https://picsum.photos/800/600?random=${Date.now()}`,
    upload_info: {
      filename: file.name,
      size: file.size,
      type: file.type,
      upload_time: new Date().toISOString()
    }
  }, '图片上传成功');
};

export const mockStartRecognition = async (imageId) => {
  const taskId = dataGenerator.generateId('task_');
  return createResponse({
    task_id: taskId,
    status: 'processing',
    message: '识别任务已启动'
  }, '识别开始');
};

export const mockGetRecognitionProgress = async (taskId) => {
  const progress = {
    task_id: taskId,
    status: Math.random() > 0.7 ? 'completed' : 'processing',
    progress: Math.floor(Math.random() * 100),
    estimated_remaining: Math.random() > 0.5 ? 30 : null
  };
  
  if (progress.status === 'completed') {
    const result = dataGenerator.generateRecognitionRecord();
    result.task_id = taskId;
    progress.result = result;
  }
  
  return createResponse(progress);
};

export const mockGetRecognitionHistory = async (params = {}) => {
  const { page = 1, perPage = 20, keyword, dynasty } = params;
  
  let records = [...mockSession.recognitionRecords];
  
  // 模拟搜索过滤
  if (keyword) {
    records = records.filter(record => 
      record.title.includes(keyword) || 
      record.original_text.includes(keyword) ||
      record.person.includes(keyword)
    );
  }
  
  if (dynasty) {
    records = records.filter(record => record.dynasty === dynasty);
  }
  
  const paginated = dataGenerator.generatePaginatedResponse(records, page, perPage);
  return createResponse(paginated);
};

// AI功能相关
export const mockGetAIInterpretation = async (recognitionId) => {
  const interpretation = dataGenerator.generateAIInterpretation();
  return createResponse({
    interpretation_id: interpretation.interpretation_id,
    recognition_id: recognitionId,
    results: interpretation.results
  });
};

export const mockChatWithAI = async (message, conversationId = null) => {
  const chatMessage = dataGenerator.generateChatMessage();
  const msgId = dataGenerator.generateId('msg_');
  
  // 保存对话历史
  if (!mockSession.chatHistory[conversationId || 'default']) {
    mockSession.chatHistory[conversationId || 'default'] = [];
  }
  
  mockSession.chatHistory[conversationId || 'default'].push({
    id: msgId,
    type: 'user',
    content: message,
    timestamp: new Date().toISOString()
  });
  
  mockSession.chatHistory[conversationId || 'default'].push({
    id: dataGenerator.generateId('msg_'),
    type: 'assistant',
    content: chatMessage.reply.content,
    timestamp: new Date().toISOString(),
    sources: chatMessage.reply.sources,
    suggestions: chatMessage.reply.suggestions
  });
  
  return createResponse({
    message_id: msgId,
    conversation_id: conversationId || 'default',
    reply: chatMessage.reply
  });
};

// 知识库相关
export const mockGetArticles = async (params = {}) => {
  const { page = 1, perPage = 10, category, tag, keyword } = params;
  
  let articles = [...mockSession.articles];
  
  // 模拟搜索和过滤
  if (category) {
    articles = articles.filter(article => article.metadata.category === category);
  }
  
  if (keyword) {
    articles = articles.filter(article => 
      article.title.includes(keyword) || 
      article.content.includes(keyword)
    );
  }
  
  const paginated = dataGenerator.generatePaginatedResponse(articles, page, perPage);
  return createResponse(paginated);
};

export const mockGetArticleDetail = async (articleId) => {
  const article = mockSession.articles.find(a => a.id == articleId);
  
  if (!article) {
    return createErrorResponse(404, '文章不存在');
  }
  
  return createResponse(article);
};

// 收藏相关
export const mockGetFavorites = async (params = {}) => {
  const { page = 1, perPage = 20, type } = params;
  
  let favorites = [...mockSession.favorites];
  
  if (type) {
    favorites = favorites.filter(fav => fav.type === type);
  }
  
  const paginated = dataGenerator.generatePaginatedResponse(favorites, page, perPage);
  return createResponse(paginated);
};

export const mockAddFavorite = async (itemId, type, notes = '') => {
  const favorite = dataGenerator.generateFavorite();
  favorite.id = dataGenerator.generateId('fav_');
  favorite.type = type;
  favorite.item_id = itemId;
  favorite.notes = notes;
  favorite.created_at = new Date().toISOString();
  
  mockSession.favorites.unshift(favorite);
  return createResponse(favorite, '收藏成功');
};

export const mockRemoveFavorite = async (favoriteId) => {
  const index = mockSession.favorites.findIndex(fav => fav.id === favoriteId);
  
  if (index === -1) {
    return createErrorResponse(404, '收藏不存在');
  }
  
  mockSession.favorites.splice(index, 1);
  return createResponse(null, '取消收藏成功');
};

// 通知相关
export const mockGetNotifications = async (params = {}) => {
  const { page = 1, perPage = 20, unread_only = false } = params;
  
  let notifications = [...mockSession.notifications];
  
  if (unread_only) {
    notifications = notifications.filter(notif => !notif.is_read);
  }
  
  const paginated = dataGenerator.generatePaginatedResponse(notifications, page, perPage);
  return createResponse(paginated);
};

export const mockMarkNotificationRead = async (notificationIds) => {
  mockSession.notifications.forEach(notif => {
    if (notificationIds.includes(notif.id)) {
      notif.is_read = true;
    }
  });
  
  return createResponse(null, '标记已读成功');
};

// 统计数据相关
export const mockGetUserStats = async () => {
  const stats = dataGenerator.generateStats();
  return createResponse(stats);
};

// ==================== 工具方法 ====================
export const resetMockData = () => {
  initializeMockSession();
  return true;
};

export const clearMockUser = () => {
  mockUser = null;
  mockTokens = null;
  return true;
};

// ==================== 初始化 ====================
initializeMockSession();

export default {
  // 响应控制
  setResponseDelay,
  setResponseScenario,
  getActiveScenario,
  
  // 用户状态
  setMockUser,
  getMockUser,
  setMockTokens,
  
  // 会话管理
  initializeMockSession,
  resetMockData,
  clearMockUser,
  
  // Mock API
  mockLogin,
  mockRegister,
  mockRefreshToken,
  mockUploadImage,
  mockStartRecognition,
  mockGetRecognitionProgress,
  mockGetRecognitionHistory,
  mockGetAIInterpretation,
  mockChatWithAI,
  mockGetArticles,
  mockGetArticleDetail,
  mockGetFavorites,
  mockAddFavorite,
  mockRemoveFavorite,
  mockGetNotifications,
  mockMarkNotificationRead,
  mockGetUserStats
};