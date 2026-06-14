import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/store'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('setToken', () => {
    it('should set token to localStorage', () => {
      const store = useUserStore()
      store.setToken('test-token-123')
      
      expect(localStorage.getItem('token')).toBe('test-token-123')
    })
  })

  describe('setUserInfo', () => {
    it('should set userInfo to localStorage', () => {
      const store = useUserStore()
      const userInfo = {
        id: 1,
        nickname: '测试用户',
        phone: '13800138000',
        role: 1
      }
      
      store.setUserInfo(userInfo)
      
      const storedUserInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      expect(storedUserInfo.id).toBe(1)
      expect(storedUserInfo.nickname).toBe('测试用户')
      expect(storedUserInfo.phone).toBe('13800138000')
    })
  })

  describe('logout', () => {
    it('should clear token and userInfo from localStorage', () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userInfo', JSON.stringify({ id: 1, nickname: 'test' }))
      
      const store = useUserStore()
      store.logout()
      
      expect(localStorage.getItem('token')).toBe(null)
      expect(localStorage.getItem('userInfo')).toBe(null)
    })
  })

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockLogin = vi.fn().mockResolvedValue({
        success: true,
        data: {
          token: 'mock-token',
          userInfo: {
            id: 1,
            nickname: '测试用户',
            phone: '13800138000',
            role: 1
          }
        }
      })

      vi.doMock('@/api', () => ({
        userApi: {
          login: mockLogin
        }
      }))

      const store = useUserStore()
      const result = await store.login({ username: '13800138000', password: 'password' })
      
      expect(result.success).toBe(true)
      expect(result.data.token).toBe('mock-token')
      expect(localStorage.getItem('token')).toBe('mock-token')
    })

    it('should handle login failure', async () => {
      const mockLogin = vi.fn().mockResolvedValue({
        success: false,
        message: '登录失败'
      })

      vi.doMock('@/api', () => ({
        userApi: {
          login: mockLogin
        }
      }))

      const store = useUserStore()
      const result = await store.login({ username: 'wrong', password: 'wrong' })
      
      expect(result.success).toBe(false)
      expect(result.message).toBe('登录失败')
    })
  })
})
