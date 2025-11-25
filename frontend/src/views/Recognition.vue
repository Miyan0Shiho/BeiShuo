<script setup>
import { ref } from 'vue'
import { postChat, streamChatFetch, postInterpretationSections } from '../api/ai'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'

const router = useRouter()
const appStore = useAppStore()

// 标签页状态
const activeTab = ref('status')
const uploadModalOpen = ref(false)
const saveModalOpen = ref(false)

// 识别状态
const recognitionState = ref('waiting')
const processingProgress = ref(0)
const processingStatus = ref('准备识别...')

// 图片上传
const fileInput = ref(null)
const modalFileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const dragActive = ref(false)

// 识别结果数据
const recognitionResult = ref({
    text: `维大唐开元二十有九年，岁次辛巳，秋八月丁丑朔，十三日己丑。故朝散大夫、守秘书少监、集贤院学士、上柱国、赐紫金鱼袋、赠秘书监、江夏李公，字太白，葬于当涂青山之阳。

公之生也，先天地而生；公之没也，后天地而没。其为文也，拔地倚天，陵轹万古；其为志也，怀瑾握瑜，含英咀华。

公性倜傥，好神仙，喜纵横，击剑为任侠，轻财好施。常欲济苍生，安社稷，然遭逢乱世，有志不伸。乃浪迹江湖，浮游四方，与名流贤士，诗酒唱和。

公之诗，雄奇豪放，清新飘逸，名动天下，传于后世。其代表作有《将进酒》、《望庐山瀑布》、《蜀道难》等，皆为千古绝唱。`,
    wordCount: 286,
    confidence: 98.7,
    dynasty: '唐代',
    year: '公元741年',
    location: '当涂青山',
    time: '刚刚'
})

// 校对数据
const currentColumn = ref(1)
const totalColumns = ref(12)

// 校对弹窗
const correctionPopup = ref({
    visible: false,
    x: 0,
    y: 0,
    candidates: ['维', '惟', '唯'],
    selectedWord: null,
    customInput: ''
})

// AI阐释标签页
const interpretationTab = ref('history')
const aiQuestion = ref('')
const aiAnswer = ref('')
const aiSources = ref([])
const conversationId = ref('')
const aiLoading = ref(false)
const messages = ref([])
const sectionsHistory = ref('')
const sectionsCulture = ref('')
const sectionsFigures = ref([])
const sectionsSources = ref([])
const sectionsLoading = ref(false)

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
            if (!inCode) {
                inCode = true
                codeBuf = []
                closeLists()
            } else {
                inCode = false
                html += `<pre class="code"><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>`
                codeBuf = []
            }
            continue
        }
        if (inCode) { codeBuf.push(line); continue }
        if (!line.trim()) { closeLists(); html += '<br/>' ; continue }

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
    if (inCode) {
        html += `<pre class="code"><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>`
    }
    return html
}

// 保存表单
const saveForm = ref({
    title: '',
    tags: []
})

const availableTags = ['汉代碑文', '唐代碑文', '宋代碑文', '名人碑刻', '地方历史']

// 历史记录
const recentHistory = ref([
    {
        id: 1,
        name: '李白墓碑文',
        preview: '维大唐开元二十有九年，岁次辛巳，秋八月丁丑朔，十三日己丑...',
        date: '今天 14:30',
        confidence: 98.7
    },
    {
        id: 2,
        name: '兰亭集序',
        preview: '永和九年，岁在癸丑，暮春之初，会于会稽山阴之兰亭，修禊事也...',
        date: '昨天 09:15',
        confidence: 97.5
    },
    {
        id: 3,
        name: '天下第一行书',
        preview: '天下第一行书《兰亭集序》，东晋王羲之书，被誉为"天下第一行书"...',
        date: '2023-10-28 16:42',
        confidence: 96.8
    }
])

// 推荐碑文
const recommendations = ref([
    {
        id: 1,
        title: '汉代隶书碑文精选',
        dynasty: '汉代',
        description: '此碑文展示了汉代隶书的典型特征，笔画浑厚有力，结构端庄稳重，是研究汉代书法艺术的重要资料。'
    },
    {
        id: 2,
        title: '唐代楷书墓志铭',
        dynasty: '唐代',
        description: '该墓志铭采用标准的唐代楷书书写，字体端庄秀丽，结构严谨，体现了唐代书法的巅峰水平。'
    },
    {
        id: 3,
        title: '魏晋时期碑文残片',
        dynasty: '魏晋',
        description: '此残片保留了魏晋时期书法艺术的特点，字体介于隶书与楷书之间，展现了书法演变的重要阶段。'
    }
])

