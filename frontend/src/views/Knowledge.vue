<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'
import { fetchKnowledgeHome, fetchKnowledgeList, fetchKnowledgeCategories, fetchKnowledgeDynasties } from '../api/knowledge'
import { postChat, streamChatFetch } from '../api/ai'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 响应式数据
const searchQuery = ref('')
const selectedCategory = ref('全部推荐')
const isRefreshing = ref(false)
const articles = ref([])
const categories = ref(['全部推荐'])
const dynasties = ref([])
const loading = ref(false)
const recommendationPage = ref(1)
const showPreferences = ref(false)
const showTagModal = ref(false)
const selectedTagInfo = ref(null)
const favorites = ref([])

// Mock Tag Library
const tagLibrary = {
  '唐代': { description: '中国历史上最强盛的朝代之一，书法艺术达到高峰，楷书、草书均有极大发展。', example: '颜真卿《多宝塔碑》' },
  '汉代': { description: '隶书发展的鼎盛时期，碑刻数量众多，风格多样。', example: '《张迁碑》、《曹全碑》' },
  '楷书': { description: '楷书也叫正楷、真书、正书。由隶书逐渐演变而来，更趋简化，横平竖直。', example: '欧阳询《九成宫醴泉铭》' },
  '行书': { description: '介于楷书和草书之间的一种字体，书写流畅，实用性强。', example: '王羲之《兰亭序》' },
  '草书': { description: '结构简省、笔画连绵。有章草、今草、狂草之分。', example: '怀素《自叙帖》' },
  '隶书': { description: '字形多呈宽扁，横画长而竖画短，讲究“蚕头燕尾”、“一波三折”。', example: '《曹全碑》' },
  '墓志铭': { description: '记录死者生平事迹的石刻，埋于墓中。', example: '《张黑女墓志》' },
  '碑刻': { description: '刻在石碑上的文字，多为记事、颂德。', example: '《颜氏家庙碑》' }
}

const preferences = ref({
  dynasties: [],
  categories: []
})

// AI对话相关数据
const chatQuestion = ref('')
const chatLoading = ref(false)
const chatMessages = ref([])
const chatConversationId = ref('')
const chatExpanded = ref(false)

// API配置
const baseUrl = ref(window.location.origin + '/api/v1')

// 获取知识库数据
const loadKnowledgeData = async () => {
  loading.value = true
  try {
    const homeData = await fetchKnowledgeHome(baseUrl.value, userStore.token || '')
    articles.value = homeData.featured || []
    
    // 更新分类和朝代数据
    const categoryData = await fetchKnowledgeCategories(baseUrl.value, userStore.token || '')
    const dynastyData = await fetchKnowledgeDynasties(baseUrl.value, userStore.token || '')
    
    // 处理分类数据
    const categoryNames = categoryData.map(cat => cat.name)
    const dynastyNames = dynastyData.map(dyn => dyn.name + '碑文')
    
    // 合并分类选项
    categories.value = ['全部推荐', ...categoryNames, ...dynastyNames]
    
    dynasties.value = dynastyData
  } catch (error) {
    console.error('加载知识库数据失败:', error)
    appStore.addNotification({
      type: 'error',
      message: '加载知识库数据失败',
      duration: 3000
    })
  } finally {
    loading.value = false
  }
}

// 过滤后的碑文
const filteredArticles = computed(() => {
  let filtered = articles.value

  // 按分类过滤 (单选)
  if (selectedCategory.value !== '全部推荐') {
    filtered = filtered.filter(article => {
      return article.dynasty?.includes(selectedCategory.value.replace('碑文', '')) ||
        article.category?.includes(selectedCategory.value)
    })
  }
  
  // 按偏好过滤 (多选)
  if (preferences.value.dynasties.length > 0 || preferences.value.categories.length > 0) {
    filtered = filtered.filter(article => {
      const matchDynasty = preferences.value.dynasties.length === 0 || 
        preferences.value.dynasties.some(d => article.dynasty?.includes(d))
      const matchCategory = preferences.value.categories.length === 0 || 
        preferences.value.categories.some(c => article.category?.includes(c))
      return matchDynasty && matchCategory
    })
  }

  // 按搜索词过滤
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.toLowerCase()
    filtered = filtered.filter(article => {
      return article.title?.toLowerCase().includes(keyword) ||
        article.author?.toLowerCase().includes(keyword) ||
        article.content?.toLowerCase().includes(keyword) ||
        article.description?.toLowerCase().includes(keyword)
    })
  }

  return filtered
})

