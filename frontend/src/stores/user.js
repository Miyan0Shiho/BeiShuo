import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '../api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)
  const isLoggedIn = computed(() => !!user.value && !!token.value)
  
  // 登录
  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await authApi.login(
        credentials.email, 
        credentials.password,
        credentials.rememberMe || false
      )
      
      // 保存 token 和用户信息
      token.value = response.token
      user.value = response.user
      
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      localStorage.setItem('token_expires_at', response.expires_at)
      
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }
  
  // 注册
  const register = async (userData) => {
    loading.value = true
    try {
      const response = await authApi.register(
        userData.name,
        userData.email,
        userData.password
      )
      
      // 注册成功后自动登录
      token.value = response.token
      user.value = response.user
      
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      localStorage.setItem('token_expires_at', response.expires_at)
      
      return { success: true }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }
  
  // 登出
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 无论请求是否成功，都清除本地状态
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('token_expires_at')
    }
  }
  
  // 刷新用户信息
  const refreshProfile = async () => {
    if (!token.value) return
    
    try {
      const profile = await authApi.getProfile()
      user.value = profile
      localStorage.setItem('user', JSON.stringify(profile))
    } catch (error) {
      console.error('刷新用户信息失败:', error)
      // 如果获取失败，可能是 token 过期，登出用户
      if (error.message.includes('未登录') || error.message.includes('失败')) {
        await logout()
      }
    }
  }
  
  // 刷新 Token
  const refreshAuthToken = async () => {
    if (!token.value) return false
    
    try {
      const response = await authApi.refreshToken()
      token.value = response.token
      localStorage.setItem('token', response.token)
      localStorage.setItem('token_expires_at', response.expires_at)
      return true
    } catch (error) {
      console.error('刷新Token失败:', error)
      await logout()
      return false
    }
  }
  
  // 初始化用户状态
  const initUser = async () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      try {
        user.value = JSON.parse(savedUser)
        // 后台刷新用户信息以确保数据最新
        refreshProfile()
      } catch (e) {
        console.error('解析用户信息失败:', e)
        await logout()
      }
    }
  }
  
  return {
    user,
    token,
    loading,
    isLoggedIn,
    login,
    register,
    logout,
    refreshProfile,
    refreshAuthToken,
    initUser
  }
})
