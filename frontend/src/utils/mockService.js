/**
 * Mock服务管理器
 * 统一控制所有API的Mock模式切换和降级处理
 */

import mockApi from '../mock/mockApi.js';

// Mock模式配置
const mockConfig = {
  enabled: import.meta.env.VITE_USE_MOCK === 'true',
  fallback: true, // 网络错误时自动降级到Mock
  delay: 500, // 默认延迟（毫秒）
  simulateErrors: false // 是否模拟错误
};

// API路径映射到Mock函数
const apiMappings = {
  // 认证相关
  'post /auth/login': mockApi.mockLogin,
  'post /auth/register': mockApi.mockRegister,
  'post /auth/refresh': mockApi.mockRefreshToken,
  
  // 识别相关
  'post /upload/image': mockApi.mockUploadImage,
  'post /recognition/start': mockApi.mockStartRecognition,
  'get /recognition/progress/:id': mockApi.mockGetRecognitionProgress,
  'get /recognition/history': mockApi.mockGetRecognitionHistory,
  
  // AI相关
  'post /ai/interpretation': mockApi.mockGetAIInterpretation,
  'post /ai/chat': mockApi.mockChatWithAI,
  'get /ai/recommendations': mockApi.mockGetRecommendations,
  
  // 文章相关
  'get /articles': mockApi.mockGetArticles,
  'get /articles/:id': mockApi.mockGetArticleDetail,
  
  // 收藏相关
  'get /favorites': mockApi.mockGetFavorites,
  'post /favorites': mockApi.mockAddFavorite,
  'delete /favorites/:id': mockApi.mockRemoveFavorite,
  
  // 通知相关
  'get /notifications': mockApi.mockGetNotifications,
  'post /notifications/read': mockApi.mockMarkNotificationRead,
  
  // 用户统计
  'get /user/stats': mockApi.mockGetUserStats
};

/**
 * 启用或禁用Mock模式
 * @param {boolean} enabled - 是否启用Mock模式
 */
export const setMockEnabled = (enabled) => {
  mockConfig.enabled = enabled;
  console.log(`[Mock Service] Mock模式已${enabled ? '启用' : '禁用'}`);
  return enabled;
};

/**
 * 获取Mock模式状态
 * @returns {boolean} Mock模式是否启用
 */
export const isMockEnabled = () => mockConfig.enabled;

/**
 * 设置Mock响应延迟
 * @param {number} delay - 延迟时间（毫秒）
 */
export const setMockDelay = (delay) => {
  mockConfig.delay = delay;
  return delay;
};

/**
 * 设置是否模拟错误响应
 * @param {boolean} enabled - 是否启用错误模拟
 */
export const setMockErrors = (enabled) => {
  mockConfig.simulateErrors = enabled;
  if (enabled) {
    mockApi.setResponseScenario('error');
  } else {
    mockApi.setResponseScenario('normal');
  }
  return enabled;
};

/**
 * 设置Mock响应场景
 * @param {string} scenario - 场景名称 (normal/slow/error/network/offline)
 */
export const setMockScenario = (scenario) => {
  const result = mockApi.setResponseScenario(scenario);
  if (result) {
    console.log(`[Mock Service] 已切换到Mock场景: ${scenario}`);
  }
  return result;
};

/**
 * 查找匹配的Mock处理函数
 * @param {string} method - HTTP方法
 * @param {string} url - 请求URL
 * @returns {Function|null} Mock处理函数
 */
export const findMockHandler = (method, url) => {
  const normalizedMethod = method.toLowerCase();
  
  // 尝试精确匹配
  const exactMatch = `${normalizedMethod} ${url}`;
  if (apiMappings[exactMatch]) {
    return apiMappings[exactMatch];
  }
  
  // 尝试路径参数匹配
  for (const [pattern, handler] of Object.entries(apiMappings)) {
    if (pattern.startsWith(`${normalizedMethod} `)) {
      const pathPattern = pattern.substring(normalizedMethod.length + 1);
      if (matchPathPattern(url, pathPattern)) {
        return handler;
      }
    }
  }
  
  return null;
};

/**
 * 路径模式匹配
 * @param {string} url - 请求URL
 * @param {string} pattern - 路径模式 (如 /users/:id)
 * @returns {boolean} 是否匹配
 */
const matchPathPattern = (url, pattern) => {
  // 简单的路径参数匹配
  const urlParts = url.split('/').filter(Boolean);
  const patternParts = pattern.split('/').filter(Boolean);
  
  if (urlParts.length !== patternParts.length) {
    return false;
  }
  
  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(':') || patternParts[i].startsWith('*')) {
      continue;
    }
    if (patternParts[i] !== urlParts[i]) {
      return false;
    }
  }
  
  return true;
};

/**
 * 执行Mock请求
 * @param {string} method - HTTP方法
 * @param {string} url - 请求URL
 * @param {Object} data - 请求数据
 * @param {Object} config - 请求配置
 * @returns {Promise} Mock响应
 */
export const executeMockRequest = async (method, url, data = null, config = {}) => {
  console.log(`[Mock Request] ${method.toUpperCase()} ${url}`, data);
  
  const handler = findMockHandler(method, url);
  if (handler) {
    try {
      // 根据不同的API类型传递参数
      let result;
      if (url.includes('/recognition/progress/')) {
        const taskId = url.split('/').pop();
        result = await handler(taskId);
      } else if (url.includes('/articles/') && method === 'get') {
        const articleId = url.split('/').pop();
        result = await handler(articleId);
      } else if (url.includes('/favorites/') && method === 'delete') {
        const favoriteId = url.split('/').pop();
        result = await handler(favoriteId);
      } else {
        result = await handler(data);
      }
      
      console.log(`[Mock Response] ${method.toUpperCase()} ${url}`, result);
      return result;
    } catch (error) {
      console.error(`[Mock Error] ${method.toUpperCase()} ${url}`, error);
      throw error;
    }
  } else {
    // 如果没有找到对应的Mock处理函数，生成通用的Mock响应
    const mockResponse = {
      success: true,
      data: {
        message: 'Mock响应',
        request: { method, url, data }
      },
      timestamp: new Date().toISOString()
    };
    
    console.log(`[Mock Fallback] ${method.toUpperCase()} ${url}`, mockResponse);
    return mockResponse;
  }
};

/**
 * 初始化Mock服务
 */
export const initializeMockService = () => {
  if (mockConfig.enabled) {
    mockApi.initializeMockSession();
    console.log('[Mock Service] Mock服务已初始化');
    
    // 显示Mock模式提示
    if (typeof window !== 'undefined') {
      console.log('%c🚀 Mock模式已启用', 'background: #222; color: #00ff00; padding: 4px 8px; border-radius: 4px;');
    }
  }
};

// 初始化
initializeMockService();

export default {
  setMockEnabled,
  isMockEnabled,
  setMockDelay,
  setMockErrors,
  setMockScenario,
  findMockHandler,
  executeMockRequest,
  initializeMockService
};