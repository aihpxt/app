import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 共享数据类型定义
export interface SharedState {
  // 用户偏好设置
  preferences: {
    theme: 'light' | 'dark'
    language: 'zh-CN' | 'en'
    notifications: boolean
  }
  
  // 当前选中的学校
  selectedSchools: (string | number)[]
  
  // 收藏的学校
  favorites: (string | number)[]
  
  // 浏览历史
  browsingHistory: Array<{
    id: string | number
    name: string
    timestamp: number
  }>
  
  // 搜索历史
  searchHistory: string[]
  
  // 统计数据
  statistics: {
    totalSchools: number
    publicSchools: number
    privateSchools: number
    keySchools: number
  }
  
  // 页面间传递数据
  transferData: Record<string, unknown>
  
  // 用户信息
  userInfo: {
    id?: number
    name?: string
    avatar?: string
    grade?: string
    targetScore?: number
    targetSchool?: string
  }
  
  // 学习目标数据
  learningGoals: Array<{
    id: number
    title: string
    subject: string
    target: string
    deadline: string
    progress: number
    status: 'active' | 'completed' | 'overdue'
  }>
  
  // 学习计划数据
  studyPlans: Array<{
    id: number
    title: string
    subject: string
    date: string
    time: string
    duration: number
    completed: boolean
    priority: 'high' | 'medium' | 'low'
  }>
}

