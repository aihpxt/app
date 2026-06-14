/**
 * 系统类型定义文件
 */

// 用户信息类型
export interface UserInfo {
  id: string | number
  nickname: string
  name?: string
  avatar?: string
  email?: string
  phone?: string
  role?: number
  createdAt?: string
  updatedAt?: string
}

// 学校信息类型
export interface School {
  id: string | number
  name: string
  city: string
  prefecture?: string
  district?: string
  type: number
  typeName?: string
  type_name?: string
  address?: string
  phone?: string
  website?: string
  description?: string
  logo?: string
  rating?: number
  students?: number
  teachers?: number
  foundedYear?: number
  founded_year?: number
  admissionScore?: number
  min_score?: number | null
  minScore?: number | null
  min_rank?: number
  minRank?: number
  one_rate?: number
  oneRate?: number
  two_rate?: number
  features?: string[]
  tags?: string[]
  nature?: string
  is_public?: number
  is_key?: number | boolean
  tuition?: number | string
  boarding?: string
  style?: string
  view_count?: number
}

// 政策信息类型
export interface Policy {
  id: string | number
  title: string
  category: string
  categoryName?: string
  content: string
  source?: string
  publishDate?: string
  effectiveDate?: string
  region?: string
  tags?: string[]
}

// 学生信息类型
export interface StudentInfo {
  id: string | number
  userId: string | number
  name: string
  grade: number
  city: string
  district?: string
  school?: string
  scores?: SubjectScores
  ranking?: number
  totalScore?: number
  targetSchools?: string[]
}

// 科目分数类型
export interface SubjectScores {
  chinese?: number
  math?: number
  english?: number
  physics?: number
  chemistry?: number
  biology?: number
  history?: number
  geography?: number
  politics?: number
}

// AI预测结果类型
export interface PredictionResult {
  success: boolean
  data: {
    predictedScore?: number
    probability?: number
    recommendedSchools?: School[]
    analysis?: string
  }
  message?: string
}

// AI推荐结果类型
export interface RecommendationResult {
  success: boolean
  data: {
    recommendations: School[]
    explanation?: string
    confidence?: number
  }
  message?: string
}

// 志愿填报结果类型
export interface VolunteerResult {
  success: boolean
  data: {
    volunteerList: VolunteerItem[]
    analysis?: string
    riskLevel?: 'low' | 'medium' | 'high'
  }
  message?: string
}

// 志愿项类型
export interface VolunteerItem {
  schoolId: string | number
  schoolName: string
  batch: number
  priority: number
  probability?: number
}

// 会话信息类型
export interface SessionInfo {
  id: string
  userId?: string | number
  createdAt: string
  lastMessageAt?: string
  messages?: Message[]
}

// 消息类型
export interface Message {
  id: string
  sessionId: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  type?: 'text' | 'image' | 'file' | 'card'
}

// 通知类型
export interface Notification {
  id: string | number
  userId: string | number
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  content: string
  read: boolean
  createdAt: string
  url?: string
}

// API响应类型
export interface ApiResponse<T = unknown> {
  success: boolean
  data: T
  message?: string
  code?: number
}

// 分页响应类型（后端实际返回格式）
export interface PagedResponse<T = unknown> {
  success: boolean
  data: T[]
  total: number
  page: number
  size: number
  message?: string
}

// 学校搜索参数类型
export interface SchoolSearchParams {
  keyword?: string
  city?: string
  type?: number | null
  page?: number
  size?: number
}

// 政策搜索参数类型
export interface PolicySearchParams {
  keyword?: string
  category?: string
  region?: string
  page?: number
  size?: number
}

// 统一响应结果类型
export type Result<T = unknown> = Promise<ApiResponse<T>>

// 统一分页结果类型
export type PagedResult<T = unknown> = Promise<PagedResponse<T>>

// 空值类型
export type Nullable<T> = T | null | undefined

// 可选属性类型
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

// 只读属性类型
export type ReadonlyBy<T, K extends keyof T> = Omit<T, K> & Readonly<Pick<T, K>>

// 深层部分类型
export type DeepPartial<T> = T extends object
  ? {
      [P in keyof T]?: DeepPartial<T[P]>
    }
  : T

// 深层只读类型
export type DeepReadonly<T> = T extends object
  ? {
      readonly [P in keyof T]: DeepReadonly<T[P]>
    }
  : T

// 类型守卫：检查是否为对象
export function isObject<T>(value: unknown): value is T {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

// 类型守卫：检查是否为数组
export function isArray<T>(value: unknown): value is T[] {
  return Array.isArray(value)
}

// 类型守卫：检查是否为字符串
export function isString(value: unknown): value is string {
  return typeof value === 'string'
}

// 类型守卫：检查是否为数字
export function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value)
}

// 类型守卫：检查是否为布尔值
export function isBoolean(value: unknown): value is boolean {
  return typeof value === 'boolean'
}

// 类型守卫：检查是否为Promise
export function isPromise<T>(value: unknown): value is Promise<T> {
  return value !== null && typeof value === 'object' && typeof (value as Promise<T>).then === 'function'
}

// 类型守卫：检查是否为null或undefined
export function isNil(value: unknown): value is null | undefined {
  return value === null || value === undefined
}

// 类型守卫：检查是否为空
export function isEmpty(value: unknown): boolean {
  if (isNil(value)) return true
  if (isString(value)) return value.trim() === ''
  if (isArray(value)) return value.length === 0
  if (isObject(value)) return Object.keys(value).length === 0
  return false
}