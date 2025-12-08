<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'
import { fetchArticleDetail, incrementArticleViews } from '../api/knowledge'
import { postChat, streamChatFetch, postInterpretationSections } from '../api/ai'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 响应式数据
const article = ref(null)
const loading = ref(true)
const isFavorited = ref(false)
const activeTab = ref('history') // history, culture, figures, reading
const chatQuestion = ref('')
const chatLoading = ref(false)
const chatMessages = ref([])
const chatConversationId = ref('')
const sectionsHistory = ref(null)
const sectionsCulture = ref('')
const sectionsFigures = ref([])
const sectionsSources = ref([])
const sectionsLoading = ref(false)
const timeline = ref([])
const recommendedReading = ref([])


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
      else { inCode = false; html += `<pre class=\"code\"><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>`; codeBuf = [] }
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
  if (inCode) { html += `<pre class=\"code\"><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>` }
  return html
}

// 计算属性
const articleId = computed(() => parseInt(route.params.id, 10))

// 从Markdown内容中提取原文
const extractOriginalText = (content) => {
  if (!content) return ''
  
  // 匹配## 原文到下一个##之间的内容
  const originalRegex = /## 原文\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(originalRegex)
  
  if (match && match[1]) {
    return renderMarkdown(match[1].trim())
  }
  
  return '暂无原文数据'
}

// 从Markdown内容中提取译文
const extractTranslationText = (content) => {
  if (!content) return ''
  
  // 匹配## 翻译或## 译文到下一个##之间的内容
  const translationRegex = /## (翻译|译文)\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(translationRegex)
  
  if (match && match[2]) {
    return renderMarkdown(match[2].trim())
  }
  
  return '暂无译文数据'
}

// 从Markdown内容中提取历史背景
const extractHistoryBackground = (content) => {
  if (!content) return ''
  
  // 匹配## 历史背景到下一个##之间的内容
  const historyRegex = /## 历史背景\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(historyRegex)
  
  if (match && match[1]) {
    return match[1].trim()
  }
  
  return ''
}

// 从Markdown内容中提取文化意义
const extractCulturalSignificance = (content) => {
  if (!content) return ''
  
  // 匹配## 文化意义到下一个##之间的内容
  const cultureRegex = /## 文化意义\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(cultureRegex)
  
  if (match && match[1]) {
    return match[1].trim()
  }
  
  return ''
}

// 从Markdown内容中提取相关人物
const extractRelatedFigures = (content) => {
  if (!content) return ''
  
  // 匹配## 相关人物到下一个##之间的内容
  const figuresRegex = /## 相关人物\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(figuresRegex)
  
  if (match && match[1]) {
    return match[1].trim()
  }
  
  return ''
}

// 从Markdown内容中提取延伸阅读
const extractFurtherReading = (content) => {
  if (!content) return ''
  
  // 匹配## 延伸阅读或## 相关时间线到下一个##之间的内容
  const readingRegex = /## (延伸阅读|相关阅读|参考资料)\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(readingRegex)
  
  if (match && match[2]) {
    return match[2].trim()
  }
  
  return ''
}

// 从Markdown内容中提取推荐阅读
const extractRecommendedReading = (content) => {
  if (!content) return []
  
  // 匹配## 延伸阅读或## 相关阅读或## 参考资料到下一个##之间的内容
  const readingRegex = /## (延伸阅读|相关阅读|参考资料)\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(readingRegex)
  
  if (match && match[2]) {
    const readingContent = match[2].trim()
    const readingItems = []
    
    // 匹配推荐阅读条目，格式：- [标题](链接) 或 - 标题
    const itemRegex = /-\s*(?:\[(.*?)\]\((.*?)\)|(.*?))\n/g
    let itemMatch
    
    while ((itemMatch = itemRegex.exec(readingContent + '\n')) !== null) {
      const title = itemMatch[1] || itemMatch[3]
      const url = itemMatch[2] || ''
      if (title) {
        readingItems.push({ title: title.trim(), url: url.trim() })
      }
    }
    
    return readingItems
  }
  
  return []
}



