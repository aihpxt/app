import axios from 'axios'
import { ElMessage } from 'element-plus'

// 普通接口
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000
})

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

apiClient.interceptors.response.use(
  res => res.data,
  err => {
    ElMessage.error('请求失败')
    return Promise.reject(err)
  }
)

// AI 接口（关键修复：支持流式 + 长超时）
const aiApiClient = axios.create({
  baseURL: import.meta.env.VITE_AI_API_URL || '/ai',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' }
})

// AI 响应拦截器，与apiClient保持一致
aiApiClient.interceptors.response.use(
  res => res.data,
  err => {
    ElMessage.error('AI服务请求失败')
    return Promise.reject(err)
  }
)

export { apiClient, aiApiClient }