import { defineStore } from 'pinia'
import { aiApi } from '@/api'
import type { School } from '@/types'

export const useAiStore = defineStore('ai', {
  state: () => ({
    predictionResult: null as unknown,
    recommendations: [] as School[],
    loading: false
  }),

  getters: {
    getPredictionResult: (state) => state.predictionResult,
    getRecommendations: (state) => state.recommendations
  },

  actions: {
    async predictAdmission(studentData: unknown) {
      this.loading = true
      try {
        const response = await aiApi.predictAdmission(studentData)
        if (response.success) {
          this.predictionResult = response.data
          return { success: true as const, data: response.data }
        }
        return { success: false as const, message: response.message }
      } catch (error) {
        return { success: false as const, message: (error as Error).message }
      } finally {
        this.loading = false
      }
    },

    async getRecommendations(studentData: unknown) {
      this.loading = true
      try {
        const response = await aiApi.recommendSchools({ studentData })
        if (response.success) {
          this.recommendations = response.data.recommendations
          return { success: true as const, data: response.data }
        }
        return { success: false as const, message: response.message }
      } catch (error) {
        return { success: false as const, message: (error as Error).message }
      } finally {
        this.loading = false
      }
    }
  }
})