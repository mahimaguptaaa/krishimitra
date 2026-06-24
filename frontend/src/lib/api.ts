import axios from 'axios'
const api = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000' })
api.interceptors.request.use(c => {
  const t = typeof window !== 'undefined' ? localStorage.getItem('km_token') : null
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})
api.interceptors.response.use(r => r, e => {
  if (e.response?.status === 401) {
    localStorage.removeItem('km_token')
    window.location.href = '/'
  }
  return Promise.reject(e)
})
export default api
