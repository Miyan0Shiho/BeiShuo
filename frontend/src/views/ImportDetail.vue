<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const importId = computed(() => route.params.id)
const data = ref(null)
const loading = ref(true)
const errorMessage = ref('')


const loadDetail = async () => {
  try {
    loading.value = true
    const baseUrl = window.location.origin + '/api/v1'
    const token = userStore.token || localStorage.getItem('token') || ''
    const res = await fetch(`${baseUrl}/imports/${importId.value}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const json = await res.json()
    data.value = json.data || null
    if (!data.value) throw new Error('导入记录不存在')
    errorMessage.value = ''
  } catch (e) {
    errorMessage.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}



onMounted(() => {
  userStore.initUser?.()
  loadDetail()
})
</script>

<template>
  <div class="min-h-screen bg-light bg-texture text-dark font-sans">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6 flex justify-between items-center">
        <nav class="text-sm text-dark/60">
          <ol class="flex flex-wrap items-center">
            <li><router-link to="/favorites?tab=my-imports" class="hover:text-primary transition-custom">我的碑文</router-link></li>
            <li class="mx-2"><i class="fas fa-angle-right text-xs"></i></li>
            <li class="text-primary">我的导入详情</li>
          </ol>
        </nav>
        <button @click="$router.back()" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-dark/70 hover:bg-gray-50 transition-custom">
          返回
        </button>
      </div>

      <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-md p-4 text-red-700 mb-6">
        <div class="flex justify-between items-center">
          <span>{{ errorMessage }}</span>
          <button @click="errorMessage=''" class="text-red-500 hover:text-red-700"><i class="fas fa-times"></i></button>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="text-center">
          <i class="fas fa-spinner fa-spin text-4xl text-primary mb-4"></i>
          <p class="text-dark/60">加载中...</p>
        </div>
      </div>

      <div v-else-if="data" class="grid lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-white rounded-xl shadow-sm p-6">
          <h1 class="text-2xl font-serif font-bold text-primary mb-2">{{ data.title || data.filename }}</h1>
          <div class="flex items-center text-sm text-dark/60 mb-4">
            <i class="fas fa-calendar-alt mr-1.5"></i>
            <span>{{ data.created_at || '' }}</span>
            <span class="mx-2">|</span>
            <i class="fas fa-tag mr-1.5"></i>
            <span>{{ data.category || '未分类' }}</span>
          </div>
          <div class="prose max-w-none text-dark/90 leading-relaxed">
            <pre class="whitespace-pre-wrap text-sm">{{ data.content || '' }}</pre>
          </div>
        </div>
        <div class="space-y-6">
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold text-primary mb-3">元数据</h3>
            <ul class="space-y-2 text-sm">
              <li class="flex justify-between"><span class="text-dark/60">源ID</span><span class="font-medium">{{ data.source_id || '-' }}</span></li>
              <li class="flex justify-between"><span class="text-dark/60">时间戳</span><span class="font-medium">{{ data.timestamp || '-' }}</span></li>
              <li class="flex justify-between"><span class="text-dark/60">朝代</span><span class="font-medium">{{ data.dynasty || '-' }}</span></li>
              <li class="flex justify-between"><span class="text-dark/60">分类</span><span class="font-medium">{{ data.category || '-' }}</span></li>
            </ul>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>
