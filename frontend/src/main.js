import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 设置测试用的有效token
const devToken = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInVzZXJuYW1lIjoidGVzdF91c2VyIiwiaWF0IjoxNzY1MTgzMjA1LCJleHAiOjE3NjUyNjk2MDV9.IDen5EfQ-On_HV_O8VKAcCa-4H7Byu7lRIxTcvNnn4meE6tAVbPAiqOoXW2-whxLq6BMRetd4YuOyeR_Klx9Dg'
if (typeof window !== 'undefined' && !localStorage.getItem('token')) {
  localStorage.setItem('token', devToken)
}

app.mount('#app')
