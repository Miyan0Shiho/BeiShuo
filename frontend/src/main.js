import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const devToken = import.meta.env.VITE_DEV_TOKEN
if (typeof window !== 'undefined' && devToken && !localStorage.getItem('token')) {
  localStorage.setItem('token', devToken)
}

app.mount('#app')
