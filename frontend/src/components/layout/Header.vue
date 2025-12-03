<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()

// 响应式导航
const isMobileMenuOpen = ref(false)
const isLoginModalOpen = ref(false)
const isRegisterModalOpen = ref(false)
const showPassword = ref(false)

// 表单数据
const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  name: '',
  email: '',
  password: ''
})

// 导航菜单
const navItems = [
  { name: '首页', path: '/', icon: 'fas fa-home' },
  { name: '碑文识别', path: '/recognition', icon: 'fas fa-camera' },
  { name: '我的碑文', path: '/favorites', icon: 'fas fa-history' },
  { name: '碑文知识库', path: '/knowledge', icon: 'fas fa-lightbulb' }
]

// 当前页面
const currentPage = computed(() => {
  return navItems.find(item => item.path === route.path)?.name || ''
})

// 移动端菜单切换
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 导航到指定页面
const navigateTo = (path) => {
  router.push(path)
  isMobileMenuOpen.value = false
}

// 模态框操作
const openLoginModal = () => {
  isLoginModalOpen.value = true
  isRegisterModalOpen.value = false
  document.body.style.overflow = 'hidden'
}

const openRegisterModal = () => {
  isRegisterModalOpen.value = true
  isLoginModalOpen.value = false
  document.body.style.overflow = 'hidden'
}

const closeModals = () => {
  isLoginModalOpen.value = false
  isRegisterModalOpen.value = false
  document.body.style.overflow = ''
}

// 表单提交
const handleLogin = async () => {
  try {
    const result = await userStore.login(loginForm.value)
    if (result.success) {
      appStore.addNotification({
        type: 'success',
        message: '登录成功!',
        duration: 3000
      })
      closeModals()
    } else {
      appStore.addNotification({
        type: 'error',
        message: result.error || '登录失败',
        duration: 3000
      })
    }
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      message: error.message || '登录失败',
      duration: 3000
    })
  }
}

const handleRegister = async () => {
  try {
    const result = await userStore.register(registerForm.value)
    if (result.success) {
      appStore.addNotification({
        type: 'success',
        message: '注册成功!',
        duration: 3000
      })
      closeModals()
      // 注册成功后自动跳转到登录
      isLoginModalOpen.value = true
    } else {
      appStore.addNotification({
        type: 'error',
        message: result.error || '注册失败',
        duration: 3000
      })
    }
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      message: error.message || '注册失败',
      duration: 3000
    })
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/')
  appStore.addNotification({
    type: 'success',
    message: '已成功退出登录',
    duration: 3000
  })
}

// 滚动事件处理
const handleScroll = () => {
  const header = document.querySelector('header')
  if (window.scrollY > 50) {
    header?.classList.add('shadow-md', 'bg-white/95')
  } else {
    header?.classList.remove('shadow-md')
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('open-register-modal', openRegisterModal)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('open-register-modal', openRegisterModal)
})
</script>