// 创建共享状态存储
export const useSharedStore = defineStore('shared', () => {
  // 响应式状态
  const preferences = ref<SharedState['preferences']>({
    theme: 'dark',
    language: 'zh-CN',
    notifications: true
  })
  
  const selectedSchools = ref<(string | number)[]>([])
  const favorites = ref<(string | number)[]>([])
  const browsingHistory = ref<SharedState['browsingHistory']>([])
  const searchHistory = ref<string[]>([])
  const statistics = ref<SharedState['statistics']>({
    totalSchools: 0,
    publicSchools: 0,
    privateSchools: 0,
    keySchools: 0
  })
  const transferData = ref<Record<string, unknown>>({})
  
  // 用户信息
  const userInfo = ref<SharedState['userInfo']>({
    id: 1,
    name: '学生用户',
    avatar: '',
    grade: '初三',
    targetScore: 650,
    targetSchool: '云南师范大学附属中学'
  })
  
  // 学习目标数据
  const learningGoals = ref<SharedState['learningGoals']>([
    { id: 1, title: '数学冲刺', subject: '数学', target: '提高到110分', deadline: '2025-06-30', progress: 75, status: 'active' },
    { id: 2, title: '英语听力提升', subject: '英语', target: '听力满分', deadline: '2025-06-30', progress: 60, status: 'active' },
    { id: 3, title: '物理实验复习', subject: '物理', target: '实验题满分', deadline: '2025-06-15', progress: 100, status: 'completed' },
    { id: 4, title: '语文作文训练', subject: '语文', target: '作文50分以上', deadline: '2025-06-30', progress: 45, status: 'active' },
    { id: 5, title: '化学方程式背诵', subject: '化学', target: '全部掌握', deadline: '2025-06-10', progress: 90, status: 'active' }
  ])
  
  // 学习计划数据
  const studyPlans = ref<SharedState['studyPlans']>([
    { id: 1, title: '数学函数专题', subject: '数学', date: new Date().toISOString().split('T')[0], time: '08:00-09:30', duration: 90, completed: true, priority: 'high' },
    { id: 2, title: '英语阅读练习', subject: '英语', date: new Date().toISOString().split('T')[0], time: '10:00-11:30', duration: 90, completed: false, priority: 'high' },
    { id: 3, title: '物理力学复习', subject: '物理', date: new Date().toISOString().split('T')[0], time: '14:00-15:30', duration: 90, completed: false, priority: 'medium' },
    { id: 4, title: '语文古诗词背诵', subject: '语文', date: new Date().toISOString().split('T')[0], time: '16:00-17:00', duration: 60, completed: false, priority: 'medium' },
    { id: 5, title: '化学实验题练习', subject: '化学', date: new Date().toISOString().split('T')[0], time: '19:00-20:30', duration: 90, completed: false, priority: 'low' }
  ])
  
  // 计算属性
  const isLoggedIn = computed(() => {
    return !!localStorage.getItem('token')
  })
  
  const favoriteCount = computed(() => favorites.value.length)
  const selectedCount = computed(() => selectedSchools.value.length)
  
  // 初始化从本地存储加载数据
  const initFromStorage = () => {
    // 加载收藏
    const savedFavorites = localStorage.getItem('favorites')
    if (savedFavorites) {
      try {
        favorites.value = JSON.parse(savedFavorites)
      } catch {
        favorites.value = []
      }
    }
    
    // 加载浏览历史
    const savedHistory = localStorage.getItem('browsingHistory')
    if (savedHistory) {
      try {
        browsingHistory.value = JSON.parse(savedHistory)
      } catch {
        browsingHistory.value = []
      }
    }
    
    // 加载搜索历史
    const savedSearchHistory = localStorage.getItem('searchHistory')
    if (savedSearchHistory) {
      try {
        searchHistory.value = JSON.parse(savedSearchHistory)
      } catch {
        searchHistory.value = []
      }
    }
    
    // 加载偏好设置
    const savedPreferences = localStorage.getItem('preferences')
    if (savedPreferences) {
      try {
        preferences.value = { ...preferences.value, ...JSON.parse(savedPreferences) }
      } catch {}
    }
  }
  
  // 保存收藏到本地存储
  const saveFavorites = () => {
    localStorage.setItem('favorites', JSON.stringify(favorites.value))
  }
  
  // 添加收藏
  const addFavorite = (schoolId: string | number) => {
    if (!favorites.value.includes(schoolId)) {
      favorites.value.push(schoolId)
      saveFavorites()
    }
  }
  
  // 移除收藏
  const removeFavorite = (schoolId: string | number) => {
    const index = favorites.value.indexOf(schoolId)
    if (index > -1) {
      favorites.value.splice(index, 1)
      saveFavorites()
    }
  }
  
  // 切换收藏状态
  const toggleFavorite = (schoolId: string | number): boolean => {
    if (favorites.value.includes(schoolId)) {
      removeFavorite(schoolId)
      return false
    } else {
      addFavorite(schoolId)
      return true
    }
  }
  
  // 检查是否已收藏
  const isFavorited = (schoolId: string | number): boolean => {
    return favorites.value.includes(schoolId)
  }
  
  // 添加到选择列表
  const addSelected = (schoolId: string | number, maxCount = 4): boolean => {
    if (selectedSchools.value.includes(schoolId)) {
      removeSelected(schoolId)
      return false
    }
    if (selectedSchools.value.length >= maxCount) {
      return false
    }
    selectedSchools.value.push(schoolId)
    return true
  }
  
  // 从选择列表移除
  const removeSelected = (schoolId: string | number) => {
    const index = selectedSchools.value.indexOf(schoolId)
    if (index > -1) {
      selectedSchools.value.splice(index, 1)
    }
  }
  
  // 清空选择列表
  const clearSelected = () => {
    selectedSchools.value = []
  }
  
  // 添加浏览记录
  const addBrowsingHistory = (schoolId: string | number, schoolName: string) => {
    // 移除重复记录
    browsingHistory.value = browsingHistory.value.filter(h => h.id !== schoolId)
    
    // 添加到开头
    browsingHistory.value.unshift({
      id: schoolId,
      name: schoolName,
      timestamp: Date.now()
    })
    
    // 保留最近20条记录
    if (browsingHistory.value.length > 20) {
      browsingHistory.value = browsingHistory.value.slice(0, 20)
    }
    
    // 保存到本地存储
    localStorage.setItem('browsingHistory', JSON.stringify(browsingHistory.value))
  }
  
  // 添加搜索历史
  const addSearchHistory = (keyword: string) => {
    if (!keyword.trim()) return
    
    // 移除重复记录
    searchHistory.value = searchHistory.value.filter(h => h !== keyword)
    
    // 添加到开头
    searchHistory.value.unshift(keyword)
    
    // 保留最近10条记录
    if (searchHistory.value.length > 10) {
      searchHistory.value = searchHistory.value.slice(0, 10)
    }
    
    // 保存到本地存储
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
  }
  
  // 清空搜索历史
  const clearSearchHistory = () => {
    searchHistory.value = []
    localStorage.removeItem('searchHistory')
  }
  
  // 更新统计数据
  const updateStatistics = (stats: Partial<SharedState['statistics']>) => {
    statistics.value = { ...statistics.value, ...stats }
  }
  
  // 设置传递数据
  const setTransferData = (key: string, data: unknown) => {
    transferData.value[key] = data
  }
  
  // 获取传递数据
  const getTransferData = (key: string): unknown => {
    return transferData.value[key]
  }
  
  // 清除传递数据
  const clearTransferData = (key?: string) => {
    if (key) {
      delete transferData.value[key]
    } else {
      transferData.value = {}
    }
  }
  
  // 更新偏好设置
  const updatePreferences = (newPreferences: Partial<SharedState['preferences']>) => {
    preferences.value = { ...preferences.value, ...newPreferences }
    localStorage.setItem('preferences', JSON.stringify(preferences.value))
  }
  
  // 更新用户信息
  const updateUserInfo = (newInfo: Partial<SharedState['userInfo']>) => {
    userInfo.value = { ...userInfo.value, ...newInfo }
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    eventBus.emit(Events.USER_INFO_UPDATED, userInfo.value)
  }
  
  // 添加学习目标
  const addLearningGoal = (goal: Omit<SharedState['learningGoals'][0], 'id'>) => {
    const newGoal = {
      ...goal,
      id: Date.now()
    }
    learningGoals.value.push(newGoal)
    saveLearningGoals()
    eventBus.emit(Events.GOAL_ADDED, newGoal)
  }
  
  // 更新学习目标
  const updateLearningGoal = (id: number, updates: Partial<SharedState['learningGoals'][0]>) => {
    const index = learningGoals.value.findIndex(g => g.id === id)
    if (index > -1) {
      learningGoals.value[index] = { ...learningGoals.value[index], ...updates }
      saveLearningGoals()
      eventBus.emit(Events.GOAL_UPDATED, learningGoals.value[index])
    }
  }
  
  // 删除学习目标
  const deleteLearningGoal = (id: number) => {
    const index = learningGoals.value.findIndex(g => g.id === id)
    if (index > -1) {
      const deletedGoal = learningGoals.value[index]
      learningGoals.value.splice(index, 1)
      saveLearningGoals()
      eventBus.emit(Events.GOAL_DELETED, deletedGoal)
    }
  }
  
  // 保存学习目标到本地存储
  const saveLearningGoals = () => {
    localStorage.setItem('learningGoals', JSON.stringify(learningGoals.value))
  }
  
  // 添加学习计划
  const addStudyPlan = (plan: Omit<SharedState['studyPlans'][0], 'id'>) => {
    const newPlan = {
      ...plan,
      id: Date.now()
    }
    studyPlans.value.push(newPlan)
    saveStudyPlans()
    eventBus.emit(Events.PLAN_ADDED, newPlan)
  }
  
  // 更新学习计划
  const updateStudyPlan = (id: number, updates: Partial<SharedState['studyPlans'][0]>) => {
    const index = studyPlans.value.findIndex(p => p.id === id)
    if (index > -1) {
      studyPlans.value[index] = { ...studyPlans.value[index], ...updates }
      saveStudyPlans()
      eventBus.emit(Events.PLAN_UPDATED, studyPlans.value[index])
    }
  }
  
  // 删除学习计划
  const deleteStudyPlan = (id: number) => {
    const index = studyPlans.value.findIndex(p => p.id === id)
    if (index > -1) {
      const deletedPlan = studyPlans.value[index]
      studyPlans.value.splice(index, 1)
      saveStudyPlans()
      eventBus.emit(Events.PLAN_DELETED, deletedPlan)
    }
  }
  
  // 保存学习计划到本地存储
  const saveStudyPlans = () => {
    localStorage.setItem('studyPlans', JSON.stringify(studyPlans.value))
  }
  
  // 导出数据
  const exportData = () => {
    const data = {
      favorites: favorites.value,
      browsingHistory: browsingHistory.value,
      searchHistory: searchHistory.value,
      preferences: preferences.value,
      learningGoals: learningGoals.value,
      studyPlans: studyPlans.value,
      userInfo: userInfo.value
    }
    return JSON.stringify(data, null, 2)
  }
  
  // 初始化
  initFromStorage()
  
  return {
    // 状态
    preferences,
    selectedSchools,
    favorites,
    browsingHistory,
    searchHistory,
    statistics,
    transferData,
    userInfo,
    learningGoals,
    studyPlans,
    
    // 计算属性
    isLoggedIn,
    favoriteCount,
    selectedCount,
    
    // 方法
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorited,
    addSelected,
    removeSelected,
    clearSelected,
    addBrowsingHistory,
    addSearchHistory,
    clearSearchHistory,
    updateStatistics,
    setTransferData,
    getTransferData,
    clearTransferData,
    updatePreferences,
    updateUserInfo,
    addLearningGoal,
    updateLearningGoal,
    deleteLearningGoal,
    addStudyPlan,
    updateStudyPlan,
    deleteStudyPlan,
    exportData,
    initFromStorage,
    saveFavorites,
    saveLearningGoals,
    saveStudyPlans
  }
})

