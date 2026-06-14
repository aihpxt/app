/**
 * 类型检查工具函数
 * 提供统一的类型验证和数据安全访问方法
 */

/**
 * 检查值是否为有效的对象（非null、非数组、非Promise）
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value) && !isPromise(value)
}

/**
 * 检查值是否为Promise对象
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isPromise(value) {
  return value !== null && typeof value === 'object' && typeof value.then === 'function'
}

/**
 * 检查值是否为有效的数组
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isArray(value) {
  return Array.isArray(value)
}

/**
 * 检查值是否为字符串
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isString(value) {
  return typeof value === 'string'
}

/**
 * 检查值是否为数字
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isNumber(value) {
  return typeof value === 'number' && !isNaN(value)
}

/**
 * 检查值是否为布尔值
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isBoolean(value) {
  return typeof value === 'boolean'
}

/**
 * 检查值是否为函数
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isFunction(value) {
  return typeof value === 'function'
}

/**
 * 检查值是否为null或undefined
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isNil(value) {
  return value === null || value === undefined
}

/**
 * 安全访问对象属性
 * @param {object} obj - 目标对象
 * @param {string} path - 属性路径，支持点分隔如 'a.b.c'
 * @param {any} defaultValue - 默认值
 * @returns {any}
 */
export function safeGet(obj, path, defaultValue = undefined) {
  if (!isObject(obj)) {
    return defaultValue
  }
  
  const keys = path.split('.')
  let result = obj
  
  for (const key of keys) {
    if (!isObject(result) && !isArray(result)) {
      return defaultValue
    }
    result = result[key]
    if (isNil(result)) {
      return defaultValue
    }
  }
  
  return result
}

/**
 * 安全访问用户信息属性
 * @param {object} userInfo - 用户信息对象
 * @param {string} field - 属性字段名
 * @param {any} defaultValue - 默认值
 * @returns {any}
 */
export function safeGetUserInfo(userInfo, field, defaultValue = '') {
  if (!isObject(userInfo)) {
    return defaultValue
  }
  const value = userInfo[field]
  return isNil(value) ? defaultValue : value
}

/**
 * 安全访问用户昵称
 * @param {object} userInfo - 用户信息对象
 * @param {string} defaultValue - 默认值
 * @returns {string}
 */
export function safeGetUserNickname(userInfo, defaultValue = '用户') {
  return safeGetUserInfo(userInfo, 'nickname', defaultValue)
}

/**
 * 安全访问用户头像
 * @param {object} userInfo - 用户信息对象
 * @param {string} defaultValue - 默认头像URL
 * @returns {string}
 */
export function safeGetUserAvatar(userInfo, defaultValue = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png') {
  return safeGetUserInfo(userInfo, 'avatar', defaultValue)
}

/**
 * 安全访问用户名称（兼容name和nickname字段）
 * @param {object} userInfo - 用户信息对象
 * @param {string} defaultValue - 默认值
 * @returns {string}
 */
export function safeGetUserName(userInfo, defaultValue = '用户') {
  if (!isObject(userInfo)) {
    return defaultValue
  }
  return userInfo.name || userInfo.nickname || defaultValue
}

/**
 * 安全渲染用户信息，防止Promise对象直接渲染
 * @param {object} userInfo - 用户信息对象
 * @returns {boolean} - 是否可以安全渲染
 */
export function canRenderUserInfo(userInfo) {
  return isObject(userInfo)
}

/**
 * 解析localStorage中的JSON数据，带有异常处理
 * @param {string} key - localStorage键名
 * @param {any} defaultValue - 默认值
 * @returns {any}
 */
export function safeParseLocalStorage(key, defaultValue = {}) {
  try {
    const value = localStorage.getItem(key)
    if (isNil(value)) {
      return defaultValue
    }
    return JSON.parse(value)
  } catch (error) {
    console.error(`解析localStorage[${key}]失败:`, error)
    return defaultValue
  }
}

/**
 * 设置localStorage中的JSON数据，带有异常处理
 * @param {string} key - localStorage键名
 * @param {any} value - 要存储的值
 * @returns {boolean} - 是否成功
 */
export function safeSetLocalStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch (error) {
    console.error(`设置localStorage[${key}]失败:`, error)
    return false
  }
}

/**
 * 移除localStorage中的数据，带有异常处理
 * @param {string} key - localStorage键名
 * @returns {boolean} - 是否成功
 */
export function safeRemoveLocalStorage(key) {
  try {
    localStorage.removeItem(key)
    return true
  } catch (error) {
    console.error(`移除localStorage[${key}]失败:`, error)
    return false
  }
}

/**
 * XSS防护：转义HTML特殊字符
 * @param {string} str - 待转义的字符串
 * @returns {string} - 转义后的字符串
 */
export function escapeHtml(str) {
  if (!isString(str)) {
    return str
  }
  const div = document.createElement('div')
  div.textContent = str
  return div.innerHTML
}

/**
 * XSS防护：清理HTML标签
 * @param {string} str - 待清理的字符串
 * @param {boolean} keepWhitespace - 是否保留空白字符
 * @returns {string} - 清理后的字符串
 */
export function stripHtml(str, keepWhitespace = true) {
  if (!isString(str)) {
    return str
  }
  const temp = document.createElement('div')
  temp.innerHTML = str
  const text = temp.textContent || temp.innerText || ''
  return keepWhitespace ? text : text.replace(/\s+/g, ' ').trim()
}

