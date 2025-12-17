<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { fetchKnowledgeHome } from '../api/knowledge'

const router = useRouter()
const userStore = useUserStore()
const baseUrl = ref(window.location.origin + '/api/v1')

// 功能特性数据
const features = ref([
  {
    icon: 'fas fa-camera',
    title: '碑文识别',
    description: '拍摄或上传碑文图片，AI自动识别并转化为现代汉字，支持多朝代字体识别。',
    benefits: ['支持拍照与图片上传', '多朝代字体智能识别', '高清图片处理']
  },
  {
    icon: 'fas fa-pen-fancy',
    title: '人工校对',
    description: '对识别结果进行逐字校对，确保内容准确性，支持手动修改与标注。',
    benefits: ['逐字校对功能', '手动修改与标注', '修改历史记录']
  },
  {
    icon: 'fas fa-book-open',
    title: 'AI阐释',
    description: '多维度解读碑文内容，包括历史背景、文化意义、相关人物与事件等。',
    benefits: ['历史背景分析', '文化意义阐释', '相关人物事件解读']
  },
  {
    icon: 'fas fa-comments',
    title: 'AI对话',
    description: '与AI进行深度对话，提出问题或继续探讨相关历史，拓展知识边界。',
    benefits: ['智能问答系统', '上下文理解', '知识拓展推荐']
  },
  {
    icon: 'fas fa-history',
    title: '历史记录',
    description: '自动保存所有识别结果，方便随时查看与管理历史记录，支持分类整理。',
    benefits: ['完整历史记录', '分类与标签', '快速搜索功能']
  },
  {
    icon: 'fas fa-lightbulb',
    title: '兴趣推荐',
    description: '基于您的使用习惯，智能推荐相关碑文与文化主题，拓展历史视野。',
    benefits: ['个性化推荐', '文化主题探索', '相关碑文推荐']
  }
])

// 使用流程
const steps = ref([
  {
    number: 1,
    icon: 'fas fa-camera',
    title: '拍摄或上传',
    description: '拍摄碑文照片或从相册上传图片，支持多种格式'
  },
  {
    number: 2,
    icon: 'fas fa-magic',
    title: 'AI识别',
    description: '系统自动识别碑文内容，转化为现代汉字文本'
  },
  {
    number: 3,
    icon: 'fas fa-edit',
    title: '校对修正',
    description: '对识别结果进行人工校对，确保内容准确无误'
  },
  {
    number: 4,
    icon: 'fas fa-book-reader',
    title: '阅读阐释',
    description: '查看AI对碑文的多维度阐释，与AI对话深入了解'
  }
])

// 推荐碑文数据
const recommendations = ref([])
const isLoadingRecommendations = ref(false)

// 获取推荐碑文数据
const loadRecommendations = async () => {
  try {
    isLoadingRecommendations.value = true
    const homeData = await fetchKnowledgeHome(baseUrl.value, userStore.token || '')
    recommendations.value = homeData.featured || []
  } catch (error) {
    console.error('获取推荐碑文失败:', error)
  } finally {
    isLoadingRecommendations.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadRecommendations()
})

// 时间线数据
// TODO: 待接入AI生成的时间线数据
const timeline = ref([])

// 相关人物
// TODO: 待接入AI生成的相关人物数据
const relatedPeople = ref([])

// 标签页状态
const activeTab = ref('history')

// 识别演示文本
const recognitionText = ref(`维大唐开元二十有九年，岁次辛巳，秋八月丁丑朔，十三日己丑。故朝散大夫、守秘书少监、集贤院学士、上柱国、赐紫金鱼袋、赠秘书监、江夏李公，字太白，葬于当涂青山之阳。

公之生也，先天地而生；公之没也，后天地而没。其为文也，拔地倚天，陵轹万古；其为志也，怀瑾握瑜，含英咀华。

公性倜傥，好神仙，喜纵横，击剑为任侠，轻财好施。常欲济苍生，安社稷，然遭逢乱世，有志不伸。乃浪迹江湖，浮游四方，与名流贤士，诗酒唱和。

公之诗，雄奇豪放，清新飘逸，名动天下，传于后世。其代表作有《将进酒》、《望庐山瀑布》、《蜀道难》等，皆为千古绝唱。`)

