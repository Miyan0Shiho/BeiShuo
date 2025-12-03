import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister } from '../api/auth.js'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(null)
  const baseUrl = ref(import.meta.env.VITE_BACKEND_BASE || 'http://localhost:8080')
  const isLoggedIn = computed(() => !!token.value)
  
  // 登录
  const login = async (credentials) => {
    try {
      const data = await apiLogin({
        baseUrl: baseUrl.value,
        email: credentials.email,
        password: credentials.password,
        remember_me: credentials.remember_me || false
      })
      
      // 保存用户信息和token
      user.value = data.user
      token.value = data.token
      
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('token', token.value)
      
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.message }
    }
  }
  
  // 注册
  const register = async (userData) => {
    try {
      await apiRegister({
        baseUrl: baseUrl.value,
        name: userData.name,
        email: userData.email,
        password: userData.password
      })
      
      return { success: true }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: error.message }
    }
  }
  
  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }
  
  // 初始化用户状态
  const initUser = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }
  
  return {
    user,
    token,
    isLoggedIn,
    login,
    register,
    logout,
    initUser
  }
})
