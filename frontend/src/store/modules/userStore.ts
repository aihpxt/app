import { defineStore } from 'pinia'
import { userApi } from '@/api'
import type { UserInfo, ApiResponse } from '@/types'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: ((): UserInfo => {
      try {
        const stored = localStorage.getItem('userInfo')
        return stored ? JSON.parse(stored) : {} as UserInfo
      } catch {
        return {} as UserInfo
      }
    })(),
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
    setToken(token: string) {
      this.token = token
      localStorage.setItem('token', token)
      this.isLoggedIn = true
    },

    setUserInfo(userInfo: UserInfo) {
      this.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },

    async login(loginData: { username: string; password: string }): Promise<ApiResponse<{ token: string; userInfo: UserInfo }>> {
      try {
        const response = await userApi.login(loginData)
        if (response.success) {
          // 兼容不同的响应格式：可能是 token 或 access_token
          const responseData = response.data as any
          const token = responseData?.token || responseData?.access_token
          const userInfo = responseData?.userInfo || {
            id: 1,
            phone: loginData.username,
            nickname: '用户',
            role: 1
          }
          
          if (token) {
            this.setToken(token)
            this.setUserInfo(userInfo)
          }
          return { success: true, data: { token, userInfo }, message: '登录成功' }
        }
        return { success: false, data: response.data, message: response.message || '登录失败' }
      } catch (error) {
        return { success: false, data: {} as { token: string; userInfo: UserInfo }, message: (error as Error).message || '登录失败' }
      }
    },

    async register(registerData: { username: string; password: string; email?: string; phone?: string }): Promise<ApiResponse<unknown>> {
      try {
        const response = await userApi.register(registerData)
        if (response.success) {
          return { success: true, data: response.data, message: '注册成功' }
        }
        return { success: false, data: response.data, message: response.message }
      } catch (error) {
        return { success: false, data: {}, message: (error as Error).message || '注册失败' }
      }
    },

    async fetchUserInfo(): Promise<ApiResponse<UserInfo>> {
      if (this.isRefreshing) return { success: false, data: {} as UserInfo, message: '正在刷新中' }
      
      this.isRefreshing = true
      try {
        const response = await userApi.getUserInfo()
        if (response.success) {
          this.setUserInfo(response.data)
          return { success: true, data: response.data }
        }
        return { success: false, data: {} as UserInfo, message: response.message }
      } catch (error: unknown) {
        const axiosError = error as { response?: { status?: number } }
        if (axiosError.response?.status === 401) {
          this.logout()
          return { success: false, data: {} as UserInfo, message: '未登录或登录已过期' }
        }
        return { success: false, data: {} as UserInfo, message: (error as Error)?.message || '获取用户信息失败' }
      } finally {
        this.isRefreshing = false
      }
    },

    async initUserSession(): Promise<void> {
      if (!this.token) return
      await this.fetchUserInfo()
    },

    async updateUserInfo(userData: Partial<UserInfo>): Promise<ApiResponse<UserInfo>> {
      try {
        const response = await userApi.updateUserInfo(userData)
        if (response.success) {
          this.setUserInfo(response.data)
          return { success: true, data: response.data, message: '更新成功' }
        }
        return { success: false, data: {} as UserInfo, message: response.message }
      } catch (error) {
        return { success: false, data: {} as UserInfo, message: (error as Error).message || '更新失败' }
      }
    },

    logout(): void {
      this.token = ''
      this.userInfo = {} as UserInfo
      this.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }
})