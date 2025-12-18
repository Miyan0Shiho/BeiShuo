<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { postChat, streamChatFetch, postInterpretationSections, uploadImage, startRecognition as startRecognitionApi, fetchRecognitionHistory, fetchRecommendedInscriptions } from '../api/ai'
import { createInscription } from '../api/inscription'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const baseUrl = ref(window.location.origin)

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

const recognitionId = ref('')
const savedInscriptionId = ref(null)
const textLines = ref([])
const recognitionOptions = ref({
    det_mode: 'sp',
    return_position: true,
    return_choices: true,
    version: 'beta',
    det_layout: false,
    only_plain_text: false,
    return_layout: false,
    hp_line_words_angel: 'left2right',
    sp_line_words_angel: 'top2bottom'
})
const originalImageUrl = ref('')
const originalImageSize = ref({ width: 0, height: 0 })
const lineStripUrls = ref([])
const lineStripRects = ref([])
const lineStripDims = ref([])
const lineConfidences = ref([])
const stripContainerRef = ref(null)
const stripHighlight = ref({ visible: false, left: 0, top: 0, width: 0, height: 0 })
const stripOverlayStyle = computed(() => ({
    position: 'absolute',
    left: stripHighlight.value.left + 'px',
    top: stripHighlight.value.top + 'px',
    width: stripHighlight.value.width + 'px',
    height: stripHighlight.value.height + 'px',
    display: stripHighlight.value.visible ? 'block' : 'none',
    border: '2px solid rgba(255,165,0,0.9)',
    background: 'rgba(255,165,0,0.25)',
}))
const detModeSelection = ref('sp')
const directionSelection = ref('top2bottom')
const previewModeSelection = ref('vertical')
const directionOptions = computed(() => detModeSelection.value === 'sp'
    ? [
        { id: 'top2bottom', label: '从上到下' },
        { id: 'bottom2top', label: '从下到上' }
    ]
    : [
        { id: 'left2right', label: '从左到右' },
        { id: 'right2left', label: '从右到左' }
    ]
)
watch(detModeSelection, (v) => {
    directionSelection.value = v === 'sp' ? 'top2bottom' : 'left2right'
    previewModeSelection.value = v === 'hp' ? 'horizontal' : 'vertical'
})

// 原图裁剪与置信度工具
const loadImage = (src) => new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
})

const buildStripForLineVertical = async (img, line, targetWidth = 80) => {
    const words = Array.isArray(line.words) ? line.words : []
    if (!words.length) return { url: '', rects: [] }
    const strips = []
    const rects = []
    let totalHeight = 0
    for (const w of words) {
        const pos = w.position || []
        const x1 = pos[0]; const y1 = pos[1]; const x2 = pos[2]; const y2 = pos[3]
        const wWidth = Math.max(1, (x2 || 0) - (x1 || 0))
        const wHeight = Math.max(1, (y2 || 0) - (y1 || 0))
        const scale = targetWidth / wWidth
        const h = Math.round(wHeight * scale)
        strips.push({ x: x1 || 0, y: y1 || 0, w: wWidth, h: wHeight, dh: h, scale })
        rects.push({ left: 0, top: totalHeight, width: targetWidth, height: h })
        totalHeight += h
    }
    const canvas = document.createElement('canvas')
    canvas.width = targetWidth
    canvas.height = totalHeight
    const ctx = canvas.getContext('2d')
    let y = 0
    for (const s of strips) {
        ctx.drawImage(img, s.x, s.y, s.w, s.h, 0, y, targetWidth, s.dh)
        y += s.dh
    }
    return { url: canvas.toDataURL('image/png'), rects, baseW: targetWidth, baseH: totalHeight }
}

const buildStripForLineHorizontal = async (img, line, targetHeight = 80) => {
    const words = Array.isArray(line.words) ? line.words : []
    if (!words.length) return { url: '', rects: [] }
    const pieces = []
    const rects = []
    let totalWidth = 0
    for (const w of words) {
        const pos = w.position || []
        const x1 = pos[0]; const y1 = pos[1]; const x2 = pos[2]; const y2 = pos[3]
        const wWidth = Math.max(1, (x2 || 0) - (x1 || 0))
        const wHeight = Math.max(1, (y2 || 0) - (y1 || 0))
        const scale = targetHeight / wHeight
        const wScaled = Math.round(wWidth * scale)
        pieces.push({ x: x1 || 0, y: y1 || 0, w: wWidth, h: wHeight, dw: wScaled, scale })
        rects.push({ left: totalWidth, top: 0, width: wScaled, height: targetHeight })
        totalWidth += wScaled
    }
    const canvas = document.createElement('canvas')
    canvas.width = totalWidth
    canvas.height = targetHeight
    const ctx = canvas.getContext('2d')
    let x = 0
    for (const p of pieces) {
        ctx.drawImage(img, p.x, p.y, p.w, p.h, x, 0, p.dw, targetHeight)
        x += p.dw
    }
    return { url: canvas.toDataURL('image/png'), rects, baseW: totalWidth, baseH: targetHeight }
}

