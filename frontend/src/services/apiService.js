/**
 * 统一API服务入口
 * 按功能模块导出所有API服务
 */

import authService from './authService';
import recognitionService from './recognitionService';
import correctionService from './correctionService';
import aiService from './aiService';
import knowledgeService from './knowledgeService';
import favoriteService from './favoriteService';

// 工具类服务
import toolsService from './toolsService';
import statsService from './statsService';
import notificationService from './notificationService';

// ==================== 导出所有服务 ====================
export const auth = authService;
export const recognition = recognitionService;
export const correction = correctionService;
export const ai = aiService;
export const knowledge = knowledgeService;
export const favorites = favoriteService;
export const tools = toolsService;
export const stats = statsService;
export const notifications = notificationService;

// ==================== 工具方法 ====================

/**
 * 批量API调用工具
 * @param {Array} apiCalls - API调用数组 [{ service, method, params }]
 * @returns {Promise} 返回所有API调用的结果数组
 */
export const batchApiCall = async (apiCalls) => {
  try {
    const results = await Promise.allSettled(
      apiCalls.map(({ service, method, params }) => 
        service[method](params)
      )
    );
    
    return results.map((result, index) => ({
      index,
      success: result.status === 'fulfilled',
      data: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason : null
    }));
  } catch (error) {
    console.error('Batch API call error:', error);
    throw error;
  }
};

/**
 * 带重试的API调用
 * @param {Function} apiCall - API调用函数
 * @param {number} maxRetries - 最大重试次数
 * @param {number} delay - 重试延迟（毫秒）
 * @returns {Promise}
 */
export const retryApiCall = async (apiCall, maxRetries = 3, delay = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      console.warn(`API call attempt ${attempt} failed:`, error);
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // 指数退避
      const waitTime = delay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
};

/**
 * 创建分页查询工具
 * @param {Function} apiCall - API调用函数
 * @param {Object} params - 查询参数
 * @param {number} pageSize - 每页大小
 * @returns {Promise} 返回分页数据和元信息
 */
export const createPagedQuery = async (apiCall, params = {}, pageSize = 20) => {
  const page = params.page || 1;
  const queryParams = {
    ...params,
    page,
    per_page: params.per_page || pageSize
  };
  
  const response = await apiCall(queryParams);
  
  return {
    data: response.data || response,
    pagination: response.pagination || {
      current_page: page,
      per_page: queryParams.per_page,
      total_count: response.data?.length || 0,
      total_pages: Math.ceil((response.total_count || 0) / queryParams.per_page)
    }
  };
};

/**
 * API健康检查
 * @returns {Promise}
 */
export const healthCheck = async () => {
  try {
    // 尝试调用一个简单的API端点
    const response = await fetch('/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

/**
 * 获取API配置信息
 * @returns {Object} 配置对象
 */
export const getApiConfig = () => ({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  version: 'v1',
  features: {
    batchProcessing: true,
    realTimeUpdates: true,
    fileUpload: true,
    offlineMode: false
  }
});

export default {
  auth,
  recognition,
  correction,
  ai,
  knowledge,
  favorites,
  tools,
  stats,
  notifications,
  batchApiCall,
  retryApiCall,
  createPagedQuery,
  healthCheck,
  getApiConfig
};