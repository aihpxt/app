// 导入类型检查工具函数
import * as validator from './validator.js'

// 日期格式化
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

// 数字格式化（千分位）
export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 分数格式化
export function formatScore(score) {
  if (score === null || score === undefined) return '-'
  return Number(score).toFixed(1)
}

// 百分比格式化
export function formatPercent(value, decimals = 2) {
  if (value === null || value === undefined) return '0%'
  return (value * 100).toFixed(decimals) + '%'
}

// 手机号脱敏
export function maskPhone(phone) {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 身份证号脱敏
export function maskIdCard(idCard) {
  if (!idCard || idCard.length !== 18) return idCard
  return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
}

// 文件大小格式化
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 学校类型映射
export const schoolTypeMap = {
  1: '普通高中',
  2: '重点高中',
  3: '中等职业学校',
  4: '民办高中'
}

// 州市列表
export const cityList = [
  '昆明市',
  '曲靖市',
  '玉溪市',
  '保山市',
  '昭通市',
  '丽江市',
  '普洱市',
  '临沧市',
  '楚雄州',
  '红河州',
  '文山州',
  '西双版纳州',
  '大理州',
  '德宏州',
  '怒江州',
  '迪庆州'
]

// 政策分类
export const policyCategories = [
  { value: '招生政策', label: '招生政策' },
  { value: '加分政策', label: '加分政策' },
  { value: '志愿填报', label: '志愿填报' },
  { value: '招生计划', label: '招生计划' },
  { value: '改革方案', label: '改革方案' }
]

// 导出类型检查工具函数
export const {
  isObject,
  isPromise,
  isArray,
  isString,
  isNumber,
  isBoolean,
  isFunction,
  isNil,
  safeGet,
  safeGetUserInfo,
  safeGetUserNickname,
  safeGetUserAvatar,
  safeGetUserName,
  canRenderUserInfo,
  safeParseLocalStorage,
  safeSetLocalStorage,
  safeRemoveLocalStorage,
  escapeHtml,
  stripHtml,
  isValidEmail,
  isValidPhone,
  isValidPassword,
  isValidUrl,
  isValidIdCard,
  generateId,
  generateUniqueId,
  debounce,
  throttle,
  deepClone,
  deepMerge,
  isEmptyObject,
  isEmptyArray,
  isEmpty,
  toStringSafe,
  toNumberSafe,
  toBooleanSafe,
  toArraySafe,
  toObjectSafe
} = validator

// 本地存储封装（使用safeParseLocalStorage）
export const storage = {
  set(key, value) {
    return safeSetLocalStorage(key, value)
  },
  get(key, defaultValue = null) {
    return safeParseLocalStorage(key, defaultValue)
  },
  remove(key) {
    return safeRemoveLocalStorage(key)
  },
  clear() {
    try {
      localStorage.clear()
      return true
    } catch (e) {
      console.error('Storage clear error:', e)
      return false
    }
  }
}