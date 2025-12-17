// 确保baseUrl格式正确，避免重复的/api/v1
function normalizeBaseUrl(url) {
  if (url && url.endsWith('/api/v1')) {
    return url
  } else if (url && !url.includes('/api/v1')) {
    return `${url}/api/v1`
  }
  return url
}

export async function postChat({ baseUrl, token, recognitionId, message, conversationId }) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl)
  const url = `${normalizedBaseUrl}/ai/chat`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const body = {
    recognition_id: recognitionId || 'rec_local',
    message,
    conversation_id: conversationId || undefined
  }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function streamChatFetch({ baseUrl, token, recognitionId, message, conversationId, onEvent }) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl)
  const url = `${normalizedBaseUrl}/ai/chat/stream`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const body = {
    recognition_id: recognitionId || 'rec_local',
    message,
    conversation_id: conversationId || undefined
  }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok || !res.body) throw new Error('stream open failed')
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split("\n\n")
    buffer = parts.pop() || ''
    for (const p of parts) {
      const line = p.trim()
      if (!line.startsWith('data:')) continue
      const json = line.slice(5).trim()
      try {
        const evt = JSON.parse(json)
        if (onEvent) onEvent(evt)
      } catch (e) {
      }
    }
  }
}

export async function postInterpretationSections({ baseUrl, token, text, recognitionId, inscriptionId, conversationId }) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl)
  const url = `${normalizedBaseUrl}/ai/interpretation/sections`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const body = {
    text,
    recognition_id: recognitionId || undefined,
    inscription_id: inscriptionId || undefined,
    conversation_id: conversationId || undefined
  }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '生成失败'
  throw new Error(msg)
}

export async function uploadImage({ baseUrl, token, file }) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl)
  const url = `${normalizedBaseUrl}/upload/image`
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const form = new FormData()
  form.append('image', file)
  const res = await fetch(url, { method: 'POST', headers, body: form })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '上传失败'
  throw new Error(msg)
}

export async function startRecognition({ baseUrl, token, imageUrl, imageBase64, options }) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl)
  const url = `${normalizedBaseUrl}/recognition/start`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const body = {
    image_url: imageUrl || undefined,
    image_base64: imageBase64 || undefined,
    options: options || {}
  }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '识别失败'
  throw new Error(msg)
}

export async function fetchRecognitionHistory({ baseUrl, token, page = 1, size = 10 }) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl)
  const url = `${normalizedBaseUrl}/recommendation/recognition/history?page=${page - 1}&size=${size}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) {
    // 适配API返回格式：将list转换为records，并格式化字段
    const formattedRecords = (data.data.list || []).map(record => ({
      id: record.id,
      preview: record.recognition_text || record.inscription_title || '识别记录',
      date: record.created_at,
      confidence: record.confidence,
      image_path: record.image_path,
      recognition_text: record.recognition_text
    }))
    return {
      records: formattedRecords,
      total: data.data.total || 0,
      page: data.data.page + 1, // 后端从0开始，前端从1开始
      size: data.data.size || size
    }
  }
  const msg = data && data.message ? data.message : '获取识别历史失败'
  throw new Error(msg)
}

export async function fetchRecommendedInscriptions({ baseUrl, token, recognition_id, text, page = 1, size = 10 }) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl)
  const url = `${normalizedBaseUrl}/recommendation/inscriptions`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const body = {
    recognition_id: recognition_id || undefined,
    text: text || undefined,
    page: page,
    size: size
  }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) {
    // 适配API返回格式：直接返回的数组转换为records
    return {
      records: data.data || [],
      total: data.data ? data.data.length : 0,
      page: page,
      size: size
    }
  }
  const msg = data && data.message ? data.message : '获取推荐碑文失败'
  throw new Error(msg)
}