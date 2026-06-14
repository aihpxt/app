import { onCLS, onFCP, onLCP, onINP, type Metric } from 'web-vitals'

interface PerformanceEntry {
  startTime: number
  endTime: number
  duration: number
  type: string
  name: string
  details?: Record<string, unknown>
}

interface PerformanceStats {
  totalTime: number
  networkTime: number
  renderTime: number
  componentCount: number
  errors: number
  warnings: number
}

const performanceEntries: PerformanceEntry[] = []
const stats: PerformanceStats = {
  totalTime: 0,
  networkTime: 0,
  renderTime: 0,
  componentCount: 0,
  errors: 0,
  warnings: 0
}

let pageStartTime = 0
let pageEndTime = 0

export const startPerformanceTracking = () => {
  pageStartTime = performance.now()
  
  if (window.performance && window.performance.mark) {
    window.performance.mark('app-start')
  }
  
  console.log('[Performance] 开始性能追踪')
}

export const endPerformanceTracking = () => {
  pageEndTime = performance.now()
  stats.totalTime = pageEndTime - pageStartTime
  
  if (window.performance && window.performance.mark) {
    window.performance.mark('app-end')
    window.performance.measure('app-total', 'app-start', 'app-end')
  }
  
  logPerformanceReport()
}

export const trackEvent = (name: string, type: string = 'custom', details?: Record<string, unknown>) => {
  const entry: PerformanceEntry = {
    startTime: performance.now(),
    endTime: performance.now(),
    duration: 0,
    type,
    name,
    details
  }
  
  performanceEntries.push(entry)
  
  if (type === 'component') {
    stats.componentCount++
  }
  
  console.debug(`[Performance] 事件追踪: ${name} (${type})`)
}

export const trackAsyncOperation = async <T>(
  name: string, 
  operation: () => Promise<T>,
  type: string = 'async'
): Promise<T> => {
  const startTime = performance.now()
  
  try {
    const result = await operation()
    
    const duration = performance.now() - startTime
    performanceEntries.push({
      startTime,
      endTime: performance.now(),
      duration,
      type,
      name
    })
    
    console.debug(`[Performance] 异步操作完成: ${name} (${duration.toFixed(2)}ms)`)
    
    return result
  } catch (error) {
    const duration = performance.now() - startTime
    performanceEntries.push({
      startTime,
      endTime: performance.now(),
      duration,
      type: 'error',
      name: `[ERROR] ${name}`,
      details: { error: String(error) }
    })
    
    stats.errors++
    console.error(`[Performance] 异步操作失败: ${name} (${duration.toFixed(2)}ms)`, error)
    
    throw error
  }
}

export const trackNetworkRequest = (url: string, duration: number, status: number) => {
  stats.networkTime += duration
  
  performanceEntries.push({
    startTime: performance.now() - duration,
    endTime: performance.now(),
    duration,
    type: 'network',
    name: url,
    details: { status }
  })
  
  if (status >= 400) {
    stats.errors++
  }
  
  console.debug(`[Performance] 网络请求: ${url} (${duration.toFixed(2)}ms, status: ${status})`)
}

export const trackRender = (componentName: string, duration: number) => {
  stats.renderTime += duration
  
  performanceEntries.push({
    startTime: performance.now() - duration,
    endTime: performance.now(),
    duration,
    type: 'render',
    name: componentName
  })
  
  console.debug(`[Performance] 组件渲染: ${componentName} (${duration.toFixed(2)}ms)`)
}

export const addWarning = (message: string, details?: Record<string, unknown>) => {
  stats.warnings++
  
  performanceEntries.push({
    startTime: performance.now(),
    endTime: performance.now(),
    duration: 0,
    type: 'warning',
    name: message,
    details
  })
  
  console.warn(`[Performance] 警告: ${message}`, details)
}

