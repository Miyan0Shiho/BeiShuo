<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'
import { getInscription, updateInscription } from '../api/inscription'
import { postInterpretationSections } from '../api/ai'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const inscription = ref(null)
const loading = ref(true)
const activeTab = ref('history')
const sectionsHistory = ref('')
const sectionsCulture = ref('')
const sectionsFigures = ref([])
const sectionsSources = ref([])
const sectionsLoading = ref(false)
const timeline = ref([])
const correctedText = ref('')
const errorMessage = ref('')
const isEditing = ref(false)

const inscriptionId = computed(() => parseInt(route.params.id, 10))

const escapeHtml = (str) => {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

const renderMarkdown = (md) => {
  if (!md) return ''
  const lines = md.split('\n')
  let html = ''
  let inUl = false
  let inOl = false
  let inCode = false
  let codeBuf = []
  const closeLists = () => {
    if (inUl) { html += '</ul>'; inUl = false }
    if (inOl) { html += '</ol>'; inOl = false }
  }
  const formatInline = (text) => {
    let s = escapeHtml(text)
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>')
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>')
    return s
  }
  for (let raw of lines) {
    const line = raw.replace(/\r$/, '')
    if (line.trim().startsWith('```')) {
      if (!inCode) { inCode = true; codeBuf = []; closeLists() }
      else { inCode = false; html += `<pre class="code"><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>`; codeBuf = [] }
      continue
    }
    if (inCode) { codeBuf.push(line); continue }
    if (!line.trim()) { closeLists(); html += '<br/>'; continue }
    const h3 = line.match(/^###\s+(.*)/)
    if (h3) { closeLists(); html += `<h3>${formatInline(h3[1])}</h3>`; continue }
    const h4 = line.match(/^##\s+(.*)/)
    if (h4) { closeLists(); html += `<h4>${formatInline(h4[1])}</h4>`; continue }
    if (/^(-|\*)\s+/.test(line)) {
      if (!inUl) { closeLists(); html += '<ul>'; inUl = true }
      html += `<li>${formatInline(line.replace(/^(-|\*)\s+/, ''))}</li>`
      continue
    }
    const ol = line.match(/^\d+\.\s+(.*)/)
    if (ol) {
      if (!inOl) { closeLists(); html += '<ol>'; inOl = true }
      html += `<li>${formatInline(ol[1])}</li>`
      continue
    }
    closeLists()
    html += `<p>${formatInline(line)}</p>`
  }
  closeLists()
  if (inCode) { html += `<pre class="code"><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>` }
  return html
}

const loadInscription = async () => {
  try {
    loading.value = true
    const baseUrl = window.location.origin
    const token = userStore.token || localStorage.getItem('token') || ''
    const data = await getInscription({ baseUrl, token, id: inscriptionId.value })
    inscription.value = data
    correctedText.value = (data && (data.corrected_text || data.content)) || ''
    errorMessage.value = ''
  } catch (e) {
    errorMessage.value = (e && e.message) ? e.message : '加载碑文失败'
    appStore.addNotification({ type: 'error', message: '加载碑文失败', duration: 3000 })
    // 不自动跳转，让用户看到错误
    // router.push('/favorites')
  } finally {
    loading.value = false
  }
}

const fetchInterpretation = async () => {
  if (!inscription.value) return
  const storageKey = `interpretation_${inscription.value.id}`
  const cached = localStorage.getItem(storageKey)
  if (cached) {
    try {
      const data = JSON.parse(cached)
      sectionsHistory.value = data.history || ''
      sectionsCulture.value = data.culture || ''
      sectionsFigures.value = data.figures || []
      sectionsSources.value = data.sources || []
      timeline.value = data.timeline || []
      return
    } catch (e) {
      localStorage.removeItem(storageKey)
    }
  }

  const baseUrl = window.location.origin
  const token = userStore.token || localStorage.getItem('token') || ''
  const text = `${inscription.value.title || ''} ${inscription.value.dynasty || ''}\n\n${(inscription.value.content || '')}`.trim()
  try {
    sectionsLoading.value = true
    const data = await postInterpretationSections({ baseUrl, token, text, inscriptionId: inscription.value.id })
    const s = data.sections || {}
    sectionsHistory.value = s.history_markdown || ''
    sectionsCulture.value = s.culture_markdown || ''
    sectionsFigures.value = s.figures || []
    sectionsSources.value = data.sources || []
    if (Array.isArray(s.timeline)) {
      timeline.value = s.timeline.map(t => ({ year: t.year, event: (t.title ? t.title + '：' : '') + (t.description || '') }))
    } else {
      timeline.value = []
    }
    
    // Cache the result
    localStorage.setItem(storageKey, JSON.stringify({
      history: sectionsHistory.value,
      culture: sectionsCulture.value,
      figures: sectionsFigures.value,
      sources: sectionsSources.value,
      timeline: timeline.value,
      timestamp: Date.now()
    }))
  } catch (e) {
    errorMessage.value = (e && e.message) ? e.message : 'AI阐释生成失败'
    sectionsHistory.value = ''
    sectionsCulture.value = ''
    sectionsFigures.value = []
    sectionsSources.value = []
    timeline.value = []
  } finally {
    sectionsLoading.value = false
  }
}

const startEditing = () => {
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
  correctedText.value = (inscription.value.corrected_text || inscription.value.content || '')
}

const saveCorrections = async () => {
  try {
    const baseUrl = window.location.origin
    const token = userStore.token || localStorage.getItem('token') || ''
    await updateInscription({ baseUrl, token, id: inscriptionId.value, title: inscription.value.title, correctedText: correctedText.value, status: inscription.value.status })
    appStore.addNotification({ type: 'success', message: '已保存校对结果', duration: 2000 })
    errorMessage.value = ''
    isEditing.value = false
    // Reload to update view
    loadInscription()
  } catch (e) {
    errorMessage.value = (e && e.message) ? e.message : '保存失败'
    appStore.addNotification({ type: 'error', message: '保存失败', duration: 3000 })
  }
}

const saveAsNew = async () => {
  try {
    const baseUrl = window.location.origin + '/api/v1'
    const token = userStore.token || localStorage.getItem('token') || ''
    const response = await fetch(`${baseUrl}/inscription/save`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ itemId: inscriptionId.value })
    })
    
    if (response.ok) {
        appStore.addNotification({ type: 'success', message: '已保存副本到我的碑文', duration: 2000 })
    } else {
        const err = await response.json()
        throw new Error(err.message || '保存失败')
    }
  } catch (e) {
    appStore.addNotification({ type: 'error', message: e.message || '保存副本失败', duration: 3000 })
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) loadInscription()
})