// 换一批功能
const refreshRecommendations = async () => {
  isRefreshing.value = true
  recommendationPage.value += 1
  try {
    // 使用 fetchKnowledgeList 获取新的一页数据
    const data = await fetchKnowledgeList(baseUrl.value, userStore.token || '', {
      page: recommendationPage.value,
      size: 6 // 每次获取6条
    })
    
    if (data && (data.items || data.list)) {
      const newItems = data.items || data.list
      if (newItems.length > 0) {
        // 智能去重：过滤掉当前已存在的
        const currentIds = new Set(articles.value.map(a => a.id))
        const uniqueItems = newItems.filter(item => !currentIds.has(item.id))
        
        if (uniqueItems.length > 0) {
          articles.value = uniqueItems
        } else {
          // 如果去重后没有新数据，且页码已经很大，可能数据循环了，重置页码
          recommendationPage.value = 0
          const retryData = await fetchKnowledgeList(baseUrl.value, userStore.token || '', { page: 0, size: 6 })
          articles.value = retryData.items || retryData.list || []
        }
      } else {
         // 没有更多数据，回到第一页
         recommendationPage.value = 0
         const retryData = await fetchKnowledgeList(baseUrl.value, userStore.token || '', { page: 0, size: 6 })
         articles.value = retryData.items || retryData.list || []
      }
    }

    appStore.addNotification({
      type: 'success',
      message: '已刷新推荐内容',
      duration: 2000
    })
  } catch (error) {
    console.error('刷新推荐内容失败:', error)
    // 降级：如果列表接口失败，尝试重新加载首页数据
    try {
      await loadKnowledgeData()
    } catch(e) {}
  } finally {
    isRefreshing.value = false
  }
}

// 查看标签详情
const viewTagInfo = (tag) => {
  const info = tagLibrary[tag] || { description: '暂无详细描述', example: '暂无示例' }
  selectedTagInfo.value = { name: tag, ...info }
  showTagModal.value = true
}

// 获取推荐标签
const getRecommendTags = () => {
  // 从文章中提取推荐标签
  const tags = new Set()
  articles.value.forEach(article => {
    // 添加朝代作为标签
    if (article.dynasty) {
      tags.add(article.dynasty)
    }
    // 添加分类作为标签
    if (article.category) {
      tags.add(article.category)
    }
  })
  return Array.from(tags)
}

// 查看文章详情
const viewArticle = (id) => {
  router.push(`/knowledge/article/${id}`)
}

// 切换分类
const selectCategory = (category) => {
  selectedCategory.value = category
}