export const logPerformanceReport = () => {
  const report = {
    pageLoadTime: stats.totalTime.toFixed(2) + 'ms',
    networkTime: stats.networkTime.toFixed(2) + 'ms',
    renderTime: stats.renderTime.toFixed(2) + 'ms',
    componentCount: stats.componentCount,
    errors: stats.errors,
    warnings: stats.warnings,
    entryCount: performanceEntries.length
  }
  
  console.group('[Performance] 性能报告')
  console.table(report)
  console.groupEnd()
  
  if (stats.errors > 0) {
    console.warn(`[Performance] 检测到 ${stats.errors} 个错误，请检查日志`)
  }
  
  if (stats.warnings > 0) {
    console.warn(`[Performance] 检测到 ${stats.warnings} 个警告`)
  }
  
  if (stats.totalTime > 3000) {
    console.warn(`[Performance] 页面加载时间较长 (${stats.totalTime.toFixed(2)}ms)，建议优化`)
  }
}

export const getPerformanceStats = (): PerformanceStats => {
  return { ...stats }
}

export const getPerformanceEntries = (): PerformanceEntry[] => {
  return [...performanceEntries]
}

export const resetPerformanceTracking = () => {
  performanceEntries.length = 0
  stats.totalTime = 0
  stats.networkTime = 0
  stats.renderTime = 0
  stats.componentCount = 0
  stats.errors = 0
  stats.warnings = 0
  pageStartTime = 0
  pageEndTime = 0
}

export const measureLCP = () => {
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries()
      entries.forEach(entry => {
        console.log(`[Performance] LCP: ${entry.startTime.toFixed(2)}ms - ${(entry as unknown as { url?: string }).url}`)
      })
    })
    
    observer.observe({ type: 'largest-contentful-paint', buffered: true })
  }
}

export const measureFID = () => {
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries()
      entries.forEach(entry => {
        console.log(`[Performance] FID: ${(entry as unknown as { processingStart?: number; startTime?: number }).processingStart 
          ? ((entry as unknown as { processingStart: number; startTime: number }).processingStart - (entry as unknown as { startTime: number }).startTime).toFixed(2)
          : 'N/A'}ms`)
      })
    })
    
    observer.observe({ type: 'first-input', buffered: true })
  }
}

export const measureCLS = () => {
  let clsValue = 0
  
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((entryList) => {
      entryList.getEntries().forEach(entry => {
        if (!((entry as unknown as { hadRecentInput?: boolean }).hadRecentInput)) {
          clsValue += (entry as unknown as { value: number }).value
          console.log(`[Performance] CLS 更新: ${clsValue.toFixed(2)}`)
        }
      })
    })
    
    observer.observe({ type: 'layout-shift', buffered: true })
    
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        console.log(`[Performance] 最终 CLS: ${clsValue.toFixed(2)}`)
      }
    })
  }
}

export const initPerformanceMonitoring = () => {
  startPerformanceTracking()
  measureLCP()
  measureFID()
  measureCLS()
  
  window.addEventListener('load', () => {
    endPerformanceTracking()
  })
  
  window.addEventListener('beforeunload', () => {
    logPerformanceReport()
  })
  
  console.log('[Performance] 性能监控已初始化')
}

export { stats }

// Store collected metrics
const vitalsMetrics: Record<string, number> = {}

function sendToAnalytics(metric: Metric) {
  vitalsMetrics[metric.name] = metric.value
  
  // Send to backend metrics endpoint
  try {
    const body = JSON.stringify({
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
      id: metric.id,
      navigationType: metric.navigationType,
      timestamp: Date.now()
    })
    
    // Use sendBeacon for reliability (works during page unload)
    if (navigator.sendBeacon) {
      const apiUrl = import.meta.env.VITE_API_URL || '/api'
      navigator.sendBeacon(`${apiUrl}/v1/metrics/web-vitals`, body)
    }
  } catch (e) {
    console.warn('Failed to report web vital:', e)
  }
}

export function initWebVitals() {
  onCLS(sendToAnalytics)
  onFCP(sendToAnalytics)
  onLCP(sendToAnalytics)
  onINP(sendToAnalytics)
}

export function getVitalsMetrics() {
  return { ...vitalsMetrics }
}
