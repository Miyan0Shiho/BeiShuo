import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const isLoading = ref(false)
  const sidebarOpen = ref(false)
  const theme = ref('light')
  const notifications = ref([])
  
  // 设置加载状态
  const setLoading = (loading) => {
    isLoading.value = loading
  }
  
  // 切换侧边栏
  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }
  
  // 设置主题
  const setTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }
  
  // 添加通知
  const addNotification = (notification) => {
    const id = Date.now()
    notifications.value.push({
      id,
      ...notification,
      timestamp: new Date()
    })
    
    // 自动移除通知
    if (notification.autoRemove !== false) {
      setTimeout(() => {
        removeNotification(id)
      }, notification.duration || 5000)
    }
    
    return id
  }
  
  // 移除通知
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  // 初始化应用
  const initApp = () => {
    // 初始化主题
    const savedTheme = localStorage.getItem('theme') || 'light'
    setTheme(savedTheme)
  }
  
  return {
    // 状态
    isLoading,
    sidebarOpen,
    theme,
    notifications,
    
    // 方法
    setLoading,
    toggleSidebar,
    setTheme,
    addNotification,
    removeNotification,
    initApp
  }
})
