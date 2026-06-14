import { createPinia, defineStore } from 'pinia'
import { userApi, schoolApi, aiApi } from '@/api'

const store = createPinia()

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
    isLoggedIn: !!localStorage.getItem('token'),
    isRefreshing: false
  }),

  getters: {
    getToken: (state) => state.token,
    getUserInfo: (state) => state.userInfo,
    getIsLoggedIn: (state) => state.isLoggedIn,
    getIsRefreshing: (state) => state.isRefreshing
  },

  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
      this.isLoggedIn = true
    },

    setUserInfo(userInfo) {
      this.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },

    async login(loginData) {
      try {
        const response = await userApi.login(loginData)
        if (response.success) {
          this.setToken(response.data.token)
          this.setUserInfo(response.data.userInfo)
          return { success: true, message: '登录成功' }
        }
        return { success: false, message: response.message }
      } catch (error) {
        return { success: false, message: error.message || '登录失败' }
      }
    },

    async register(registerData) {
      try {
        const response = await userApi.register(registerData)
        if (response.success) {
          return { success: true, message: '注册成功' }
        }
        return { success: false, message: response.message }
      } catch (error) {
        return { success: false, message: error.message || '注册失败' }
      }
    },

    async fetchUserInfo() {
      if (this.isRefreshing) return { success: false, message: '正在刷新中' }
      
      this.isRefreshing = true
      try {
        const response = await userApi.getUserInfo()
        if (response.success) {
          this.setUserInfo(response.data)
          return { success: true }
        }
        return { success: false, message: response.message }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.isRefreshing = false
      }
    },

    async initUserSession() {
      if (!this.token) return
      await this.fetchUserInfo()
    },

    async updateUserInfo(userData) {
      try {
        const response = await userApi.updateUserInfo(userData)
        if (response.success) {
          this.setUserInfo(response.data)
          return { success: true, message: '更新成功' }
        }
        return { success: false, message: response.message }
      } catch (error) {
        return { success: false, message: error.message || '更新失败' }
      }
    },

    logout() {
      this.token = ''
      this.userInfo = {}
      this.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }
})

export const useSchoolStore = defineStore('school', {
  state: () => ({
    schoolList: [],
    currentSchool: null,
    searchParams: {
      keyword: '',
      city: '',
      type: null,
      page: 1,
      size: 10
    },
    total: 0,
    loading: false
  }),

  getters: {
    getSchoolList: (state) => state.schoolList,
    getCurrentSchool: (state) => state.currentSchool,
    getSearchParams: (state) => state.searchParams,
    // 增加兼容字段：让页面取 items 也能拿到数据
    items: (state) => state.schoolList,
  },

  actions: {
    setSearchParams(params) {
      this.searchParams = { ...this.searchParams, ...params }
    },

    async fetchSchoolList(params = {}) {
      this.loading = true
      try {
        const searchParams = { ...this.searchParams, ...params }
        console.log('请求参数:', searchParams)
        const response = await schoolApi.getSchoolList(searchParams)
        console.log('API响应:', response)

        // 完全匹配后端返回格式 { success, data: { items, total, page, size, statistics } }
        if (response?.success) {
          const responseData = response.data || {}
          this.schoolList = Array.isArray(responseData) ? responseData : (responseData.items || [])
          this.total = responseData.total || response.total || 0
          this.searchParams.page = responseData.page || response.page || 1
          this.searchParams.size = responseData.size || response.size || 10

          console.log('✅ 学校列表加载成功:', this.schoolList.length, '条')
          return {
            success: true,
            items: this.schoolList,
            total: this.total,
          }
        } else {
          this.schoolList = []
          this.total = 0
          console.log('❌ 获取学校列表失败:', response)
          return { success: false, message: response?.message || '获取失败' }
        }
      } catch (error) {
        console.error('❌ 请求学校列表异常:', error)
        this.schoolList = []
        this.total = 0
        return { success: false, message: error.message || '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async fetchSchoolDetail(id) {
      try {
        const response = await schoolApi.getSchoolDetail(id)
        if (response?.success) {
          this.currentSchool = response.data
          return { success: true, data: response.data }
        } else {
          return { success: false, message: '获取学校详情失败' }
        }
      } catch (error) {
        console.error('获取学校详情失败:', error)
        return { success: false, message: error.message }
      }
    },

    // 重置列表（可选，分页/搜索用）
    resetSchoolList() {
      this.schoolList = []
      this.total = 0
      this.searchParams.page = 1
    }
  }
})

export const useAiStore = defineStore('ai', {
  state: () => ({
    predictionResult: null,
    recommendations: [],
    loading: false
  }),

  getters: {
    getPredictionResult: (state) => state.predictionResult,
    getRecommendations: (state) => state.recommendations
  },

  actions: {
    async predictAdmission(studentData) {
      this.loading = true
      try {
        const response = await aiApi.predictAdmission(studentData)
        if (response.success) {
          this.predictionResult = response.data
          return { success: true, data: response.data }
        }
        return { success: false, message: response.message }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.loading = false
      }
    },

    async getRecommendations(studentData) {
      this.loading = true
      try {
        const response = await aiApi.recommendSchools({ studentData })
        if (response.success) {
          this.recommendations = response.data.recommendations
          return { success: true, data: response.data }
        }
        return { success: false, message: response.message }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.loading = false
      }
    }
  }
})

export default store