// 相关人物
const relatedFigures = ref([
    { name: '杜甫', role: '唐代诗人，与李白并称"李杜"' },
    { name: '唐玄宗', role: '唐朝皇帝，开创开元盛世' },
    { name: '贺知章', role: '唐代诗人，称李白为"谪仙人"' }
])

// 时间线
const timeline = ref([
    { year: '701年', event: '李白出生于碎叶城（今吉尔吉斯斯坦托克马克附近）' },
    { year: '724年', event: '李白开始漫游天下，离开蜀地' },
    { year: '742年', event: '李白被召入长安，供奉翰林' },
    { year: '762年', event: '李白病逝于当涂，享年62岁' }
])

// 方法
const openUploadModal = () => {
    uploadModalOpen.value = true
}

const closeUploadModal = () => {
    uploadModalOpen.value = false
    previewUrl.value = ''
    selectedFile.value = null
}

const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
        processFile(file)
    }
}

const processFile = (file) => {
    // 验证文件类型
    const validTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!validTypes.includes(file.type)) {
        appStore.addNotification({
            type: 'error',
            message: '请上传JPG、PNG或WEBP格式的图片',
            duration: 3000
        })
        return
    }

    // 验证文件大小
    if (file.size > 10 * 1024 * 1024) {
        appStore.addNotification({
            type: 'error',
            message: '图片大小不能超过10MB',
            duration: 3000
        })
        return
    }

    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
}

const handleDragOver = (event) => {
    event.preventDefault()
    dragActive.value = true
}

const handleDragLeave = () => {
    dragActive.value = false
}

const handleDrop = (event) => {
    event.preventDefault()
    dragActive.value = false
    const file = event.dataTransfer.files[0]
    if (file) {
        processFile(file)
    }
}

const removePreviewImage = () => {
    previewUrl.value = ''
    selectedFile.value = null
    if (modalFileInput.value) {
        modalFileInput.value.value = ''
    }
}

const confirmUpload = () => {
    if (!selectedFile.value) {
        appStore.addNotification({
            type: 'error',
            message: '请先选择图片',
            duration: 2000
        })
        return
    }

    closeUploadModal()
    startRecognition()
}

const startRecognition = () => {
    recognitionState.value = 'processing'
    processingProgress.value = 0

    const interval = setInterval(() => {
        processingProgress.value += 10

        if (processingProgress.value <= 30) {
            processingStatus.value = '正在分析碑文文字结构'
        } else if (processingProgress.value <= 60) {
            processingStatus.value = '识别文字内容'
        } else if (processingProgress.value <= 80) {
            processingStatus.value = '进行文字校正'
        } else {
            processingStatus.value = '生成识别结果'
        }

        if (processingProgress.value >= 100) {
            clearInterval(interval)
            recognitionState.value = 'completed'
        }
    }, 300)
}

const viewResults = () => {
    activeTab.value = 'result'
}

const switchTab = (tab) => {
    activeTab.value = tab
}

const switchInterpretationTab = (tab) => {
    interpretationTab.value = tab
}

const showInterpretation = async () => {
    activeTab.value = 'interpretation'
    if (!sectionsHistory.value && recognitionResult.value?.text) {
        const baseUrl = 'http://localhost:8080/api/v1'
        const token = localStorage.getItem('token') || ''
        try {
            sectionsLoading.value = true
            appStore.addNotification({ type: 'info', message: '正在生成AI阐释...', duration: 2000 })
            const data = await postInterpretationSections({ baseUrl, token, text: recognitionResult.value.text })
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
        } catch (e) {
            appStore.addNotification({ type: 'error', message: 'AI阐释生成失败', duration: 3000 })
        } finally {
            sectionsLoading.value = false
        }
    }
}

const prevColumn = () => {
    if (currentColumn.value > 1) {
        currentColumn.value--
    }
}

const nextColumn = () => {
    if (currentColumn.value < totalColumns.value) {
        currentColumn.value++
    }
}

const showCorrectionPopup = (event, word) => {
    const rect = event.target.getBoundingClientRect()
    correctionPopup.value = {
        visible: true,
        x: rect.left,
        y: rect.bottom + window.scrollY + 5,
        candidates: word.candidates || ['维', '惟', '唯'],
        selectedWord: word,
        customInput: ''
    }
}

const hideCorrectionPopup = () => {
    correctionPopup.value.visible = false
}

const selectCandidate = (candidate) => {
    correctionPopup.value.customInput = candidate
}

const confirmCorrection = () => {
    const newWord = correctionPopup.value.customInput.trim()
    if (newWord && correctionPopup.value.selectedWord) {
        correctionPopup.value.selectedWord.char = newWord
    }
    hideCorrectionPopup()
}

const copyResult = () => {
    navigator.clipboard.writeText(recognitionResult.value.text)
    appStore.addNotification({
        type: 'success',
        message: '已复制到剪贴板',
        duration: 2000
    })
}

