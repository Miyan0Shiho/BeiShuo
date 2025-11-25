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