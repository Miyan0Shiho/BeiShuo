<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { inscriptionsData } from '../data/inscriptionsData'

const router = useRouter()
const appStore = useAppStore()

// 响应式数据
const searchQuery = ref('')
const selectedCategory = ref('全部推荐')
const isRefreshing = ref(false)

// 分类选项
const categories = [
  '全部推荐',
  '汉代碑文',
  '唐代碑文',
  '宋代碑文',
  '名人碑刻',
  '书法艺术',
  '地方历史'
]

// 过滤后的碑文
const filteredArticles = computed(() => {
  let filtered = inscriptionsData.featuredInscriptions

  // 按分类过滤
  if (selectedCategory.value !== '全部推荐') {
    filtered = filtered.filter(article => {
      return article.dynasty?.includes(selectedCategory.value.replace('碑文', '')) ||
        article.category?.includes(selectedCategory.value)
    })
  }

  // 按搜索词过滤
  if (searchQuery.value.trim()) {
    filtered = inscriptionsData.searchInscriptions(searchQuery.value)

    // 如果还有分类筛选,需要再次过滤
    if (selectedCategory.value !== '全部推荐') {
      filtered = filtered.filter(article => {
        return article.dynasty?.includes(selectedCategory.value.replace('碑文', '')) ||
          article.category?.includes(selectedCategory.value)
      })
    }
  }

  return filtered
})

// 换一批功能
const refreshRecommendations = () => {
  isRefreshing.value = true
  // 模拟加载
  setTimeout(() => {
    isRefreshing.value = false
    appStore.addNotification({
      type: 'success',
      message: '已刷新推荐内容',
      duration: 2000
    })
  }, 1000)
}

// 查看文章详情
const viewArticle = (id) => {
  router.push(`/knowledge/article/${id}`)
}

// 切换分类
const selectCategory = (category) => {
  selectedCategory.value = category
}

// 收藏功能
const toggleFavorite = (article, event) => {
  event.stopPropagation()
  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
  const index = favorites.indexOf(article.id)

  if (index > -1) {
    favorites.splice(index, 1)
    appStore.addNotification({
      type: 'info',
      message: '已取消收藏',
      duration: 2000
    })
  } else {
    favorites.push(article.id)
    appStore.addNotification({
      type: 'success',
      message: '收藏成功',
      duration: 2000
    })
  }

  localStorage.setItem('favorites', JSON.stringify(favorites))
}

// 检查是否已收藏
const isFavorited = (articleId) => {
  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
  return favorites.includes(articleId)
}

onMounted(() => {
  // 初始化
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
            <button @click="refreshRecommendations" :disabled="isRefreshing"
              class="px-4 py-2 bg-white border border-primary text-primary rounded-md font-medium hover:bg-primary/5 transition-custom flex items-center disabled:opacity-50">
              <i :class="isRefreshing ? 'fas fa-spinner fa-spin' : 'fas fa-sync-alt'" class="mr-2"></i>
              换一批
            </button>
            <button
              class="px-4 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center">
              <i class="fas fa-sliders-h mr-2"></i>
              调整偏好
            </button>
            <router-link to="/favorites"
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

        <!-- 分类筛选 -->
        <div class="flex flex-wrap gap-2 mt-4">
          <button v-for="category in categories" :key="category" @click="selectCategory(category)" :class="selectedCategory === category
            ? 'bg-primary text-white'
            : 'bg-light text-dark/70 hover:bg-secondary/30'"
            class="px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-custom">
            {{ category }}
          </button>
        </div>
      </div>

      <!-- 热门碑刻推荐 -->
      <div class="mb-16">
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="article in filteredArticles" :key="article.id"
            class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-custom group cursor-pointer"
            @click="viewArticle(article.id)">
            <div class="relative">
              <img :src="article.image" :alt="article.title"
                class="w-full h-48 object-cover group-hover:scale-105 transition-custom duration-500">
              <div class="absolute top-3 left-3 bg-primary text-white text-xs font-medium px-2 py-1 rounded">
                {{ article.dynasty }}
              </div>
              <div
                class="absolute top-3 right-3 bg-accent text-white text-xs font-medium px-2 py-1 rounded-full flex items-center">
                <i class="fas fa-eye mr-1"></i>
                {{ Math.floor(article.views / 1000) }}k
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
                {{ article.description }}
              </p>
              <div class="flex flex-wrap gap-2 mb-4">
                <span class="bg-secondary/30 text-primary text-xs px-2 py-1 rounded-full">
                  {{ article.category }}
                </span>
              </div>
              <div class="flex justify-between items-center pt-3 border-t border-gray-100">
                <div class="flex items-center text-sm text-dark/50">
                  <i class="fas fa-history mr-1"></i>
                  <span>最近更新: 3天前</span>
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
                  <img :src="article.image" :alt="article.title"
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
                  <span class="text-dark/50 text-sm">{{ article.year }}</span>
                </div>
                <p class="text-dark/70 mb-3 line-clamp-2 md:line-clamp-1">
                  {{ article.description }}
                </p>
                <div class="flex flex-wrap gap-2 mb-4">
                  <span class="bg-secondary/30 text-primary text-xs px-2 py-1 rounded-full">
                    {{ article.category }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <div class="flex items-center text-dark/50 text-sm">
                    <span class="flex items-center mr-4">
                      <i class="fas fa-eye mr-1"></i>
                      {{ Math.floor(article.views / 100) * 100 }}
                    </span>
                    <span class="flex items-center">
                      <i class="fas fa-heart mr-1"></i>
                      {{ Math.floor(Math.random() * 100) }}
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
