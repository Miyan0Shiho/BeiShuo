import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'

// 导入Mock服务
import { initializeMockService } from './utils/mockService.js'
import mockApi from './mock/mockApi.js';

const app = createApp(App)
const pinia = createPinia()

// 初始化Mock服务
initializeMockService()

// 如果启用了Mock模式，初始化Mock会话数据
const useMock = import.meta.env.VITE_USE_MOCK === 'true'
if (useMock) {
  console.log('🚀 应用启动在Mock模式下');
  mockApi.initializeMockSession()
}

app.use(pinia)
app.use(router)

app.mount('#app')
