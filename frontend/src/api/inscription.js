export async function listMyInscriptions({ baseUrl, token, page = 1, size = 10, q }) {
  const params = new URLSearchParams()
  params.append('page', page)
  params.append('size', size)
  if (q) params.append('q', q)
  const url = `${baseUrl}/api/v1/inscription/list?${params.toString()}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function getInscription({ baseUrl, token, id }) {
  const url = `${baseUrl}/api/v1/inscription/${id}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function createInscription({ baseUrl, token, title, text, image_url, dynasty, status = 'active' }) {
  const url = `${baseUrl}/api/v1/inscription`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const body = { title, text, image_url, imageUrl: image_url, dynasty, status }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '创建失败'
  throw new Error(msg)
}

export async function updateInscription({ baseUrl, token, id, title, correctedText, status }) {
  const url = `${baseUrl}/api/v1/inscription/${id}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const body = { title, corrected_text: correctedText, status }
  const res = await fetch(url, { method: 'PUT', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '更新失败'
  throw new Error(msg)
}

export async function deleteInscription({ baseUrl, token, id }) {
  const url = `${baseUrl}/api/v1/inscription/${id}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'DELETE', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return true
  const msg = data && data.message ? data.message : '删除失败'
  throw new Error(msg)
}
