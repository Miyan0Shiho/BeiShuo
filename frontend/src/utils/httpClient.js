/**
 * HTTP客户端 - 统一请求封装
 */

import axios from 'axios';
import { isMockEnabled, findMockHandler, executeMockRequest } from './mockService.js';

// 环境配置
const config = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
}

// 创建axios实例
const httpClient = axios.create(config);

// Token存储键名
const TOKEN_KEY = 'bishuo_auth_token';
const REFRESH_TOKEN_KEY = 'bishuo_refresh_token';

// ==================== 请求拦截器 ====================
httpClient.interceptors.request.use(
  async (config) => {
    // 添加请求时间戳
    config.metadata = { startTime: Date.now() };
    
    // 添加认证Token
    const token = localStorage.getItem(TOKEN_KEY);
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加请求ID（用于追踪）
    config.headers['X-Request-ID'] = generateRequestId();
    
    // Mock模式检查 - 如果启用了Mock且找到对应的Mock处理函数，则直接返回Mock响应
    if (isMockEnabled() && findMockHandler(config.method, config.url)) {
      console.log(`🚀 [MOCK Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
      // 使用Promise.resolve包装以确保正确的异步行为
      throw {
        isMockRequest: true,
        mockData: await executeMockRequest(config.method, config.url, config.data, config)
      };
    }
    
    console.log(`🚀 [API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    
    return config;
  },
  (error) => {
    // 处理Mock请求的特殊错误
    if (error.isMockRequest) {
      return Promise.resolve(error.mockData);
    }
    
    console.error('❌ [API Request Error]', error);
    return Promise.reject(error);
  }
);

// ==================== 响应拦截器 ====================
httpClient.interceptors.response.use(
  (response) => {
    // 计算请求耗时
    const endTime = Date.now();
    const duration = endTime - response.config.metadata.startTime;
    
    console.log(`✅ [API Response] ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`, response.data);
    
    // 返回标准化响应数据
    return handleResponse(response);
  },
  async (error) => {
    // 处理Mock请求的特殊情况
    if (error.isMockRequest) {
      return Promise.resolve(error.mockData);
    }
    
    const originalRequest = error.config;
    
    // 记录错误信息
    console.error(`❌ [API Error] ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`, {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    // 处理401错误 - Token过期
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // 尝试刷新Token
        await refreshToken();
        
        // 重新发送原请求
        const newToken = localStorage.getItem(TOKEN_KEY);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        
        return httpClient(originalRequest);
      } catch (refreshError) {
        // 刷新失败，清除Token并跳转到登录页
        clearAuthTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // 处理其他错误状态码
    if (error.response?.status === 403) {
      showErrorMessage('权限不足，无法访问此资源');
    } else if (error.response?.status === 404) {
      showErrorMessage('请求的资源不存在');
    } else if (error.response?.status >= 500) {
      showErrorMessage('服务器内部错误，请稍后重试');
    } else if (error.code === 'ECONNABORTED') {
      showErrorMessage('请求超时，请检查网络连接');
    } else if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
      // 网络错误处理 - 尝试降级到Mock模式
      if (originalRequest && findMockHandler(originalRequest.method, originalRequest.url)) {
        console.log(`⚠️ [Network Error] 降级到Mock模式: ${originalRequest.method?.toUpperCase()} ${originalRequest.url}`);
        showErrorMessage('网络连接失败，已切换到离线模式');
        try {
          const mockResponse = await executeMockRequest(
            originalRequest.method,
            originalRequest.url,
            originalRequest.data,
            originalRequest
          );
          return Promise.resolve(mockResponse);
        } catch (mockError) {
          console.error('❌ [Mock Fallback Error]', mockError);
        }
      }
      showErrorMessage('网络连接失败，请检查网络设置');
    }
    
    return Promise.reject(handleError(error));
  }
);

// ==================== 响应数据处理 ====================
function handleResponse(response) {
  const { data } = response;
  
  // 如果响应已经是标准格式，直接返回
  if (data.success !== undefined) {
    return data;
  }
  
  // 包装为标准格式
  return {
    success: true,
    data: data,
    message: 'success'
  };
}

// ==================== 错误处理 ====================
function handleError(error) {
  if (error.response) {
    // 服务器响应错误
    const { status, data } = error.response;
    
    return {
      success: false,
      status,
      message: data.message || data.error || '请求失败',
      code: data.code || 'UNKNOWN_ERROR',
      data: data.data || null
    };
  } else if (error.request) {
    // 网络错误
    return {
      success: false,
      status: 0,
      message: '网络连接失败，请检查网络设置',
      code: 'NETWORK_ERROR'
    };
  } else {
    // 其他错误
    return {
      success: false,
      status: -1,
      message: error.message || '未知错误',
      code: 'UNKNOWN_ERROR'
    };
  }
}

// ==================== Token管理 ====================
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

async function refreshToken() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  try {
    const response = await axios.post(`${config.baseURL}/auth/refresh`, {}, {
      headers: {
        'Authorization': `Bearer ${refreshToken}`
      }
    });
    
    if (response.data.success) {
      const { token, expires_at } = response.data.data;
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(REFRESH_TOKEN_KEY, token); // 刷新token通常会获得新的token
      return token;
    } else {
      throw new Error('Token refresh failed');
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    throw error;
  }
}

function clearAuthTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// ==================== 错误提示 ====================
function showErrorMessage(message) {
  // 这里可以集成全局消息提示组件
  console.warn('🚨 Error:', message);
  
  // 如果有全局消息提示，可以这样调用：
  // ElMessage.error(message);
  // 或者使用事件总线发送全局事件
}

// ==================== 请求方法封装 ====================
export const http = {
  get: (url, config = {}) => httpClient.get(url, config),
  post: (url, data = {}, config = {}) => httpClient.post(url, data, config),
  put: (url, data = {}, config = {}) => httpClient.put(url, data, config),
  patch: (url, data = {}, config = {}) => httpClient.patch(url, data, config),
  delete: (url, config = {}) => httpClient.delete(url, config),
  upload: (url, formData, config = {}) => httpClient.post(url, formData, {
    ...config,
    headers: {
      ...config.headers,
      'Content-Type': 'multipart/form-data'
    }
  })
};

// ==================== 认证相关 ====================
export const auth = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token, refreshToken) => {
    localStorage.setItem(TOKEN_KEY, token);
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
  },
  clearToken: clearAuthTokens,
  isAuthenticated: () => !!localStorage.getItem(TOKEN_KEY)
};

// ==================== 配置导出 ====================
export { config };
export default httpClient;