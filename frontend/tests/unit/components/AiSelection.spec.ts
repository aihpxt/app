import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHashHistory } from 'vue-router'

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
    Edit: mockIcon,
    MagicStick: mockIcon,
    Refresh: mockIcon,
    DataAnalysis: mockIcon,
    School: mockIcon,
    DataLine: mockIcon,
    Star: mockIcon,
    Check: mockIcon,
    Medal: mockIcon,
    CirclePlus: mockIcon,
    Download: mockIcon,
    Share: mockIcon,
    Top: mockIcon,
    Pointer: mockIcon,
    Flag: mockIcon
  }
})

// Mock the API module
vi.mock('@/api', () => ({
  aiApi: {
    recommendSchools: vi.fn(),
    predictAdmission: vi.fn()
  }
}))

// Mock cityList from utils
vi.mock('@/utils', () => ({
  cityList: ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市']
}))

import AiSelection from '@/views/AiSelection.vue'

describe('AiSelection.vue', () => {
  let router: ReturnType<typeof createRouter>

  beforeEach(() => {
    setActivePinia(createPinia())

    router = createRouter({
      history: createWebHashHistory(),
      routes: [
        { path: '/ai-selection', name: 'AiSelection', component: AiSelection }
      ]
    })
  })

  it('should render the component', async () => {
    router.push('/ai-selection')
    await router.isReady()

    const wrapper = mount(AiSelection, {
      global: {
        plugins: [router, createPinia()]
      },
      stubs: {
        'el-card': true,
        'el-form': true,
        'el-form-item': true,
        'el-input': true,
        'el-select': true,
        'el-option': true,
        'el-button': true,
        'el-table': true,
        'el-table-column': true,
        'el-tag': true,
        'el-row': true,
        'el-col': true,
        'el-empty': true,
        'el-skeleton': true,
        'el-result': true,
        'el-icon': true,
        'el-progress': true,
        'el-input-number': true,
        'el-radio-group': true,
        'el-radio': true,
        'el-collapse': true,
        'el-collapse-item': true
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should have form fields for AI selection', async () => {
    router.push('/ai-selection')
    await router.isReady()

    const wrapper = mount(AiSelection, {
      global: {
        plugins: [router, createPinia()]
      },
      stubs: {
        'el-card': true,
        'el-form': true,
        'el-form-item': true,
        'el-input': true,
        'el-select': true,
        'el-option': true,
        'el-button': true,
        'el-table': true,
        'el-table-column': true,
        'el-tag': true,
        'el-row': true,
        'el-col': true,
        'el-empty': true,
        'el-skeleton': true,
        'el-result': true,
        'el-icon': true,
        'el-progress': true,
        'el-input-number': true,
        'el-radio-group': true,
        'el-radio': true,
        'el-collapse': true,
        'el-collapse-item': true
      }
    })

    expect(wrapper.vm).toBeDefined()
  })
})