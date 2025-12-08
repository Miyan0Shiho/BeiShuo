// 知识库相关API调用
// 该文件包含知识库相关的所有API调用函数
export async function fetchKnowledgeHome(baseUrl, token) {
  const url = `${baseUrl}/api/v1/knowledge/home`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function fetchKnowledgeList(baseUrl, token, params = {}) {
  const { page = 0, size = 10, keyword, dynasty, category } = params
  const searchParams = new URLSearchParams()
  searchParams.append('page', page)
  searchParams.append('size', size)
  if (keyword) searchParams.append('keyword', keyword)
  if (dynasty) searchParams.append('dynasty', dynasty)
  if (category) searchParams.append('category', category)
  
  const url = `${baseUrl}/api/v1/knowledge/list?${searchParams.toString()}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function fetchArticleDetail(baseUrl, token, articleId) {
  const url = `${baseUrl}/api/v1/knowledge/articles/${articleId}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function searchKnowledge(baseUrl, token, params = {}) {
  const { q, type = 'all', category, dynasty, page = 1, per_page = 20 } = params
  const searchParams = new URLSearchParams()
  searchParams.append('q', q)
  searchParams.append('type', type)
  if (category) searchParams.append('category', category)
  if (dynasty) searchParams.append('dynasty', dynasty)
  searchParams.append('page', page)
  searchParams.append('per_page', per_page)
  
  const url = `${baseUrl}/api/v1/knowledge/search?${searchParams.toString()}`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function fetchKnowledgeCategories(baseUrl, token) {
  const url = `${baseUrl}/api/v1/knowledge/categories`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

export async function fetchKnowledgeDynasties(baseUrl, token) {
  const url = `${baseUrl}/api/v1/knowledge/dynasties`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '请求失败'
  throw new Error(msg)
}

/**
 * 增加文章查看次数
 * @param {string} baseUrl - API基础URL
 * @param {string} token - 认证令牌
 * @param {number|string} articleId - 文章ID
 * @returns {Promise<void>} - 无返回值
 */
export async function incrementArticleViews(baseUrl, token, articleId) {
  const url = `${baseUrl}/api/v1/knowledge/articles/${articleId}/views`
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { method: 'POST', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return
  const msg = data && data.message ? data.message : '更新失败'
  throw new Error(msg)
}