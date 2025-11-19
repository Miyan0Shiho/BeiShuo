<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAppStore } from './stores/app'
import { useUserStore } from './stores/user'
import Header from './components/layout/Header.vue'
import Footer from './components/layout/Footer.vue'
import Notifications from './components/common/Notifications.vue'

const appStore = useAppStore()
const userStore = useUserStore()

// 初始化应用
onMounted(() => {
  appStore.initApp()
  userStore.initUser()
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-light bg-texture">
    <!-- 通知组件 -->
    <Notifications />
    
    <!-- 页头 -->
    <Header />
    
    <!-- 主要内容区域 -->
    <main class="flex-grow">
      <RouterView />
    </main>
    
    <!-- 页脚 -->
    <Footer />
  </div>
</template>

<style scoped>
/* 应用级样式 */
</style>