/**
 * 验证邮箱格式
 * @param {string} email - 待验证的邮箱
 * @returns {boolean}
 */
export function isValidEmail(email) {
  if (!isString(email)) {
    return false
  }
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

/**
 * 验证手机号码格式（中国大陆）
 * @param {string} phone - 待验证的手机号
 * @returns {boolean}
 */
export function isValidPhone(phone) {
  if (!isString(phone)) {
    return false
  }
  const re = /^1[3-9]\d{9}$/
  return re.test(phone)
}

/**
 * 验证密码强度（至少6位，包含大小写字母和数字）
 * @param {string} password - 待验证的密码
 * @returns {boolean}
 */
export function isValidPassword(password) {
  if (!isString(password)) {
    return false
  }
  return password.length >= 6
}

/**
 * 验证URL格式
 * @param {string} url - 待验证的URL
 * @returns {boolean}
 */
export function isValidUrl(url) {
  if (!isString(url)) {
    return false
  }
  try {
    new URL(url)
    return true
  } catch (_) {
    return false
  }
}

/**
 * 验证身份证号码格式
 * @param {string} idCard - 待验证的身份证号码
 * @returns {boolean}
 */
export function isValidIdCard(idCard) {
  if (!isString(idCard)) {
    return false
  }
  const re = /^\d{17}[\dXx]$/
  return re.test(idCard)
}

/**
 * 生成随机ID
 * @param {number} length - ID长度
 * @returns {string}
 */
export function generateId(length = 16) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 生成唯一ID（基于时间戳）
 * @returns {string}
 */
export function generateUniqueId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * 防抖函数
 * @param {function} fn - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {function} - 防抖后的函数
 */
export function debounce(fn, delay) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {function} fn - 要节流的函数
 * @param {number} delay - 节流时间（毫秒）
 * @returns {function} - 节流后的函数
 */
export function throttle(fn, delay) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

/**
 * 对象深拷贝
 * @param {any} obj - 待拷贝的对象
 * @returns {any} - 拷贝后的对象
 */
export function deepClone(obj) {
  if (isNil(obj) || !isObject(obj)) {
    return obj
  }
  
  if (isArray(obj)) {
    return obj.map(item => deepClone(item))
  }
  
  const clone = {}
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      clone[key] = deepClone(obj[key])
    }
  }
  return clone
}

/**
 * 合并对象（深合并）
 * @param {object} target - 目标对象
 * @param {...object} sources - 源对象
 * @returns {object} - 合并后的对象
 */
export function deepMerge(target, ...sources) {
  if (!sources.length) return target
  const source = sources.shift()
  
  if (isObject(target) && isObject(source)) {
    for (const key in source) {
      if (isObject(source[key])) {
        if (!target[key]) Object.assign(target, { [key]: {} })
        deepMerge(target[key], source[key])
      } else {
        Object.assign(target, { [key]: source[key] })
      }
    }
  }
  
  return deepMerge(target, ...sources)
}

/**
 * 检查对象是否为空
 * @param {object} obj - 待检查的对象
 * @returns {boolean}
 */
export function isEmptyObject(obj) {
  return isObject(obj) && Object.keys(obj).length === 0
}

/**
 * 检查数组是否为空
 * @param {array} arr - 待检查的数组
 * @returns {boolean}
 */
export function isEmptyArray(arr) {
  return isArray(arr) && arr.length === 0
}

/**
 * 检查值是否为空（null、undefined、空字符串、空数组、空对象）
 * @param {any} value - 待检查的值
 * @returns {boolean}
 */
export function isEmpty(value) {
  if (isNil(value)) return true
  if (isString(value)) return value.trim() === ''
  if (isArray(value)) return value.length === 0
  if (isObject(value)) return Object.keys(value).length === 0
  return false
}

/**
 * 安全类型转换：转换为字符串
 * @param {any} value - 待转换的值
 * @param {string} defaultValue - 默认值
 * @returns {string}
 */
export function toStringSafe(value, defaultValue = '') {
  if (isNil(value)) return defaultValue
  if (isString(value)) return value
  try {
    return String(value)
  } catch (_) {
    return defaultValue
  }
}

/**
 * 安全类型转换：转换为数字
 * @param {any} value - 待转换的值
 * @param {number} defaultValue - 默认值
 * @returns {number}
 */
export function toNumberSafe(value, defaultValue = 0) {
  if (isNil(value)) return defaultValue
  if (isNumber(value)) return value
  const num = Number(value)
  return isNaN(num) ? defaultValue : num
}

/**
 * 安全类型转换：转换为布尔值
 * @param {any} value - 待转换的值
 * @returns {boolean}
 */
export function toBooleanSafe(value) {
  if (isBoolean(value)) return value
  if (isString(value)) return value.toLowerCase() === 'true' || value === '1'
  if (isNumber(value)) return value !== 0
  return !!value
}

/**
 * 安全类型转换：转换为数组
 * @param {any} value - 待转换的值
 * @param {array} defaultValue - 默认值
 * @returns {array}
 */
export function toArraySafe(value, defaultValue = []) {
  if (isNil(value)) return defaultValue
  if (isArray(value)) return value
  return [value]
}

/**
 * 安全类型转换：转换为对象
 * @param {any} value - 待转换的值
 * @param {object} defaultValue - 默认值
 * @returns {object}
 */
export function toObjectSafe(value, defaultValue = {}) {
  if (isNil(value)) return defaultValue
  if (isObject(value)) return value
  try {
    return JSON.parse(value)
  } catch (_) {
    return defaultValue
  }
}