// 从Markdown内容中提取时间线
const extractTimeline = (content) => {
  if (!content) return []
  
  // 匹配## 相关时间线到下一个##之间的内容
  const timelineRegex = /## 相关时间线\s*([\s\S]*?)(?=## |$)/i
  const match = content.match(timelineRegex)
  
  if (match && match[1]) {
    const timelineContent = match[1].trim()
    const timelineItems = []
    
    // 匹配时间线条目，格式：- 年份：事件
    const itemRegex = /-\s*(\d{4}年?)\s*[:：]\s*(.*?)\n/g
    let itemMatch
    
    while ((itemMatch = itemRegex.exec(timelineContent + '\n')) !== null) {
      const year = itemMatch[1].trim()
      const event = itemMatch[2].trim()
      if (year && event) {
        timelineItems.push({ year, event })
      }
    }
    
    return timelineItems
  }
  
  return []
}

// 加载碑文
const loadArticle = async () => {
  try {
    loading.value = true
    
    // 重置AI阐释状态，确保切换文章时重新生成阐释
    sectionsHistory.value = null
    sectionsCulture.value = ''
    sectionsFigures.value = []
    sectionsSources.value = []
    timeline.value = []
    recommendedReading.value = []
    
    // API配置
    const baseUrl = 'http://localhost:8080'
    const token = userStore.token || ''
    
    // 调用真实API获取文章详情
    const articleData = await fetchArticleDetail(baseUrl, token, articleId.value)
    
    if (!articleData) {
      appStore.addNotification({
        type: 'error',
        message: '碑文不存在',
        duration: 3000
      })
      router.push('/knowledge')
      return
    }
    
    article.value = articleData
    
    // 碑刻年代直接从数据库获取，不需要从内容中提取
    // extractedYear.value = articleData.year || extractYear(articleData.content) || '未知年代'
    
    // 检查是否已收藏
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
    isFavorited.value = favorites.includes(articleId.value)
    
    // 增加文章查看次数
    try {
      await incrementArticleViews(baseUrl, token, articleId.value)
    } catch (error) {
      console.error('增加查看次数失败:', error)
    }

  } catch (error) {
    console.error('加载碑文失败:', error)
    appStore.addNotification({
      type: 'error',
      message: '加载碑文失败',
      duration: 3000
    })
  } finally {
    loading.value = false
  }
}

// 收藏/取消收藏
const toggleFavorite = () => {
  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')

  if (isFavorited.value) {
    const index = favorites.indexOf(articleId.value)
    if (index > -1) {
      favorites.splice(index, 1)
    }
    isFavorited.value = false
    appStore.addNotification({
      type: 'info',
      message: '已取消收藏',
      duration: 2000
    })
  } else {
    favorites.push(articleId.value)
    isFavorited.value = true
    appStore.addNotification({
      type: 'success',
      message: '收藏成功',
      duration: 2000
    })
  }

  localStorage.setItem('favorites', JSON.stringify(favorites))
}

