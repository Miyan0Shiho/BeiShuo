<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
// 导入修复后的具体服务
import { 
  uploadImage, 
  startRecognition as startRecognitionAPI,
  getRecognitionProgress,
  getRecognitionHistory,
  getRecognitionDetail,
  deleteRecognition,
  exportRecognitions,
  shareRecognition as shareRecognitionAPI,
  getSharedRecognition
} from '../services/recognitionService.js'
import { 
  getInterpretation,
  aiChat,
  getRecommendations,
  batchInterpretation
} from '../services/aiService.js'
import { 
  addFavorite,
  deleteFavorite as removeFavorite,
  getFavorites
} from '../services/favoriteService.js'
// 保留必要的Mock API用于降级方案
import { 
  mockGetRecognitionHistory,
  mockGetAIInterpretation,
  mockChatWithAI,
  mockAddFavorite,
  setResponseScenario
} from '../mock/mockApi.js'

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
const isCancelInProgress = ref(false) // 取消操作状态

// 图片上传
const fileInput = ref(null)
const modalFileInput = ref(null)
const selectedFiles = ref([]) // 改为支持多文件
const uploadProgress = ref(0) // 实时上传进度
const isDragging = ref(false) // 拖拽状态
const isUploading = ref(false) // 上传状态
const previewMode = ref('grid') // 预览模式：grid/list
const dragCounter = ref(0) // 拖拽计数器（处理嵌套拖拽）

// 新增：拖拽区域引用
const dropZoneRef = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const dragActive = ref(false)

// 识别结果数据
const recognitionResult = ref({
    text: '',
    wordCount: 0,
    confidence: 0,
    dynasty: '',
    year: '',
    location: '',
    time: ''
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

// AI阐释相关数据
const aiInterpretation = ref({
    history: [],
    culture: [],
    people: [],
    reading: []
})
const isLoadingInterpretation = ref(false)
const aiChatHistory = ref([])
const currentAIQuestion = ref('')

// 保存表单
const saveForm = ref({
    title: '',
    tags: []
})

const availableTags = ['汉代碑文', '唐代碑文', '宋代碑文', '名人碑刻', '地方历史']

// 历史记录
const recentHistory = ref([])

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
    // 清除多文件选择
    selectedFiles.value.forEach(fileItem => {
        if (fileItem.previewUrl) {
            URL.revokeObjectURL(fileItem.previewUrl)
        }
    })
    selectedFiles.value = []
    isDragging.value = false
    dragCounter.value = 0
    uploadProgress.value = 0
    previewMode.value = 'grid'
}

const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    processFiles(files)
}

// 创建压缩后的预览图
const createCompressedPreview = (file) => {
    return new Promise((resolve, reject) => {
        if (file.size < 500 * 1024) { // 小于500KB的文件直接使用原图预览
            resolve(URL.createObjectURL(file))
            return
        }
        
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = (event) => {
            const img = new Image()
            img.src = event.target.result
            img.onload = () => {
                // 创建canvas用于压缩
                const canvas = document.createElement('canvas')
                const ctx = canvas.getContext('2d')
                
                // 计算压缩尺寸，保持宽高比
                const maxDimension = 800 // 最大预览尺寸为800px
                let width = img.width
                let height = img.height
                
                if (width > height && width > maxDimension) {
                    height *= maxDimension / width
                    width = maxDimension
                } else if (height > maxDimension) {
                    width *= maxDimension / height
                    height = maxDimension
                }
                
                canvas.width = width
                canvas.height = height
                
                // 绘制压缩图像
                ctx.drawImage(img, 0, 0, width, height)
                
                // 将canvas转换为dataURL（质量控制）
                const quality = file.size > 2 * 1024 * 1024 ? 0.7 : 0.9
                const compressedDataUrl = canvas.toDataURL(file.type, quality)
                
                resolve(compressedDataUrl)
            }
            img.onerror = reject
        }
        reader.onerror = reject
    })
}

// 压缩图片文件（用于上传）
const compressImage = async (file) => {
    // 文件小于1MB不需要压缩
    if (file.size < 1024 * 1024) {
        return file
    }
    
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = (event) => {
            const img = new Image()
            img.src = event.target.result
            img.onload = () => {
                const canvas = document.createElement('canvas')
                const ctx = canvas.getContext('2d')
                
                // 确定压缩尺寸和质量
                let width = img.width
                let height = img.height
                let quality = 0.8
                
                // 根据原文件大小动态调整压缩质量和尺寸
                if (file.size > 5 * 1024 * 1024) {
                    quality = 0.6
                    // 大文件进行尺寸压缩
                    const maxDimension = 1600
                    if (width > height && width > maxDimension) {
                        height *= maxDimension / width
                        width = maxDimension
                    } else if (height > maxDimension) {
                        width *= maxDimension / height
                        height = maxDimension
                    }
                }
                
                canvas.width = width
                canvas.height = height
                ctx.drawImage(img, 0, 0, width, height)
                
                // 将canvas转换为Blob
                canvas.toBlob((blob) => {
                    if (blob) {
                        const compressedFile = new File([blob], file.name, { type: file.type })
                        resolve(compressedFile)
                    } else {
                        resolve(file) // 如果压缩失败，返回原文件
                    }
                }, file.type, quality)
            }
            img.onerror = reject
        }
        reader.onerror = reject
    })
}

// 文件处理队列
const fileProcessingQueue = []
let isProcessingQueue = false