onMounted(() => {
  userStore.initUser()
  if (isNaN(inscriptionId.value)) {
    errorMessage.value = '无效的碑文ID'
    return
  }
  loadInscription().then(fetchInterpretation)
})
</script>

<template>
  <div class="min-h-screen bg-light bg-texture text-dark font-sans">
    <div v-if="errorMessage" class="fixed top-20 left-0 right-0 z-50 px-4 sm:px-6 lg:px-8 pointer-events-none">
      <div class="max-w-7xl mx-auto">
        <div class="bg-red-50/95 border border-red-200 text-red-700 rounded-md p-4 shadow-lg backdrop-blur-sm pointer-events-auto flex justify-between items-center">
          <div class="flex items-center">
            <i class="fas fa-exclamation-triangle mr-3 text-lg"></i>
            <span class="font-medium">{{ errorMessage }}</span>
          </div>
          <button @click="errorMessage = ''" class="text-red-500 hover:text-red-700 transition-colors">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="text-center">
        <i class="fas fa-spinner fa-spin text-4xl text-primary mb-4"></i>
        <p class="text-dark/60">加载中...</p>
      </div>
    </div>

    <div v-else-if="inscription" class="py-8 md:py-12">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 mb-6">
        <nav class="text-sm text-dark/60">
          <ol class="flex flex-wrap items-center">
            <li><router-link to="/favorites" class="hover:text-primary transition-custom">我的碑文</router-link></li>
            <li class="mx-2"><i class="fas fa-angle-right text-xs"></i></li>
            <li class="text-primary">{{ inscription.title }}</li>
          </ol>
        </nav>
      </div>

      <div class="container mx-auto px-4 sm:px-6 lg:px-8 mb-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-4">
          <div>
            <div class="flex items-center space-x-3 mb-3">
              <h1 class="text-3xl md:text-4xl font-serif font-bold text-primary">{{ inscription.title }}</h1>
              <span class="bg-primary/10 text-primary text-sm px-3 py-1 rounded-full font-medium">{{ inscription.dynasty || '识别碑文' }}</span>
            </div>
            <div class="flex flex-wrap items-center text-dark/60 space-x-4 text-sm">
              <div class="flex items-center">
                <i class="fas fa-calendar-alt mr-1.5"></i>
                <span>{{ inscription.created_at ? new Date(inscription.created_at).toLocaleDateString() : '未知日期' }}</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-tag mr-1.5"></i>
                <span>识别结果</span>
              </div>
            </div>
          </div>
          <div class="flex space-x-3 mt-4 md:mt-0">
            <button @click="saveAsNew" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-dark/70 hover:bg-gray-50 transition-custom flex items-center">
              <i class="fas fa-copy mr-2"></i>
              另存副本
            </button>
            <template v-if="!isEditing">
              <button @click="startEditing" class="px-4 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center">
                <i class="fas fa-edit mr-2"></i>
                编辑内容
              </button>
            </template>
            <template v-else>
              <button @click="cancelEditing" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-dark/70 hover:bg-gray-50 transition-custom">
                取消
              </button>
              <button @click="saveCorrections" class="px-4 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center">
                <i class="fas fa-save mr-2"></i>
                保存修改
              </button>
            </template>
          </div>
        </div>
      </div>

      <div class="container mx-auto px-4 sm:px-6 lg:px-8 mb-12">
        <div class="grid lg:grid-cols-3 gap-8">
          <div class="lg:col-span-1">
            <div class="bg-white rounded-xl shadow-sm overflow-hidden sticky top-24">
              <div class="relative">
                <img :alt="inscription.title" :src="inscription.cover_image_url || inscription.image_url || 'https://via.placeholder.com/400x600?text=No+Image'" class="w-full h-auto object-cover">
              </div>
              <div class="p-5">
                <h3 class="text-lg font-semibold mb-3">碑刻信息</h3>
                <ul class="space-y-3 text-sm">
                  <li class="flex justify-between">
                    <span class="text-dark/60">碑刻年代</span>
                    <span class="font-medium">{{ inscription.dynasty || '未知年代' }}</span>
                  </li>
                  <li class="flex justify-between">
                    <span class="text-dark/60">创建时间</span>
                    <span class="font-medium">{{ inscription.created_at ? new Date(inscription.created_at).toLocaleDateString() : '未知' }}</span>
                  </li>
                  <li class="flex justify-between">
                    <span class="text-dark/60">状态</span>
                    <span class="font-medium">{{ inscription.status || 'active' }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div class="lg:col-span-2">
            <div class="bg-white rounded-xl shadow-sm p-6 md:p-8 mb-8">
              <div class="mb-6">
                <h2 class="text-2xl font-serif font-bold text-primary">识别文本</h2>
                <div class="mt-4">
                  <div v-if="!isEditing" class="border border-gray-200 rounded-lg p-6 bg-white/50 min-h-[200px] hover:bg-gray-50 transition-colors">
                    <div class="text-dark/90 leading-relaxed whitespace-pre-wrap text-lg font-serif">{{ correctedText || inscription.text || inscription.content }}</div>
                    <div v-if="!correctedText && !inscription.text && !inscription.content" class="text-dark/40 text-center py-8">暂无内容</div>
                  </div>
                  <div v-else class="grid md:grid-cols-2 gap-6">
                    <div class="border border-gray-200 rounded-lg p-4 bg-gray-50 h-[500px] flex flex-col">
                      <h4 class="font-medium text-dark/60 mb-2 text-sm flex-shrink-0">原始识别结果 (参考)</h4>
                      <div class="text-sm leading-relaxed whitespace-pre-wrap overflow-y-auto flex-grow p-2 bg-white rounded border border-gray-100">{{ inscription.text || inscription.content || '无原始内容' }}</div>
                    </div>
                    <div class="h-[500px] flex flex-col">
                      <h4 class="font-medium text-primary mb-2 text-sm flex-shrink-0">编辑内容</h4>
                      <textarea v-model="correctedText" class="w-full flex-grow border border-gray-300 rounded-md p-4 text-base focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary font-serif resize-none" placeholder="在此输入校对后的内容..."></textarea>
                    </div>
                  </div>
                </div>
              </div>

              <div class="border-b border-gray-200 mb-6">
                <nav aria-label="Tabs" class="-mb-px flex space-x-8">
                  <button @click="activeTab = 'history'" :class="['py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap', activeTab === 'history' ? 'border-primary text-primary' : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300']">历史背景</button>
                  <button @click="activeTab = 'culture'" :class="['py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap', activeTab === 'culture' ? 'border-primary text-primary' : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300']">文化意义</button>
                  <button @click="activeTab = 'figures'" :class="['py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap', activeTab === 'figures' ? 'border-primary text-primary' : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300']">相关人物</button>
                  <button @click="activeTab = 'reading'" :class="['py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap', activeTab === 'reading' ? 'border-primary text-primary' : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300']">延伸阅读</button>
                </nav>
              </div>

              <div class="grid md:grid-cols-3 gap-8">
                <div class="md:col-span-2">
                  <div v-show="activeTab === 'history'" class="prose max-w-none text-dark/90 leading-relaxed mb-6" v-html="renderMarkdown(sectionsHistory || (sectionsLoading ? '### 正在生成历史背景...\n- 请稍候' : ''))"></div>
                  <div v-show="activeTab === 'culture'" class="prose max-w-none text-dark/90 leading-relaxed mb-6" v-html="renderMarkdown(sectionsCulture || (sectionsLoading ? '### 正在生成文化意义...\n- 请稍候' : ''))"></div>
                  <div v-show="activeTab === 'figures'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                    <div v-if="sectionsLoading && (!sectionsFigures || !sectionsFigures.length)" class="text-sm text-dark/60">正在生成相关人物...</div>
                    <div v-for="p in sectionsFigures" :key="p.name" class="mb-3">
                      <div class="font-semibold">{{ p.name }} <span class="text-dark/60 text-xs">{{ p.role }}</span></div>
                      <div class="text-sm">{{ p.description }}</div>
                    </div>
                  </div>
                  <div v-show="activeTab === 'reading'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                    <div class="text-sm text-dark/60 mb-2">引用来源</div>
                    <div class="flex flex-wrap gap-2">
                      <span v-for="(s, i) in sectionsSources" :key="i" class="text-xs px-2 py-1 bg-secondary/30 text-primary rounded">{{ (s.snippet || '').slice(0, 32) }}</span>
                    </div>
                  </div>
                </div>
                <div class="space-y-6">
                  <div class="bg-light p-5 rounded-xl border border-gray-100">
                    <h4 class="text-lg font-semibold text-primary mb-4 flex items-center">
                      <i class="fas fa-history mr-2"></i>
                      相关时间线
                    </h4>
                    <div v-if="timeline && timeline.length > 0" class="space-y-4">
                      <div v-for="(item, index) in timeline" :key="index" class="relative pl-6 pb-4 last:pb-0">
                        <div class="absolute left-0 top-0 w-3 h-3 bg-primary rounded-full mt-1.5 -ml-1.5 border-3 border-white"></div>
                        <div class="absolute left-0 top-4 w-0.5 h-full bg-gray-200 -ml-0.25"></div>
                        <div class="text-sm">
                          <span class="font-semibold text-primary">{{ item.year }}</span>
                          <span class="ml-2 text-dark/80">{{ item.event }}</span>
                        </div>
                      </div>
                    </div>
                    <div v-else-if="sectionsLoading" class="text-sm text-dark/60 flex items-center">
                      <i class="fas fa-spinner fa-spin mr-2"></i>
                      生成中...
                    </div>
                    <div v-else class="text-sm text-dark/60 flex items-center">
                      <i class="fas fa-hourglass-half mr-2"></i>
                      暂无时间线数据
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <i class="fas fa-exclamation-circle text-6xl text-gray-300 mb-4"></i>
      <h2 class="text-2xl font-semibold text-gray-600 mb-4">碑文不存在</h2>
      <router-link to="/favorites" class="text-primary hover:underline">返回我的碑文</router-link>
    </div>
  </div>
</template>

<style scoped>
.bg-texture {
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3-3.134-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23d2b48c' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
}
.transition-custom { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.prose { color: inherit; }
.prose p { margin-bottom: 1em; }
</style>