const buildStripForLine = async (img, line, mode) => {
    if (mode === 'horizontal') return buildStripForLineHorizontal(img, line)
    return buildStripForLineVertical(img, line)
}

const computeLineConfidence = (line) => {
    const words = Array.isArray(line.words) ? line.words : []
    let sum = 0, n = 0
    for (const w of words) {
        let c = typeof w.confidence === 'number' ? w.confidence : (typeof w.det_confidence === 'number' ? w.det_confidence : null)
        if (c !== null) { sum += c; n++ }
    }
    return n ? Math.round((sum / n) * 100) : 0
}

const formatWordConfidence = (w) => {
    const c = typeof w.confidence === 'number' ? w.confidence : (typeof w.det_confidence === 'number' ? w.det_confidence : 0)
    return Math.round(c * 100)
}

const onWordEnter = (li, wi) => {
    if (typeof li !== 'number' || typeof wi !== 'number') {
        stripHighlight.value.visible = false
        return
    }
    currentColumn.value = li + 1
    const rects = lineStripRects.value[li] || []
    const r = rects[wi]
    if (!r || !stripContainerRef.value) {
        stripHighlight.value.visible = false
        return
    }
    const cw = stripContainerRef.value.clientWidth || 0
    const ch = stripContainerRef.value.clientHeight || 0
    const dims = (lineStripDims.value[li]) || { baseW: 80, baseH: (rects.length ? rects.reduce((acc, it) => acc + it.height, 0) : 0) }
    const imgW = dims.baseW
    const imgH = dims.baseH
    const scale = Math.min(cw / imgW, ch / imgH)
    const rw = Math.round(imgW * scale)
    const rh = Math.round(imgH * scale)
    const offsetX = Math.floor((cw - rw) / 2)
    const offsetY = Math.floor((ch - rh) / 2)
    const left = offsetX + Math.round(r.left * scale)
    const top = offsetY + Math.round(r.top * scale)
    const width = Math.max(1, Math.round(r.width * scale))
    const height = Math.max(1, Math.round(r.height * scale))
    stripHighlight.value = { visible: true, left, top, width, height }
}

const onWordLeave = () => {
    stripHighlight.value.visible = false
}

// 校对数据
const currentColumn = ref(1)
const totalColumns = ref(12)
const currentLine = computed(() => {
    const idx = currentColumn.value - 1
    return (Array.isArray(textLines.value) && textLines.value[idx]) ? textLines.value[idx] : { words: [] }
})
const currentWords = computed(() => Array.isArray(currentLine.value.words) ? currentLine.value.words : [])

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
const recentHistory = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)
const isLoadingHistory = ref(false)

// 推荐碑文
const recommendations = ref([])
const isLoadingRecommendations = ref(false)

// 获取识别历史
const loadRecognitionHistory = async () => {
    try {
        isLoadingHistory.value = true
        const data = await fetchRecognitionHistory({
            baseUrl: baseUrl.value,
            token: userStore.token,
            page: currentPage.value,
            size: pageSize.value
        })
        recentHistory.value = data.records || []
        totalRecords.value = data.total || 0
    } catch (error) {
        console.error('获取识别历史失败:', error)
        recentHistory.value = []
        totalRecords.value = 0
    } finally {
        isLoadingHistory.value = false
    }
}

// 获取推荐碑文
const loadRecommendedInscriptions = async () => {
    try {
        isLoadingRecommendations.value = true
        const data = await fetchRecommendedInscriptions({
            baseUrl: baseUrl.value,
            token: userStore.token,
            text: recognitionResult.value.text,
            recognition_id: recognitionId.value,
            page: 1,
            size: 3
        })
        recommendations.value = data.records || []
    } catch (error) {
        console.error('获取推荐碑文失败:', error)
    } finally {
        isLoadingRecommendations.value = false
    }
}

// 查看识别记录
const viewModalOpen = ref(false)
const currentViewItem = ref(null)

const viewRecognition = (item) => {
    currentViewItem.value = item
    viewModalOpen.value = true
}

const closeViewModal = () => {
    viewModalOpen.value = false
    currentViewItem.value = null
}

const saveHistoryItem = async (item) => {
    try {
        const baseUrl = window.location.origin
        const token = localStorage.getItem('token') || ''
        const title = (item.inscription_title || item.preview || '识别记录').slice(0, 100)
        const text = item.recognition_text || item.preview || ''
        const image_url = item.image_path ? `${baseUrl}${item.image_path}` : ''
        await createInscription({ baseUrl, token, title, text, image_url, dynasty: '', status: 'active' })
        appStore.addNotification({
            type: 'success',
            message: '记录已保存到我的碑文',
            duration: 2000
        })
    } catch (e) {
        appStore.addNotification({
            type: 'error',
            message: '保存失败，请稍后重试',
            duration: 3000
        })
    }
}

// 组件挂载时加载数据
onMounted(() => {
    loadRecognitionHistory()
    if (recognitionResult.value.text) {
        loadRecommendedInscriptions()
    }
})

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

    uploadModalOpen.value = false
    startRecognition()
}

