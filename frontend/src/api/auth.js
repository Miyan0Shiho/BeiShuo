/**
 * 用户认证相关API接口
 * 提供登录、注册、登出、获取用户信息等功能
 */

const baseUrl = 'http://localhost:8080/api/v1'

/**
 * 用户登录
 * @param {Object} credentials - 登录凭据
 * @param {string} credentials.email - 邮箱
 * @param {string} credentials.password - 密码
 * @param {boolean} credentials.remember_me - 是否记住登录状态
 * @returns {Promise<Object>} 登录结果
 */
export async function login(credentials) {
  try {
    const response = await fetch(`${baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.message || '登录失败')
    }

    if (!data.success) {
      throw new Error(data.message || '登录失败')
    }

    return data
  } catch (error) {
    console.error('登录API调用失败:', error)
    throw error
  }
}

/**
 * 用户注册
 * @param {Object} userData - 用户注册数据
 * @param {string} userData.name - 姓名
 * @param {string} userData.email - 邮箱
 * @param {string} userData.password - 密码
 * @returns {Promise<Object>} 注册结果
 */
export async function register(userData) {
  try {
    const response = await fetch(`${baseUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.message || '注册失败')
    }

    if (!data.success) {
      throw new Error(data.message || '注册失败')
    }

    return data
  } catch (error) {
    console.error('注册API调用失败:', error)
    throw error
  }
}

/**
 * 获取当前用户信息
 * @param {string} token - JWT令牌
 * @returns {Promise<Object>} 用户信息
 */
export async function getProfile(token) {
  try {
    const response = await fetch(`${baseUrl}/auth/profile`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.message || '获取用户信息失败')
    }

    if (!data.success) {
      throw new Error(data.message || '获取用户信息失败')
    }

    return data
  } catch (error) {
    console.error('获取用户信息API调用失败:', error)
    throw error
  }
}

/**
 * 刷新令牌
 * @param {string} token - 当前令牌
 * @returns {Promise<Object>} 刷新结果
 */
export async function refreshToken(token) {
  try {
    const response = await fetch(`${baseUrl}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.message || '令牌刷新失败')
    }

    if (!data.success) {
      throw new Error(data.message || '令牌刷新失败')
    }

    return data
  } catch (error) {
    console.error('令牌刷新API调用失败:', error)
    throw error
  }
}

/**
 * 用户登出
 * @param {string} token - JWT令牌
 * @returns {Promise<Object>} 登出结果
 */
export async function logout(token) {
  try {
    const response = await fetch(`${baseUrl}/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.message || '登出失败')
    }

    if (!data.success) {
      throw new Error(data.message || '登出失败')
    }

    return data
  } catch (error) {
    console.error('登出API调用失败:', error)
    throw error
  }
}