const processQueue = async () => {
    if (isProcessingQueue || fileProcessingQueue.length === 0) return
    
    isProcessingQueue = true
    
    while (fileProcessingQueue.length > 0) {
        const { file, callback, errorCallback } = fileProcessingQueue.shift()
        try {
            await callback(file)
        } catch (error) {
            errorCallback(error)
        }
        // 短暂延迟避免浏览器卡顿
        await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    isProcessingQueue = false
}

// 优化的批量文件处理
const processFiles = async (files) => {
    const validFiles = []
    const errors = []
    
    // 限制同时处理的文件数量
    if (selectedFiles.value.length + files.length > 10) {
        appStore.addNotification({
            type: 'warning',
            message: '最多同时处理10个文件，请分批上传',
            duration: 3000
        })
        // 只处理能容纳的文件数量
        files = files.slice(0, 10 - selectedFiles.value.length)
    }

    // 批量文件验证
    files.forEach(file => {
        // 验证文件类型
        const validTypes = ['image/jpeg', 'image/png', 'image/webp']
        if (!validTypes.includes(file.type)) {
            errors.push(`${file.name}: 不支持的文件格式，请选择JPG、PNG或WEBP图片`)
            return
        }

        // 验证文件大小
        if (file.size > 10 * 1024 * 1024) {
            errors.push(`${file.name}: 文件大小超过10MB限制`)
            return
        }

        // 添加到处理队列
        const fileId = Date.now() + Math.random()
        const fileItem = {
            id: fileId,
            file: file,
            previewUrl: null, // 稍后异步设置
            name: file.name,
            size: file.size,
            type: file.type,
            uploaded: false,
            processing: false,
            originalFile: file,
            compressedFile: null // 稍后异步设置
        }
        
        validFiles.push(fileItem)
        
        // 添加到处理队列进行异步预览生成和压缩
        fileProcessingQueue.push({
            file: fileItem,
            callback: async (fileItem) => {
                try {
                    // 生成压缩预览
                    fileItem.previewUrl = await createCompressedPreview(fileItem.file)
                    
                    // 对于大文件进行压缩（后台进行，不阻塞UI）
                    if (fileItem.size > 1024 * 1024) {
                        fileItem.processing = true
                        fileItem.compressedFile = await compressImage(fileItem.file)
                        fileItem.processing = false
                    }
                } catch (error) {
                    console.error('处理文件时出错:', error)
                    // 使用原图作为备选
                    if (!fileItem.previewUrl) {
                        fileItem.previewUrl = URL.createObjectURL(fileItem.file)
                    }
                }
            },
            errorCallback: (error) => {
                console.error('队列处理错误:', error)
                // 降级到直接使用原始URL
                fileItem.previewUrl = URL.createObjectURL(fileItem.file)
            }
        })
    })

    // 显示错误信息
    if (errors.length > 0) {
        appStore.addNotification({
            type: 'error',
            message: errors.join('\n'),
            duration: 5000
        })
    }

    // 添加有效文件到选择列表
    if (validFiles.length > 0) {
        selectedFiles.value = [...selectedFiles.value, ...validFiles]
        
        // 开始处理队列
        processQueue()
        
        // 显示成功提示
        appStore.addNotification({
            type: 'success',
            message: `已添加 ${validFiles.length} 个有效文件`,
            duration: 2000
        })
    }
    
    // 添加文件处理完成事件
    const fileList = document.querySelector('.file-list')
    if (fileList) {
        fileList.style.opacity = '1'
    }
}

const processFile = (file) => {
    // 兼容单文件选择
    processFiles([file])
}

// 新增：增强的拖拽功能
const handleDragEnter = (event) => {
    event.preventDefault()
    dragCounter.value++
    
    if (dragCounter.value === 1) {
        isDragging.value = true
    }
}

const handleDragOver = (event) => {
    event.preventDefault()
    event.stopPropagation()
}

const handleDragLeave = (event) => {
    event.preventDefault()
    dragCounter.value--
    
    if (dragCounter.value === 0) {
        isDragging.value = false
    }
}

const handleDrop = (event) => {
    event.preventDefault()
    event.stopPropagation()
    
    dragCounter.value = 0
    isDragging.value = false
    
    const files = Array.from(event.dataTransfer.files)
    if (files.length > 0) {
        processFiles(files)
    }
}

const removeFile = (fileId) => {
    const index = selectedFiles.value.findIndex(f => f.id === fileId)
    if (index !== -1) {
        URL.revokeObjectURL(selectedFiles.value[index].previewUrl)
        selectedFiles.value.splice(index, 1)
    }
    
    // 清空文件输入
    if (modalFileInput.value) {
        modalFileInput.value.value = ''
    }
}

const clearAllFiles = () => {
    // 清理所有预览URL
    selectedFiles.value.forEach(file => {
        URL.revokeObjectURL(file.previewUrl)
    })
    selectedFiles.value = []
    
    // 清空文件输入
    if (modalFileInput.value) {
        modalFileInput.value.value = ''
    }
}

const getFileSizeString = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const previewModeToggle = () => {
    previewMode.value = previewMode.value === 'grid' ? 'list' : 'grid'
}

// 重复的拖拽函数已移除，保留上方的版本

const removePreviewImage = () => {
    previewUrl.value = ''
    selectedFile.value = null
    if (selectedFiles.value && selectedFiles.value.length > 0) {
        // 清理所有预览URL
        selectedFiles.value.forEach(fileItem => {
            if (fileItem.previewUrl) {
                URL.revokeObjectURL(fileItem.previewUrl)
            }
        })
        selectedFiles.value = []
    }
    if (modalFileInput.value) {
        modalFileInput.value.value = ''
    }
}

const confirmUpload = () => {
    if (!selectedFiles.value || selectedFiles.value.length === 0) {
        appStore.addNotification({
            type: 'error',
            message: '请先选择图片',
            duration: 2000
        })
        return
    }

    // 先备份当前要处理的文件
    const fileToProcess = selectedFiles.value[0]
    
    // 保存文件引用，避免被 closeUploadModal 清空
    selectedFile.value = fileToProcess.file // 保存原始File对象
    
    // 关闭模态框（在开始识别之后）
    startRecognition()
    
    // 确保在识别过程中不会重复关闭模态框
    setTimeout(() => {
        if (uploadModalOpen.value) {
            closeUploadModal()
        }
    }, 100)
}

const startRecognition = async () => {
    // 确保有文件用于识别（优先使用selectedFile，然后尝试从selectedFiles获取）
    let fileToProcess = selectedFile.value
    
    // 如果selectedFile不存在，尝试从selectedFiles中获取
    if (!fileToProcess && selectedFiles.value && selectedFiles.value.length > 0) {
        // 确保获取到原始File对象
        const fileItem = selectedFiles.value[0]
        fileToProcess = fileItem.file || fileItem.originalFile
        selectedFile.value = fileToProcess // 同步保存
    }
    
    if (!fileToProcess) {
        appStore.addNotification({
            type: 'error',
            message: '请先选择图片',
            duration: 2000
        })
        return
    }

    recognitionState.value = 'processing'
    processingProgress.value = 0
    processingStatus.value = '开始识别图片...'

    try {
        processingStatus.value = '上传图片到服务器...'
        processingProgress.value = 10
        
        // 1. 上传图片（优先使用压缩后的文件，提高上传速度）
        const uploadFormData = new FormData()
        
        // 查找对应的fileItem以获取可能存在的compressedFile
        let fileToUpload = fileToProcess
        if (selectedFiles.value && selectedFiles.value.length > 0) {
            const fileItem = selectedFiles.value.find(item => 
                item.file === fileToProcess || item.originalFile === fileToProcess
            )
            
            if (fileItem && fileItem.compressedFile) {
                fileToUpload = fileItem.compressedFile
                console.log(`使用压缩文件上传: ${fileToUpload.size} bytes (原文件: ${fileToProcess.size} bytes)`)
            }
        }
        
        uploadFormData.append('image', fileToUpload)
        uploadFormData.append('type', 'inscription')
        // 添加是否使用压缩文件的标记
        uploadFormData.append('is_compressed', fileToUpload !== fileToProcess)
        
        const uploadResponse = await uploadImage(uploadFormData)
        
        if (!uploadResponse.success) {
            throw new Error('图片上传失败: ' + (uploadResponse.message || '未知错误'))
        }
        
        const { file_id } = uploadResponse.data
        
        processingStatus.value = '开始识别...'
        processingProgress.value = 30
        
        // 2. 开始识别
        const recognitionStartResponse = await startRecognitionAPI({
            file_id: file_id,
            type: 'inscription',
            options: {
                enhance_quality: true,
                recognize_character: true
            }
        })
        
        if (!recognitionStartResponse.success) {
            throw new Error('开始识别失败: ' + (recognitionStartResponse.message || '未知错误'))
        }
        
        const { task_id } = recognitionStartResponse.data
        
        // 添加取消识别控制变量
        let isCanceled = false
        
        // 取消识别函数（供UI调用）
        const cancelRecognition = () => {
            isCanceled = true
            processingStatus.value = '正在取消识别...'
            // 可选：通知服务器取消任务
            try {
                cancelRecognitionTask(task_id)
            } catch (error) {
                console.log('取消任务通知失败:', error)
            }
        }
        
        // 暴露取消函数给外部
        window.currentRecognitionTask = cancelRecognition
        
        // 3. 优化的轮询获取识别进度（智能退避算法）
        let progressResponse
        const maxRetries = 60 // 最大重试次数
        let retryCount = 0
        let errorCount = 0
        const maxErrors = 3 // 最大错误重试次数
        
        // 状态提示映射
        const statusMessages = {
            'preprocessing': '预处理图片...',
            'recognizing': '文字识别中...',
            'postprocessing': '后处理结果...',
            'extracting_metadata': '提取元数据...'
        }
        
        while (retryCount < maxRetries && !isCanceled) {
            // 智能退避算法：初始0.5秒，逐步增加到2秒
            const baseDelay = 500
            const maxDelay = 2000
            const currentDelay = Math.min(baseDelay + (retryCount * 50), maxDelay)
            
            await new Promise(resolve => setTimeout(resolve, currentDelay))
            
            try {
                progressResponse = await getRecognitionProgress(task_id)
                
                if (!progressResponse.success) {
                    errorCount++
                    console.warn(`获取进度失败(${errorCount}/${maxErrors}):`, progressResponse.message)
                    
                    if (errorCount >= maxErrors) {
                        throw new Error('获取识别进度失败次数过多: ' + (progressResponse.message || '未知错误'))
                    }
                    
                    // 短暂延迟后重试
                    await new Promise(resolve => setTimeout(resolve, 1000))
                    continue
                }
                
                // 重置错误计数
                errorCount = 0
                
                const { progress, status, result } = progressResponse.data
                
                // 更新进度和状态（使用友好提示）
                const displayProgress = Math.min(progress * 100, 90)
                processingProgress.value = displayProgress
                
                // 使用友好的状态提示
                const displayStatus = statusMessages[status] || `识别中 (${Math.round(displayProgress)}%)`
                processingStatus.value = displayStatus
                
                // 进度增加时提供更详细的反馈
                if (retryCount > 0 && retryCount % 5 === 0) {
                    const estimatedTime = Math.round((1 - progress) * 10) // 估算剩余时间（秒）
                    if (estimatedTime > 0) {
                        console.log(`进度: ${Math.round(displayProgress)}%, 预计剩余时间: ~${estimatedTime}秒`)
                    }
                }
                
                // 如果识别完成
                if (status === 'completed' && result) {
                    processingProgress.value = 95
                    processingStatus.value = '处理识别结果...'
                    
                    // 处理识别结果
                    recognitionResult.value = {
                        text: result.text || '识别结果为空',
                        wordCount: result.text?.length || 0,
                        confidence: result.confidence || 0,
                        dynasty: result.metadata?.dynasty || '待识别',
                        year: result.metadata?.year || '待识别',
                        location: result.metadata?.location || '待识别',
                        time: new Date().toLocaleString('zh-CN'),
                        service: '真实OCR服务',
                        words: result.words || [], // 字符级识别结果
                        recognition_id: result.id // 保存识别ID用于后续操作
                    }
                    
                    // 清理取消函数引用
                    delete window.currentRecognitionTask
                    isCancelInProgress.value = false
                    break
                }
                
                // 如果识别失败
                if (status === 'failed') {
                    throw new Error('识别失败: ' + (result?.error_message || '未知错误'))
                }
                
            } catch (error) {
                errorCount++
                console.error(`轮询错误(${errorCount}/${maxErrors}):`, error)
                
                if (errorCount >= maxErrors) {
                    delete window.currentRecognitionTask
                    isCancelInProgress.value = false
                    throw error
                }
                
                // 指数退避重试
                const backoffDelay = 1000 * Math.pow(2, errorCount - 1)
                console.log(`将在 ${backoffDelay}ms 后重试...`)
                await new Promise(resolve => setTimeout(resolve, backoffDelay))
            }
            
            retryCount++
        }
        
        // 清理取消函数引用
        delete window.currentRecognitionTask
        isCancelInProgress.value = false
        
        if (isCanceled) {
            isCancelInProgress.value = false
            throw new Error('识别已取消')
        }
        
        if (retryCount >= maxRetries) {
            throw new Error('识别超时，请重试')
        }
        
        processingProgress.value = 100
        processingStatus.value = '识别完成'
        
        setTimeout(() => {
            recognitionState.value = 'completed'
        }, 500)
        
        // 获取AI阐释
        if (recognitionResult.value.text) {
            await fetchAIInterpretation()
        }
        
        appStore.addNotification({
            type: 'success',
            message: `碑文识别完成，识别到 ${recognitionResult.value.wordCount} 个字符，置信度 ${(recognitionResult.value.confidence * 100).toFixed(1)}%`,
            duration: 3000
        })
    } catch (error) {
        // 处理错误并重置取消状态
        isCancelInProgress.value = false
        console.error('碑文识别失败:', error)
        
        // 降级处理：如果API服务失败，回退到模拟识别
        processingStatus.value = 'API服务暂不可用，使用模拟识别...'
        
        try {
            // 使用模拟识别作为降级方案
            await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟处理时间
            
            const mockResult = {
                text: "维太平之元，岁在丁卯，三月乙丑，予与二三子游于崇山峻岭之间，观天地之悠悠，感古今之变化，忆先贤之功德，思来者之无穷。",
                confidence: 0.85,
                service: '模拟识别',
                words: [],
                recognition_id: `mock-${Date.now()}`
            }
            
            recognitionResult.value = {
                ...mockResult,
                wordCount: mockResult.text.length,
                dynasty: '唐代',
                year: '天宝年间',
                location: '长安',
                time: new Date().toLocaleString('zh-CN')
            }
            
            processingProgress.value = 100
            processingStatus.value = '模拟识别完成'
            
            setTimeout(() => {
                recognitionState.value = 'completed'
            }, 500)
            
            appStore.addNotification({
                type: 'warning',
                message: 'API服务暂不可用，已切换到模拟识别模式',
                duration: 5000
            })
            
            // 获取模拟AI阐释
            if (recognitionResult.value.text) {
                await fetchAIInterpretation()
            }
            
        } catch (mockError) {
            // 如果连模拟都失败了
            recognitionState.value = 'waiting'
            processingProgress.value = 0
            processingStatus.value = '准备识别...'
            
            appStore.addNotification({
                type: 'error',
                message: error.message || '碑文识别失败，请检查网络连接或重试',
                duration: 5000
            })
        }
    }
}

const viewResults = () => {
    activeTab.value = 'result'
}

const switchTab = (tab) => {
    activeTab.value = tab
}

// 处理取消识别操作
const handleCancelRecognition = () => {
    // 显示确认对话框
    if (!confirm('确定要取消当前识别任务吗？')) {
        return
    }
    
    // 设置取消状态
    isCancelInProgress.value = true
    processingStatus.value = '正在取消识别...'
    
    // 调用当前任务的取消函数（如果存在）
    if (window.currentRecognitionTask && typeof window.currentRecognitionTask === 'function') {
        try {
            window.currentRecognitionTask()
            console.log('取消识别请求已发送')
        } catch (cancelError) {
            console.error('取消操作失败:', cancelError)
            isCancelInProgress.value = false
            
            // 显示错误通知
            appStore.addNotification({
                type: 'error',
                message: '取消识别失败，请稍后重试',
                duration: 2000
            })
        }
    } else {
        // 降级方案：直接重置状态
        console.warn('无法获取取消函数，使用降级方案')
        setTimeout(() => {
            resetRecognitionState()
            appStore.addNotification({
                type: 'info',
                message: '识别已取消',
                duration: 2000
            })
        }, 500)
    }
}

// 重置识别状态
const resetRecognitionState = () => {
    recognitionState.value = 'waiting'
    processingProgress.value = 0
    processingStatus.value = '准备识别...'
    isCancelInProgress.value = false
    
    // 清理取消函数引用
    if (window.currentRecognitionTask) {
        delete window.currentRecognitionTask
    }
}

const switchInterpretationTab = (tab) => {
    interpretationTab.value = tab
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

const shareRecognition = () => {
    const shareText = `我在碑文识别中发现了这段文字：${recognitionResult.value.text.substring(0, 50)}...`
    
    if (navigator.share) {
        // 使用Web Share API
        navigator.share({
            title: '碑文识别结果',
            text: shareText,
            url: window.location.href
        }).catch(err => {
            console.log('分享失败:', err)
            // 降级到复制到剪贴板
            copyToClipboard(shareText)
        })
    } else {
        // 降级到复制到剪贴板
        copyToClipboard(shareText)
    }
}

const copyToClipboard = (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            appStore.addNotification({
                type: 'success',
                message: '已复制分享内容到剪贴板',
                duration: 2000
            })
        }).catch(() => {
            fallbackCopyToClipboard(text)
        })
    } else {
        fallbackCopyToClipboard(text)
    }
}