// 事件总线 - 用于页面间通信
class EventBus {
  private listeners: Record<string, Array<(data?: unknown) => void>> = {}
  
  on(event: string, callback: (data?: unknown) => void) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }
  
  off(event: string, callback?: (data?: unknown) => void) {
    if (!this.listeners[event]) return
    
    if (callback) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback)
    } else {
      this.listeners[event] = []
    }
  }
  
  emit(event: string, data?: unknown) {
    if (!this.listeners[event]) return
    
    this.listeners[event].forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error('EventBus error:', error)
      }
    })
  }
  
  once(event: string, callback: (data?: unknown) => void) {
    const onceCallback = (data?: unknown) => {
      callback(data)
      this.off(event, onceCallback)
    }
    this.on(event, onceCallback)
  }
}

export const eventBus = new EventBus()

// 全局事件名称
export const Events = {
  // 收藏相关
  FAVORITE_ADDED: 'favorite_added',
  FAVORITE_REMOVED: 'favorite_removed',
  
  // 选择相关
  SCHOOL_SELECTED: 'school_selected',
  SCHOOL_DESELECTED: 'school_deselected',
  SELECTION_CLEARED: 'selection_cleared',
  
  // 浏览相关
  SCHOOL_VIEWED: 'school_viewed',
  
  // 搜索相关
  SEARCH_PERFORMED: 'search_performed',
  
  // 数据更新
  STATISTICS_UPDATED: 'statistics_updated',
  
  // 用户相关
  USER_LOGIN: 'user_login',
  USER_LOGOUT: 'user_logout',
  USER_INFO_UPDATED: 'user_info_updated',
  
  // 偏好设置
  PREFERENCES_UPDATED: 'preferences_updated',
  
  // 学习目标相关
  GOAL_ADDED: 'goal_added',
  GOAL_UPDATED: 'goal_updated',
  GOAL_DELETED: 'goal_deleted',
  
  // 学习计划相关
  PLAN_ADDED: 'plan_added',
  PLAN_UPDATED: 'plan_updated',
  PLAN_DELETED: 'plan_deleted'
}
