import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '../api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  
  // 登录
  const login = async (credentials) => {
    try {
      const response = await authApi.login(credentials)
      
      if (response.success && response.data) {
        // 保存用户信息和令牌
        user.value = response.data.user
        token.value = response.data.token
        
        // 保存到本地存储
        localStorage.setItem('user', JSON.stringify(user.value))
        localStorage.setItem('token', token.value)
        
        return { success: true }
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.message }
    }
  }
  
  // 注册
  const register = async (userData) => {
    try {
      const response = await authApi.register(userData)
      
      if (response.success) {
        return { success: true }
      } else {
        throw new Error(response.message || '注册失败')
      }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: error.message }
    }
  }
  
  // 登出
  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout(token.value)
      }
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      // 清除本地状态
      user.value = null
      token.value = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  }
  
  // 获取当前用户信息
  const fetchProfile = async () => {
    try {
      if (!token.value) {
        throw new Error('未登录')
      }
      
      const response = await authApi.getProfile(token.value)
      
      if (response.success && response.data) {
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(user.value))
        return { success: true }
      } else {
        throw new Error(response.message || '获取用户信息失败')
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取失败，清除登录状态
      logout()
      return { success: false, error: error.message }
    }
  }
  
  // 刷新令牌
  const refreshToken = async () => {
    try {
      if (!token.value) {
        throw new Error('未登录')
      }
      
      const response = await authApi.refreshToken(token.value)
      
      if (response.success && response.data) {
        token.value = response.data.token
        localStorage.setItem('token', token.value)
        return { success: true }
      } else {
        throw new Error(response.message || '令牌刷新失败')
      }
    } catch (error) {
      console.error('令牌刷新失败:', error)
      // 如果刷新失败，清除登录状态
      logout()
      return { success: false, error: error.message }
    }
  }
  
  // 初始化用户状态
  const initUser = async () => {
    const savedUser = localStorage.getItem('user')
    const savedToken = localStorage.getItem('token')
    
    if (savedUser && savedToken) {
      user.value = JSON.parse(savedUser)
      token.value = savedToken
      
      // 验证令牌是否有效
      try {
        await fetchProfile()
      } catch (error) {
        console.error('初始化用户状态失败:', error)
        // 如果验证失败，清除登录状态
        logout()
      }
    }
  }
  
  return {
    user,
    token,
    isLoggedIn,
    login,
    register,
    logout,
    fetchProfile,
    refreshToken,
    initUser
  }
})