// 分享
const shareArticle = () => {
  if (navigator.share) {
    navigator.share({
      title: article.value.title,
      text: article.value.description,
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href)
    appStore.addNotification({
      type: 'success',
      message: '链接已复制到剪贴板',
      duration: 2000
    })
  }
}

const sendChatQuestion = async () => {
  const q = chatQuestion.value.trim()
  if (!q) return
  const baseUrl = 'http://localhost:8080'
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

const fetchArticleInterpretation = async () => {
  if (sectionsHistory.value === null && article.value) {
    const baseUrl = 'http://localhost:8080'
    const token = userStore.token || ''
    // 发送完整的碑文内容给AI，包括标题、朝代、年份和完整文本
    const text = `${article.value.title} ${article.value.dynasty || ''} ${article.value.year || ''}\n\n${article.value.content || ''}`.trim()
    try {
      sectionsLoading.value = true
      const data = await postInterpretationSections({ baseUrl, token, text, inscriptionId: article.value.id })
      const s = data.sections || {}
      sectionsHistory.value = s.history_markdown || ''
      sectionsCulture.value = s.culture_markdown || ''
      sectionsFigures.value = s.figures || []
      sectionsSources.value = data.sources || []
      // 覆盖右侧时间线
      // 将简化的 timeline 映射为 {year,event}
      // 如果包含 title/description，则合并
      if (Array.isArray(s.timeline)) {
        timeline.value = s.timeline.map(t => ({ year: t.year, event: (t.title ? t.title + '：' : '') + (t.description || '') }))
      } else {
        // 如果AI没有返回时间线，尝试从Markdown内容中提取
        timeline.value = extractTimeline(article.value.content)
      }
      
      // 处理推荐阅读
      if (Array.isArray(s.recommended_reading)) {
        recommendedReading.value = s.recommended_reading
      } else {
        // 如果AI没有返回推荐阅读，尝试从Markdown内容中提取
        recommendedReading.value = extractRecommendedReading(article.value.content)
      }
    } catch (e) {
      appStore.addNotification({ type: 'error', message: 'AI阐释生成失败', duration: 3000 })
      // 如果AI调用失败，尝试从Markdown内容中提取
      timeline.value = extractTimeline(article.value.content)
      recommendedReading.value = extractRecommendedReading(article.value.content)
    } finally {
      sectionsLoading.value = false
    }
  }
}

// 监听路由变化，重新加载文章并滚动到顶部
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadArticle()
    // 滚动到页面顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
})

// 生命周期钩子
onMounted(() => {
  userStore.initUser()
  loadArticle()
})

// 监听article变化，当article加载完成后调用AI生成阐释
watch(article, (newArticle) => {
  if (newArticle && sectionsHistory.value === null) {
    fetchArticleInterpretation()
  }
}, { deep: true })
</script>