const startRecognition = async () => {
    recognitionState.value = 'processing'
    savedInscriptionId.value = null
    processingProgress.value = 0
    const baseUrl = window.location.origin
    const token = localStorage.getItem('token') || ''
    try {
        // 上传图片
        const uploadRes = await uploadImage({ baseUrl, token, file: selectedFile.value })
        const imageUrl = uploadRes.image_url
        if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
            // 如果已经是完整的URL，直接使用
            originalImageUrl.value = imageUrl
        } else {
            // 否则拼接baseUrl
            originalImageUrl.value = `${baseUrl}${imageUrl.startsWith('/') ? imageUrl : ('/' + imageUrl)}`
        }

        // 识别
        const timer = setInterval(() => {
            processingProgress.value = Math.min(processingProgress.value + 8, 95)
            if (processingProgress.value <= 30) processingStatus.value = '正在分析碑文文字结构'
            else if (processingProgress.value <= 60) processingStatus.value = '识别文字内容'
            else if (processingProgress.value <= 80) processingStatus.value = '进行文字校正'
            else processingStatus.value = '生成识别结果'
        }, 300)
        const opts = { ...recognitionOptions.value }
        if (detModeSelection.value === 'sp') {
            opts.det_mode = 'sp'
            opts.sp_line_words_angel = directionSelection.value
        } else {
            opts.det_mode = 'hp'
            opts.hp_line_words_angel = directionSelection.value
        }
        const rec = await startRecognitionApi({ baseUrl, token, imageUrl, options: opts })
        clearInterval(timer)
        processingProgress.value = 100

        const r = rec.result || {}
        recognitionId.value = r.recognition_id || ''
        textLines.value = Array.isArray(r.text_lines) ? r.text_lines : []
        let txt = typeof r.text === 'string' ? r.text : ''
        if (!txt && Array.isArray(r.texts) && r.texts.length) {
            txt = r.texts.join('\n')
        }
        originalImageSize.value = { width: r.width || 0, height: r.height || 0 }
        
        // 检查是否是缓存命中，如果是，从返回结果中获取图片URL
        if (r.image_url) {
            // 如果结果中包含image_url，说明是从数据库读取的缓存结果
            // 构建完整的图片URL
            if (r.image_url.startsWith('http://') || r.image_url.startsWith('https://')) {
                // 如果已经是完整的URL，直接使用
                originalImageUrl.value = r.image_url
            } else {
                // 否则拼接baseUrl
                originalImageUrl.value = `${baseUrl}${r.image_url.startsWith('/') ? r.image_url : ('/' + r.image_url)}`
            }
        }
        
        lineConfidences.value = (textLines.value || []).map(computeLineConfidence)
        totalColumns.value = Array.isArray(textLines.value) ? textLines.value.length : 0
        console.log('=== 开始构建拼接图 ===')
        console.log('originalImageUrl.value:', originalImageUrl.value)
        console.log('textLines.value.length:', textLines.value.length)
        console.log('textLines.value:', textLines.value)
        
        try {
            if (originalImageUrl.value && textLines.value.length) {
                console.log('开始加载原始图片')
                const img = await loadImage(originalImageUrl.value)
                console.log('原始图片加载成功:', img.width, 'x', img.height)
                
                const urls = []
                const rectsAll = []
                const dimsAll = []
                
                for (const line of textLines.value) {
                    console.log('处理文本行:', line.text)
                    const out = await buildStripForLine(img, line, previewModeSelection.value)
                    urls.push(out.url)
                    rectsAll.push(out.rects)
                    dimsAll.push({ baseW: out.baseW, baseH: out.baseH })
                    console.log('生成的strip URL:', out.url.substring(0, 50), '...')
                }
                
                lineStripUrls.value = urls
                lineStripRects.value = rectsAll
                lineStripDims.value = dimsAll
                console.log('拼接图构建完成，strip数量:', urls.length)
            } else {
                console.log('构建拼接图条件不满足:')
                console.log('originalImageUrl.value:', originalImageUrl.value)
                console.log('textLines.value.length:', textLines.value.length)
            }
        } catch (e) {
            console.error('构建拼接图失败:', e)
            console.error(e.stack)
        }
        console.log('=== 拼接图构建结束 ===')
        const conf = typeof r.confidence === 'number' ? r.confidence : 0
        const now = new Date()
        recognitionResult.value = {
            text: txt,
            wordCount: (r.word_count || txt.length || 0),
            confidence: conf,
            dynasty: '',
            year: '',
            location: '',
            time: now.toLocaleString()
        }
        recognitionState.value = 'completed'
        activeTab.value = 'result'
        appStore.addNotification({ type: 'success', message: '识别完成', duration: 2000 })
        
        // 刷新历史记录
        loadRecognitionHistory()
    } catch (e) {
        appStore.addNotification({ type: 'error', message: '识别失败，请稍后重试', duration: 3000 })
        recognitionState.value = 'waiting'
    }
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
        const baseUrl = window.location.origin
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
        candidates: Array.isArray(word.choices) ? word.choices : (word.candidates || []),
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
        if (typeof correctionPopup.value.selectedWord.text === 'string') {
            correctionPopup.value.selectedWord.text = newWord
        } else {
            correctionPopup.value.selectedWord.char = newWord
        }
    }
    hideCorrectionPopup()
}

