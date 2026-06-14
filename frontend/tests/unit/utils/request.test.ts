import { apiClient, aiApiClient } from '@/utils/request'

describe('Request Utilities', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('apiClient', () => {
    it('should have correct timeout', () => {
      expect(apiClient.defaults.timeout).toBe(15000)
    })

    it('should have correct headers', () => {
      expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
      expect(apiClient.defaults.headers['Accept']).toBe('application/json')
    })

    it('should handle token in request interceptor', () => {
      localStorage.setItem('token', 'test-token-123')
      
      const config = { headers: {} } as any
      const result = apiClient.interceptors.request.handlers[0].fulfilled(config)
      
      expect(result.headers.Authorization).toBe('Bearer test-token-123')
    })

    it('should handle 401 error in response interceptor', () => {
      const originalLocation = window.location.href
      
      const error = {
        response: {
          status: 401
        }
      }
      
      try {
        apiClient.interceptors.response.handlers[0].rejected(error)
      } catch (e) {
        // Expected to reject
      }
      
      expect(localStorage.getItem('token')).toBe(null)
      expect(localStorage.getItem('userInfo')).toBe(null)
      
      window.history.replaceState({}, '', originalLocation)
    })
  })

  describe('aiApiClient', () => {
    it('should have correct timeout', () => {
      expect(aiApiClient.defaults.timeout).toBe(90000)
    })

    it('should have correct headers', () => {
      expect(aiApiClient.defaults.headers['Content-Type']).toBe('application/json')
      expect(aiApiClient.defaults.headers['Accept']).toBe('application/json, text/event-stream')
    })

    it('should handle token in request interceptor', () => {
      localStorage.setItem('token', 'test-ai-token')
      
      const config = { headers: {} } as any
      const result = aiApiClient.interceptors.request.handlers[0].fulfilled(config)
      
      expect(result.headers.Authorization).toBe('Bearer test-ai-token')
    })
  })
})
