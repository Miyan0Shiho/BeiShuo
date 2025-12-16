// 认证相关API调用
export async function login({ baseUrl, email, password, remember_me }) {
  const url = `${baseUrl}/api/v1/auth/login`
  const headers = { 'Content-Type': 'application/json' }
  const body = {
    email,
    password,
    remember_me
  }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '登录失败'
  throw new Error(msg)
}

export async function register({ baseUrl, name, email, password }) {
  const url = `${baseUrl}/api/v1/auth/register`
  const headers = { 'Content-Type': 'application/json' }
  const body = {
    name,
    email,
    password
  }
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '注册失败'
  throw new Error(msg)
}

export async function getProfile({ baseUrl, token }) {
  const url = `${baseUrl}/api/v1/auth/profile`
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
  const res = await fetch(url, { method: 'GET', headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data && data.success) return data.data
  const msg = data && data.message ? data.message : '获取用户信息失败'
  throw new Error(msg)
}