const saveCorrections = async () => {
    const baseUrl = window.location.origin
    const token = localStorage.getItem('token') || ''
    const correctedText = (textLines.value || []).map(tl => tl.text || '').join('\n') || recognitionResult.value.text || ''
    const corrections = []
    try {
        const url = `${baseUrl}/api/v1/recognition/${recognitionId.value || 'rec_local'}/correct`
        const headers = { 'Content-Type': 'application/json' }
        if (token) headers['Authorization'] = `Bearer ${token}`
        const body = { corrected_text: correctedText, corrections }
        const res = await fetch(url, { method: 'PUT', headers, body: JSON.stringify(body) })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        if (!data || !data.success) throw new Error(data && data.message ? data.message : '保存失败')
        appStore.addNotification({ type: 'success', message: '校对结果已保存', duration: 2000 })
    } catch (e) {
        appStore.addNotification({ type: 'error', message: '保存失败，请稍后重试', duration: 3000 })
    }
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

const saveInscription = async () => {
    try {
        const baseUrl = window.location.origin
        const token = localStorage.getItem('token') || ''
        if (!token) {
            appStore.addNotification({
                type: 'error',
                message: '未登录，无法保存。请先登录后再保存',
                duration: 3000
            })
            return
        }
        const title = saveForm.value.title.trim()
        const text = (textLines.value || []).map(tl => tl.text || '').join('\n') || recognitionResult.value.text || ''
        const image_url = originalImageUrl.value || ''
        const dynasty = recognitionResult.value.dynasty || ''
        await createInscription({ baseUrl, token, title, text, image_url, dynasty, status: 'active' })
        console.log('保存碑文成功:', title)
        appStore.addNotification({
            type: 'success',
            message: `已保存"${title}"到我的碑文`,
            duration: 3000
        })
        closeSaveModal()
        // 刷新历史记录以更新状态
        loadRecognitionHistory()
    } catch (e) {
        console.error('保存碑文失败:', e)
        appStore.addNotification({
            type: 'error',
            message: `保存失败: ${e.message || '未知错误'}`,
            duration: 5000
        })
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

    saveInscription()
}

const sendAiQuestion = async () => {
    const q = aiQuestion.value.trim()
    if (!q) return
    const baseUrl = window.location.origin
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

const dislikeResult = async () => {
    try {
        // 显示确认对话框
        if (!confirm('确定对当前识别结果不满意吗？系统将重新执行识别。')) {
            return
        }
        
        // 这里需要获取当前识别结果的图片哈希值
        // 假设recognitionResult对象中包含image_hash字段
        const imageHash = recognitionResult.value.image_hash || ''
        if (!imageHash) {
            appStore.addNotification({
                type: 'error',
                message: '无法获取图片哈希值，无法重新识别',
                duration: 3000
            })
            return
        }
        
        // 调用API删除OCR缓存
        const baseUrl = window.location.origin
        const token = localStorage.getItem('token') || ''
        const url = `${baseUrl}/api/v1/recognition/result/${imageHash}/dislike`
        const headers = { 'Content-Type': 'application/json' }
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }
        
        const response = await fetch(url, { method: 'POST', headers })
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        if (data && data.success) {
            appStore.addNotification({
                type: 'success',
                message: '已删除缓存，将重新执行识别',
                duration: 3000
            })
            
            // 重新执行OCR识别
            recognitionState.value = 'processing'
            processingProgress.value = 0
            processingStatus.value = '准备重新识别...'
            
            // 这里需要获取当前上传的图片文件或URL，然后重新调用startRecognitionApi
            // 由于当前代码中没有保存原始图片文件，我们可以提示用户重新上传
            uploadModalOpen.value = true
        } else {
            const msg = data && data.message ? data.message : '操作失败'
            throw new Error(msg)
        }
    } catch (e) {
        console.error('处理不满意结果失败:', e)
        appStore.addNotification({
            type: 'error',
            message: `操作失败: ${e.message}`,
            duration: 3000
        })
    }
}

const saveAndNavigateToDetails = async (item = null) => {
    const baseUrl = window.location.origin
    const token = localStorage.getItem('token') || ''
    if (!token) {
        appStore.addNotification({
            type: 'warning',
            message: '请先登录以查看详情和编辑',
            duration: 3000
        })
        return
    }

    // 如果是当前结果且已保存，直接跳转
    if (!item && savedInscriptionId.value) {
        router.push(`/my-inscriptions/${savedInscriptionId.value}`)
        return
    }

    try {
        let title, text, image_url, dynasty
        
        if (item) {
            // From history item
            title = (item.inscription_title || item.preview || '识别记录').slice(0, 100)
            text = item.recognition_text || item.preview || ''
            image_url = item.image_path ? `${baseUrl}${item.image_path}` : ''
            dynasty = ''
        } else {
            // From current result
            title = (recognitionResult.value.text || '').slice(0, 20) || '未命名碑文'
            text = recognitionResult.value.text || ''
            image_url = originalImageUrl.value || ''
            dynasty = recognitionResult.value.dynasty || ''
        }

        appStore.addNotification({ type: 'info', message: '正在前往详情页...', duration: 1000 })
        const data = await createInscription({ baseUrl, token, title, text, image_url, dynasty, status: 'active' })
        
        if (data && data.id) {
            if (!item) savedInscriptionId.value = data.id
            router.push(`/my-inscriptions/${data.id}`)
        }
    } catch (e) {
        console.error('进入详情页失败:', e)
        appStore.addNotification({
            type: 'error',
            message: '无法进入详情页，请稍后重试',
            duration: 3000
        })
    }
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
                            <div
                                class="w-24 h-24 bg-secondary/30 rounded-full flex items-center justify-center mb-6 mx-auto">
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
                            <div
                                class="w-24 h-24 bg-secondary/30 rounded-full flex items-center justify-center mb-6 mx-auto">
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
                            <div
                                class="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mb-6 mx-auto">
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
                                <div class="flex justify-center space-x-6 min-w-max md:min-w-0">
                                    <!-- 原始图片列（按当前行拼接裁剪条） -->
                                    <div class="w-64 flex-shrink-0">
                                        <div ref="stripContainerRef"
                                            class="relative bg-gray-100 rounded-lg overflow-hidden border border-gray-200 h-[500px] flex items-start justify-center">
                                            <img v-if="lineStripUrls[currentColumn - 1]"
                                                :src="lineStripUrls[currentColumn - 1]"
                                                class="w-full h-full object-contain" alt="拼接图" />
                                            <div :style="stripOverlayStyle"></div>
                                        </div>
                                        <div class="text-center text-xs text-dark/60 mt-2">
                                            拼接图高亮
                                            <div class="mt-2 flex items-center justify-center gap-2">
                                                <label class="inline-flex items-center gap-1 cursor-pointer text-xs">
                                                    <input type="radio" value="vertical" v-model="previewModeSelection"
                                                        class="sr-only">
                                                    <span
                                                        :class="['px-2 py-1 rounded-full', previewModeSelection === 'vertical' ? 'bg-primary text-white' : 'bg-gray-100 text-dark/70']">竖向拼接</span>
                                                </label>
                                                <label class="inline-flex items-center gap-1 cursor-pointer text-xs">
                                                    <input type="radio" value="horizontal"
                                                        v-model="previewModeSelection" class="sr-only">
                                                    <span
                                                        :class="['px-2 py-1 rounded-full', previewModeSelection === 'horizontal' ? 'bg-primary text-white' : 'bg-gray-100 text-dark/70']">横向拼接</span>
                                                </label>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 识别文字列 -->
                                    <div class="w-32 flex-shrink-0">
                                        <div
                                            class="bg-gray-50 rounded-lg border border-gray-200 h-[500px] p-2 overflow-y-auto">
                                            <div class="space-y-1 text-center">
                                                <div class="mb-2">
                                                    <span v-for="(w, wi) in currentWords" :key="wi"
                                                        class="block py-3 hover:bg-yellow-100 cursor-pointer rounded text-lg"
                                                        @mouseenter="onWordEnter(currentColumn - 1, wi)"
                                                        @mouseleave="onWordLeave"
                                                        @click="showCorrectionPopup($event, w)">
                                                        {{ w.text || w.char || '' }}
                                                        <span class="block text-[10px] text-dark/50">{{
                                                            formatWordConfidence(w) }}%</span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="text-center text-xs text-dark/60 mt-2">识别文字（第 {{ currentColumn }} 列
                                            / 共 {{ totalColumns }} 列）</div>
                                    </div>

                                    <!-- 校正结果列 -->
                                    <div class="w-32 flex-shrink-0">
                                        <div
                                            class="bg-primary/5 rounded-lg border border-primary/20 h-[500px] p-2 overflow-y-auto">
                                            <div class="space-y-2 text-center">
                                                <div v-if="correctionPopup.visible">
                                                    <div class="text-xs text-dark/60 mb-1">候选字</div>
                                                    <span v-for="(c, ci) in correctionPopup.candidates" :key="ci"
                                                        class="block py-2 hover:bg-primary/10 cursor-pointer rounded text-lg"
                                                        @click="selectCandidate(c)">{{ c }}</span>
                                                    <div class="mt-2 flex flex-col items-center gap-2">
                                                        <input v-model="correctionPopup.customInput"
                                                            class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                                                            placeholder="自定义" />
                                                        <button @click="confirmCorrection"
                                                            class="w-full px-2 py-1 bg-primary text-white rounded text-xs">确定</button>
                                                    </div>
                                                </div>
                                                <div v-else class="text-dark/60 text-xs mt-4">点击左侧文字以选择候选字</div>
                                            </div>
                                        </div>
                                        <div class="text-center text-xs text-primary mt-2">校正候选</div>
                                    </div>
                                </div>
                            </div>

                        </div>

                        <!-- 底部操作 -->
                        <div class="flex justify-between">
                            <button @click="prevColumn"
                                class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                <i class="fas fa-arrow-left mr-1"></i>
                                上一页
                            </button>
                            <button @click="saveCorrections"
                                class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-custom">
                                保存校对结果
                            </button>
                            <button @click="nextColumn"
                                class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom">
                                下一页
                                <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                    </div>

                    <!-- 识别结果内容 -->
                    <div v-show="activeTab === 'result'" class="p-6 md:p-8 flex-grow flex flex-col">
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
                                <button @click="dislikeResult"
                                    class="p-2 text-dark/70 hover:text-red-500 hover:bg-gray-100 rounded-md transition-custom"
                                    title="不满意结果">
                                    <i class="fas fa-thumbs-down"></i>
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

                        <div class="border border-gray-200 rounded-lg p-4 min-h-[16rem] md:min-h-[20rem] flex-grow overflow-y-auto mb-6 bg-gray-50">
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

                        </div>
                    </div>

                    <!-- AI阐释内容 -->
                    <div v-show="activeTab === 'interpretation'" class="p-6 md:p-8">
                        <div v-if="sectionsLoading" class="mb-4 flex items-center text-dark/70 text-sm">
                            <i class="fas fa-spinner fa-spin mr-2 text-primary"></i>
                            AI阐释生成中...
                        </div>

                        <!-- 阐释标签页与操作栏 -->
                        <div class="border-b border-gray-200 mb-6 flex flex-col sm:flex-row justify-between items-center gap-4">
                            <nav class="-mb-px flex space-x-8 overflow-x-auto w-full sm:w-auto no-scrollbar">
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
                            
                            <div class="pb-2 w-full sm:w-auto flex justify-end">
                                <button @click="openSaveModal"
                                    class="px-4 py-2 border border-gray-300 text-primary rounded-md hover:bg-primary/5 transition-custom flex items-center font-medium text-sm">
                                    <i class="fas fa-save mr-2"></i>
                                    保存到我的碑文
                                </button>
                            </div>
                        </div>

                        <!-- 阐释内容 -->
                        <div class="grid md:grid-cols-3 gap-8 items-start">
                            <!-- 左侧：主要阐释内容 -->
                            <div class="md:col-span-2 flex flex-col h-full">
                                <div class="flex-grow min-h-[300px]">
                                    <div v-show="interpretationTab === 'history'"
                                        class="prose max-w-none text-dark/90 leading-relaxed mb-6"
                                        v-html="renderMarkdown(sectionsHistory || (sectionsLoading ? '### 正在生成历史背景...\n- 请稍候' : ''))">
                                    </div>
                                    <div v-show="interpretationTab === 'culture'"
                                        class="prose max-w-none text-dark/90 leading-relaxed mb-6"
                                        v-html="renderMarkdown(sectionsCulture || (sectionsLoading ? '### 正在生成文化意义...\n- 请稍候' : ''))">
                                    </div>
                                    <div v-show="interpretationTab === 'people'"
                                        class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                                        <div v-if="sectionsLoading && (!sectionsFigures || !sectionsFigures.length)"
                                            class="text-sm text-dark/60">正在生成相关人物...</div>
                                        <div v-for="p in sectionsFigures" :key="p.name" class="mb-3">
                                            <div class="font-semibold">{{ p.name }} <span class="text-dark/60 text-xs">{{
                                                    p.role }}</span></div>
                                            <div class="text-sm">{{ p.description }}</div>
                                        </div>
                                    </div>
                                    <div v-show="interpretationTab === 'reading'"
                                        class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                                        <div class="text-sm text-dark/60 mb-2">引用来源</div>
                                        <div class="flex flex-wrap gap-2">
                                            <span v-for="(s, i) in sectionsSources" :key="i"
                                                class="text-xs px-2 py-1 bg-secondary/30 text-primary rounded">{{ (s.snippet
                                                || '').slice(0, 32) }}</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- AI对话入口 -->
                                <div class="bg-secondary/30 p-4 rounded-lg border border-secondary mt-auto">
                                    <div class="flex items-start">
                                        <div class="flex-shrink-0 mr-3">
                                            <i class="fas fa-robot text-primary text-xl"></i>
                                        </div>
                                        <div class="flex-grow">
                                            <div class="space-y-3 mb-3 max-h-80 min-h-[60px] overflow-auto custom-scrollbar">
                                                <div v-if="messages.length === 0" class="text-sm text-dark/50 italic py-2">
                                                    对碑文内容有疑问？在这里提问，AI将为您解答...
                                                </div>
                                                <div v-for="m in messages" :key="m.id"
                                                    :class="m.role === 'user' ? 'text-right' : 'text-left'">
                                                    <div
                                                        :class="m.role === 'user' ? 'inline-block px-3 py-2 rounded-lg bg-primary text-white' : 'inline-block px-3 py-2 rounded-lg bg-white border border-gray-200 text-dark'">
                                                        <span v-if="m.role === 'user'"
                                                            class="whitespace-pre-line text-sm">{{ m.content }}</span>
                                                        <div v-else class="prose text-sm"
                                                            v-html="renderMarkdown(m.content)"></div>
                                                        <i v-if="m.role === 'assistant' && m.status === 'sending'"
                                                            class="fas fa-spinner fa-spin ml-2 text-primary"></i>
                                                    </div>
                                                    <div v-if="m.role === 'assistant' && m.references && m.references.length"
                                                        class="mt-1">
                                                        <span v-for="(s, i) in m.references" :key="i"
                                                            class="inline-block mr-1 mb-1 text-xs px-2 py-1 bg-secondary/30 text-primary rounded">{{
                                                            (s.snippet || '').slice(0, 24) }}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="flex">
                                                <input v-model="aiQuestion" type="text" placeholder="请输入您的问题..."
                                                    @keyup.enter="sendAiQuestion"
                                                    class="flex-grow px-4 py-2 rounded-l-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" />
                                                <button @click="sendAiQuestion"
                                                    class="bg-primary text-white px-4 py-2 rounded-r-md hover:bg-primary/90 transition-custom"
                                                    :disabled="aiLoading">
                                                    <i class="fas fa-paper-plane"></i>
                                                </button>
                                            </div>
                                            <div v-if="aiLoading" class="mt-3 text-sm text-dark/60">正在生成...</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 右侧：相关信息 -->
                            <div class="space-y-6 md:sticky md:top-6 md:self-start">
                                <!-- 时间线 -->
                                <div class="bg-light p-5 rounded-xl border border-gray-100">
                                    <h4 class="text-lg font-semibold text-primary mb-4 flex items-center">
                                        <i class="fas fa-history mr-2"></i>
                                        相关时间线
                                    </h4>
                                    <div v-if="timeline && timeline.length" class="space-y-4 max-h-[250px] overflow-y-auto custom-scrollbar pr-2">
                                        <div v-for="(item, index) in timeline" :key="index" class="flex">
                                            <div class="flex-shrink-0 w-12 text-right pr-2 relative">
                                                <span
                                                    class="inline-block w-2.5 h-2.5 bg-primary rounded-full absolute right-0 top-1.5 translate-x-1/2 z-10"></span>
                                                <span class="text-xs font-medium text-primary block leading-tight">{{ item.year }}</span>
                                            </div>
                                            <div
                                                :class="['flex-grow border-l border-gray-200 pl-3 -ml-[5px]', index < timeline.length - 1 ? 'pb-4' : '']">
                                                <p class="text-dark/80 text-sm leading-relaxed">{{ item.event }}</p>
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
                                    <div v-if="sectionsFigures && sectionsFigures.length" class="space-y-3 max-h-[250px] overflow-y-auto custom-scrollbar pr-2">
                                        <div v-for="p in sectionsFigures" :key="p.name"
                                            class="flex items-center p-2 hover:bg-white rounded-md transition-custom cursor-pointer">
                                            <div
                                                class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mr-3 flex-shrink-0">
                                                <i class="fas fa-user text-primary"></i>
                                            </div>
                                            <div>
                                                <p class="font-medium text-dark">{{ p.name }}</p>
                                                <p class="text-xs text-dark/60">{{ p.role }}</p>
                                                <p class="text-xs text-dark/60 mt-1" v-if="p.description">{{
                                                    p.description }}</p>
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
                
                <!-- 加载状态 -->
                <div v-if="isLoadingRecommendations" class="flex justify-center items-center py-10">
                    <div class="text-center">
                        <i class="fas fa-spinner fa-spin text-2xl text-primary mb-2"></i>
                        <p class="text-dark/60">加载中...</p>
                    </div>
                </div>
                
                <!-- 空数据状态 -->
                <div v-else-if="recommendations.length === 0" class="flex justify-center items-center py-10">
                    <div class="text-center text-dark/60">
                        <i class="fas fa-lightbulb mb-2 text-xl"></i>
                        <p>暂无相关碑文推荐</p>
                    </div>
                </div>
                
                <!-- 数据列表 -->
                <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div v-for="item in recommendations" :key="item.id"
                        class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-custom border border-gray-100 cursor-pointer">
                        <!-- 图片显示 -->
                        <div class="h-48 overflow-hidden bg-gray-100">
                            <!-- 从excerpt中提取图片链接 -->
                            <img 
                                v-if="item.cover_image || (item.excerpt && item.excerpt.includes('图片链接：'))" 
                                :src="item.cover_image || (item.excerpt.match(/- 图片链接：(.*?)\n/)?.[1] || '')" 
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
                            <router-link 
                                :to="`/knowledge/article/${item.id}`" 
                                class="text-primary text-sm font-medium flex items-center hover:text-accent transition-custom"
                            >
                                查看详情
                                <i class="fas fa-arrow-right ml-2 text-xs"></i>
                            </router-link>
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
                    
                    <!-- 加载状态 -->
                    <div v-if="isLoadingHistory" class="flex justify-center items-center py-10">
                        <div class="text-center">
                            <i class="fas fa-spinner fa-spin text-2xl text-primary mb-2"></i>
                            <p class="text-dark/60">加载中...</p>
                        </div>
                    </div>
                    
                    <!-- 空数据状态 -->
                    <div v-else-if="recentHistory.length === 0" class="flex justify-center items-center py-10">
                        <div class="text-center text-dark/60">
                            <i class="fas fa-inbox mb-2 text-xl"></i>
                            <p>暂无识别记录</p>
                        </div>
                    </div>
                    
                    <!-- 数据列表 -->
                    <div v-else>
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
                                            <div class="w-12 h-12 rounded bg-gray-100 overflow-hidden relative">
                                                <img v-if="item.image_path" 
                                                     :src="`${baseUrl}${item.image_path}`" 
                                                     :alt="item.preview" 
                                                     class="w-full h-full object-cover"
                                                     @error="$event.target.style.display = 'none'"
                                                />
                                                <i v-else class="fas fa-image text-gray-400 absolute w-12 h-12 flex items-center justify-center"></i>
                                            </div>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="text-sm text-dark line-clamp-2 max-w-xs">{{ item.preview || '无识别内容' }}</div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-dark/70">{{ item.date || item.created_at }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                                                {{ item.confidence }}%
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button @click="saveAndNavigateToDetails(item)"
                                                class="text-primary hover:text-accent mr-3 transition-custom">查看详情</button>
                                            <button class="text-dark/70 hover:text-dark transition-custom">删除</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                            <div class="text-sm text-dark/70">显示 {{ (currentPage - 1) * pageSize + 1 }} 至 {{ Math.min(currentPage * pageSize, totalRecords) }}，共 {{ totalRecords }} 条记录</div>
                            <div class="flex space-x-1">
                                <button
                                    class="px-3 py-1 border border-gray-300 rounded-md text-dark/50 hover:bg-gray-100 disabled:opacity-50"
                                    :disabled="currentPage === 1">
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

            <!-- 查看识别记录弹窗 -->
            <teleport to="body">
                <transition name="modal-fade">
                    <div v-if="viewModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <div @click="closeViewModal" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
                        <div class="relative bg-white rounded-xl shadow-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                            <div
                                class="p-6 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white z-10">
                                <h3 class="text-xl font-semibold text-dark">识别记录详情</h3>
                                <button @click="closeViewModal" class="text-dark/70 hover:text-dark transition-custom">
                                    <i class="fas fa-times text-xl"></i>
                                </button>
                            </div>
                            <div class="p-6">
                                <!-- 识别图片 -->
                                <div class="mb-6">
                                    <h4 class="text-lg font-semibold text-dark mb-3">识别图片</h4>
                                    <div class="bg-gray-100 rounded-lg overflow-hidden">
                                        <img v-if="currentViewItem.image_path" 
                                             :src="`${baseUrl}${currentViewItem.image_path}`" 
                                             :alt="currentViewItem.preview" 
                                             class="w-full h-auto max-h-96 object-contain"
                                        />
                                        <div v-else class="h-64 bg-gray-100 flex items-center justify-center">
                                            <i class="fas fa-image text-gray-300 text-5xl"></i>
                                        </div>
                                    </div>
                                </div>
                                <!-- 识别结果 -->
                                <div>
                                    <h4 class="text-lg font-semibold text-dark mb-3">识别结果</h4>
                                    <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 text-dark/90 whitespace-pre-wrap">
                                        {{ currentViewItem.recognition_text || '暂无识别文本' }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </transition>
            </teleport>
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

                            <div class="mb-6">
                                <div class="flex items-center gap-4 mb-3">
                                    <span class="text-sm text-dark/70">排版样式</span>
                                    <label class="inline-flex items-center gap-2 cursor-pointer">
                                        <input type="radio" value="sp" v-model="detModeSelection" class="sr-only">
                                        <span
                                            :class="['px-3 py-1 rounded-full text-sm', detModeSelection === 'sp' ? 'bg-primary text-white' : 'bg-gray-100 text-dark/70']">竖排</span>
                                    </label>
                                    <label class="inline-flex items-center gap-2 cursor-pointer">
                                        <input type="radio" value="hp" v-model="detModeSelection" class="sr-only">
                                        <span
                                            :class="['px-3 py-1 rounded-full text-sm', detModeSelection === 'hp' ? 'bg-primary text-white' : 'bg-gray-100 text-dark/70']">横排</span>
                                    </label>
                                </div>
                                <div class="flex items-center gap-3">
                                    <span class="text-sm text-dark/70">文字排序方向</span>
                                    <select v-model="directionSelection"
                                        class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary">
                                        <option v-for="opt in directionOptions" :key="opt.id" :value="opt.id">{{
                                            opt.label }}</option>
                                    </select>
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
    line-clamp: 2;
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