const escapeHtml = (str) => {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
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

const sendChatQuestion = async () => {
  const q = chatQuestion.value.trim()
  if (!q) return
  const baseUrl = window.location.origin
  const token = userStore.token || ''
  const userMsg = { id: Date.now() + '-u', role: 'user', content: q, status: 'success', references: [], created_at: new Date().toISOString() }
  chatMessages.value.push(userMsg)
  chatQuestion.value = ''
  const assistantMsg = { id: Date.now() + '-a', role: 'assistant', content: '', status: 'sending', references: [], created_at: new Date().toISOString() }
  chatMessages.value.push(assistantMsg)
  chatLoading.value = true
  try {
    await streamChatFetch({ baseUrl, token, recognitionId: 'rec_local', message: q, conversationId: chatConversationId.value, onEvent: (evt) => {
      if (!evt || !evt.event) return
      if (evt.event === 'status') {
        if (evt.data && evt.data.status === 'success') assistantMsg.status = 'success'
      } else if (evt.event === 'references') {
        assistantMsg.references = evt.data || []
      } else if (evt.event === 'delta') {
        if (evt.data && typeof evt.data.text === 'string') assistantMsg.content += evt.data.text
      }
    }})
  } catch (e) {
    try {
      const data = await postChat({ baseUrl, token, recognitionId: 'rec_local', message: q, conversationId: chatConversationId.value })
      chatConversationId.value = data.conversation_id || chatConversationId.value
      assistantMsg.content = (data.reply && data.reply.content) || ''
      assistantMsg.references = (data.reply && data.reply.sources) || []
      assistantMsg.status = 'success'
    } catch (err) {
      assistantMsg.status = 'failed'
      appStore.addNotification({ type: 'error', message: 'AI对话失败', duration: 3000 })
    }
  } finally {
    chatLoading.value = false
  }
}

// 收藏功能
const toggleFavorite = (article, event) => {
  event.stopPropagation()
  const index = favorites.value.indexOf(article.id)
  
  if (index > -1) {
    favorites.value = favorites.value.filter(id => id !== article.id)
    appStore.addNotification({ type: 'info', message: '已取消收藏', duration: 2000 })
  } else {
    favorites.value = [...favorites.value, article.id]
    appStore.addNotification({ type: 'success', message: '收藏成功', duration: 2000 })
  }
  
  localStorage.setItem('favorites', JSON.stringify(favorites.value))
}

// 检查是否已收藏
const isFavorited = (articleId) => {
  return favorites.value.includes(articleId)
}

// 保存偏好设置
const savePreferences = () => {
  localStorage.setItem('knowledge_preferences', JSON.stringify(preferences.value))
  showPreferences.value = false
  appStore.addNotification({ type: 'success', message: '偏好设置已保存', duration: 2000 })
}

onMounted(() => {
  userStore.initUser()
  loadKnowledgeData()
  
  // 加载收藏
  const storedFav = localStorage.getItem('favorites')
  if (storedFav) {
    try { favorites.value = JSON.parse(storedFav) } catch (e) { favorites.value = [] }
  }
  
  // 加载偏好
  const storedPref = localStorage.getItem('knowledge_preferences')
  if (storedPref) {
    try { preferences.value = JSON.parse(storedPref) } catch (e) {}
  }
})

// 监听搜索查询变化
watch(searchQuery, (newQuery) => {
  if (newQuery.trim()) {
    // 可以在这里添加防抖处理
    console.log('搜索:', newQuery)
  }
})
</script>

<template>
  <div class="py-12 md:py-16 bg-light bg-texture min-h-screen">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="mb-10">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 class="text-2xl md:text-3xl font-serif font-bold text-primary mb-2">
              碑文知识库
            </h1>
            <p class="text-dark/70">
              为您收录碑刻文字与相关资料，帮助您更方便地查阅与探索。
            </p>
          </div>
          <div class="mt-4 md:mt-0 flex space-x-3">
            <button @click="showPreferences = true"
              class="px-4 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center">
              <i class="fas fa-filter mr-2"></i>
              筛选
            </button>
            <router-link to="/favorites?tab=my-collections"
              class="px-4 py-2 bg-white border border-primary text-primary rounded-md font-medium hover:bg-primary/5 transition-custom flex items-center">
              <i class="fas fa-heart mr-2"></i>
              我的收藏
            </router-link>
          </div>
        </div>
      </div>

      <!-- 搜索区域 -->
      <div class="bg-white rounded-xl shadow-sm p-4 mb-4">
        <div class="flex flex-col md:flex-row gap-4">
          <!-- 搜索框 -->
          <div class="w-full md:w-auto flex items-center space-x-2">
            <div class="relative flex-grow md:flex-grow-0 md:w-64">
              <input v-model="searchQuery" type="text" placeholder="搜索碑文关键词..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-custom">
              <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            </div>
            <button
              class="px-4 py-2 bg-primary text-white rounded-full text-sm font-medium whitespace-nowrap transition-custom hover:bg-primary/90">
              <i class="fas fa-search mr-1"></i>
              搜索
            </button>
          </div>
        </div>
      </div>

      <!-- 推荐标签 -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-dark/70">推荐标签</h3>
          <button @click="showTagModal = true" class="text-xs text-primary hover:text-accent flex items-center">
            标签图谱 <i class="fas fa-book-open ml-1"></i>
          </button>
        </div>
        <div class="flex overflow-x-auto pb-2 gap-2 scrollbar-hide">
          <!-- 全部推荐 -->
          <button
            @click="selectCategory('全部推荐')"
            :class="selectedCategory === '全部推荐'
              ? 'bg-primary text-white'
              : 'bg-white border border-primary text-primary hover:bg-primary/5'"
            class="px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-custom flex-shrink-0">
            全部推荐
          </button>
          <!-- 动态生成的推荐标签 -->
          <button
            v-for="tag in getRecommendTags()"
            :key="tag"
            @click="selectCategory(tag)"
            :class="selectedCategory === tag
              ? 'bg-primary text-white'
              : 'bg-white border border-primary text-primary hover:bg-primary/5'"
            class="px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-custom flex-shrink-0">
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- 分类筛选 -->
      <div class="bg-white rounded-xl shadow-sm p-4 mb-4">
        <div class="flex flex-wrap gap-2">
          <button v-for="category in categories.filter(cat => cat !== '全部推荐')" :key="category" @click="selectCategory(category)" :class="selectedCategory === category
            ? 'bg-primary text-white'
            : 'bg-light text-dark/70 hover:bg-secondary/30'"
            class="px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-custom">
            {{ category }}
          </button>
        </div>
      </div>

      <!-- 热门碑刻推荐 -->
      <div class="mb-16">
        <!-- 加载状态 -->
        <div v-if="loading" class="flex justify-center items-center py-20">
          <div class="text-center">
            <i class="fas fa-spinner fa-spin text-4xl text-primary mb-4"></i>
            <p class="text-dark/60">加载中...</p>
          </div>
        </div>
        
        <!-- 数据为空状态 -->
        <div v-else-if="filteredArticles.length === 0" class="bg-white rounded-xl shadow-sm p-8 text-center">
          <i class="fas fa-search text-4xl text-gray-300 mb-4"></i>
          <h3 class="text-xl font-semibold text-gray-600 mb-2">未找到相关内容</h3>
          <p class="text-gray-500">请尝试调整搜索条件或分类</p>
        </div>
        
        <!-- 文章列表 -->
        <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="article in filteredArticles" :key="article.id"
            class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-custom group cursor-pointer"
            @click="viewArticle(article.id)">
            <div class="relative">
              <img :src="article.cover_image || 'https://via.placeholder.com/400x200?text=No+Image'" :alt="article.title"
                class="w-full h-48 object-cover group-hover:scale-105 transition-custom duration-500">
              <div class="absolute top-3 left-3 bg-primary text-white text-xs font-medium px-2 py-1 rounded">
                {{ article.dynasty || '未知朝代' }}
              </div>
              <div
                class="absolute top-3 right-3 bg-accent text-white text-xs font-medium px-2 py-1 rounded-full flex items-center">
                <i class="fas fa-eye mr-1"></i>
                {{ article.views ? Math.floor(article.views / 1000) + 'k' : '0' }}
              </div>
            </div>
            <div class="p-5">
              <div class="flex justify-between items-start mb-3">
                <h3 class="font-semibold text-xl text-primary group-hover:text-accent transition-custom">
                  {{ article.title }}
                </h3>
                <button @click="toggleFavorite(article, $event)"
                  :class="isFavorited(article.id) ? 'text-red-500' : 'text-dark/40 hover:text-red-500'"
                  class="transition-custom">
                  <i :class="isFavorited(article.id) ? 'fas fa-heart' : 'far fa-heart'"></i>
                </button>
              </div>
              <p class="text-dark/70 text-sm mb-4 line-clamp-2">
                {{ article.excerpt || article.description || '暂无描述' }}
              </p>
              <div class="flex flex-wrap gap-2 mb-4">
                <span class="bg-secondary/30 text-primary text-xs px-2 py-1 rounded-full">
                  {{ article.category || '未分类' }}
                </span>
                <span v-if="article.author" class="bg-secondary/30 text-primary text-xs px-2 py-1 rounded-full">
                  {{ article.author }}
                </span>
              </div>
              <div class="flex justify-between items-center pt-3 border-t border-gray-100">
                <div class="flex items-center text-sm text-dark/50">
                  <i class="fas fa-history mr-1"></i>
                  <span>最近更新: {{ article.updated_at ? new Date(article.updated_at).toLocaleDateString() : '未知' }}</span>
                </div>
                <a class="text-primary font-medium text-sm hover:text-accent transition-custom">
                  查看详情 <i class="fas fa-arrow-right ml-1 text-xs"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最新收录碑刻 -->
      <div>
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl md:text-2xl font-serif font-bold text-primary flex items-center">
            <i class="fas fa-clock mr-2 text-accent"></i>
            最新收录碑刻
          </h2>
          <a class="text-primary text-sm hover:text-accent transition-custom flex items-center">
            查看全部 <i class="fas fa-angle-right ml-1"></i>
          </a>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-5">
          <div class="space-y-5">
            <div v-for="article in filteredArticles.slice(0, 2)" :key="article.id"
              class="flex flex-col md:flex-row gap-4 pb-5 border-b border-gray-100 last:border-0">
              <div class="md:w-1/4">
                <div class="relative rounded-lg overflow-hidden h-40 md:h-auto">
                  <img :src="article.cover_image || 'https://via.placeholder.com/400x200?text=No+Image'" :alt="article.title"
                    class="w-full h-full object-cover hover:scale-105 transition-custom duration-500">
                  <div class="absolute top-2 left-2 bg-accent text-white text-xs font-medium px-2 py-1 rounded">
                    新收录
                  </div>
                </div>
              </div>
              <div class="md:w-3/4">
                <div class="flex justify-between items-start mb-2">
                  <h3 class="font-semibold text-xl text-primary hover:text-accent transition-custom">
                    {{ article.title }}
                  </h3>
                  <span class="text-dark/50 text-sm">{{ article.metadata?.publish_date ? new Date(article.metadata.publish_date).getFullYear() : '未知年份' }}</span>
                </div>
                <p class="text-dark/70 mb-3 line-clamp-2 md:line-clamp-1">
                  {{ article.excerpt || article.description || '暂无描述' }}
                </p>
                <div class="flex flex-wrap gap-2 mb-4">
                  <span v-if="article.category" class="bg-secondary/30 text-primary text-xs px-2 py-1 rounded-full">
                    {{ article.category }}
                  </span>
                  <span v-if="article.dynasty" class="bg-secondary/30 text-primary text-xs px-2 py-1 rounded-full">
                    {{ article.dynasty }}
                  </span>
                  <span v-if="article.author" class="bg-secondary/30 text-primary text-xs px-2 py-1 rounded-full">
                    {{ article.author }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <div class="flex items-center text-dark/50 text-sm">
                    <span class="flex items-center mr-4">
                      <i class="fas fa-eye mr-1"></i>
                      {{ article.views || 0 }}
                    </span>
                    <span class="flex items-center">
                      <i class="fas fa-heart mr-1"></i>
                      {{ article.stats?.likes || 0 }}
                    </span>
                  </div>
                  <button @click="viewArticle(article.id)"
                    class="px-4 py-2 bg-primary text-white rounded-md text-sm font-medium hover:bg-primary/90 transition-custom">
                    查看详情
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI对话组件 -->
    <div class="fixed bottom-6 right-6 z-50">
      <!-- 展开/收起按钮 -->
      <button
        v-if="!chatExpanded"
        @click="chatExpanded = true"
        class="bg-primary text-white rounded-full w-14 h-14 shadow-lg flex items-center justify-center hover:bg-primary/90 transition-custom"
      >
        <i class="fas fa-robot text-xl"></i>
      </button>

      <!-- 聊天窗口 -->
      <div
        v-else
        class="bg-white rounded-xl shadow-xl w-80 max-w-full max-h-[80vh] flex flex-col transition-custom"
      >
        <!-- 聊天头部 -->
        <div class="bg-primary text-white p-4 rounded-t-xl flex justify-between items-center">
          <div class="flex items-center">
            <i class="fas fa-robot mr-2"></i>
            <h3 class="font-semibold">碑文知识助手</h3>
          </div>
          <button @click="chatExpanded = false" class="text-white hover:text-gray-200 transition-custom">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <!-- 聊天消息 -->
        <div class="flex-grow p-4 overflow-y-auto space-y-4">
          <div
            v-for="message in chatMessages"
            :key="message.id"
            :class="message.role === 'user' ? 'text-right' : 'text-left'"
          >
            <div
              :class="message.role === 'user' 
                ? 'inline-block px-4 py-2 rounded-lg bg-primary text-white' 
                : 'inline-block px-4 py-2 rounded-lg bg-light border border-gray-200 text-dark'"
            >
              <div v-if="message.role === 'user'" class="text-sm whitespace-pre-line">{{ message.content }}</div>
              <div v-else class="prose text-sm" v-html="renderMarkdown(message.content)"></div>
              <i v-if="message.role === 'assistant' && message.status === 'sending'" class="fas fa-spinner fa-spin ml-2 text-primary"></i>
            </div>
            <div v-if="message.role === 'assistant' && message.references && message.references.length" class="mt-1">
              <span v-for="(s, i) in message.references" :key="i" class="inline-block mr-1 mb-1 text-xs px-2 py-1 bg-secondary/30 text-primary rounded">{{ (s.snippet || '').slice(0, 24) }}</span>
            </div>
          </div>
        </div>

        <!-- 聊天输入 -->
        <div class="p-4 border-t border-gray-200">
          <div class="flex gap-2">
            <input
              v-model="chatQuestion"
              type="text"
              placeholder="请输入您的问题..."
              class="flex-grow px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-custom"
              @keyup.enter="sendChatQuestion"
            >
            <button
              @click="sendChatQuestion"
              :disabled="chatLoading"
              class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-custom disabled:opacity-50"
            >
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
          <div v-if="chatLoading" class="mt-2 text-xs text-gray-500 flex items-center justify-center">
            <i class="fas fa-spinner fa-spin mr-1"></i>
            正在生成...
          </div>
        </div>
      </div>
    </div>

    <!-- 偏好设置弹窗 -->
    <div v-if="showPreferences" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg w-full max-w-lg max-h-[90vh] flex flex-col animate-fade-in-up">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 class="text-lg font-medium text-primary">筛选</h3>
          <button @click="showPreferences = false" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="px-6 py-4 flex-grow overflow-y-auto">
          <div class="mb-6">
            <h4 class="font-medium text-dark mb-3">朝代偏好</h4>
            <div class="flex flex-wrap gap-2">
              <label v-for="dyn in dynasties" :key="dyn.id" class="inline-flex items-center px-3 py-2 rounded-full border cursor-pointer transition-custom"
                :class="preferences.dynasties.includes(dyn.name) ? 'bg-primary/10 border-primary text-primary' : 'border-gray-200 hover:bg-gray-50'">
                <input type="checkbox" :value="dyn.name" v-model="preferences.dynasties" class="hidden">
                <span>{{ dyn.name }}</span>
              </label>
            </div>
          </div>
          <div>
            <h4 class="font-medium text-dark mb-3">分类偏好</h4>
            <div class="flex flex-wrap gap-2">
              <label v-for="cat in categories.filter(c => c !== '全部推荐' && !c.includes('碑文'))" :key="cat" class="inline-flex items-center px-3 py-2 rounded-full border cursor-pointer transition-custom"
                :class="preferences.categories.includes(cat) ? 'bg-primary/10 border-primary text-primary' : 'border-gray-200 hover:bg-gray-50'">
                <input type="checkbox" :value="cat" v-model="preferences.categories" class="hidden">
                <span>{{ cat }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
          <button @click="preferences = { dynasties: [], categories: [] }" class="px-4 py-2 text-dark/70 hover:text-dark">重置</button>
          <button @click="savePreferences" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90">保存设置</button>
        </div>
      </div>
    </div>

    <!-- 标签详情弹窗 -->
    <div v-if="showTagModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col animate-fade-in-up">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 class="text-lg font-medium text-primary">{{ selectedTagInfo ? selectedTagInfo.name : '标签图谱' }}</h3>
          <button @click="showTagModal = false; selectedTagInfo = null" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="px-6 py-4 flex-grow overflow-y-auto">
          <div v-if="selectedTagInfo">
            <div class="mb-4">
              <h4 class="text-sm font-semibold text-gray-500 uppercase mb-1">描述</h4>
              <p class="text-dark/80">{{ selectedTagInfo.description }}</p>
            </div>
            <div class="mb-6">
              <h4 class="text-sm font-semibold text-gray-500 uppercase mb-1">典型示例</h4>
              <p class="text-primary">{{ selectedTagInfo.example }}</p>
            </div>
            <button @click="selectCategory(selectedTagInfo.name); showTagModal = false; selectedTagInfo = null" 
              class="w-full py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-custom">
              查看相关碑文
            </button>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(info, name) in tagLibrary" :key="name" 
              class="p-4 border border-gray-100 rounded-lg hover:shadow-md cursor-pointer transition-custom"
              @click="selectedTagInfo = { name, ...info }">
              <div class="flex justify-between items-center mb-2">
                <h4 class="font-semibold text-primary">{{ name }}</h4>
                <i class="fas fa-chevron-right text-gray-300 text-xs"></i>
              </div>
              <p class="text-sm text-dark/60 line-clamp-2">{{ info.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bg-texture {
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23d2b48c' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
}
</style>
