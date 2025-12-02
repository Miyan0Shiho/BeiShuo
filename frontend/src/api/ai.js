export async function postChat({ baseUrl, token, recognitionId, message, conversationId }) {
  const url = `${baseUrl}/ai/chat`
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
  const url = `${baseUrl}/ai/chat/stream`
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
  const url = `${baseUrl}/ai/interpretation/sections`
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
  const url = `${baseUrl}/upload/image`
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const form = new FormData()
  form.append('image', file)
  const res = await fetch(url, { method: 'POST', headers, body: form })
  
  // 处理401未授权错误
  if (res.status === 401) {
    throw new Error('未授权访问，请先登录')
  }
  
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '上传失败'
  throw new Error(msg)
}

export async function startRecognition({ baseUrl, token, imageUrl, imageBase64, options }) {
  const url = `${baseUrl}/recognition/start`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  
  // 处理URL编码问题：如果imageUrl已经被编码，先解码
  let processedImageUrl = imageUrl
  if (imageUrl && typeof imageUrl === 'string') {
    // 检查是否包含URL编码的字符
    if (imageUrl.includes('%3A') || imageUrl.includes('%2F') || imageUrl.includes('%3F')) {
      try {
        processedImageUrl = decodeURIComponent(imageUrl)
        console.log('检测到编码的URL，解码后:', processedImageUrl)
      } catch (e) {
        console.warn('URL解码失败，使用原始URL:', imageUrl)
      }
    }
  }
  
  const body = {
    image_url: processedImageUrl || undefined,
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