<template>
  <header class="sticky top-0 z-50 bg-white/90 backdrop-blur-sm shadow-sm transition-custom">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16 md:h-20">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center">
            <i class="fas fa-monument text-primary text-2xl md:text-3xl mr-2"></i>
            <span class="text-xl md:text-2xl font-serif font-bold text-primary">碑说</span>
          </router-link>
        </div>

        <!-- 桌面端导航 -->
        <nav class="hidden md:flex space-x-8">
          <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="nav-link flex items-center"
            :class="{ 'active': route.path === item.path }">
            <i :class="item.icon" class="mr-1"></i>
            {{ item.name }}
          </router-link>
        </nav>

        <!-- 用户操作区域 -->
        <div class="flex items-center space-x-4">
          <template v-if="userStore.isLoggedIn">
            <div class="flex items-center space-x-3">
              <img :src="userStore.user?.avatar || '/images/default-avatar.png'" :alt="userStore.user?.name"
                class="w-8 h-8 rounded-full object-cover">
              <span class="hidden sm:block text-sm font-medium">{{ userStore.user?.name }}</span>
            </div>
            <button @click="handleLogout" class="text-sm text-red-600 hover:text-red-700 font-medium">
              退出
            </button>
          </template>

          <template v-else>
            <button @click="openLoginModal"
              class="px-3 py-2 bg-transparent border border-primary text-primary rounded-md text-sm hover:bg-primary/5 transition-custom">
              登录
            </button>
            <button @click="openRegisterModal"
              class="px-3 py-2 bg-white text-primary border border-white/20 rounded-md text-sm hover:bg-gray-100 transition-custom">
              注册
            </button>
          </template>

          <!-- 移动端菜单按钮 -->
          <button @click="toggleMobileMenu" class="md:hidden text-dark hover:text-primary transition-custom">
            <i class="fas fa-bars text-xl"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 移动端导航菜单 -->
    <div v-show="isMobileMenuOpen" class="md:hidden bg-white border-t">
      <div class="container mx-auto px-4 py-3 space-y-3">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path"
          class="block py-2 px-3 rounded-md nav-link"
          :class="{ 'active': route.path === item.path, 'bg-secondary/50': route.path === item.path }"
          @click="navigateTo(item.path)">
          <i :class="item.icon" class="mr-2"></i>
          {{ item.name }}
        </router-link>

        <div v-if="!userStore.isLoggedIn" class="pt-2 flex space-x-3 border-t border-gray-100">
          <button @click="openLoginModal"
            class="flex-1 py-2 bg-transparent border border-primary text-primary rounded-md text-sm hover:bg-primary/5 transition-custom">
            登录
          </button>
          <button @click="openRegisterModal"
            class="flex-1 py-2 bg-white text-primary border border-white/20 rounded-md text-sm hover:bg-gray-100 transition-custom">
            注册
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- 登录模态框 -->
  <teleport to="body">
    <transition name="modal-fade">
      <div v-if="isLoginModalOpen" class="fixed inset-0 z-50 flex items-center justify-center">
        <div @click="closeModals" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
        <div
          class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 overflow-hidden transform transition-all">
          <div class="p-6 md:p-8">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-2xl font-serif font-bold text-primary">用户登录</h3>
              <button @click="closeModals" class="text-dark/50 hover:text-dark transition-custom">
                <i class="fas fa-times text-xl"></i>
              </button>
            </div>
            <form @submit.prevent="handleLogin">
              <div class="mb-4">
                <label class="block text-sm font-medium text-dark/70 mb-1" for="login-email">邮箱</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i class="fas fa-envelope text-dark/40"></i>
                  </div>
                  <input v-model="loginForm.email"
                    class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    id="login-email" type="email" placeholder="请输入您的邮箱" required />
                </div>
              </div>
              <div class="mb-6">
                <div class="flex justify-between items-center mb-1">
                  <label class="block text-sm font-medium text-dark/70" for="login-password">密码</label>
                  <a href="javascript:void(0);"
                    class="text-sm text-primary hover:text-accent transition-custom">忘记密码?</a>
                </div>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i class="fas fa-lock text-dark/40"></i>
                  </div>
                  <input v-model="loginForm.password"
                    class="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    id="login-password" :type="showPassword ? 'text' : 'password'" placeholder="请输入您的密码" required />
                  <button type="button" @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-dark/40 hover:text-dark">
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>
              <button type="submit"
                class="w-full py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-custom mb-4">登录</button>
              <div class="text-center text-sm text-dark/60">
                <span>还没有账号? </span>
                <button type="button" @click="openRegisterModal"
                  class="text-primary font-medium hover:text-accent transition-custom">立即注册</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>
  </teleport>

  <!-- 注册模态框 -->
  <teleport to="body">
    <transition name="modal-fade">
      <div v-if="isRegisterModalOpen" class="fixed inset-0 z-50 flex items-center justify-center">
        <div @click="closeModals" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
        <div
          class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 overflow-hidden transform transition-all">
          <div class="p-6 md:p-8">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-2xl font-serif font-bold text-primary">用户注册</h3>
              <button @click="closeModals" class="text-dark/50 hover:text-dark transition-custom">
                <i class="fas fa-times text-xl"></i>
              </button>
            </div>
            <form @submit.prevent="handleRegister">
              <div class="mb-4">
                <label class="block text-sm font-medium text-dark/70 mb-1" for="register-name">姓名</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i class="fas fa-user text-dark/40"></i>
                  </div>
                  <input v-model="registerForm.name"
                    class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    id="register-name" type="text" placeholder="请输入您的姓名" required />
                </div>
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-dark/70 mb-1" for="register-email">邮箱</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i class="fas fa-envelope text-dark/40"></i>
                  </div>
                  <input v-model="registerForm.email"
                    class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    id="register-email" type="email" placeholder="请输入您的邮箱" required />
                </div>
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-dark/70 mb-1" for="register-password">密码</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i class="fas fa-lock text-dark/40"></i>
                  </div>
                  <input v-model="registerForm.password"
                    class="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    id="register-password" :type="showPassword ? 'text' : 'password'" placeholder="请设置密码" required />
                  <button type="button" @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-dark/40 hover:text-dark">
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>
              <button type="submit"
                class="w-full py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-custom">注册账号</button>
              <div class="text-center text-sm text-dark/60 mt-4">
                <span>已有账号? </span>
                <button type="button" @click="openLoginModal"
                  class="text-primary font-medium hover:text-accent transition-custom">立即登录</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<style scoped>
/* 模态框过渡动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active>div:last-child,
.modal-fade-leave-active>div:last-child {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from>div:last-child {
  transform: scale(0.9);
}

.modal-fade-leave-to>div:last-child {
  transform: scale(0.9);
}
</style>
