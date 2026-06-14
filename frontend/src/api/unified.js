/**
 * 统一API接口
 * 整合所有后端服务的统一调用接口
 */

import axios from 'axios'

// 统一API基础URL
const GATEWAY_BASE_URL = 'http://localhost:8081'
const AI_SERVICE_BASE_URL = 'http://localhost:8000'

// 创建axios实例
const gatewayClient = axios.create({
  baseURL: GATEWAY_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const aiClient = axios.create({
  baseURL: AI_SERVICE_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
gatewayClient.interceptors.request.use(
  config => {
    // 添加token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
gatewayClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

/**
 * 智能体相关API
 */
export const agentAPI = {
  // 智能体对话
  chat: (message, context = {}) => {
    return gatewayClient.post('/api/agents/chat', { message, context })
  },

  // 获取所有智能体
  listAgents: () => {
    return gatewayClient.get('/api/agents/list')
  },

  // 获取智能体信息
  getAgentInfo: (agentId) => {
    return gatewayClient.get(`/api/agents/info?id=${agentId}`)
  },

  // 获取智能体统计
  getAgentStats: () => {
    return gatewayClient.get('/api/agents/stats')
  },

  // 获取分派规则
  getDispatchRules: () => {
    return gatewayClient.get('/api/agents/rules')
  }
}

/**
 * 学校相关API
 */
export const schoolAPI = {
  // 获取学校列表
  getSchools: (filters = {}) => {
    return gatewayClient.get('/api/schools', { params: filters })
  },

  // 获取学校详情
  getSchoolDetail: (schoolId) => {
    return gatewayClient.get(`/api/schools/${schoolId}`)
  },

  // 搜索学校
  searchSchools: (keyword) => {
    return gatewayClient.get('/api/schools/search', { params: { keyword } })
  },

  // 对比学校
  compareSchools: (schoolIds) => {
    return gatewayClient.post('/api/schools/compare', { schoolIds })
  },

  // 收藏学校
  favoriteSchool: (schoolId) => {
    return gatewayClient.post('/api/schools/favorite', { schoolId })
  },

  // 取消收藏
  unfavoriteSchool: (schoolId) => {
    return gatewayClient.delete(`/api/schools/favorite/${schoolId}`)
  },

  // 获取收藏列表
  getFavorites: () => {
    return gatewayClient.get('/api/schools/favorites')
  }
}

/**
 * 政策相关API
 */
export const policyAPI = {
  // 获取政策列表
  getPolicies: (filters = {}) => {
    return gatewayClient.get('/api/policies', { params: filters })
  },

  // 获取政策详情
  getPolicyDetail: (policyId) => {
    return gatewayClient.get(`/api/policies/${policyId}`)
  },

  // 搜索政策
  searchPolicies: (keyword) => {
    return gatewayClient.get('/api/policies/search', { params: { keyword } })
  }
}

/**
 * 用户相关API
 */
export const userAPI = {
  // 获取用户信息
  getUserInfo: () => {
    return gatewayClient.get('/api/user/info')
  },

  // 更新用户信息
  updateUserInfo: (userInfo) => {
    return gatewayClient.put('/api/user/info', userInfo)
  },

  // 获取用户画像
  getUserProfile: () => {
    return gatewayClient.get('/api/auth/me')
  },

  // 获取用户活动
  getUserActivities: (limit = 20) => {
    return gatewayClient.get('/api/user/activities', { params: { limit } })
  }
}

/**
 * 电话系统相关API
 */
export const callCenterAPI = {
  // 获取通话记录
  getCallRecords: (phoneNumber) => {
    return gatewayClient.get('/api/call-center/records', {
      params: { phone_number: phoneNumber }
    })
  },

  // 保存通话记录
  saveCallRecord: (record) => {
    return gatewayClient.post('/api/call-center/records', record)
  },

  // 获取统计信息
  getStatistics: () => {
    return gatewayClient.get('/api/call-center/statistics')
  }
}

/**
 * 渠道相关API
 */
export const channelAPI = {
  // Web渠道请求
  webRequest: (request) => {
    return gatewayClient.post('/api/channels/web', request)
  },

  // 电话渠道请求
  phoneRequest: (request) => {
    return gatewayClient.post('/api/channels/phone', request)
  },

  // 微信渠道请求
  wechatRequest: (request) => {
    return gatewayClient.post('/api/channels/wechat', request)
  },

  // 获取渠道统计
  getChannelStats: () => {
    return gatewayClient.get('/api/channels/stats')
  }
}

/**
 * 数据同步相关API
 */
export const syncAPI = {
  // 获取同步状态
  getSyncStatus: () => {
    return gatewayClient.get('/api/sync/status')
  },

  // 执行同步任务
  syncTask: (taskName) => {
    return gatewayClient.post('/api/sync/task', { task_name: taskName })
  },

  // 同步所有任务
  syncAll: () => {
    return gatewayClient.post('/api/sync/all')
  },

  // 获取同步历史
  getSyncHistory: (limit = 10) => {
    return gatewayClient.get('/api/sync/history', { params: { limit } })
  }
}

/**
 * 服务相关API
 */
export const serviceAPI = {
  // 获取服务状态
  getServiceStatus: () => {
    return gatewayClient.get('/services')
  },

  // 获取系统指标
  getMetrics: () => {
    return gatewayClient.get('/metrics')
  },

  // 注册服务
  registerService: (serviceInfo) => {
    return gatewayClient.post('/services/register', serviceInfo)
  }
}

/**
 * Skills相关API
 */
export const skillAPI = {
  // 列出所有Skills
  listSkills: () => {
    return gatewayClient.get('/api/skills/list')
  },

  // 执行Skill
  executeSkill: (skillName, params = {}) => {
    return gatewayClient.post('/api/skills/execute', {
      skill_name: skillName,
      params
    })
  },

  // 获取Skill集成统计
  getIntegrationStats: () => {
    return gatewayClient.get('/api/skills/stats')
  }
}

/**
 * 统一服务类
 */
class UnifiedService {
  constructor() {
    this.currentUser = null
    this.currentSession = null
    this.messageQueue = []
  }

  // 初始化
  async initialize() {
    try {
      // 获取用户信息
      const userInfo = await userAPI.getUserInfo()
      this.currentUser = userInfo

      // 创建会话
      const session = await this.createSession()
      this.currentSession = session

      return {
        success: true,
        user: this.currentUser,
        session: this.currentSession
      }
    } catch (error) {
      console.error('Initialize error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  // 创建会话
  async createSession() {
    try {
      const response = await gatewayClient.post('/api/session/create', {
        user_id: this.currentUser?.id || 'anonymous',
        channel: 'web'
      })
      return response
    } catch (error) {
      console.error('Create session error:', error)
      return null
    }
  }

  // 统一消息发送
  async sendMessage(message, options = {}) {
    const request = {
      message,
      session_id: this.currentSession?.id,
      context: options.context || {},
      ...options
    }

    try {
      const response = await channelAPI.webRequest(request)
      return response
    } catch (error) {
      console.error('Send message error:', error)
      throw error
    }
  }

  // 统一搜索
  async search(keyword, type = 'all') {
    const requests = []

    if (type === 'all' || type === 'schools') {
      requests.push(schoolAPI.searchSchools(keyword))
    }

    if (type === 'all' || type === 'policies') {
      requests.push(policyAPI.searchPolicies(keyword))
    }

    try {
      const results = await Promise.all(requests)
      return {
        success: true,
        results: results.flat(),
        keyword
      }
    } catch (error) {
      console.error('Search error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  // 获取统一用户画像
  async getUnifiedProfile() {
    try {
      const profile = await userAPI.getUserProfile()
      return profile
    } catch (error) {
      console.error('Get profile error:', error)
      return null
    }
  }

  // 跨渠道消息同步
  async syncMessage(message, sourceChannel) {
    try {
      await gatewayClient.post('/api/channels/sync', {
        message,
        source_channel: sourceChannel
      })
      return { success: true }
    } catch (error) {
      console.error('Sync message error:', error)
      return { success: false, error: error.message }
    }
  }

  // 获取系统状态
  async getSystemStatus() {
    try {
      const [services, metrics] = await Promise.all([
        serviceAPI.getServiceStatus(),
        serviceAPI.getMetrics()
      ])

      return {
        success: true,
        services,
        metrics
      }
    } catch (error) {
      console.error('Get system status error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
}

// 创建统一服务实例
const unifiedService = new UnifiedService()

export default unifiedService
