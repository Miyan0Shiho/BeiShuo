// 认证相关 API

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

/**
 * 用户登录
 * @param {string} email 
 * @param {string} password 
 * @param {boolean} rememberMe 
 * @returns {Promise<{token: string, expires_at: string, user: Object}>}
 */
export async function login(email, password, rememberMe = false) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, remember_me: rememberMe })
  })
  
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.message || '登录失败')
  }
  
  const data = await res.json()
  if (data.success) {
    return data.data
  }
  throw new Error(data.message || '登录失败')
}

/**
 * 用户注册
 * @param {string} name 
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise<{token: string, expires_at: string, user: Object}>}
 */
export async function register(name, email, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  })
  
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.message || '注册失败')
  }
  
  const data = await res.json()
  if (data.success) {
    return data.data
  }
  throw new Error(data.message || '注册失败')
}

/**
 * 用户登出
 * @returns {Promise<void>}
 */
export async function logout() {
  const token = localStorage.getItem('token')
  if (!token) return
  
  await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  }).catch(() => {})
}

/**
 * 获取当前用户信息
 * @returns {Promise<Object>}
 */
export async function getProfile() {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('未登录')
  }
  
  const res = await fetch(`${API_BASE}/auth/profile`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  
  if (!res.ok) {
    throw new Error('获取用户信息失败')
  }
  
  const data = await res.json()
  if (data.success) {
    return data.data
  }
  throw new Error(data.message || '获取用户信息失败')
}

/**
 * 刷新 Token
 * @returns {Promise<{token: string, expires_at: string}>}
 */
export async function refreshToken() {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('未登录')
  }
  
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  
  if (!res.ok) {
    throw new Error('刷新Token失败')
  }
  
  const data = await res.json()
  if (data.success) {
    return data.data
  }
  throw new Error(data.message || '刷新Token失败')
}
