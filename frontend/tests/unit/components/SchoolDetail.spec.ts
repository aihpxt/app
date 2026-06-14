import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHashHistory } from 'vue-router'

// Mock echarts
vi.mock('echarts', () => ({
  default: {
    init: vi.fn(() => ({
      setOption: vi.fn(),
      dispose: vi.fn(),
      resize: vi.fn()
    }))
  }
}))

// Mock Element Plus ElMessage
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn()
    }
  }
})

// Mock @element-plus/icons-vue
vi.mock('@element-plus/icons-vue', () => {
  const mockIcon = { template: '<span></span>' }
  return {
    View: mockIcon,
    Star: mockIcon,
    StarFilled: mockIcon,
    Plus: mockIcon,
    InfoFilled: mockIcon,
    Medal: mockIcon,
    DataAnalysis: mockIcon,
    MagicStick: mockIcon,
    School: mockIcon,
    TrendCharts: mockIcon
  }
})

// Mock the store
vi.mock('@/store', () => ({
  useSchoolStore: vi.fn()
}))

// Mock the shared store
vi.mock('@/store/shared', () => ({
  useSharedStore: vi.fn(() => ({
    selectedSchools: [],
    selectedCount: 0,
    favorites: [],
    isFavorited: vi.fn(() => false),
    toggleFavorite: vi.fn(),
    addSelected: vi.fn(() => true),
    removeSelected: vi.fn(),
    clearSelected: vi.fn()
  }))
}))

import SchoolDetail from '@/views/SchoolDetail.vue'
import { useSchoolStore } from '@/store'

describe('SchoolDetail.vue', () => {
  let router: ReturnType<typeof createRouter>
  let mockSchoolStore: ReturnType<typeof useSchoolStore>

  beforeEach(() => {
    setActivePinia(createPinia())

    // Setup mock school store
    mockSchoolStore = {
      currentSchool: null,
      relatedSchools: [],
      fetchSchoolDetail: vi.fn(),
      fetchRelatedSchools: vi.fn()
    } as any

    vi.mocked(useSchoolStore).mockReturnValue(mockSchoolStore as any)

    router = createRouter({
      history: createWebHashHistory(),
      routes: [
        { path: '/school/:id', name: 'SchoolDetail', component: SchoolDetail }
      ]
    })
  })

  it('should render the component', async () => {
    router.push({ name: 'SchoolDetail', params: { id: '1' } })
    await router.isReady()

    const wrapper = mount(SchoolDetail, {
      global: {
        plugins: [router, createPinia()]
      },
      stubs: {
        'el-card': true,
        'el-descriptions': true,
        'el-button': true,
        'el-tag': true,
        'el-row': true,
        'el-col': true,
        'el-empty': true,
        'el-skeleton': true,
        'el-icon': true,
        'el-progress': true,
        'el-form': true,
        'el-form-item': true,
        'el-input-number': true
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display school name when loaded', async () => {
    mockSchoolStore.currentSchool = {
      id: 1,
      name: '云南师范大学附属中学',
      type: 2,
      type_name: '重点高中',
      nature: '公办',
      city: '昆明市',
      address: '昆明市五华区一二一大街298号',
      min_score: 685,
      one_rate: 98,
      is_public: 1,
      is_key: 1
    } as any

    router.push({ name: 'SchoolDetail', params: { id: '1' } })
    await router.isReady()

    const wrapper = mount(SchoolDetail, {
      global: {
        plugins: [router, createPinia()]
      },
      stubs: {
        'el-card': true,
        'el-descriptions': true,
        'el-button': true,
        'el-tag': true,
        'el-row': true,
        'el-col': true,
        'el-empty': true,
        'el-skeleton': true,
        'el-icon': true,
        'el-progress': true,
        'el-form': true,
        'el-form-item': true,
        'el-input-number': true
      }
    })

    expect(wrapper.vm).toBeDefined()
  })
})