// 方法
const startRecognition = () => {
  router.push('/recognition')
}

const viewKnowledgeBase = () => {
  router.push('/knowledge')
}

const viewHistory = () => {
  router.push('/history')
}

const openRegister = () => {
  // 触发 Header 中监听的全局事件，打开注册模态框
  window.dispatchEvent(new Event('open-register-modal'))
}

const watchDemo = () => {
  // 观看演示 — 当前不做操作
}
</script>

<template>
  <div class="home-page bg-light bg-texture min-h-screen">
    <!-- Hero 区域 -->
    <section class="relative bg-secondary py-16 md:py-24 overflow-hidden">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="grid md:grid-cols-2 gap-8 items-center">
          <div class="text-center md:text-left">
            <h1
              class="text-4xl md:text-5xl lg:text-6xl font-serif font-bold text-primary leading-tight mb-4 text-shadow">
              AI赋能<br>碑文解读新体验
            </h1>
            <p class="text-lg md:text-xl text-dark/80 mb-8 max-w-lg mx-auto md:mx-0">
              通过先进AI技术识别碑文内容，探索历史背景与文化意义，让古老文字焕发新生。
            </p>
            <div class="flex flex-col sm:flex-row justify-center md:justify-start gap-4">
              <button @click="startRecognition"
                class="px-6 py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 shadow-md hover:shadow-lg transition-custom flex items-center justify-center">
                <i class="fas fa-camera mr-2"></i>
                开始识别
              </button>
              <button
                class="px-6 py-3 border border-primary text-primary rounded-md font-medium hover:bg-primary/5 transition-custom flex items-center justify-center">
                <i class="fas fa-info-circle mr-2"></i>
                了解更多
              </button>
            </div>
          </div>
          <div class="hidden md:block relative">
            <img alt="古代石碑展示"
              class="rounded-lg shadow-xl w-full h-auto object-cover transform hover:scale-[1.02] transition-custom duration-500"
              src="/gemdesign/assets/page/1988264127725830144/8c939d4ad1088f74dbcdbfb264c6e042.png">
            <div
              class="absolute -bottom-6 -left-6 bg-white p-4 rounded-lg shadow-lg max-w-xs transform rotate-[-3deg] hover:rotate-0 transition-custom">
              <div class="flex items-start">
                <div class="bg-accent/20 p-2 rounded-full mr-3">
                  <i class="fas fa-check text-primary"></i>
                </div>
                <div>
                  <p class="font-medium text-primary">AI精准识别</p>
                  <p class="text-sm text-dark/70">98%以上识别准确率</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 装饰元素 -->
      <div
        class="absolute top-0 right-0 w-64 h-64 bg-accent/10 rounded-full filter blur-3xl -translate-y-1/2 translate-x-1/3">
      </div>
      <div
        class="absolute bottom-0 left-0 w-96 h-96 bg-primary/5 rounded-full filter blur-3xl translate-y-1/3 -translate-x-1/3">
      </div>
    </section>

    <!-- 功能特点 -->
    <section class="py-16 md:py-24 bg-white">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl md:text-4xl font-serif font-bold text-primary mb-4">核心功能</h2>
          <p class="text-dark/70 text-lg">碑说平台通过AI技术，为您提供全方位的碑文解读体验</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="(feature, index) in features" :key="index"
            class="bg-light rounded-xl p-6 shadow-sm hover:shadow-md transition-custom border border-gray-100 group">
            <div
              class="w-14 h-14 bg-primary/10 rounded-lg flex items-center justify-center mb-5 group-hover:bg-primary/20 transition-custom">
              <i :class="feature.icon + ' text-primary text-2xl'"></i>
            </div>
            <h3 class="text-xl font-semibold text-primary mb-3">{{ feature.title }}</h3>
            <p class="text-dark/70 mb-4">{{ feature.description }}</p>
            <ul class="space-y-2 text-sm text-dark/70">
              <li v-for="(benefit, idx) in feature.benefits" :key="idx" class="flex items-center">
                <i class="fas fa-check text-accent mr-2"></i>
                {{ benefit }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section class="py-16 md:py-24 bg-secondary/30">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl md:text-4xl font-serif font-bold text-primary mb-4">简单四步，探索历史</h2>
          <p class="text-dark/70 text-lg">轻松使用碑说平台，开启您的历史文化探索之旅</p>
        </div>
        <div class="relative">
          <!-- 连接线 -->
          <div class="hidden md:block absolute top-1/2 left-0 w-full h-1 bg-accent/30 -translate-y-1/2 z-0"></div>
          <div class="grid md:grid-cols-4 gap-8 relative z-10">
            <div v-for="step in steps" :key="step.number" class="flex flex-col items-center text-center">
              <div
                class="w-16 h-16 md:w-20 md:h-20 bg-primary text-white rounded-full flex items-center justify-center text-xl md:text-2xl font-bold mb-4 shadow-md">
                {{ step.number }}
              </div>
              <div class="bg-white p-5 rounded-xl shadow-sm w-full">
                <div class="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <i :class="step.icon + ' text-primary text-xl'"></i>
                </div>
                <h3 class="text-xl font-semibold text-primary mb-2">{{ step.title }}</h3>
                <p class="text-dark/70">{{ step.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 碑文识别与推荐 -->
    <section class="py-16 md:py-24 bg-white">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl md:text-4xl font-serif font-bold text-primary mb-4">AI碑文识别</h2>
          <p class="text-dark/70 text-lg">上传碑文图片，AI自动识别文字内容并提供相关碑文推荐</p>
        </div>
        
        <!-- 碑文识别区域 -->
        <div class="bg-light rounded-2xl shadow-sm overflow-hidden mb-16">
          <div class="grid md:grid-cols-2">
            <!-- 左侧：图片上传与识别 -->
            <div class="p-6 md:p-8 flex flex-col">
              <h3 class="text-xl font-semibold text-primary mb-4 flex items-center">
                <i class="fas fa-camera mr-2"></i>
                上传碑文图片
              </h3>
              <div class="bg-white rounded-xl p-4 shadow-sm flex-grow flex flex-col items-center justify-center">
                <div class="relative w-full max-w-md aspect-square bg-gray-100 rounded-lg overflow-hidden mb-4">
                  <img alt="碑文示例图" class="w-full h-full object-cover" src="/images/多宝塔碑1.jpg">
                  <div
                    class="absolute inset-0 bg-black/30 opacity-0 hover:opacity-100 transition-custom flex items-center justify-center">
                    <button class="bg-white text-primary px-4 py-2 rounded-md font-medium">
                      <i class="fas fa-upload mr-1"></i>
                      上传图片
                    </button>
                  </div>
                </div>
                <div class="w-full max-w-md">
                  <button @click="startRecognition"
                    class="w-full py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center justify-center">
                    <i class="fas fa-magic mr-2"></i>
                    开始识别
                  </button>
                </div>
                <div class="mt-4 text-sm text-dark/60 text-center">
                  <p>支持 JPG、PNG、WEBP 格式，最大 10MB</p>
                  <p class="mt-1">识别过程仅需几秒，支持多朝代字体</p>
                </div>
              </div>
            </div>
            
            <!-- 右侧：识别结果展示 -->
            <div class="p-6 md:p-8 bg-secondary/50 border-t md:border-t-0 md:border-l border-secondary">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-semibold text-primary flex items-center">
                  <i class="fas fa-file-alt mr-2"></i>
                  识别结果
                </h3>
                <div class="flex space-x-2">
                  <button class="p-2 text-dark/70 hover:text-primary hover:bg-white/50 rounded-md transition-custom"
                    title="复制文本">
                    <i class="fas fa-copy"></i>
                  </button>
                  <button class="p-2 text-dark/70 hover:text-primary hover:bg-white/50 rounded-md transition-custom"
                    title="下载文本">
                    <i class="fas fa-download"></i>
                  </button>
                </div>
              </div>
              <div class="bg-white rounded-xl p-5 shadow-sm h-[calc(100%-4rem)] flex flex-col">
                <div class="mb-4">
                  <div class="flex flex-wrap gap-3 text-sm">
                    <div class="flex items-center text-dark/70">
                      <i class="fas fa-clock mr-1"></i>
                      <span>识别完成</span>
                    </div>
                    <div class="flex items-center text-dark/70">
                      <i class="fas fa-font mr-1"></i>
                      <span>286字</span>
                    </div>
                    <div class="flex items-center text-dark/70">
                      <i class="fas fa-percentage mr-1"></i>
                      <span>98.7% 置信度</span>
                    </div>
                    <div class="flex items-center text-dark/70">
                      <i class="fas fa-history mr-1"></i>
                      <span>唐代碑文</span>
                    </div>
                  </div>
                </div>
                <div class="flex-grow overflow-y-auto text-dark/90 leading-relaxed text-sm font-serif whitespace-pre-wrap">
                  {{ recognitionText }}
                </div>
                <div class="mt-6 grid grid-cols-2 gap-3">
                  <button
                    class="py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center justify-center">
                    <i class="fas fa-book-reader mr-2"></i>
                    AI阐释
                  </button>
                  <button
                    class="py-3 border border-primary text-primary rounded-md font-medium hover:bg-primary/5 transition-custom flex items-center justify-center">
                    <i class="fas fa-comments mr-2"></i>
                    智能问答
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 相关碑文推荐 -->
        <div>
          <h3 class="text-2xl font-serif font-bold text-primary mb-8 text-center">相关碑文推荐</h3>
          
          <!-- 推荐加载状态 -->
          <div v-if="isLoadingRecommendations" class="text-center py-8 text-dark/60">
            <i class="fas fa-spinner fa-spin text-xl mr-2"></i>
            正在加载推荐碑文...
          </div>
          
          <!-- 空数据状态 -->
          <div v-else-if="recommendations.length === 0" class="text-center py-10">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-4">
              <i class="fas fa-lightbulb text-gray-400 text-3xl"></i>
            </div>
            <p class="text-dark/60">暂无相关碑文推荐</p>
          </div>
          
          <!-- 数据列表 -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="item in recommendations" :key="item.id"
                class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-custom border border-gray-100 cursor-pointer">
                <!-- 图片显示 -->
                <div class="h-48 overflow-hidden bg-gray-100">
                    <!-- 从excerpt中提取图片链接 -->
                    <img 
                        v-if="item.cover_image_url || (item.excerpt && item.excerpt.includes('图片链接：'))" 
                        :src="item.cover_image_url || (item.excerpt.match(/- 图片链接：(.*?)\n/)?.[1] || '')" 
                        :alt="item.title" 
                        class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                        @error="(e) => { e.target.style.display = 'none'; e.target.nextElementSibling.style.display = 'flex'; }"
                    />
                    <!-- 本地占位图 -->
                    <div class="h-full bg-gray-100 flex items-center justify-center" style="display: none;">
                        <i class="fas fa-monument text-gray-300 text-5xl"></i>
                    </div>
                </div>
                <div class="p-5">
                    <h4 class="text-lg font-serif font-medium text-dark mb-2">{{ item.title }}</h4>
                    <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ item.description || item.excerpt }}</p>
                    <!-- 查看详情跳转 -->
                    <div class="flex justify-between items-center">
                        <span class="text-xs text-gray-500">{{ item.dynasty || '未知朝代' }}</span>
                        <a @click="router.push('/knowledge/article/' + item.id)" href="javascript:void(0);" class="text-primary text-sm font-medium flex items-center hover:text-accent transition-custom cursor-pointer">
                            查看详情
                            <i class="fas fa-arrow-right ml-2 text-xs"></i>
                        </a>
                    </div>
                </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI阐释展示 -->
    <section class="py-16 md:py-24 bg-light">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl md:text-4xl font-serif font-bold text-primary mb-4">AI深度阐释</h2>
          <p class="text-dark/70 text-lg">不仅仅是文字识别，更能深入解读碑文背后的历史文化内涵</p>
        </div>
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <div class="p-6 md:p-8">
            <!-- 阐释标签页 -->
            <div class="border-b border-gray-200 mb-6">
              <nav class="-mb-px flex space-x-8">
                <button v-for="tab in [
                  { id: 'history', label: '历史背景' },
                  { id: 'culture', label: '文化意义' },
                  { id: 'people', label: '相关人物' },
                  { id: 'reading', label: '延伸阅读' }
                ]" :key="tab.id" @click="activeTab = tab.id" :class="[
                  'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
                ]">
                  {{ tab.label }}
                </button>
              </nav>
            </div>
            <!-- 阐释内容 -->
            <div class="grid md:grid-cols-3 gap-8">
              <!-- 左侧：主要阐释内容 -->
              <div class="md:col-span-2">
                <h3 class="text-2xl font-serif font-semibold text-primary mb-4">李白墓碑文历史背景分析</h3>
                <div class="text-dark/90 leading-relaxed mb-6 space-y-4">
                  <p>李白墓碑文撰写于大唐开元二十九年（公元741年），正值盛唐时期，这是中国历史上政治稳定、经济繁荣、文化昌盛的黄金时代。</p>
                  <p>开元年间，唐玄宗李隆基励精图治，任用贤能，开创了"开元盛世"。这一时期，文化艺术得到极大发展，诗歌创作达到顶峰，出现了李白、杜甫、王维等一大批杰出诗人。</p>
                  <p>
                    李白（701年－762年），字太白，号青莲居士，是唐代最伟大的浪漫主义诗人之一，被后人誉为"诗仙"。他的一生历经坎坷，曾供奉翰林，后因得罪权贵而离开长安，开始漫游四方。安史之乱爆发后，他因参与永王李璘幕府而被流放夜郎，途中遇赦。晚年漂泊东南一带，最终病逝于当涂（今属安徽）。
                  </p>
                  <p>此碑文撰写于李白去世前一年，反映了当时文人对李白文学成就的高度评价，也体现了盛唐时期文人的精神风貌和价值取向。</p>
                </div>
                <!-- AI对话入口 -->
                <div class="bg-secondary/30 p-4 rounded-lg border border-secondary">
                  <div class="flex items-start">
                    <div class="flex-shrink-0 mr-3">
                      <i class="fas fa-robot text-primary text-xl"></i>
                    </div>
                    <div class="flex-grow">
                      <p class="text-dark/80 mb-3">对这段历史背景有疑问？我可以为您解答更多细节</p>
                      <div class="flex">
                        <input type="text" placeholder="请输入您的问题..."
                          class="flex-grow px-4 py-2 rounded-l-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" />
                        <button
                          class="bg-primary text-white px-4 py-2 rounded-r-md hover:bg-primary/90 transition-custom">
                          <i class="fas fa-paper-plane"></i>
                        </button>
                      </div>
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
                  <div v-if="timeline && timeline.length" class="space-y-4">
                    <div v-for="(item, index) in timeline" :key="index" class="flex">
                      <div class="flex-shrink-0 w-16 text-right pr-3 relative">
                        <span class="inline-block w-3 h-3 bg-primary rounded-full absolute right-0 top-1"></span>
                        <span class="text-sm font-medium text-primary block">{{ item.year }}</span>
                      </div>
                      <div class="flex-grow border-l border-gray-200 pl-3 pb-4">
                        <p class="text-dark/80 text-sm">{{ item.event }}</p>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-sm text-dark/60 flex items-center">
                    <i class="fas fa-spinner fa-spin mr-2"></i>
                    正在生成中...
                  </div>
                </div>
                <!-- 相关人物 -->
                <div class="bg-light p-5 rounded-xl border border-gray-100">
                  <h4 class="text-lg font-semibold text-primary mb-4 flex items-center">
                    <i class="fas fa-users mr-2"></i>
                    相关人物
                  </h4>
                  <div v-if="relatedPeople && relatedPeople.length" class="space-y-3">
                    <a v-for="(person, index) in relatedPeople" :key="index" href="javascript:void(0);"
                      class="flex items-center p-2 hover:bg-white rounded-md transition-custom">
                      <div class="w-10 h-10 rounded-full bg-gray-200 mr-3 flex items-center justify-center">
                        <i class="fas fa-user text-gray-400"></i>
                      </div>
                      <div>
                        <p class="font-medium text-dark">{{ person.name }}</p>
                        <p class="text-xs text-dark/60">{{ person.role }}</p>
                      </div>
                    </a>
                  </div>
                  <div v-else class="text-sm text-dark/60 flex items-center">
                    <i class="fas fa-spinner fa-spin mr-2"></i>
                    正在生成中...
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 兴趣推荐 -->
    <section class="py-16 md:py-24 bg-white">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl md:text-4xl font-serif font-bold text-primary mb-4">探索更多碑文</h2>
          <p class="text-dark/70 text-lg">基于您的兴趣，发现更多精彩的历史碑文与文化遗产</p>
        </div>
        
        <!-- 推荐加载状态 -->
        <div v-if="isLoadingRecommendations" class="text-center py-8 text-dark/60">
          <i class="fas fa-spinner fa-spin text-xl mr-2"></i>
          正在加载推荐碑文...
        </div>
        
        <!-- 空数据状态 -->
        <div v-else-if="recommendations.length === 0" class="text-center py-10">
          <div class="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-4">
            <i class="fas fa-lightbulb text-gray-400 text-3xl"></i>
          </div>
          <p class="text-dark/60">暂无推荐碑文</p>
        </div>
        
        <!-- 数据列表 -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="item in recommendations" :key="item.id"
              class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-custom border border-gray-100 cursor-pointer">
              <!-- 图片显示 -->
              <div class="h-48 overflow-hidden bg-gray-100">
                  <!-- 从excerpt中提取图片链接 -->
                  <img 
                      v-if="item.cover_image_url || (item.excerpt && item.excerpt.includes('图片链接：'))" 
                      :src="item.cover_image_url || (item.excerpt.match(/- 图片链接：(.*?)\n/)?.[1] || '')" 
                      :alt="item.title" 
                      class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                      @error="(e) => { e.target.style.display = 'none'; e.target.nextElementSibling.style.display = 'flex'; }"
                  />
                  <!-- 本地占位图 -->
                  <div class="h-full bg-gray-100 flex items-center justify-center" style="display: none;">
                      <i class="fas fa-monument text-gray-300 text-5xl"></i>
                  </div>
              </div>
              <div class="p-5">
                  <h4 class="text-lg font-serif font-medium text-dark mb-2">{{ item.title }}</h4>
                  <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ item.description || item.excerpt }}</p>
                  <!-- 查看详情跳转 -->
                  <div class="flex justify-between items-center">
                      <span class="text-xs text-gray-500">{{ item.dynasty || '未知朝代' }}</span>
                      <a @click="router.push('/knowledge/article/' + item.id)" href="javascript:void(0);" class="text-primary text-sm font-medium flex items-center hover:text-accent transition-custom cursor-pointer">
                          查看详情
                          <i class="fas fa-arrow-right ml-2 text-xs"></i>
                      </a>
                  </div>
              </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA 区域 -->
    <section class="py-20 bg-primary text-white">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl md:text-4xl font-serif font-bold mb-6">开始您的碑文探索之旅</h2>
        <p class="text-xl mb-8 opacity-90 max-w-3xl mx-auto">上传碑文图片，AI自动识别并提供详细阐释</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button @click="openRegister"
            class="px-8 py-4 bg-white text-primary rounded-md text-lg font-semibold hover:bg-gray-100 transition-custom flex items-center justify-center border border-white/20">
            <i class="fas fa-user-plus mr-2 text-primary"></i>
            免费注册
          </button>
          <button @click="watchDemo"
            class="px-8 py-4 bg-transparent border-2 border-white text-white rounded-md text-lg font-semibold hover:bg-white/10 transition-custom flex items-center justify-center">
            <i class="fas fa-play mr-2 text-white"></i>
            观看演示
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.text-shadow {
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
}

.bg-texture {
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23d2b48c' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
}
</style>
