import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)
  
  // 登录
  const login = async (credentials) => {
    try {
      // 这里应该调用API
      // const response = await api.login(credentials)
      
      // 模拟登录成功
      user.value = {
        id: 1,
        name: '张三',
        email: credentials.email,
        avatar: '/images/default-avatar.png'
      }
      
      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.message }
    }
  }
  
  // 注册
  const register = async (userData) => {
    try {
      // 这里应该调用API
      // const response = await api.register(userData)
      
      // 模拟注册成功
      console.log('注册成功:', userData)
      return { success: true }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: error.message }
    }
  }
  
  // 登出
  const logout = () => {
    user.value = null
    localStorage.removeItem('user')
  }
  
  // 初始化用户状态
  const initUser = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
  }
  
  return {
    user,
    isLoggedIn,
    login,
    register,
    logout,
    initUser
  }
})
