import axios, { type AxiosInstance, type AxiosResponse, type AxiosRequestConfig } from 'axios'

interface CacheEntry {
  data: unknown
  timestamp: number
  ttl: number
}

interface RetryConfig extends AxiosRequestConfig {
  _retryCount?: number
}

const cache = new Map<string, CacheEntry>()

const createCacheKey = (method: string, url: string, params?: unknown, data?: unknown): string => {
  const paramsStr = params ? JSON.stringify(params) : ''
  const dataStr = data ? JSON.stringify(data) : ''
  return `${method}:${url}:${paramsStr}:${dataStr}`
}

const getFromCache = (key: string): unknown | null => {
  const cached = cache.get(key)
  if (!cached) return null
  if (Date.now() - cached.timestamp > cached.ttl) {
    cache.delete(key)
    return null
  }
  return cached.data
}

const setToCache = (key: string, data: unknown, ttl: number = 60000): void => {
  cache.set(key, { data, timestamp: Date.now(), ttl })
}

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
})

const retryInterceptor = (config: RetryConfig, retries: number = 2): Promise<AxiosResponse> => {
  const currentRetry = config._retryCount || 0
  
  return new Promise((resolve, reject) => {
    const request = apiClient.request(config)
    
    request.then(resolve).catch((error) => {
      if (currentRetry < retries && error.response?.status >= 500) {
        config._retryCount = currentRetry + 1
        const delay = Math.pow(2, currentRetry + 1) * 1000
        setTimeout(() => {
          resolve(retryInterceptor(config, retries))
        }, delay)
      } else {
        reject(error)
      }
    })
  })
}

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  const cacheKey = createCacheKey(config.method?.toUpperCase() || 'GET', config.url || '', config.params, config.data)
  const cachedData = getFromCache(cacheKey)
  
  if (cachedData && config.method?.toUpperCase() === 'GET') {
    return Promise.reject({ type: 'cached', data: cachedData })
  }
  
  return config
})

apiClient.interceptors.response.use(
  (res: AxiosResponse) => {
    if (res.config.method?.toUpperCase() === 'GET') {
      const cacheKey = createCacheKey('GET', res.config.url || '', res.config.params, res.config.data)
      const ttl = parseInt(res.headers['cache-control']?.split('max-age=')[1] || '60') * 1000
      setToCache(cacheKey, res.data, ttl)
    }
    return res.data
  },
  (err) => {
    if (err.type === 'cached') {
      return Promise.resolve(err.data)
    }
    
    if (err.response) {
      const status = err.response.status
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        window.location.href = '/login'
      } else if (status === 403) {
        console.error('权限不足')
      } else if (status >= 500) {
        console.error('服务器错误:', err.response.data)
      }
    } else if (err.request) {
      console.error('请求超时或网络错误')
    }
    
    return Promise.reject(err)
  }
)

const aiApiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_AI_API_URL || '/ai',
  timeout: 90000,
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
  },
  responseType: 'text'
})

aiApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

aiApiClient.interceptors.response.use(
  (res: AxiosResponse) => {
    let data = res.data
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch {
        data = { response: data }
      }
    }
    return data
  },
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
    return Promise.reject(err)
  }
)

export { apiClient, aiApiClient, cache }
export type { AxiosRequestConfig, RetryConfig }