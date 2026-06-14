import { defineStore } from 'pinia'
import { schoolApi } from '@/api'
import type { School, PagedResponse } from '@/types'

export const useSchoolStore = defineStore('school', {
  state: () => ({
    schoolList: [] as School[],
    currentSchool: null as School | null,
    relatedSchools: [] as School[],
    searchParams: {
      keyword: '',
      city: '',
      type: null as number | null,
      nature: '',
      min_score: null as number | null,
      max_score: null as number | null,
      sort_by: 'default',
      page: 1,
      size: 10
    },
    total: 0,
    loading: false,
    stats: {
      total: 0,
      public_count: 0,
      private_count: 0,
      key_count: 0,
      city_stats: [] as Array<{ name: string; count: number }>
    }
  }),

  getters: {
    getSchoolList: (state) => state.schoolList,
    getCurrentSchool: (state) => state.currentSchool,
    getRelatedSchools: (state) => state.relatedSchools,
    getSearchParams: (state) => state.searchParams,
    getStats: (state) => state.stats,
    items: (state) => state.schoolList,
  },

  actions: {
    setSearchParams(params: Partial<typeof this.searchParams>) {
      this.searchParams = { ...this.searchParams, ...params }
    },

    async fetchSchoolList(params: Partial<typeof this.searchParams> = {}) {
      this.loading = true
      try {
        const searchParams = { ...this.searchParams, ...params }
        console.log('请求参数:', searchParams)
        const response = await schoolApi.getSchoolList(searchParams as any)
        console.log('API响应:', response)

        if (response?.success) {
          const data = response as unknown as PagedResponse<School>
          const items = Array.isArray(data.data) ? data.data : []
          this.schoolList = items.map((item: any) => ({
            ...item,
            type: item.type || item.school_type,
            type_name: item.type_name || item.typeName,
            min_score: item.min_score || item.minScore,
            min_rank: item.min_rank || item.minRank,
            one_rate: item.one_rate || item.oneRate,
            is_public: item.is_public ?? item.isPublic,
            nature: item.nature || item.school_nature,
            is_key: item.is_key ?? item.isKey
          }))
          this.total = data.total || 0
          this.searchParams.page = data.page || 1
          this.searchParams.size = data.size || 10

          console.log('✅ 学校列表加载成功:', this.schoolList.length, '条')
          return {
            success: true as const,
            items: this.schoolList,
            total: this.total,
          }
        } else {
          this.schoolList = []
          this.total = 0
          console.log('❌ 获取学校列表失败:', response)
          return { success: false as const, message: response?.message || '获取失败' }
        }
      } catch (error) {
        console.error('❌ 请求学校列表异常:', error)
        this.schoolList = []
        this.total = 0
        return {
          success: false as const,
          message: (error as Error).message || '获取学校列表失败',
        }
      } finally {
        this.loading = false
      }
    },

    async fetchSchoolDetail(id: string | number) {
      try {
        const response = await schoolApi.getSchoolDetail(id)
        if (response?.success) {
          this.currentSchool = response.data
          // 获取相关学校
          this.fetchRelatedSchools(id)
          return { success: true as const, data: response.data }
        } else {
          return { success: false as const, message: '获取学校详情失败' }
        }
      } catch (error) {
        console.error('获取学校详情失败:', error)
        return { success: false as const, message: '获取学校详情失败' }
      }
    },

    async fetchRelatedSchools(id: string | number, limit = 5) {
      try {
        const response = await schoolApi.getRelatedSchools(id, limit)
        if (response?.success) {
          this.relatedSchools = response.data || []
          return { success: true as const, data: this.relatedSchools }
        }
        return { success: false as const, data: [] }
      } catch (error) {
        console.error('获取相关学校失败:', error)
        return { success: false as const, data: [] }
      }
    },

    async fetchSchoolStats() {
      try {
        const response = await schoolApi.getSchoolStats()
        if (response?.success) {
          this.stats = response.data || this.stats
          return { success: true as const, data: this.stats }
        }
        return { success: false as const, message: '获取统计数据失败' }
      } catch (error) {
        console.error('获取统计数据失败:', error)
        return { success: false as const, message: '获取统计数据失败' }
      }
    },

    async fetchSchoolsBatch(schoolIds: number[]) {
      try {
        const response = await schoolApi.getSchoolsBatch(schoolIds)
        if (response?.success) {
          return { success: true as const, data: response.data || [] }
        }
        return { success: false as const, message: '获取学校信息失败' }
      } catch (error) {
        console.error('批量获取学校失败:', error)
        return { success: false as const, message: '获取学校信息失败' }
      }
    },

    resetSchoolList() {
      this.schoolList = []
      this.total = 0
      this.searchParams.page = 1
    }
  }
})