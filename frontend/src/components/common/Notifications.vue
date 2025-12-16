<script setup>
import { useAppStore } from '../../stores/app'

const appStore = useAppStore()

// 移除通知
const removeNotification = (id) => {
  appStore.removeNotification(id)
}

// 获取通知类型图标
const getNotificationIcon = (type) => {
  const icons = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return icons[type] || icons.info
}

// 获取通知类型样式
const getNotificationClass = (type) => {
  const classes = {
    success: 'bg-green-50 text-green-800 border-green-200',
    error: 'bg-red-50 text-red-800 border-red-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200'
  }
  return classes[type] || classes.info
}
</script>

<template>
  <div class="fixed top-20 right-4 z-[100] space-y-2">
    <div
      v-for="notification in appStore.notifications"
      :key="notification.id"
      class="flex items-start p-4 rounded-lg border shadow-lg max-w-sm animate-fade-in"
      :class="getNotificationClass(notification.type)"
    >
      <div class="flex-shrink-0">
        <i :class="getNotificationIcon(notification.type)" class="text-lg"></i>
      </div>
      <div class="ml-3 flex-1">
        <p class="text-sm font-medium">
          {{ notification.message }}
        </p>
        <p class="text-xs opacity-75 mt-1">
          {{ new Date(notification.timestamp).toLocaleTimeString() }}
        </p>
      </div>
      <button
        @click="removeNotification(notification.id)"
        class="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* 通知动画 */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>
