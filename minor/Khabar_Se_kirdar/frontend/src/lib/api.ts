import axios from 'axios'

const baseURL =
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '' : 'http://127.0.0.1:8000')

export const api = axios.create({
  baseURL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (!(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json'
  }
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const d = err.response?.data?.detail
    let message = err.message
    if (typeof d === 'string') message = d
    else if (Array.isArray(d)) message = d.map((x: { msg?: string }) => x.msg).filter(Boolean).join(', ')
    return Promise.reject(new Error(message || 'Request failed'))
  },
)

export function staticUrl(path: string) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (path.startsWith('/')) return `${baseURL}${path}`
  return `${baseURL}/${path}`
}