const downloadResult = () => {
    const blob = new Blob([recognitionResult.value.text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '碑文识别结果.txt'
    a.click()
    URL.revokeObjectURL(url)
}

const openSaveModal = () => {
    saveModalOpen.value = true
}

const closeSaveModal = () => {
    saveModalOpen.value = false
    saveForm.value = {
        title: '',
        tags: []
    }
}

const toggleTag = (tag) => {
    const index = saveForm.value.tags.indexOf(tag)
    if (index > -1) {
        saveForm.value.tags.splice(index, 1)
    } else {
        saveForm.value.tags.push(tag)
    }
}

const confirmSave = () => {
    if (!saveForm.value.title.trim()) {
        appStore.addNotification({
            type: 'error',
            message: '请输入碑文标题',
            duration: 2000
        })
        return
    }

    if (saveForm.value.tags.length === 0) {
        appStore.addNotification({
            type: 'error',
            message: '请至少选择一个标签',
            duration: 2000
        })
        return
    }

    appStore.addNotification({
        type: 'success',
        message: '保存成功',
        duration: 2000
    })
    closeSaveModal()
}

const sendAiQuestion = async () => {
    const q = aiQuestion.value.trim()
    if (!q) return
    const baseUrl = 'http://localhost:8080/api/v1'
    const token = localStorage.getItem('token') || ''
    const userMsg = { id: Date.now() + '-u', role: 'user', content: q, status: 'success', references: [], created_at: new Date().toISOString() }
    messages.value.push(userMsg)
    aiQuestion.value = ''
    const assistantMsg = { id: Date.now() + '-a', role: 'assistant', content: '', status: 'sending', references: [], created_at: new Date().toISOString() }
    messages.value.push(assistantMsg)
    aiLoading.value = true
    try {
        await streamChatFetch({
            baseUrl,
            token,
            recognitionId: 'rec_local',
            message: q,
            conversationId: conversationId.value,
            onEvent: (evt) => {
                if (!evt || !evt.event) return
                if (evt.event === 'status') {
                    if (evt.data && evt.data.status === 'success') assistantMsg.status = 'success'
                } else if (evt.event === 'references') {
                    assistantMsg.references = evt.data || []
                } else if (evt.event === 'delta') {
                    if (evt.data && typeof evt.data.text === 'string') assistantMsg.content += evt.data.text
                }
            }
        })
    } catch (e) {
        try {
            const data = await postChat({ baseUrl, token, recognitionId: 'rec_local', message: q, conversationId: conversationId.value })
            conversationId.value = data.conversation_id || conversationId.value
            assistantMsg.content = (data.reply && data.reply.content) || ''
            assistantMsg.references = (data.reply && data.reply.sources) || []
            assistantMsg.status = 'success'
        } catch (err) {
            assistantMsg.status = 'failed'
            appStore.addNotification({ type: 'error', message: 'AI对话失败', duration: 3000 })
        }
    } finally {
        aiLoading.value = false
    }
}

const triggerFileInput = () => {
    modalFileInput.value?.click()
}
</script>

<template>
    <div class="recognition-page bg-light bg-texture min-h-screen py-12 md:py-16">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <!-- 页面标题 -->
            <div class="mb-10 text-center md:text-left md:flex md:items-center md:justify-between">
                <div>
                    <h1 class="text-[clamp(1.8rem,4vw,2.5rem)] font-serif font-bold text-primary mb-2">碑文识别</h1>
                    <p class="text-dark/70 max-w-2xl">
                        上传碑文图片，AI将自动识别文字内容并提供历史文化阐释，探索古老文字背后的故事
                    </p>
                </div>
                <div class="mt-4 md:mt-0">
                    <button @click="openUploadModal"
                        class="px-5 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 shadow-md hover:shadow-lg transition-custom flex items-center mx-auto md:mx-0">
                        <i class="fas fa-upload mr-2"></i>
                        上传图片
                    </button>
                </div>
            </div>

            <!-- 主内容区 -->
            <div class="grid grid-cols-1 gap-8 lg:gap-12">
                <!-- 识别结果区域 -->
                <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 flex flex-col">
                    <!-- 标签页导航 -->
                    <div class="border-b border-gray-100">
                        <div class="flex overflow-x-auto">
                            <button @click="switchTab('status')" :class="[
                                'flex-1 py-4 px-6 font-medium border-b-2 whitespace-nowrap transition-custom',
                                activeTab === 'status' ? 'text-primary border-primary' : 'text-dark/50 border-transparent hover:text-dark/70'
                            ]">
                                图片上传
                            </button>
                            <button @click="switchTab('proofread')" :class="[
                                'flex-1 py-4 px-6 font-medium border-b-2 whitespace-nowrap transition-custom',
                                activeTab === 'proofread' ? 'text-primary border-primary' : 'text-dark/50 border-transparent hover:text-dark/70'
                            ]">
                                详细校对
                            </button>
                            <button @click="switchTab('result')" :class="[
                                'flex-1 py-4 px-6 font-medium border-b-2 whitespace-nowrap transition-custom',
                                activeTab === 'result' ? 'text-primary border-primary' : 'text-dark/50 border-transparent hover:text-dark/70'
                            ]">
                                识别结果
                            </button>
                            <button @click="switchTab('interpretation')" :class="[
                                'flex-1 py-4 px-6 font-medium border-b-2 whitespace-nowrap transition-custom',
                                activeTab === 'interpretation' ? 'text-primary border-primary' : 'text-dark/50 border-transparent hover:text-dark/70'
                            ]">
                                AI阐释
                            </button>
                        </div>
                    </div>

                    <!-- 识别状态内容 -->
                    <div v-show="activeTab === 'status'"
                        class="p-6 md:p-8 flex-grow flex flex-col items-center justify-center text-center min-h-[400px]">
                        <!-- 等待状态 -->
                        <div v-if="recognitionState === 'waiting'">
                            <div class="w-24 h-24 bg-secondary/30 rounded-full flex items-center justify-center mb-6">
                                <i class="fas fa-upload text-primary/50 text-4xl"></i>
                            </div>
                            <h3 class="text-xl font-semibold text-dark mb-3">等待上传图片</h3>
                            <p class="text-dark/70 max-w-md mb-8">上传碑文图片后，AI将自动开始识别文字内容</p>
                            <div class="w-full max-w-xs">
                                <button @click="openUploadModal"
                                    class="w-full py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center justify-center">
                                    <i class="fas fa-magic mr-2"></i>
                                    上传图片
                                </button>
                            </div>
                        </div>

                        <!-- 识别中 -->
                        <div v-else-if="recognitionState === 'processing'">
                            <div class="w-24 h-24 bg-secondary/30 rounded-full flex items-center justify-center mb-6">
                                <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary">
                                </div>
                            </div>
                            <h3 class="text-xl font-semibold text-dark mb-3">正在识别...</h3>
                            <div class="w-full max-w-md bg-gray-200 rounded-full h-2.5 mb-2">
                                <div class="bg-primary h-2.5 rounded-full transition-all duration-300"
                                    :style="{ width: processingProgress + '%' }"></div>
                            </div>
                            <p class="text-dark/70 text-sm mb-8">{{ processingStatus }} ({{ processingProgress }}%)</p>
                            <button
                                class="px-6 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                <i class="fas fa-stop-circle mr-1"></i>
                                取消识别
                            </button>
                        </div>

                        <!-- 识别完成 -->
                        <div v-else-if="recognitionState === 'completed'">
                            <div class="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mb-6">
                                <i class="fas fa-check text-green-500 text-4xl"></i>
                            </div>
                            <h3 class="text-xl font-semibold text-dark mb-3">识别完成</h3>
                            <p class="text-dark/70 max-w-md mb-8">
                                已成功识别碑文内容，共{{ recognitionResult.wordCount }}字，置信度{{ recognitionResult.confidence }}%
                            </p>
                            <div class="w-full max-w-xs">
                                <button @click="viewResults"
                                    class="w-full py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center justify-center">
                                    <i class="fas fa-arrow-right mr-2"></i>
                                    查看结果
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- 详细校对内容 -->
                    <div v-show="activeTab === 'proofread'" class="p-6 md:p-8">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold text-primary">详细校对</h3>
                            <div class="flex space-x-2">
                                <button
                                    class="p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom"
                                    title="保存校对结果">
                                    <i class="fas fa-save"></i>
                                </button>
                                <button
                                    class="p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom"
                                    title="恢复原始识别">
                                    <i class="fas fa-undo"></i>
                                </button>
                            </div>
                        </div>

                        <!-- 列对比导航 -->
                        <div class="mb-6">
                            <div class="flex justify-between items-center mb-4">
                                <div class="flex items-center space-x-3">
                                    <button @click="prevColumn"
                                        class="p-2 rounded-md border border-gray-200 text-dark/70 hover:bg-gray-50 transition-custom"
                                        :disabled="currentColumn === 1">
                                        <i class="fas fa-chevron-left"></i>
                                    </button>
                                    <span class="text-sm text-dark/70">
                                        第 <span class="font-medium">{{ currentColumn }}</span> 列 / 共 <span
                                            class="font-medium">{{
                                            totalColumns }}</span> 列
                                    </span>
                                    <button @click="nextColumn"
                                        class="p-2 rounded-md border border-gray-200 text-dark/70 hover:bg-gray-50 transition-custom"
                                        :disabled="currentColumn === totalColumns">
                                        <i class="fas fa-chevron-right"></i>
                                    </button>
                                </div>
                                <div class="flex items-center space-x-2">
                                    <button
                                        class="text-xs px-2 py-1 bg-primary/10 text-primary rounded hover:bg-primary/20 transition-custom">
                                        <i class="fas fa-magic mr-1"></i>
                                        自动校正全部
                                    </button>
                                    <button
                                        class="text-xs px-2 py-1 bg-gray-100 text-dark/70 rounded hover:bg-gray-200 transition-custom">
                                        <i class="fas fa-check mr-1"></i>
                                        全部确认
                                    </button>
                                </div>
                            </div>

                            <!-- 列对比展示 -->
                            <div class="relative overflow-x-auto pb-4">
                                <div class="flex space-x-4 min-w-max">
                                    <!-- 原始图片列 -->
                                    <div class="w-24 flex-shrink-0">
                                        <div
                                            class="bg-gray-100 rounded-lg overflow-hidden border border-gray-200 h-[400px]">
                                            <div class="w-full h-full flex items-center justify-center text-gray-300">
                                                <i class="fas fa-image text-5xl"></i>
                                            </div>
                                        </div>
                                        <div class="text-center text-xs text-dark/60 mt-2">原始碑文</div>
                                    </div>

                                    <!-- 识别文字列 -->
                                    <div class="w-24 flex-shrink-0">
                                        <div
                                            class="bg-gray-50 rounded-lg border border-gray-200 h-[400px] p-2 overflow-y-auto">
                                            <div class="space-y-1 text-center">
                                                <span
                                                    class="block py-2 hover:bg-yellow-100 cursor-pointer rounded">维</span>
                                                <span
                                                    class="block py-2 hover:bg-yellow-100 cursor-pointer rounded">大</span>
                                                <span
                                                    class="block py-2 hover:bg-yellow-100 cursor-pointer rounded">唐</span>
                                            </div>
                                        </div>
                                        <div class="text-center text-xs text-dark/60 mt-2">识别文字</div>
                                    </div>

                                    <!-- 校正结果列 -->
                                    <div class="w-24 flex-shrink-0">
                                        <div
                                            class="bg-primary/5 rounded-lg border border-primary/20 h-[400px] p-2 overflow-y-auto">
                                            <div class="space-y-1 text-center font-medium">
                                                <span class="block py-2">维</span>
                                                <span class="block py-2">大</span>
                                                <span class="block py-2">唐</span>
                                            </div>
                                        </div>
                                        <div class="text-center text-xs text-primary mt-2">校正结果</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 底部操作 -->
                        <div class="flex justify-between">
                            <button
                                class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                <i class="fas fa-arrow-left mr-1"></i>
                                上一页
                            </button>
                            <button
                                class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-custom">
                                保存校对结果
                            </button>
                            <button
                                class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                下一页
                                <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                    </div>

                    <!-- 识别结果内容 -->
                    <div v-show="activeTab === 'result'" class="p-6 md:p-8">
                        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-3">
                            <h3 class="text-lg font-semibold text-primary">识别结果</h3>
                            <div class="flex space-x-2">
                                <button @click="copyResult"
                                    class="p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom"
                                    title="复制文本">
                                    <i class="fas fa-copy"></i>
                                </button>
                                <button @click="downloadResult"
                                    class="p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom"
                                    title="下载文本">
                                    <i class="fas fa-download"></i>
                                </button>
                                <button
                                    class="p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom"
                                    title="编辑文本">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </div>
                        </div>

                        <div class="mb-4 flex flex-wrap items-center text-sm text-dark/70 gap-y-2">
                            <span class="flex items-center mr-4">
                                <i class="fas fa-clock mr-1"></i>
                                识别时间: {{ recognitionResult.time }}
                            </span>
                            <span class="flex items-center mr-4">
                                <i class="fas fa-font mr-1"></i>
                                字数: {{ recognitionResult.wordCount }}
                            </span>
                            <span class="flex items-center">
                                <i class="fas fa-check-circle text-green-500 mr-1"></i>
                                置信度: {{ recognitionResult.confidence }}%
                            </span>
                        </div>

                        <div class="border border-gray-200 rounded-lg p-4 h-64 md:h-80 overflow-y-auto mb-6 bg-gray-50">
                            <div class="text-dark/90 leading-relaxed whitespace-pre-line">
                                {{ recognitionResult.text }}
                            </div>
                        </div>

                        <div class="flex space-x-3">
                            <button @click="showInterpretation"
                                class="flex-1 py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center justify-center"
                                :disabled="sectionsLoading">
                                <i v-if="sectionsLoading" class="fas fa-spinner fa-spin mr-2"></i>
                                <i v-else class="fas fa-book-reader mr-2"></i>
                                查看AI阐释
                            </button>
                            <button
                                class="px-4 py-3 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                <i class="fas fa-share-alt"></i>
                            </button>
                        </div>
                    </div>

                    <!-- AI阐释内容 -->
                    <div v-show="activeTab === 'interpretation'" class="p-6 md:p-8">
                        <!-- 顶部操作按钮 -->
                        <div class="flex justify-end mb-6">
                            <button @click="openSaveModal"
                                class="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary/90 transition-custom flex items-center">
                                <i class="fas fa-bookmark mr-2"></i>
                                保存到我的碑文
                            </button>
                        </div>
                        <div v-if="sectionsLoading" class="mb-4 flex items-center text-dark/70 text-sm">
                            <i class="fas fa-spinner fa-spin mr-2 text-primary"></i>
                            AI阐释生成中...
                        </div>

                        <!-- 阐释标签页 -->
                        <div class="border-b border-gray-200 mb-6">
                            <nav class="-mb-px flex space-x-8 overflow-x-auto">
                                <button v-for="tab in [
                                    { id: 'history', label: '历史背景' },
                                    { id: 'culture', label: '文化意义' },
                                    { id: 'people', label: '相关人物' },
                                    { id: 'reading', label: '延伸阅读' }
                                ]" :key="tab.id" @click="switchInterpretationTab(tab.id)" :class="[
                    'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap transition-custom',
                    interpretationTab === tab.id
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
                                <div v-show="interpretationTab === 'history'" class="prose max-w-none text-dark/90 leading-relaxed mb-6" v-html="renderMarkdown(sectionsHistory || (sectionsLoading ? '### 正在生成历史背景...\n- 请稍候' : ''))"></div>
                                <div v-show="interpretationTab === 'culture'" class="prose max-w-none text-dark/90 leading-relaxed mb-6" v-html="renderMarkdown(sectionsCulture || (sectionsLoading ? '### 正在生成文化意义...\n- 请稍候' : ''))"></div>
                                <div v-show="interpretationTab === 'people'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                                    <div v-if="sectionsLoading && (!sectionsFigures || !sectionsFigures.length)" class="text-sm text-dark/60">正在生成相关人物...</div>
                                    <div v-for="p in sectionsFigures" :key="p.name" class="mb-3">
                                        <div class="font-semibold">{{ p.name }} <span class="text-dark/60 text-xs">{{ p.role }}</span></div>
                                        <div class="text-sm">{{ p.description }}</div>
                                    </div>
                                </div>
                                <div v-show="interpretationTab === 'reading'" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                                    <div class="text-sm text-dark/60 mb-2">引用来源</div>
                                    <div class="flex flex-wrap gap-2">
                                        <span v-for="(s, i) in sectionsSources" :key="i" class="text-xs px-2 py-1 bg-secondary/30 text-primary rounded">{{ (s.snippet || '').slice(0, 32) }}</span>
                                    </div>
                                </div>

                                <!-- AI对话入口 -->
                                <div class="bg-secondary/30 p-4 rounded-lg border border-secondary">
                                    <div class="flex items-start">
                                        <div class="flex-shrink-0 mr-3">
                                            <i class="fas fa-robot text-primary text-xl"></i>
                                        </div>
                                        <div class="flex-grow">
                                            <div class="space-y-3 mb-3 max-h-80 overflow-auto">
                                                <div v-for="m in messages" :key="m.id" :class="m.role === 'user' ? 'text-right' : 'text-left'">
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
                                                <input v-model="aiQuestion" type="text" placeholder="请输入您的问题..."
                                                    @keyup.enter="sendAiQuestion"
                                                    class="flex-grow px-4 py-2 rounded-l-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" />
                                                <button @click="sendAiQuestion"
                                                    class="bg-primary text-white px-4 py-2 rounded-r-md hover:bg-primary/90 transition-custom" :disabled="aiLoading">
                                                    <i class="fas fa-paper-plane"></i>
                                                </button>
                                            </div>
                                            <div v-if="aiLoading" class="mt-3 text-sm text-dark/60">正在生成...</div>
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
                                            <div class="flex-shrink-0 w-20 text-right pr-3 relative">
                                                <span
                                                    class="inline-block w-3 h-3 bg-primary rounded-full absolute right-0 top-1/2 -translate-y-1/2"></span>
                                                <span class="text-sm font-medium text-primary">{{ item.year }}</span>
                                            </div>
                                            <div
                                                :class="['flex-grow border-l border-gray-200 pl-3', index < timeline.length - 1 ? 'pb-4' : '']">
                                                <p class="text-dark/80">{{ item.event }}</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="text-sm text-dark/60">暂无时间线，稍后重试或完善识别文本。</div>
                                </div>

                                <!-- 相关人物（AI生成） -->
                                <div class="bg-light p-5 rounded-xl border border-gray-100">
                                    <h4 class="text-lg font-semibold text-primary mb-4 flex items-center">
                                        <i class="fas fa-users mr-2"></i>
                                        相关人物
                                    </h4>
                                    <div v-if="sectionsFigures && sectionsFigures.length" class="space-y-3">
                                        <div v-for="p in sectionsFigures" :key="p.name"
                                            class="flex items-center p-2 hover:bg-white rounded-md transition-custom cursor-pointer">
                                            <div
                                                class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mr-3">
                                                <i class="fas fa-user text-primary"></i>
                                            </div>
                                            <div>
                                                <p class="font-medium text-dark">{{ p.name }}</p>
                                                <p class="text-xs text-dark/60">{{ p.role }}</p>
                                                <p class="text-xs text-dark/60 mt-1" v-if="p.description">{{ p.description }}</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="text-sm text-dark/60">暂无人物信息，稍后重试或完善识别文本。</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 相关碑文推荐 -->
            <div class="mt-16">
                <h3 class="text-2xl font-serif font-semibold text-primary mb-6 flex items-center">
                    <i class="fas fa-lightbulb mr-3 text-accent"></i>
                    相关碑文推荐
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div v-for="item in recommendations" :key="item.id"
                        class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-custom border border-gray-100 cursor-pointer">
                        <div class="h-48 overflow-hidden bg-gray-100 flex items-center justify-center">
                            <i class="fas fa-monument text-gray-300 text-5xl"></i>
                        </div>
                        <div class="p-5">
                            <h4 class="text-lg font-serif font-medium text-dark mb-2">{{ item.title }}</h4>
                            <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ item.description }}</p>
                            <a href="javascript:void(0);"
                                class="text-primary text-sm font-medium flex items-center hover:text-accent transition-custom">
                                查看详情
                                <i class="fas fa-arrow-right ml-2 text-xs"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 最近识别记录 -->
            <div class="mt-12">
                <h2 class="text-xl font-semibold text-primary mb-6 flex items-center">
                    <i class="fas fa-history mr-2"></i>
                    最近识别记录
                </h2>
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="bg-gray-50 border-b border-gray-200">
                                    <th
                                        class="px-6 py-3 text-left text-xs font-medium text-dark/70 uppercase tracking-wider">
                                        图片</th>
                                    <th
                                        class="px-6 py-3 text-left text-xs font-medium text-dark/70 uppercase tracking-wider">
                                        识别内容</th>
                                    <th
                                        class="px-6 py-3 text-left text-xs font-medium text-dark/70 uppercase tracking-wider">
                                        时间</th>
                                    <th
                                        class="px-6 py-3 text-left text-xs font-medium text-dark/70 uppercase tracking-wider">
                                        置信度</th>
                                    <th
                                        class="px-6 py-3 text-right text-xs font-medium text-dark/70 uppercase tracking-wider">
                                        操作</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
                                <tr v-for="item in recentHistory" :key="item.id"
                                    class="hover:bg-gray-50 transition-custom">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="w-12 h-12 rounded bg-gray-100 flex items-center justify-center">
                                            <i class="fas fa-image text-gray-400"></i>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <div class="text-sm text-dark line-clamp-2 max-w-xs">{{ item.preview }}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-dark/70">{{ item.date }}</td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                                            {{ item.confidence }}%
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            class="text-primary hover:text-accent mr-3 transition-custom">查看</button>
                                        <button
                                            class="text-accent hover:text-primary mr-3 transition-custom">保存到我的碑文</button>
                                        <button class="text-dark/70 hover:text-dark transition-custom">删除</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                        <div class="text-sm text-dark/70">显示 1 至 3，共 12 条记录</div>
                        <div class="flex space-x-1">
                            <button
                                class="px-3 py-1 border border-gray-300 rounded-md text-dark/50 hover:bg-gray-100 disabled:opacity-50"
                                disabled>
                                上一页
                            </button>
                            <button class="px-3 py-1 border border-primary bg-primary text-white rounded-md">1</button>
                            <button
                                class="px-3 py-1 border border-gray-300 rounded-md text-dark/70 hover:bg-gray-100">2</button>
                            <button
                                class="px-3 py-1 border border-gray-300 rounded-md text-dark/70 hover:bg-gray-100">3</button>
                            <button
                                class="px-3 py-1 border border-gray-300 rounded-md text-dark/70 hover:bg-gray-100">4</button>
                            <button
                                class="px-3 py-1 border border-gray-300 rounded-md text-dark/70 hover:bg-gray-100">下一页</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 上传图片弹窗 -->
        <teleport to="body">
            <transition name="modal-fade">
                <div v-if="uploadModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div @click="closeUploadModal" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
                    <div class="relative bg-white rounded-xl shadow-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div
                            class="p-6 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white z-10">
                            <h3 class="text-xl font-semibold text-dark">上传碑文图片</h3>
                            <button @click="closeUploadModal" class="text-dark/70 hover:text-dark transition-custom">
                                <i class="fas fa-times text-xl"></i>
                            </button>
                        </div>
                        <div class="p-6">
                            <!-- 上传区域 -->
                            <div @dragover="handleDragOver" @dragleave="handleDragLeave" @drop="handleDrop"
                                @click="triggerFileInput" :class="[
                                    'border-2 border-dashed rounded-xl p-8 text-center transition-custom cursor-pointer mb-6',
                                    'bg-gradient-to-b from-light to-white shadow-sm',
                                    dragActive ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-primary hover:bg-primary/5'
                                ]">
                                <input ref="modalFileInput" type="file" accept="image/*" @change="handleFileSelect"
                                    class="hidden" />
                                <div class="flex flex-col items-center">
                                    <div
                                        class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-4 transform hover:scale-105 transition-custom">
                                        <i class="fas fa-camera text-primary text-3xl"></i>
                                    </div>
                                    <h3 class="text-xl font-semibold text-dark mb-2">点击上传或拖放图片</h3>
                                    <p class="text-sm text-dark/60 mb-6 max-w-md">
                                        支持 JPG、PNG、WEBP 格式，最大 10MB，建议图片清晰、文字端正以获得最佳识别效果
                                    </p>
                                </div>
                            </div>

                            <!-- 图片预览区域 -->
                            <div v-if="previewUrl" class="mb-6">
                                <div class="relative">
                                    <img :src="previewUrl" alt="预览图片"
                                        class="w-full h-64 object-contain border border-gray-200 rounded-lg" />
                                    <button @click.stop="removePreviewImage"
                                        class="absolute top-2 right-2 bg-white/80 p-2 rounded-full shadow-md hover:bg-white transition-custom">
                                        <i class="fas fa-times text-dark/70"></i>
                                    </button>
                                </div>
                                <div class="mt-2 flex justify-between items-center">
                                    <span class="text-sm text-dark/70 truncate">{{ selectedFile?.name }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="p-6 border-t border-gray-200 flex justify-end gap-3 sticky bottom-0 bg-white">
                            <button @click="closeUploadModal"
                                class="px-6 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                取消
                            </button>
                            <button @click="confirmUpload"
                                class="px-6 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom">
                                确认上传并识别
                            </button>
                        </div>
                    </div>
                </div>
            </transition>
        </teleport>

        <!-- 保存碑文弹窗 -->
        <teleport to="body">
            <transition name="modal-fade">
                <div v-if="saveModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div @click="closeSaveModal" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
                    <div class="relative bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
                        <div class="p-6 border-b border-gray-200">
                            <h3 class="text-xl font-semibold text-primary flex items-center">
                                <i class="fas fa-bookmark mr-2"></i>
                                保存碑文
                            </h3>
                        </div>
                        <div class="p-6">
                            <div class="mb-4">
                                <label class="block text-sm font-medium text-dark mb-2" for="epigraph-title">
                                    碑文标题 <span class="text-red-500">*</span>
                                </label>
                                <input v-model="saveForm.title" type="text" id="epigraph-title"
                                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                                    placeholder="请输入碑文标题">
                            </div>
                            <div class="mb-6">
                                <label class="block text-sm font-medium text-dark mb-2">
                                    选择标签 <span class="text-red-500">*</span>
                                </label>
                                <div class="flex flex-wrap gap-2">
                                    <label v-for="tag in availableTags" :key="tag"
                                        class="inline-flex items-center px-3 py-1 rounded-full border border-gray-300 cursor-pointer hover:bg-primary/5 transition-custom">
                                        <input type="checkbox" :value="tag" @change="toggleTag(tag)" class="sr-only">
                                        <span :class="[
                                            'transition-custom',
                                            saveForm.tags.includes(tag) ? 'bg-primary text-white border-primary px-3 py-1 rounded-full' : ''
                                        ]">
                                            {{ tag }}
                                        </span>
                                    </label>
                                </div>
                            </div>
                            <div class="flex justify-end space-x-3">
                                <button @click="closeSaveModal"
                                    class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                    取消
                                </button>
                                <button @click="confirmSave"
                                    class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-custom">
                                    保存
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </teleport>
    </div>
</template>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

.prose p {
    color: rgba(62, 39, 35, 0.9);
    margin-bottom: 1rem;
}

.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.transition-custom {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.bg-texture {
    background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23d2b48c' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
}
</style>
