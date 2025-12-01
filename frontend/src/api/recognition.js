// 识别相关API接口
// 提供最近识别记录、识别详情等功能的API调用

/**
 * 获取最近识别记录列表
 * @param {Object} params - 参数对象
 * @param {string} params.baseUrl - 基础URL
 * @param {string} params.token - 用户令牌
 * @param {number} params.page - 页码，默认1
 * @param {number} params.size - 每页大小，默认10
 * @returns {Promise<Object>} 识别记录列表
 */
export async function getRecentRecognitionList({ baseUrl, token, page = 1, size = 10 }) {
    const url = `${baseUrl}/recognition/recent?page=${page}&size=${size}`
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const res = await fetch(url, { method: 'GET', headers })
    
    // 处理401未授权错误
    if (res.status === 401) {
        throw new Error('未授权访问，请先登录')
    }
    
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    
    // 检查响应格式
    if (data && data.code === 200) {
        return data.data
    } else if (data && data.success) {
        return data.data
    }
    
    const msg = data && data.message ? data.message : '获取识别记录失败'
    throw new Error(msg)
}

/**
 * 获取单个识别记录详情
 * @param {Object} params - 参数对象
 * @param {string} params.baseUrl - 基础URL
 * @param {string} params.token - 用户令牌
 * @param {string} params.jobId - 识别任务ID
 * @returns {Promise<Object>} 识别记录详情
 */
export async function getRecognitionDetail({ baseUrl, token, jobId }) {
    const url = `${baseUrl}/recognition/recent/${jobId}`
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const res = await fetch(url, { method: 'GET', headers })
    
    // 处理401未授权错误
    if (res.status === 401) {
        throw new Error('未授权访问，请先登录')
    }
    
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    
    // 检查响应格式
    if (data && data.code === 200) {
        return data.data
    } else if (data && data.success) {
        return data.data
    }
    
    const msg = data && data.message ? data.message : '获取识别详情失败'
    throw new Error(msg)
}

/**
 * 获取识别历史记录
 * @param {Object} params - 参数对象
 * @param {string} params.baseUrl - 基础URL
 * @param {string} params.token - 用户令牌
 * @param {number} params.page - 页码，默认1
 * @param {number} params.size - 每页大小，默认10
 * @returns {Promise<Object>} 历史记录列表
 */
export async function getRecognitionHistory({ baseUrl, token, page = 1, size = 10 }) {
    const url = `${baseUrl}/recognition/history?page=${page}&size=${size}`
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const res = await fetch(url, { method: 'GET', headers })
    
    // 处理401未授权错误
    if (res.status === 401) {
        throw new Error('未授权访问，请先登录')
    }
    
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    
    // 检查响应格式
    if (data && data.code === 200) {
        return data.data
    } else if (data && data.success) {
        return data.data
    }
    
    const msg = data && data.message ? data.message : '获取历史记录失败'
    throw new Error(msg)
}