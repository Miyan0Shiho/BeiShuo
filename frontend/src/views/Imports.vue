<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const files = ref([])
const uploading = ref(false)
const uploadProgress = ref({})
const importResults = ref([])
const importHistory = ref([])
const selectedImport = ref(null)
const previewContent = ref('')
const editContent = ref('')
const editTitle = ref('')

const isLoggedIn = computed(() => userStore.isLoggedIn)

const handleFileSelect = (e) => {
  const list = Array.from(e.target.files || [])
  files.value = list
}
const handleDrop = (e) => {
  const list = Array.from(e.dataTransfer.files || [])
  files.value = list
}

const toUpper = () => { editContent.value = (editContent.value || '').toUpperCase() }
const toLower = () => { editContent.value = (editContent.value || '').toLowerCase() }
const trimSpaces = () => { editContent.value = (editContent.value || '').replace(/\s+/g, ' ').trim() }

const uploadFiles = async () => {
  if (!files.value.length) return
  uploading.value = true
  importResults.value = []
  const form = new FormData()
  files.value.forEach(f => form.append('files', f))
  const baseUrl = window.location.origin + '/api/v1'
  const token = userStore.token || localStorage.getItem('token') || ''
  try {
    const res = await fetch(`${baseUrl}/imports/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: form
    })
    if (res.ok) {
      const json = await res.json()
      const data = json.data || {}
      importResults.value = data.items || []
      appStore.addNotification({ type: 'success', message: `上传完成：成功 ${data.count}，失败 ${data.failed}`, duration: 3000 })
    } else {
      appStore.addNotification({ type: 'error', message: '上传失败', duration: 3000 })
    }
  } catch (e) {
    appStore.addNotification({ type: 'error', message: '网络错误，上传失败', duration: 3000 })
  } finally {
    uploading.value = false
    loadHistory()
  }
}

const selectImport = async (item) => {
  selectedImport.value = item
  previewContent.value = item.preview || ''
  editTitle.value = item.title || ''
  editContent.value = item.preview || ''
}



onMounted(() => {
  if (!isLoggedIn.value) {
    appStore.addNotification({ type: 'error', message: '请先登录后使用“我的导入”', duration: 3000 })
    router.push('/favorites')
  }
  loadHistory()
})

const loadHistory = async () => {
  const baseUrl = window.location.origin + '/api/v1'
  const token = userStore.token || localStorage.getItem('token') || ''
  try {
    const res = await fetch(`${baseUrl}/imports/list`, { headers: { 'Authorization': `Bearer ${token}` } })
    if (res.ok) {
      const json = await res.json()
      importHistory.value = json.data || []
    }
  } catch {}
}
</script>

<template>
  <div class="min-h-screen bg-light text-dark">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-serif font-bold text-primary">我的导入</h1>
      </div>
      <div class="grid lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-sm p-4">
            <h3 class="text-lg font-semibold mb-3">导入文件</h3>
            <div 
              class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer bg-gray-50"
              @dragover.prevent
              @drop.prevent="handleDrop"
            >
              <input type="file" multiple accept=".txt,.docx,.pdf" @change="handleFileSelect" />
              <p class="text-sm text-dark/60 mt-2">支持 .txt / .docx / .pdf</p>
            </div>
            <div class="mt-4">
              <button @click="uploadFiles" :disabled="uploading" class="w-full px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 disabled:opacity-50">
                {{ uploading ? '上传中...' : '开始上传' }}
              </button>
            </div>
            <div class="mt-4">
              <h4 class="text-sm font-medium mb-2">上传结果</h4>
              <div class="space-y-2 max-h-48 overflow-y-auto">
                <div v-for="it in importResults" :key="it.filename" class="flex justify-between items-center p-2 border rounded hover:bg-gray-50">
                  <div class="truncate">
                    <div class="text-sm">{{ it.filename }}</div>
                    <div class="text-xs text-dark/50" v-if="it.reason">{{ it.reason }}</div>
                  </div>
                  <div class="text-xs" :class="it.status === 'success' ? 'text-green-600' : 'text-red-600'">{{ it.status }}</div>
                  <button v-if="it.status==='success'" @click="selectImport(it)" class="text-primary text-xs ml-2">预览</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm p-4">
            <h3 class="text-lg font-semibold mb-3">预览与编辑</h3>
            <div v-if="selectedImport" class="space-y-3">
              <input v-model="editTitle" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="标题" />
              <div class="flex space-x-2">
                <button @click="toUpper" class="px-3 py-1 border rounded">大写</button>
                <button @click="toLower" class="px-3 py-1 border rounded">小写</button>
                <button @click="trimSpaces" class="px-3 py-1 border rounded">清理空白</button>
              </div>
              <textarea v-model="editContent" rows="12" class="w-full border border-gray-300 rounded-md p-3"></textarea>


            </div>
            <div v-else class="text-sm text-dark/60">请先上传并选择一条导入记录进行预览与编辑</div>
          </div>
          <div class="bg-white rounded-xl shadow-sm p-4 mt-4">
            <h3 class="text-lg font-semibold mb-3">导入历史</h3>
            <div class="space-y-2 max-h-64 overflow-y-auto">
              <div v-for="it in importHistory" :key="it.id" class="p-2 border rounded">
                <div class="text-sm font-medium">{{ it.title }}</div>
                <div class="text-xs text-dark/50">{{ it.filename }} · {{ it.created_at }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
