/**
 * 前端错误处理工具
 * 提供统一的错误分类、错误信息显示和用户友好的错误提示
 */

import { useAppStore } from '../stores/app'

/**
 * 错误类型枚举
 */
export const ErrorType = {
  NETWORK_ERROR: 'network_error',           // 网络错误
  AUTH_ERROR: 'auth_error',                 // 认证错误
  SERVER_ERROR: 'server_error',             // 服务器错误
  VALIDATION_ERROR: 'validation_error',     // 验证错误
  PERMISSION_ERROR: 'permission_error',    // 权限错误
  TIMEOUT_ERROR: 'timeout_error',          // 超时错误
  UNKNOWN_ERROR: 'unknown_error'           // 未知错误
}

/**
 * 错误信息映射
 */
const errorMessages = {
  [ErrorType.NETWORK_ERROR]: {
    title: '网络连接失败',
    message: '请检查网络连接后重试',
    action: '检查网络'
  },
  [ErrorType.AUTH_ERROR]: {
    title: '认证失败',
    message: '请重新登录后继续操作',
    action: '重新登录'
  },
  [ErrorType.SERVER_ERROR]: {
    title: '服务器错误',
    message: '服务器暂时不可用，请稍后重试',
    action: '稍后重试'
  },
  [ErrorType.VALIDATION_ERROR]: {
    title: '输入验证失败',
    message: '请检查输入内容是否符合要求',
    action: '检查输入'
  },
  [ErrorType.PERMISSION_ERROR]: {
    title: '权限不足',
    message: '您没有权限执行此操作',
    action: '联系管理员'
  },
  [ErrorType.TIMEOUT_ERROR]: {
    title: '请求超时',
    message: '操作耗时过长，请稍后重试',
    action: '稍后重试'
  },
  [ErrorType.UNKNOWN_ERROR]: {
    title: '未知错误',
    message: '发生未知错误，请稍后重试',
    action: '联系技术支持'
  }
}

/**
 * 错误分类函数
 * @param {Error} error - 原始错误对象
 * @returns {Object} 分类后的错误信息
 */
export function classifyError(error) {
  // 如果是网络错误
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return {
      type: ErrorType.NETWORK_ERROR,
      originalError: error
    }
  }
  
  // 如果是HTTP状态码错误
  if (error.status) {
    const status = error.status
    
    if (status === 401 || status === 403) {
      return {
        type: ErrorType.AUTH_ERROR,
        originalError: error
      }
    }
    
    if (status >= 400 && status < 500) {
      return {
        type: ErrorType.VALIDATION_ERROR,
        originalError: error
      }
    }
    
    if (status >= 500) {
      return {
        type: ErrorType.SERVER_ERROR,
        originalError: error
      }
    }
  }
  
  // 如果是超时错误
  if (error.name === 'TimeoutError' || error.message?.includes('timeout')) {
    return {
      type: ErrorType.TIMEOUT_ERROR,
      originalError: error
    }
  }
  
  // 默认未知错误
  return {
    type: ErrorType.UNKNOWN_ERROR,
    originalError: error
  }
}

/**
 * 显示错误通知
 * @param {Object} errorInfo - 错误信息对象
 * @param {string} errorInfo.type - 错误类型
 * @param {Error} errorInfo.originalError - 原始错误对象
 * @param {string} customMessage - 自定义错误消息
 */
export function showErrorNotification(errorInfo, customMessage = null) {
  const appStore = useAppStore()
  const errorType = errorInfo.type || ErrorType.UNKNOWN_ERROR
  const errorConfig = errorMessages[errorType]
  
  const message = customMessage || errorConfig.message
  
  appStore.addNotification({
    type: 'error',
    title: errorConfig.title,
    message: message,
    action: errorConfig.action,
    duration: 5000
  })
  
  // 在开发环境下记录详细错误信息
  if (import.meta.env.DEV) {
    console.error('错误详情:', {
      type: errorType,
      message: errorInfo.originalError?.message,
      stack: errorInfo.originalError?.stack
    })
  }
}

/**
 * 统一的错误处理函数
 * @param {Error} error - 原始错误对象
 * @param {string} customMessage - 自定义错误消息
 * @param {Function} onError - 错误回调函数
 */
export function handleError(error, customMessage = null, onError = null) {
  const errorInfo = classifyError(error)
  
  // 显示错误通知
  showErrorNotification(errorInfo, customMessage)
  
  // 执行错误回调
  if (onError && typeof onError === 'function') {
    onError(errorInfo)
  }
  
  return errorInfo
}

/**
 * API请求错误处理包装器
 * @param {Function} apiCall - API调用函数
 * @param {Object} options - 配置选项
 * @returns {Promise} 包装后的Promise
 */
export function withErrorHandling(apiCall, options = {}) {
  const {
    customErrorMessage = null,
    onError = null,
    onSuccess = null,
    timeout = 30000
  } = options
  
  return async (...args) => {
    try {
      // 设置超时
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('请求超时')), timeout)
      })
      
      const result = await Promise.race([apiCall(...args), timeoutPromise])
      
      // 执行成功回调
      if (onSuccess && typeof onSuccess === 'function') {
        onSuccess(result)
      }
      
      return result
    } catch (error) {
      const errorInfo = handleError(error, customErrorMessage, onError)
      throw errorInfo
    }
  }
}

/**
 * 图片上传专用错误处理
 * @param {Error} error - 上传错误
 */
export function handleUploadError(error) {
  const errorInfo = classifyError(error)
  
  let customMessage = null
  
  // 针对图片上传的特殊处理
  if (errorInfo.type === ErrorType.VALIDATION_ERROR) {
    customMessage = '图片格式不支持或文件过大，请选择JPG、PNG格式的图片（小于10MB）'
  } else if (errorInfo.type === ErrorType.NETWORK_ERROR) {
    customMessage = '网络不稳定，图片上传失败，请检查网络后重试'
  }
  
  handleError(error, customMessage)
  
  return errorInfo
}

/**
 * 认证错误处理
 * @param {Error} error - 认证错误
 */
export function handleAuthError(error) {
  const errorInfo = classifyError(error)
  
  // 如果是认证错误，强制用户重新登录
  if (errorInfo.type === ErrorType.AUTH_ERROR) {
    const userStore = useUserStore?.()
    if (userStore && typeof userStore.logout === 'function') {
      // 延迟执行登出，避免影响当前错误显示
      setTimeout(() => {
        userStore.logout()
      }, 2000)
    }
  }
  
  handleError(error)
  
  return errorInfo
}