<template>
  <div class="min-h-screen bg-light bg-texture text-dark font-sans">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="text-center">
        <i class="fas fa-spinner fa-spin text-4xl text-primary mb-4"></i>
        <p class="text-dark/60">加载中...</p>
      </div>
    </div>

    <!-- 碑文详情页面 -->
    <div v-else-if="article" class="py-8 md:py-12" id="inscription-detail-page">
      <!-- 面包屑导航 -->
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 mb-6">
        <nav aria-label="面包屑" class="text-sm text-dark/60">
          <ol class="flex flex-wrap items-center">
            <li><router-link to="/knowledge" class="hover:text-primary transition-custom">碑文知识库</router-link></li>
            <li class="mx-2"><i class="fas fa-angle-right text-xs"></i></li>
            <li><a href="#" class="hover:text-primary transition-custom">唐代碑文</a></li>
            <li class="mx-2"><i class="fas fa-angle-right text-xs"></i></li>
            <li class="text-primary">{{ article.title }}</li>
          </ol>
        </nav>
      </div>

      <!-- 标题区域 -->
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 mb-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-4">
          <div>
            <div class="flex items-center space-x-3 mb-3">
              <h1 class="text-3xl md:text-4xl font-serif font-bold text-primary">{{ article.title }}</h1>
              <span class="bg-primary/10 text-primary text-sm px-3 py-1 rounded-full font-medium">{{ article.dynasty || '未知朝代' }}名碑</span>
            </div>
            <div class="flex flex-wrap items-center text-dark/60 space-x-4 text-sm">
              <div class="flex items-center">
                <i class="fas fa-calendar-alt mr-1.5"></i>
                <span>{{ article.metadata?.publish_date ? new Date(article.metadata.publish_date).toLocaleDateString() : '未知日期' }}</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-pen-fancy mr-1.5"></i>
                <span>{{ article.author || '未知作者' }} 撰文</span>
              </div>
              <div class="flex items-center" v-if="article.metadata?.category">
                <i class="fas fa-tag mr-1.5"></i>
                <span>{{ article.metadata.category }}</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-eye mr-1.5"></i>
                <span>{{ article.stats?.views || 0 }} 次查看</span>
              </div>
            </div>
          </div>
          <div class="flex space-x-3 mt-4 md:mt-0">
            <button class="px-4 py-2 bg-white border border-gray-300 rounded-md text-dark/70 hover:bg-gray-50 transition-custom flex items-center">
              <i class="fas fa-download mr-2"></i>
              保存
            </button>
            <button @click="toggleFavorite" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-dark/70 hover:bg-gray-50 transition-custom flex items-center">
              <i :class="isFavorited ? 'fas' : 'far'" class="fa-bookmark mr-2"></i>
              收藏
            </button>
            <button @click="shareArticle" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-dark/70 hover:bg-gray-50 transition-custom flex items-center">
              <i class="far fa-share-square mr-2"></i>
              分享
            </button>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <span class="bg-secondary/30 text-primary text-xs px-3 py-1 rounded-full">欧阳询</span>
          <span class="bg-secondary/30 text-primary text-xs px-3 py-1 rounded-full">楷书</span>
          <span class="bg-secondary/30 text-primary text-xs px-3 py-1 rounded-full">{{ article.dynasty }}名碑</span>
          <span class="bg-secondary/30 text-primary text-xs px-3 py-1 rounded-full">皇家碑刻</span>
          <span class="bg-secondary/30 text-primary text-xs px-3 py-1 rounded-full">书法艺术</span>
        </div>
      </div>

      <!-- 碑刻图片与原文 -->
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 mb-12">
        <div class="grid lg:grid-cols-3 gap-8">
          <!-- 碑刻图片区域 -->
          <div class="lg:col-span-1">
            <div class="bg-white rounded-xl shadow-sm overflow-hidden sticky top-24">
              <div class="relative">
                <img :alt="article.title" :src="article.cover_image || 'https://via.placeholder.com/400x600?text=No+Image'" class="w-full h-auto object-cover">
                <div class="absolute top-3 right-3 bg-white/90 text-primary rounded-full px-3 py-1 text-sm font-medium flex items-center">
                  <i class="fas fa-eye mr-1.5"></i>
                  <span>{{ article.stats?.views || 0 }} 次查看</span>
                </div>
              </div>
              <div class="p-5">
                <h3 class="text-lg font-semibold mb-3">碑刻信息</h3>
                <ul class="space-y-3 text-sm">
                    <li class="flex justify-between">
                      <span class="text-dark/60">碑刻年代</span>
                      <span class="font-medium">{{ article.year || article.dynasty || '未知年代' }}</span>
                    </li>
                    <li class="flex justify-between">
                      <span class="text-dark/60">文章作者</span>
                      <span class="font-medium">{{ article.author || '未知' }}</span>
                    </li>
                    <li class="flex justify-between">
                      <span class="text-dark/60">创建时间</span>
                      <span class="font-medium">{{ article.created_at ? new Date(article.created_at).toLocaleDateString() : '未知' }}</span>
                    </li>
                    <li class="flex justify-between">
                      <span class="text-dark/60">更新时间</span>
                      <span class="font-medium">{{ article.updated_at ? new Date(article.updated_at).toLocaleDateString() : '未知' }}</span>
                    </li>
                    <li class="flex justify-between">
                      <span class="text-dark/60">阅读时长</span>
                      <span class="font-medium">{{ article.metadata?.read_time || 1 }} 分钟</span>
                    </li>
                    <li class="flex justify-between">
                      <span class="text-dark/60">字数统计</span>
                      <span class="font-medium">{{ article.metadata?.word_count || 0 }} 字</span>
                    </li>
                  </ul>
                <div class="mt-5 pt-5 border-t border-gray-100">
                  <button class="w-full py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-custom flex items-center justify-center">
                    <i class="fas fa-search-plus mr-2"></i>
                    查看高清碑刻
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 碑文原文区域 -->
          <div class="lg:col-span-2">
            <div class="bg-white rounded-xl shadow-sm p-6 md:p-8 mb-8">
              <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-serif font-bold text-primary">碑文阐释</h2>
                <div class="flex space-x-2">
                  <button class="px-3 py-1.5 bg-secondary/30 text-primary rounded-md text-sm hover:bg-secondary/50 transition-custom">
                    <br>
                  </button>
                  <button class="px-3 py-1.5 bg-secondary/30 text-primary rounded-md text-sm hover:bg-secondary/50 transition-custom">
                  </button>
                </div>
              </div>

              <!-- 原文与译文对照 -->
              <div class="mb-6 border border-gray-200 rounded-lg overflow-hidden">
                <div class="bg-gray-50 border-b border-gray-200 px-4 py-2 flex justify-between">
                  <h4 class="font-medium text-dark">原文</h4>
                  <h4 class="font-medium text-dark">现代文译文</h4>
                </div>
                <div class="flex">
                  <div class="w-1/2 p-4 border-r border-gray-200 bg-white/50 text-sm leading-relaxed overflow-y-auto h-48">
                    <div v-if="article.content" v-html="extractOriginalText(article.content)"></div>
                    <div v-else>暂无原文数据</div>
                  </div>
                  <div class="w-1/2 p-4 bg-white/50 text-sm leading-relaxed overflow-y-auto h-48">
                    <div v-if="article.content" v-html="extractTranslationText(article.content)"></div>
                    <div v-else>暂无译文数据</div>
                  </div>
                </div>
              </div>

              <!-- 阐释标签页 -->
              <div class="border-b border-gray-200 mb-6">
                <nav aria-label="Tabs" class="-mb-px flex space-x-8">
                  <button @click="activeTab = 'history'" :class="[
                    'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
                    activeTab === 'history'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
                  ]">
                    历史背景
                  </button>
                  <button @click="activeTab = 'culture'" :class="[
                    'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
                    activeTab === 'culture'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
                  ]">
                    文化意义
                  </button>
                  <button @click="activeTab = 'figures'" :class="[
                    'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
                    activeTab === 'figures'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
                  ]">
                    相关人物
                  </button>
                  <button @click="activeTab = 'reading'" :class="[
                    'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
                    activeTab === 'reading'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
                  ]">
                    延伸阅读
                  </button>
                </nav>
              </div>

              <!-- 阐释内容 -->
              <div class="grid md:grid-cols-3 gap-8">
                <!-- 左侧：主要阐释内容 -->
                <div class="md:col-span-2">
                  <h3 class="text-2xl font-serif font-semibold text-primary mb-4">{{ article.title }}历史背景分析</h3>
                  
                  <!-- 历史背景内容 -->
                  <div v-show="activeTab === 'history'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                    <div v-if="article.content" v-html="renderMarkdown(extractHistoryBackground(article.content) || '### 暂无历史背景数据')"></div>
                    <div v-else>暂无历史背景数据</div>
                  </div>

                  <!-- 文化意义内容 -->
                  <div v-show="activeTab === 'culture'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                    <div v-if="article.content" v-html="renderMarkdown(extractCulturalSignificance(article.content) || '### 暂无文化意义数据')"></div>
                    <div v-else>暂无文化意义数据</div>
                  </div>

                  <!-- 相关人物内容 -->
                  <div v-show="activeTab === 'figures'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                    <div v-if="article.content" v-html="renderMarkdown(extractRelatedFigures(article.content) || '### 暂无相关人物数据')"></div>
                    <div v-else>暂无相关人物数据</div>
                  </div>

                  <!-- 延伸阅读内容 -->
                  <div v-show="activeTab === 'reading'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                    <div v-if="article.content" v-html="renderMarkdown(extractFurtherReading(article.content) || '### 暂无延伸阅读数据')"></div>
                    <div v-else>暂无延伸阅读数据</div>
                  </div>

                  <!-- AI对话入口 -->
                  <div class="bg-secondary/30 p-4 rounded-lg border border-secondary">
                    <div class="flex items-start">
                      <div class="flex-shrink-0 mr-3">
                        <i class="fas fa-robot text-primary text-xl"></i>
                      </div>
                      <div class="flex-grow">
                        <div class="space-y-3 mb-3 max-h-80 overflow-auto">
                          <div v-for="m in chatMessages" :key="m.id" :class="m.role === 'user' ? 'text-right' : 'text-left'">
                            <div :class="m.role === 'user' ? 'inline-block px-3 py-2 rounded-lg bg-primary text-white' : 'inline-block px-3 py-2 rounded-lg bg-white border border-gray-200 text-dark'">
                              <span v-if="m.role === 'user'" class="whitespace-pre-line text-sm">{{ m.content }}</span>
                              <div v-else class="prose text-sm" v-html="renderMarkdown(m.content)"></div>
                              <i v-if="m.role === 'assistant' && m.status === 'sending'" class="fas fa-spinner fa-spin ml-2 text-primary"></i>
                            </div>
                            <div v-if="m.role === 'assistant' && m.references && m.references.length" class="mt-1">
                              <span v-for="(s, i) in m.references" :key="i" class="inline-block mr-1 mb-1 text-xs px-2 py-1 bg-secondary/30 text-primary rounded">{{ (s.snippet || '').slice(0, 24) }}</span>
                            </div>
                          </div>
                        </div>
                        <div class="flex">
                          <input v-model="chatQuestion" class="flex-grow px-4 py-2 rounded-l-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" placeholder="请输入您的问题..." type="text" @keyup.enter="sendChatQuestion">
                          <button @click="sendChatQuestion" class="bg-primary text-white px-4 py-2 rounded-r-md hover:bg-primary/90 transition-custom" :disabled="chatLoading">
                            <i class="fas fa-paper-plane"></i>
                          </button>
                        </div>
                        <div v-if="chatLoading" class="mt-3 text-sm text-dark/60">正在生成...</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 右侧：相关信息 -->
                <div class="space-y-6">
                  <!-- 时间线 -->
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

                  <!-- 相关人物 -->
                  <div class="bg-light p-5 rounded-xl border border-gray-100">
                    <h4 class="text-lg font-semibold text-primary mb-4 flex items-center">
                      <i class="fas fa-users mr-2"></i>
                      相关人物
                    </h4>
                    <!-- AI生成的相关人物 -->
                    <div v-if="sectionsFigures && sectionsFigures.length" class="space-y-3">
                      <div v-for="p in sectionsFigures" :key="p.name" class="flex items-center p-2 hover:bg-white rounded-md transition-custom">
                        <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mr-3">
                          <i class="fas fa-user text-primary"></i>
                        </div>
                        <div>
                          <p class="font-medium text-dark">{{ p.name }}</p>
                          <p class="text-xs text-dark/60">{{ p.role }}</p>
                          <p v-if="p.description" class="text-xs text-dark/60 mt-1">{{ p.description }}</p>
                        </div>
                      </div>
                    </div>
                    <!-- 从文章内容中提取的相关人物 -->
                    <div v-else-if="article.content && extractRelatedFigures(article.content)" class="prose max-w-none text-dark/90 text-sm">
                      <div v-html="renderMarkdown(extractRelatedFigures(article.content))"></div>
                    </div>
                    <!-- 无数据状态 -->
                    <div v-else class="text-sm text-dark/60">暂无人物信息，稍后重试或完善文本。</div>
                  </div>

                  <!-- 推荐阅读 -->
                  <div class="bg-light p-5 rounded-xl border border-gray-100">
                    <h4 class="text-lg font-semibold text-primary mb-4 flex items-center">
                      <i class="fas fa-book mr-2"></i>
                      推荐阅读
                    </h4>
                    <div v-if="recommendedReading && recommendedReading.length > 0" class="space-y-3">
                      <div v-for="(item, index) in recommendedReading" :key="index" class="group">
                        <a v-if="item.url" :href="item.url" target="_blank" rel="noopener noreferrer" class="flex items-center justify-between text-sm hover:text-primary transition-custom">
                          <span class="text-dark/80 group-hover:text-primary line-clamp-2">{{ item.title }}</span>
                          <i class="fas fa-external-link-alt text-xs text-primary/60 group-hover:text-primary transition-custom"></i>
                        </a>
                        <div v-else class="text-sm text-dark/80 line-clamp-2">{{ item.title }}</div>
                      </div>
                    </div>
                    <div v-else-if="sectionsLoading" class="text-sm text-dark/60 flex items-center">
                      <i class="fas fa-spinner fa-spin mr-2"></i>
                      生成中...
                    </div>
                    <div v-else class="text-sm text-dark/60 flex items-center">
                      <i class="fas fa-hourglass-half mr-2"></i>
                      暂无推荐阅读数据
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 相关碑刻推荐 -->
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 mb-12">
        <h2 class="text-2xl font-serif font-bold text-primary mb-6 flex items-center">
          <i class="fas fa-th-large mr-2 text-accent"></i>
          相关碑刻推荐
        </h2>
        <div v-if="article.related_articles && article.related_articles.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div v-for="related in article.related_articles" :key="related.id" class="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-custom">
            <router-link :to="`/knowledge/article/${related.id}`" class="block">
              <div class="h-36 overflow-hidden">
                <img :src="related.cover_image || 'https://via.placeholder.com/400x200?text=No+Image'" :alt="related.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105">
              </div>
              <div class="p-4">
                <div class="flex justify-between items-center mb-2">
                  <span v-if="related.dynasty" class="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                    {{ related.dynasty }}
                  </span>
                  <span v-if="related.category" class="text-xs bg-secondary/30 text-primary px-2 py-0.5 rounded">
                    {{ related.category }}
                  </span>
                </div>
                <h3 class="text-lg font-semibold mb-2 line-clamp-2 text-primary hover:text-primary/80 transition-custom">
                  {{ related.title }}
                </h3>
                <p class="text-sm text-dark/70 line-clamp-2 mb-3">
                  {{ related.excerpt }}
                </p>
                <div class="flex justify-between items-center text-xs text-dark/50">
                  <span class="flex items-center">
                    <i class="fas fa-eye mr-1"></i>
                    {{ related.views || 0 }}
                  </span>
                  <span>{{ new Date(related.created_at).toLocaleDateString() }}</span>
                </div>
              </div>
            </router-link>
          </div>
        </div>
        <div v-else class="bg-white rounded-xl p-8 shadow-sm text-center">
          <div class="text-dark/60 flex items-center justify-center">
            <i class="fas fa-info-circle mr-2"></i>
            暂无相关碑刻推荐
          </div>
        </div>
      </div>
    </div>

    <!-- 碑文不存在 -->
    <div v-else class="text-center py-20">
      <i class="fas fa-exclamation-circle text-6xl text-gray-300 mb-4"></i>
      <h2 class="text-2xl font-semibold text-gray-600 mb-4">碑文不存在</h2>
      <router-link to="/knowledge" class="text-primary hover:underline">返回碑文知识库</router-link>
    </div>
  </div>
</template>

<style scoped>
/* 颜色主题变量 */
:root {
  --primary: #8B5A2B;
  --secondary: #F5F5DC;
  --accent: #D2B48C;
  --dark: #3E2723;
  --light: #F9F5EB;
}

/* 背景纹理 */
.bg-texture {
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23d2b48c' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
}

/* 过渡动画 */
.transition-custom {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 文本样式 */
.prose {
  color: inherit;
}

.prose p {
  margin-bottom: 1em;
}

.prose h3 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

/* 文本截断 */
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  -webkit-line-clamp: 1;
  line-clamp: 1;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}
</style>