const fallbackCopyToClipboard = (text) => {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    try {
        document.execCommand('copy')
        appStore.addNotification({
            type: 'success',
            message: '已复制分享内容到剪贴板',
            duration: 2000
        })
    } catch (err) {
        appStore.addNotification({
            type: 'error',
            message: '复制失败，请手动复制分享内容',
            duration: 3000
        })
    }
    
    document.body.removeChild(textArea)
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

const triggerFileInput = () => {
    modalFileInput.value?.click()
}

// 获取AI阐释
const fetchAIInterpretation = async () => {
    if (!recognitionResult.value.text) return
    
    try {
        isLoadingInterpretation.value = true
        
        // 尝试使用真实API获取AI阐释
        const response = await getInterpretation({
            text: recognitionResult.value.text,
            type: 'inscription',
            dynasty: recognitionResult.value.dynasty === '待识别' ? null : recognitionResult.value.dynasty,
            year: recognitionResult.value.year === '待识别' ? null : recognitionResult.value.year,
            location: recognitionResult.value.location === '待识别' ? null : recognitionResult.value.location,
            recognition_id: recognitionResult.value.recognition_id || null
        })
        
        if (response.success) {
            aiInterpretation.value = response.data
            
            // 更新时间线和相关人物数据
            timeline.value = response.data.timeline || []
            relatedFigures.value = response.data.figures || []
            
            // 获取相关推荐
            try {
                const recommendationsResponse = await searchAIKnowledge({
                    query: recognitionResult.value.text.substring(0, 50),
                    type: 'inscription',
                    dynasty: recognitionResult.value.dynasty === '待识别' ? null : recognitionResult.value.dynasty,
                    limit: 3
                })
                
                if (recommendationsResponse.success) {
                    recommendations.value = recommendationsResponse.data.results || []
                }
            } catch (recommendError) {
                console.warn('获取推荐内容失败，使用备用数据:', recommendError)
                recommendations.value = []
            }
        } else {
            throw new Error(response.message || '获取AI阐释失败')
        }
        
    } catch (error) {
        console.error('真实API获取AI阐释失败，使用模拟数据:', error)
        
        // 降级处理：使用模拟数据
        try {
            // 完全使用Mock模式获取AI阐释作为降级方案
            const mockData = await mockGetAIInterpretation({
                text: recognitionResult.value.text,
                context: {
                    dynasty: recognitionResult.value.dynasty || '明代',
                    year: recognitionResult.value.year || '永乐年间',
                    location: recognitionResult.value.location || '北京'
                },
                aspects: ['history', 'culture', 'people', 'reading']
            })
            
            aiInterpretation.value = mockData
            timeline.value = mockData.timeline || []
            relatedFigures.value = mockData.figures || []
            
            // 获取模拟推荐
            const mockRecommendations = await mockGetRecommendations({
                text: recognitionResult.value.text,
                context: {
                    dynasty: recognitionResult.value.dynasty || '明代'
                }
            })
            recommendations.value = mockRecommendations.data || []
            
            // 显示降级提示
            appStore.addNotification({
                type: 'info',
                message: '使用模拟AI阐释数据',
                duration: 3000
            })
            
        } catch (mockError) {
            // 如果连模拟都失败了，提供默认备用数据
            appStore.addNotification({
                type: 'warning',
                message: 'AI阐释生成中，使用备用数据',
                duration: 3000
            })
            
            aiInterpretation.value = {
                history: [
                    {
                        title: '历史背景',
                        content: '这段碑文内容反映了古代文化的重要价值，对于研究历史具有重要意义。'
                    },
                    {
                        title: '文化意义',
                        content: '碑文作为古代文字记录的重要形式，保存了大量珍贵的历史信息和文化遗产。'
                    }
                ],
                timeline: [],
                figures: []
            }
            timeline.value = aiInterpretation.value.timeline || []
            relatedFigures.value = aiInterpretation.value.figures || []
            recommendations.value = []
        }
    } finally {
        isLoadingInterpretation.value = false
    }
}

// 发送AI问题
const sendAiQuestion = async () => {
    if (!aiQuestion.value.trim() || !recognitionResult.value.text) return
    
    const question = aiQuestion.value.trim()
    const userMessage = { 
        type: 'user', 
        content: question, 
        time: new Date().toLocaleString('zh-CN') 
    }
    
    aiChatHistory.value.push(userMessage)
    currentAIQuestion.value = question
    aiQuestion.value = ''
    
    try {
        appStore.addNotification({
            type: 'info',
            message: 'AI正在思考您的问题...',
            duration: 2000
        })
        
        // 尝试使用真实API进行AI对话
        const response = await aiChat({
            question: question,
            context: recognitionResult.value.text,
            recognition_id: recognitionResult.value.recognition_id || null,
            type: 'inscription',
            conversation_history: aiChatHistory.value.slice(-5).map(msg => ({
                role: msg.type === 'user' ? 'user' : 'assistant',
                content: msg.content
            }))
        })
        
        if (response.success) {
            const aiMessage = { 
                type: 'ai', 
                content: response.data.answer,
                time: new Date().toLocaleString('zh-CN'),
                confidence: response.data.confidence || 0.9,
                references: response.data.references || []
            }
            
            aiChatHistory.value.push(aiMessage)
        } else {
            throw new Error(response.message || 'AI对话失败')
        }
        
    } catch (error) {
        console.error('真实API对话失败，使用模拟回答:', error)
        
        try {
            // 降级处理：使用模拟AI对话
            const mockResponse = await mockChatWithAI({
                question: question,
                context: recognitionResult.value.text,
                conversationHistory: aiChatHistory.value.slice(-5)
            })
            
            const aiMessage = { 
                type: 'ai', 
                content: mockResponse.data.answer, 
                time: new Date().toLocaleString('zh-CN'),
                confidence: mockResponse.data.confidence || 0.9
            }
            
            aiChatHistory.value.push(aiMessage)
            
        } catch (mockError) {
            // 如果连模拟都失败了，提供默认AI回答
            aiChatHistory.value.push({
                type: 'ai',
                content: `关于您的问题「${question}」，我可以提供以下解答：\n\n根据碑文内容分析，这是一段具有历史价值的古代文献，反映了当时的文化背景和社会状况。这类碑文通常具有重要的历史研究价值，为我们了解古代社会提供了宝贵的第一手资料。`,
                time: new Date().toLocaleString('zh-CN'),
                confidence: 0.85
            })
            
            appStore.addNotification({
                type: 'info',
                message: '使用默认AI回答',
                duration: 3000
            })
        }
    }
}

// 保存到收藏
const saveToFavorites = async () => {
    if (!saveForm.value.title.trim()) {
        appStore.addNotification({
            type: 'error',
            message: '请输入碑文标题',
            duration: 2000
        })
        return
    }

    try {
        // 尝试使用真实API保存收藏
        const response = await saveFavorite({
            title: saveForm.value.title,
            content: recognitionResult.value.text,
            tags: saveForm.value.tags,
            recognition_id: recognitionResult.value.recognition_id || null,
            metadata: {
                wordCount: recognitionResult.value.wordCount,
                confidence: recognitionResult.value.confidence,
                dynasty: recognitionResult.value.dynasty === '待识别' ? null : recognitionResult.value.dynasty,
                year: recognitionResult.value.year === '待识别' ? null : recognitionResult.value.year,
                location: recognitionResult.value.location === '待识别' ? null : recognitionResult.value.location
            }
        })
        
        if (response.success) {
            const favoriteItem = {
                id: response.data.id,
                title: response.data.title,
                content: response.data.content,
                tags: response.data.tags,
                date: new Date().toLocaleString('zh-CN'),
                confidence: Math.round((recognitionResult.value.confidence || 0) * 100),
                preview: recognitionResult.value.text.substring(0, 50) + '...'
            }
            
            // 更新历史记录列表
            recentHistory.value.unshift({
                id: favoriteItem.id,
                preview: favoriteItem.preview,
                date: favoriteItem.date,
                confidence: favoriteItem.confidence
            })
            
            appStore.addNotification({
                type: 'success',
                message: '保存到我的碑文成功',
                duration: 3000
            })
            closeSaveModal()
        } else {
            throw new Error(response.message || '保存失败')
        }
        
    } catch (error) {
        console.error('真实API保存收藏失败，使用本地降级方案:', error)
        
        try {
            // 降级处理：保存到本地存储
            const favoriteItem = {
                id: `mock-fav-${Date.now()}`,
                title: saveForm.value.title,
                content: recognitionResult.value.text,
                tags: saveForm.value.tags,
                metadata: {
                    wordCount: recognitionResult.value.wordCount,
                    confidence: recognitionResult.value.confidence,
                    dynasty: recognitionResult.value.dynasty || '待识别',
                    year: recognitionResult.value.year || '待识别',
                    location: recognitionResult.value.location || '待识别',
                    aiInterpretation: aiInterpretation.value,
                    createdAt: new Date().toISOString(),
                    preview: recognitionResult.value.text.substring(0, 50) + '...'
                },
                date: new Date().toLocaleString('zh-CN'),
                confidence: Math.round((recognitionResult.value.confidence || 0) * 100)
            }
            
            // 保存到本地存储
            let favorites = JSON.parse(localStorage.getItem('mock-favorites') || '[]')
            favorites.unshift(favoriteItem)
            localStorage.setItem('mock-favorites', JSON.stringify(favorites))
            
            // 更新历史记录列表
            recentHistory.value.unshift({
                id: favoriteItem.id,
                preview: favoriteItem.metadata.preview,
                date: favoriteItem.date,
                confidence: favoriteItem.confidence
            })
            
            appStore.addNotification({
                type: 'success',
                message: '已保存到本地收藏（离线模式）',
                duration: 3000
            })
            closeSaveModal()
            
        } catch (localError) {
            console.error('本地保存也失败:', localError)
            appStore.addNotification({
                type: 'error',
                message: '保存失败，请重试',
                duration: 5000
            })
        }
    }
}

// 获取识别历史记录
const fetchRecognitionHistory = async () => {
    try {
        // 尝试使用真实API获取历史记录
        const response = await getRecognitionHistory({
            page: 1,
            limit: 20
        })
        
        if (response.success) {
            recentHistory.value = response.data.items || []
        } else {
            console.warn('API返回失败，尝试使用本地降级方案')
            throw new Error(response.message || '获取历史记录失败')
        }
    } catch (error) {
        console.error('真实API获取历史记录失败，使用降级方案:', error)
        
        try {
            // 降级方案1：使用Mock数据
            const mockHistory = await mockGetRecognitionHistory({
                page: 1,
                limit: 20
            })
            
            if (mockHistory.success) {
                recentHistory.value = mockHistory.data.items || []
            } else {
                // 降级方案2：尝试从本地存储获取
                console.warn('Mock数据获取失败，尝试从本地存储获取')
                const localFavorites = JSON.parse(localStorage.getItem('mock-favorites') || '[]')
                recentHistory.value = localFavorites.slice(0, 20).map(fav => ({
                    id: fav.id,
                    preview: fav.metadata?.preview || fav.content.substring(0, 50) + '...',
                    date: fav.date,
                    confidence: fav.confidence
                }))
            }
        } catch (localError) {
            console.error('所有降级方案都失败，使用空历史记录:', localError)
            recentHistory.value = []
        }
    }
}

// 组件挂载时获取识别历史
fetchRecognitionHistory()
</script>

<template>
    <div class="recognition-page bg-light bg-texture min-h-screen py-12 md:py-16">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <!-- 页面标题 -->
            <div class="mb-6 sm:mb-8 md:mb-10 text-center md:text-left md:flex md:items-center md:justify-between">
                <div class="px-2">
                    <h1 class="text-2xl sm:text-3xl md:text-[clamp(1.8rem,4vw,2.5rem)] font-serif font-bold text-primary mb-2">碑文识别</h1>
                    <p class="text-dark/70 max-w-2xl text-sm sm:text-base mb-4">
                        <span class="hidden sm:inline">上传碑文图片，AI将自动识别文字内容并提供历史文化阐释，探索古老文字背后的故事</span>
                        <span class="sm:hidden">上传碑文图片进行智能识别和AI阐释</span>
                    </p>
                    <!-- OCR服务状态显示 -->
                    <div class="text-xs sm:text-sm text-dark/60">
                        <span>系统采用先进AI识别技术，支持繁体字、古典文献识别</span>
                    </div>
                </div>
                <div class="mt-4 md:mt-0 px-2">
                    <button @click="openUploadModal"
                        class="w-full sm:w-auto px-4 sm:px-5 py-3 sm:py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 shadow-md hover:shadow-lg transition-custom flex items-center justify-center mx-auto md:mx-0 text-base sm:text-base">
                        <i class="fas fa-upload mr-2"></i>
                        <span class="hidden sm:inline">上传图片</span>
                        <span class="sm:hidden">上传碑文</span>
                    </button>
                </div>
            </div>

            <!-- 主内容区 -->
            <div class="grid grid-cols-1 gap-8 lg:gap-12">
                <!-- 识别结果区域 -->
                <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 flex flex-col">
                    <!-- 标签页导航 -->
                    <div class="border-b border-gray-100">
                        <!-- 桌面端标签页 -->
                        <div class="hidden sm:flex">
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

                        <!-- 移动端下拉导航 -->
                        <div class="sm:hidden px-4 py-3">
                            <div class="relative">
                                <select @change="switchTab($event.target.value)" :value="activeTab"
                                    class="w-full appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary">
                                    <option value="status">图片上传</option>
                                    <option value="proofread">详细校对</option>
                                    <option value="result">识别结果</option>
                                    <option value="interpretation">AI阐释</option>
                                </select>
                                <i class="fas fa-chevron-down absolute right-3 top-1/2 transform -translate-y-1/2 text-dark/50 text-xs pointer-events-none"></i>
                            </div>
                        </div>
                    </div>

                    <!-- 识别状态内容 -->
                    <div v-show="activeTab === 'status'"
                        class="p-4 sm:p-6 lg:p-8 flex-grow flex flex-col items-center justify-center text-center min-h-[400px]">
                        <!-- 等待状态 -->
                        <div v-if="recognitionState === 'waiting'">
                            <div class="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 bg-secondary/30 rounded-full flex items-center justify-center mb-4 sm:mb-6">
                                <i class="fas fa-upload text-primary/50 text-2xl sm:text-3xl lg:text-4xl"></i>
                            </div>
                            <h3 class="text-lg sm:text-xl font-semibold text-dark mb-2 sm:mb-3">等待上传图片</h3>
                            <p class="text-dark/70 max-w-sm sm:max-w-md mb-6 sm:mb-8 text-sm sm:text-base px-4">上传碑文图片后，AI将自动开始识别文字内容</p>
                            <div class="w-full max-w-xs px-4">
                                <button @click="openUploadModal"
                                    class="w-full py-3 sm:py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center justify-center text-base sm:text-base">
                                    <i class="fas fa-magic mr-2"></i>
                                    上传图片
                                </button>
                            </div>
                        </div>

                        <!-- 识别中 -->
                        <div v-else-if="recognitionState === 'processing'">
                            <div class="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 bg-secondary/30 rounded-full flex items-center justify-center mb-4 sm:mb-6">
                                <div class="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 lg:h-16 lg:w-16 border-t-2 border-b-2 border-primary">
                                </div>
                            </div>
                            <h3 class="text-lg sm:text-xl font-semibold text-dark mb-2 sm:mb-3">正在识别...</h3>
                            <div class="w-full max-w-sm sm:max-w-md bg-gray-200 rounded-full h-2 mb-1 sm:h-2.5 sm:mb-2">
                                <div class="bg-primary h-2 rounded-full transition-all duration-300 sm:h-2.5"
                                    :style="{ width: processingProgress + '%' }"></div>
                            </div>
                            <p class="text-dark/70 text-xs sm:text-sm mb-6 sm:mb-8 px-4">{{ processingStatus }} ({{ processingProgress }}%)</p>
                            <button
                                class="px-4 sm:px-6 py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom text-sm sm:text-base"
                                @click="handleCancelRecognition"
                                :disabled="isCancelInProgress">
                                <i class="fas fa-stop-circle mr-1"></i>
                                {{ isCancelInProgress ? '取消中...' : '取消识别' }}
                            </button>
                        </div>

                        <!-- 识别完成 -->
                        <div v-else-if="recognitionState === 'completed'">
                            <div class="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 bg-green-100 rounded-full flex items-center justify-center mb-4 sm:mb-6">
                                <i class="fas fa-check text-green-500 text-2xl sm:text-3xl lg:text-4xl"></i>
                            </div>
                            <h3 class="text-lg sm:text-xl font-semibold text-dark mb-2 sm:mb-3">识别完成</h3>
                            <p class="text-dark/70 max-w-sm sm:max-w-md mb-6 sm:mb-8 text-sm sm:text-base px-4">
                                已成功识别碑文内容，共{{ recognitionResult.wordCount }}字，置信度{{ (recognitionResult.confidence * 100).toFixed(1) }}%
                            </p>
                            <div class="w-full max-w-xs px-4">
                                <button @click="viewResults"
                                    class="w-full py-3 sm:py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center justify-center text-base sm:text-base">
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
                        <div class="flex flex-col sm:flex-row justify-between gap-3 sm:items-center">
                            <button
                                class="w-full sm:w-auto px-4 py-3 sm:py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom text-sm sm:text-base">
                                <i class="fas fa-arrow-left mr-1 sm:mr-0 sm:mr-1"></i>
                                <span class="sm:hidden">上一页</span>
                            </button>
                            <button
                                class="w-full sm:w-auto px-4 py-3 sm:py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-custom text-sm sm:text-base">
                                保存校对结果
                            </button>
                            <button
                                class="w-full sm:w-auto px-4 py-3 sm:py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom text-sm sm:text-base">
                                <span class="sm:hidden">下一页</span>
                                <i class="fas fa-arrow-right ml-1 sm:ml-0 sm:ml-1"></i>
                            </button>
                        </div>
                    </div>

                    <!-- 识别结果内容 -->
                    <div v-show="activeTab === 'result'" class="p-3 sm:p-4 lg:p-6">
                        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-3">
                            <h3 class="text-base sm:text-lg font-semibold text-primary">识别结果</h3>
                            <div class="flex space-x-1 sm:space-x-2 w-full sm:w-auto">
                                <button @click="copyResult"
                                    class="flex-1 sm:flex-none p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom text-sm"
                                    title="复制文本">
                                    <i class="fas fa-copy mr-1 sm:mr-0"></i>
                                    <span class="sm:hidden">复制</span>
                                </button>
                                <button @click="downloadResult"
                                    class="flex-1 sm:flex-none p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom text-sm"
                                    title="下载文本">
                                    <i class="fas fa-download mr-1 sm:mr-0"></i>
                                    <span class="sm:hidden">下载</span>
                                </button>
                                <button
                                    class="flex-1 sm:flex-none p-2 text-dark/70 hover:text-primary hover:bg-gray-100 rounded-md transition-custom text-sm"
                                    title="编辑文本">
                                    <i class="fas fa-edit mr-1 sm:mr-0"></i>
                                    <span class="sm:hidden">编辑</span>
                                </button>
                            </div>
                        </div>

                        <div class="mb-4 space-y-2">
                            <div class="flex flex-wrap items-center text-xs sm:text-sm text-dark/70 gap-2 sm:gap-4">
                                <span class="flex items-center">
                                    <i class="fas fa-clock mr-1"></i>
                                    识别时间: {{ recognitionResult.time }}
                                </span>
                                <span class="flex items-center">
                                    <i class="fas fa-font mr-1"></i>
                                    字数: {{ recognitionResult.wordCount }}
                                </span>
                            </div>
                            <div class="flex items-center text-xs sm:text-sm text-dark/70">
                                <i class="fas fa-check-circle text-green-500 mr-1"></i>
                                置信度: {{ (recognitionResult.confidence * 100).toFixed(1) }}%
                            </div>
                        </div>

                        <div class="border border-gray-200 rounded-lg p-3 sm:p-4 h-48 sm:h-64 lg:h-80 overflow-y-auto mb-4 sm:mb-6 bg-gray-50">
                            <div class="text-sm sm:text-base text-dark/90 leading-relaxed whitespace-pre-line">
                                {{ recognitionResult.text || '暂无识别结果' }}
                            </div>
                        </div>

                        <div class="flex flex-col sm:flex-row gap-3">
                            <button @click="switchTab('interpretation')"
                                class="flex-1 py-3 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom text-sm sm:text-base"
                                :disabled="!recognitionResult.text">
                                <i class="fas fa-book-reader mr-1 sm:mr-2"></i>
                                查看AI阐释
                            </button>
                            <button @click="shareRecognition"
                                class="px-4 py-3 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom text-sm sm:text-base">
                                <i class="fas fa-share-alt mr-1 sm:mr-0"></i>
                                <span class="sm:hidden">分享</span>
                            </button>
                        </div>
                    </div>

                    <!-- AI阐释内容 -->
                    <div v-show="activeTab === 'interpretation'" class="p-6 md:p-8">
                        <!-- 顶部操作按钮 -->
                        <div class="flex justify-end mb-6">
                            <button @click="openSaveModal"
                                class="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary/90 transition-custom flex items-center"
                                :disabled="!recognitionResult.text">
                                <i class="fas fa-bookmark mr-2"></i>
                                保存到我的碑文
                            </button>
                        </div>

                        <!-- 阐释内容 -->
                        <div class="grid md:grid-cols-3 gap-8">
                            <!-- 左侧：主要阐释内容 -->
                            <div class="md:col-span-2">
                                <h3 class="text-2xl font-serif font-semibold text-primary mb-4">碑文历史文化阐释</h3>
                                
                                <!-- 加载状态 -->
                                <div v-if="isLoadingInterpretation" class="text-center py-8">
                                    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
                                    <p class="text-dark/70">正在生成AI阐释...</p>
                                </div>
                                
                                <!-- 阐释内容 -->
                                <div v-else-if="aiInterpretation.value?.history?.length" class="prose max-w-none text-dark/90 leading-relaxed mb-6">
                                    <div class="space-y-4">
                                        <div v-for="(item, index) in aiInterpretation.value.history" :key="index">
                                            <h4 class="text-lg font-semibold text-primary mb-2">{{ item.title }}</h4>
                                            <p class="text-dark/80">{{ item.content }}</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div v-else-if="recognitionResult.text" class="text-center py-8 text-dark/60">
                                    <p>暂无AI阐释内容，请先完成碑文识别</p>
                                </div>

                                <!-- AI对话入口 -->
                                <div v-if="recognitionResult.text" class="bg-secondary/30 p-4 rounded-lg border border-secondary">
                                    <div class="flex items-start mb-4">
                                        <div class="flex-shrink-0 mr-3">
                                            <i class="fas fa-robot text-primary text-xl"></i>
                                        </div>
                                        <div class="flex-grow">
                                            <p class="text-dark/80 mb-3">对这段阐释有疑问？我可以为您解答更多细节</p>
                                        </div>
                                    </div>
                                    
                                    <!-- 对话历史 -->
                                    <div v-if="aiChatHistory.length > 0" class="mb-4 max-h-64 overflow-y-auto space-y-3">
                                        <div v-for="(message, index) in aiChatHistory" :key="index" :class="[
                                            'flex',
                                            message.type === 'user' ? 'justify-end' : 'justify-start'
                                        ]">
                                            <div :class="[
                                                'max-w-xs px-4 py-2 rounded-lg text-sm',
                                                message.type === 'user' 
                                                    ? 'bg-primary text-white' 
                                                    : 'bg-white border border-gray-200 text-dark'
                                            ]">
                                                <p>{{ message.content }}</p>
                                                <p class="text-xs opacity-70 mt-1">{{ message.time }}</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- 输入框 -->
                                    <div class="flex">
                                        <input v-model="aiQuestion" type="text" placeholder="请输入您的问题..."
                                            @keyup.enter="sendAiQuestion"
                                            class="flex-grow px-4 py-2 rounded-l-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" />
                                        <button @click="sendAiQuestion"
                                            class="bg-primary text-white px-4 py-2 rounded-r-md hover:bg-primary/90 transition-custom">
                                            <i class="fas fa-paper-plane"></i>
                                        </button>
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
                                    <div class="space-y-4">
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
                                </div>

                                <!-- 相关人物 -->
                                <div class="bg-light p-5 rounded-xl border border-gray-100">
                                    <h4 class="text-lg font-semibold text-primary mb-4 flex items-center">
                                        <i class="fas fa-users mr-2"></i>
                                        相关人物
                                    </h4>
                                    <div class="space-y-3">
                                        <div v-for="figure in relatedFigures" :key="figure.name"
                                            class="flex items-center p-2 hover:bg-white rounded-md transition-custom cursor-pointer">
                                            <div
                                                class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mr-3">
                                                <i class="fas fa-user text-primary"></i>
                                            </div>
                                            <div>
                                                <p class="font-medium text-dark">{{ figure.name }}</p>
                                                <p class="text-xs text-dark/60">{{ figure.role }}</p>
                                            </div>
                                        </div>
                                    </div>
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
                <div v-if="uploadModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4">
                    <div @click="closeUploadModal" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
                    <div class="relative bg-white rounded-xl shadow-lg w-full max-w-2xl max-h-[90vh] overflow-hidden sm:overflow-y-auto">
                        <div
                            class="p-4 sm:p-6 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white z-10">
                            <h3 class="text-lg sm:text-xl font-semibold text-dark">上传碑文图片</h3>
                            <button @click="closeUploadModal" class="text-dark/70 hover:text-dark transition-custom p-1">
                                <i class="fas fa-times text-lg sm:text-xl"></i>
                            </button>
                        </div>
                        <div class="p-4 sm:p-6 overflow-y-auto max-h-[calc(90vh-120px)] sm:max-h-none">
                            <!-- 上传区域 -->
                            <div ref="dropZoneRef" @dragenter="handleDragEnter" @dragover="handleDragOver"
                                @dragleave="handleDragLeave" @drop="handleDrop" @click="triggerFileInput"
                                :class="[
                                    'border-2 border-dashed rounded-xl p-4 sm:p-6 lg:p-8 text-center transition-all duration-300 cursor-pointer mb-4 sm:mb-6 relative overflow-hidden',
                                    'bg-gradient-to-br from-light via-white to-secondary/10 shadow-sm',
                                    isDragging ? 'border-primary bg-primary/10 border-solid scale-105' : 'border-gray-300 hover:border-primary hover:bg-primary/5'
                                ]">
                                <input ref="modalFileInput" type="file" accept="image/*" multiple @change="handleFileSelect"
                                    class="hidden" />
                                
                                <!-- 拖拽覆盖层 -->
                                <div v-if="isDragging"
                                    class="absolute inset-0 bg-primary/20 backdrop-blur-sm flex items-center justify-center z-10">
                                    <div class="bg-white rounded-xl p-4 sm:p-6 shadow-lg border-2 border-primary">
                                        <i class="fas fa-cloud-upload-alt text-primary text-2xl sm:text-3xl lg:text-4xl mb-2"></i>
                                        <p class="text-dark font-medium text-sm sm:text-base">释放文件以添加</p>
                                    </div>
                                </div>
                                
                                <div class="flex flex-col items-center">
                                    <div
                                        class="w-12 h-12 sm:w-16 sm:h-16 lg:w-20 lg:h-20 bg-primary/10 rounded-full flex items-center justify-center mb-3 sm:mb-4 transform hover:scale-105 transition-all duration-300">
                                        <i class="fas fa-camera text-primary text-2xl sm:text-2xl lg:text-3xl"></i>
                                    </div>
                                    <h3 class="text-lg sm:text-xl font-semibold text-dark mb-1 sm:mb-2">点击上传或拖放图片</h3>
                                    <p class="text-xs sm:text-sm text-dark/60 mb-3 sm:mb-4 max-w-xs sm:max-w-sm lg:max-w-md px-2">
                                        支持 JPG、PNG、WEBP 格式，最大 10MB，建议图片清晰、文字端正以获得最佳识别效果
                                    </p>
                                    <div class="flex items-center justify-center text-xs text-dark/50 space-x-2 sm:space-x-4 flex-wrap gap-y-1">
                                        <span class="flex items-center">
                                            <i class="fas fa-mouse-pointer mr-1"></i>
                                            <span class="hidden sm:inline">点击选择</span>
                                            <span class="sm:hidden">点击</span>
                                        </span>
                                        <span class="flex items-center">
                                            <i class="fas fa-hand-paper mr-1"></i>
                                            <span class="hidden sm:inline">拖拽上传</span>
                                            <span class="sm:hidden">拖拽</span>
                                        </span>
                                        <span class="flex items-center">
                                            <i class="fas fa-layer-group mr-1"></i>
                                            <span class="hidden sm:inline">支持多文件</span>
                                            <span class="sm:hidden">多文件</span>
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <!-- 文件预览和管理区域 -->
                            <div v-if="selectedFiles.length > 0" class="mb-6">
                                <div class="flex justify-between items-center mb-4">
                                    <h4 class="text-lg font-medium text-dark flex items-center">
                                        <i class="fas fa-images text-primary mr-2"></i>
                                        已选择文件 ({{ selectedFiles.length }})
                                    </h4>
                                    <div class="flex items-center space-x-2">
                                        <!-- 预览模式切换 -->
                                        <div class="flex bg-gray-100 rounded-lg p-1">
                                            <button @click="previewMode = 'grid'" :class="[
                                                'px-3 py-1 rounded-md text-xs transition-custom',
                                                previewMode === 'grid' ? 'bg-white shadow-sm text-primary' : 'text-dark/60 hover:text-dark'
                                            ]">
                                                <i class="fas fa-th-large"></i>
                                            </button>
                                            <button @click="previewMode = 'list'" :class="[
                                                'px-3 py-1 rounded-md text-xs transition-custom',
                                                previewMode === 'list' ? 'bg-white shadow-sm text-primary' : 'text-dark/60 hover:text-dark'
                                            ]">
                                                <i class="fas fa-list"></i>
                                            </button>
                                        </div>
                                        <button @click="clearAllFiles"
                                            class="px-3 py-1 text-xs text-red-600 hover:bg-red-50 rounded-md transition-custom"
                                            title="清除所有文件">
                                            <i class="fas fa-trash mr-1"></i>清除全部
                                        </button>
                                    </div>
                                </div>

                                <!-- 网格模式预览 -->
                                <div v-if="previewMode === 'grid'" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                                    <div v-for="fileItem in selectedFiles" :key="fileItem.id"
                                        class="relative group bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-300">
                                        <div class="aspect-square bg-gray-100 flex items-center justify-center">
                                            <img :src="fileItem.previewUrl" :alt="fileItem.name"
                                                class="w-full h-full object-cover" />
                                        </div>
                                        <div class="p-3">
                                            <p class="text-xs font-medium text-dark truncate" :title="fileItem.name">
                                                {{ fileItem.name }}
                                            </p>
                                            <p class="text-xs text-dark/60">{{ getFileSizeString(fileItem.size) }}</p>
                                        </div>
                                        <button @click.stop="removeFile(fileItem.id)"
                                            class="absolute top-2 right-2 bg-white/80 p-1.5 rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-all duration-300 hover:bg-white">
                                            <i class="fas fa-times text-dark/70 text-xs"></i>
                                        </button>
                                        <div v-if="fileItem.processing"
                                            class="absolute inset-0 bg-black/50 flex items-center justify-center">
                                            <div class="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                                        </div>
                                    </div>
                                </div>

                                <!-- 列表模式预览 -->
                                <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
                                    <div class="max-h-64 overflow-y-auto">
                                        <table class="w-full">
                                            <thead class="bg-gray-50">
                                                <tr>
                                                    <th class="px-4 py-3 text-left text-xs font-medium text-dark/60 uppercase">文件名</th>
                                                    <th class="px-4 py-3 text-left text-xs font-medium text-dark/60 uppercase">大小</th>
                                                    <th class="px-4 py-3 text-left text-xs font-medium text-dark/60 uppercase">状态</th>
                                                    <th class="px-4 py-3 text-right text-xs font-medium text-dark/60 uppercase">操作</th>
                                                </tr>
                                            </thead>
                                            <tbody class="divide-y divide-gray-200">
                                                <tr v-for="fileItem in selectedFiles" :key="fileItem.id" class="hover:bg-gray/50">
                                                    <td class="px-4 py-3">
                                                        <div class="flex items-center">
                                                            <img :src="fileItem.previewUrl" :alt="fileItem.name"
                                                                class="w-8 h-8 rounded object-cover mr-3" />
                                                            <div>
                                                                <p class="text-sm font-medium text-dark truncate max-w-[150px]"
                                                                    :title="fileItem.name">{{ fileItem.name }}</p>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td class="px-4 py-3 text-sm text-dark/60">{{ getFileSizeString(fileItem.size) }}</td>
                                                    <td class="px-4 py-3">
                                                        <span :class="[
                                                            'inline-flex items-center px-2 py-1 rounded-full text-xs',
                                                            fileItem.processing ? 'bg-yellow-100 text-yellow-800' :
                                                            fileItem.uploaded ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                                                        ]">
                                                            <i :class="[
                                                                'w-2 h-2 rounded-full mr-1',
                                                                fileItem.processing ? 'bg-yellow-400 animate-pulse' :
                                                                fileItem.uploaded ? 'bg-green-400' : 'bg-blue-400'
                                                            ]"></i>
                                                            {{ fileItem.processing ? '处理中' : fileItem.uploaded ? '已上传' : '待处理' }}
                                                        </span>
                                                    </td>
                                                    <td class="px-4 py-3 text-right">
                                                        <button @click="removeFile(fileItem.id)"
                                                            class="text-red-600 hover:text-red-800 transition-custom">
                                                            <i class="fas fa-trash text-sm"></i>
                                                        </button>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="p-4 sm:p-6 border-t border-gray-200 flex flex-col sm:flex-row justify-end gap-3 sticky bottom-0 bg-white">
                            <button @click="closeUploadModal"
                                class="w-full sm:w-auto px-6 py-3 sm:py-2 border border-gray-300 text-dark/70 rounded-md hover:bg-gray-50 transition-custom text-base sm:text-sm">
                                取消
                            </button>
                            <button @click="confirmUpload"
                                class="w-full sm:w-auto px-6 py-3 sm:py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom text-base sm:text-sm">
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
                                <button @click="saveToFavorites"
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
