<template>
  <div class="school-page">
    <!-- 顶部搜索栏 -->
    <div class="wx-search search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
      <input
        class="search-input"
        v-model="searchForm.name"
        placeholder="搜索学校名称"
        @keyup.enter="handleSearch"
      />
    </div>

    <!-- 快速筛选标签 -->
    <div class="filter-tags">
      <span
        v-for="city in quickCityList"
        :key="city.value"
        class="filter-chip"
        :class="{ active: searchForm.city === city.value }"
        @click="filterByCity(city.value)"
      >{{ city.label }}</span>
      <span
        class="filter-chip"
        :class="{ active: searchForm.nature === '公办' }"
        @click="filterByNature('公办')"
      >公办</span>
      <span
        class="filter-chip"
        :class="{ active: searchForm.nature === '民办' }"
        @click="filterByNature('民办')"
      >民办</span>
      <span
        v-if="searchForm.city || searchForm.nature || searchForm.type || searchForm.minScore || searchForm.maxScore"
        class="filter-chip reset"
        @click="handleReset"
      >清除筛选</span>
    </div>

    <!-- 统计概览 -->
    <div class="stats-row">
      <div class="wx-card stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">学校总数</div>
      </div>
      <div class="wx-card stat-card">
        <div class="stat-value" style="color: var(--wx-primary)">{{ stats.publicCount }}</div>
        <div class="stat-label">公办学校</div>
      </div>
      <div class="wx-card stat-card">
        <div class="stat-value" style="color: #E6A23C">{{ stats.privateCount }}</div>
        <div class="stat-label">民办学校</div>
      </div>
      <div class="wx-card stat-card">
        <div class="stat-value" style="color: var(--wx-info)">{{ stats.keyCount }}</div>
        <div class="stat-label">重点高中</div>
      </div>
    </div>

    <!-- 排序和工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <span class="sort-label">排序：</span>
        <select class="sort-select" v-model="sortBy" @change="handleSearch">
          <option value="default">综合排序</option>
          <option value="score_desc">录取分数从高到低</option>
          <option value="score_asc">录取分数从低到高</option>
          <option value="views">浏览量从高到低</option>
        </select>
      </div>
      <div class="toolbar-right">
        <span class="list-count">共 {{ filteredSchools.length }} 所</span>
        <button
          v-if="selectedSchools.length > 0"
          class="wx-btn-primary wx-btn-sm"
          @click="compareSchools"
        >对比 ({{ selectedSchools.length }})</button>
        <button
          v-if="selectedSchools.length > 0"
          class="wx-btn-text wx-btn-sm"
          @click="clearSelection"
        >清除</button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrap">
      <div class="wx-skeleton" style="height: 60px; margin-bottom: 8px;" v-for="i in 6" :key="i"></div>
    </div>

    <!-- 学校列表 -->
    <div class="wx-list" v-else-if="schoolList.length > 0">
      <div
        class="wx-list-item"
        v-for="school in filteredSchools"
        :key="school.id"
        @click="viewDetails(school)"
      >
        <div class="item-avatar">
          <img v-if="school.logo" :src="getSchoolLogo(school)" class="avatar-img" alt="" />
          <span v-else class="avatar-text">{{ school.name?.charAt(0) || '校' }}</span>
        </div>
        <div class="item-content">
          <div class="item-title">{{ school.name }}</div>
          <div class="item-subtitle">
            <span>{{ getTypeName(school) }}</span>
            <span v-if="getPrefectureName(school)"> · {{ getPrefectureName(school) }}</span>
            <span v-if="school.min_score" class="score-tag"> · {{ school.min_score }}分</span>
          </div>
        </div>
        <div class="item-right">
          <span class="view-badge" v-if="school.view_count">
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            {{ school.view_count }}
          </span>
          <span class="item-arrow">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">📭</div>
      <div class="empty-title">未找到符合条件的学校</div>
      <div class="empty-desc" v-if="searchForm.name || searchForm.city || searchForm.nature || searchForm.type">
        <span v-if="searchForm.name">搜索：{{ searchForm.name }}</span>
        <span v-if="searchForm.city">地区：{{ getCityLabel(searchForm.city) }}</span>
        <span v-if="searchForm.type">类型：{{ getTypeLabel(searchForm.type) }}</span>
        <span v-if="searchForm.nature">性质：{{ searchForm.nature }}</span>
      </div>
      <button class="wx-btn-secondary" @click="handleReset" v-if="searchForm.name || searchForm.city || searchForm.nature || searchForm.type">清除条件</button>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > 0">
      <button
        class="page-btn"
        :disabled="currentPage <= 1"
        @click="handleCurrentChange(currentPage - 1)"
      >上一页</button>
      <span class="page-info">{{ currentPage }} / {{ Math.ceil(total / pageSize) }}</span>
      <button
        class="page-btn"
        :disabled="currentPage >= Math.ceil(total / pageSize)"
        @click="handleCurrentChange(currentPage + 1)"
      >下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useSharedStore, eventBus, Events } from '../store/shared'

interface School {
  id: string | number
  name: string
  city: string
  prefecture: string
  district?: string
  type: number
  typeName?: string
  type_name?: string
  address?: string
  phone?: string
  logo?: string
  features?: string
  view_count?: number
  min_score?: number
  is_public?: number
  nature?: string
  is_key?: number | boolean
  isKey?: boolean
  level?: string
  isFavorited?: boolean
  tuition?: number | string
}

interface SearchForm {
  name: string
  city: string
  type: number | null
  nature: string
  minScore: number | null
  maxScore: number | null
}

const cityList = [
  { value: 'km', label: '昆明市' },
  { value: 'qj', label: '曲靖市' },
  { value: 'yx', label: '玉溪市' },
  { value: 'bs', label: '保山市' },
  { value: 'zt', label: '昭通市' },
  { value: 'lj', label: '丽江市' },
  { value: 'pe', label: '普洱市' },
  { value: 'lc', label: '临沧市' },
  { value: 'cx', label: '楚雄州' },
  { value: 'hh', label: '红河州' },
  { value: 'ws', label: '文山州' },
  { value: 'xsbn', label: '西双版纳州' },
  { value: 'dl', label: '大理州' },
  { value: 'dh', label: '德宏州' },
  { value: 'nj', label: '怒江州' },
  { value: 'dq', label: '迪庆州' }
]

const quickCityList = [
  { value: 'km', label: '昆明市' },
  { value: 'qj', label: '曲靖市' },
  { value: 'yx', label: '玉溪市' },
  { value: 'dl', label: '大理州' },
  { value: 'hh', label: '红河州' }
]

const router = useRouter()
const sharedStore = useSharedStore()

const loading = ref(false)
const schoolList = ref<School[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('default')

const selectedSchools = computed(() => sharedStore.selectedSchools)

const filteredSchools = computed(() => {
  return schoolList.value
})

const searchForm = reactive<SearchForm>({
  name: '',
  city: '',
  type: null,
  nature: '',
  minScore: null,
  maxScore: null
})

const localStats = ref({
  totalSchools: 0,
  publicSchools: 0,
  privateSchools: 0,
  keySchools: 0
})

const stats = computed(() => ({
  total: localStats.value.totalSchools,
  publicCount: localStats.value.publicSchools,
  privateCount: localStats.value.privateSchools,
  keyCount: localStats.value.keySchools
}))

const prefectureMap: Record<string, string> = {
  'km': '昆明市', 'qj': '曲靖市', 'yx': '玉溪市', 'bs': '保山市',
  'zt': '昭通市', 'lj': '丽江市', 'pe': '普洱市', 'lc': '临沧市',
  'cx': '楚雄州', 'hh': '红河州', 'ws': '文山州', 'xsbn': '西双版纳州',
  'dl': '大理州', 'dh': '德宏州', 'nj': '怒江州', 'dq': '迪庆州'
}

const typeMap: Record<number | string, string> = {
  1: '普通高中', 2: '重点高中', 3: '中职学校', 4: '民办学校',
  '公办': '公办', '民办': '民办', '普通高中': '普通高中', '重点高中': '重点高中'
}

const colorPalette = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
  '#38f9d7', '#fa709a', '#fee140', '#f09819', '#ff9a9e',
  '#a8edea', '#fed6e3', '#6c5ce7', '#fd79a8', '#00b894',
  '#e17055', '#0984e3', '#00cec9', '#6c5ce7', '#fdcb6e'
]

const getSchoolLogo = (school: any): string => {
  if (!school.logo) return generateSchoolLogo(school.name)
  let logoUrl = school.logo.replace(/`/g, '')
  logoUrl = logoUrl.replace('image_size=square', 'image_size=square_hd')
  return logoUrl
}

const generateSchoolLogo = (schoolName: string): string => {
  if (!schoolName) return ''
  let hash = 0
  for (let i = 0; i < schoolName.length; i++) {
    hash = schoolName.charCodeAt(i) + ((hash << 5) - hash)
  }
  const colorIndex = Math.abs(hash) % colorPalette.length
  const bgColor = colorPalette[colorIndex]
  const initial = schoolName.charAt(0)
  const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80"><rect width="100%" height="100%" rx="12" fill="${bgColor}"/><text x="40" y="52" font-family="Microsoft YaHei, sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle">${initial}</text></svg>`
  return 'data:image/svg+xml,' + encodeURIComponent(svgStr)
}

const getPrefectureName = (school: School): string => {
  if (!school) return ''
  const p = school.prefecture || school.city || school.district || ''
  return prefectureMap[p] || p
}

const getCityLabel = (value: string): string => {
  const city = cityList.find(c => c.value === value)
  return city ? city.label : value
}

const getTypeName = (school: School): string => {
  if (!school) return '未知'
  if (school.type_name) return school.type_name
  if (school.typeName) return school.typeName
  if (school.type && typeMap[school.type]) return typeMap[school.type]
  if (school.nature) return school.nature
  if (school.is_public === 1) return '公办'
  if (school.is_public === 0) return '民办'
  return '未知'
}

const getTypeLabel = (type: number | null): string => {
  if (!type) return ''
  return typeMap[type] || ''
}

const fetchSchoolList = async () => {
  loading.value = true
  try {
    const params: Record<string, unknown> = {}
    params.page = currentPage.value
    params.size = pageSize.value
    if (searchForm.name) params.keyword = searchForm.name
    if (searchForm.city) params.city = searchForm.city
    if (searchForm.type && searchForm.type !== 0) params.type = searchForm.type
    if (sortBy.value && sortBy.value !== 'default') params.sort_by = sortBy.value
    if (searchForm.minScore) params.min_score = searchForm.minScore
    if (searchForm.maxScore) params.max_score = searchForm.maxScore
    if (searchForm.nature) params.nature = searchForm.nature

    const queryString = new URLSearchParams(params as any).toString()
    const response = await fetch(`/api/schools?${queryString}`)
    const result = await response.json()

    if (result.success) {
      const data = result.data || {}
      const items = Array.isArray(data.items) ? data.items : (Array.isArray(data) ? data : [])
      schoolList.value = items.map((item: any) => ({
        ...item,
        type: item.type || item.school_type,
        type_name: item.type_name || item.typeName,
        min_score: item.min_score || item.minScore,
        min_rank: item.min_rank || item.minRank,
        one_rate: item.one_rate || item.oneRate,
        is_public: item.is_public ?? item.isPublic,
        nature: item.nature || item.school_nature,
        is_key: item.is_key ?? item.isKey,
        isFavorited: sharedStore.isFavorited(item.id)
      }))
      total.value = data.total || schoolList.value.length

      if (data.statistics) {
        localStats.value = {
          totalSchools: data.statistics.total || 0,
          publicSchools: data.statistics.public_count || 0,
          privateSchools: data.statistics.private_count || 0,
          keySchools: data.statistics.key_count || 0
        }
        sharedStore.updateStatistics(localStats.value)
      } else {
        updateStats()
      }
    } else {
      if (result.message && result.message !== '网络请求失败') {
        ElMessage.warning(result.message)
      }
      schoolList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取学校列表失败:', error)
    schoolList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const stats = {
    totalSchools: schoolList.value.length,
    publicSchools: schoolList.value.filter(s => {
      if (Number(s.is_public) === 1) return true
      if (Number(s.is_public) === 0) return false
      if (s.nature === '公办') return true
      if (s.nature === '民办') return false
      const tn = getTypeName(s)
      if (tn === '公办' || tn === '公办学校') return true
      if (tn === '民办' || tn === '民办学校') return false
      if (s.type === 4) return false
      if (s.type === 2 || s.type === 1) return true
      if (Number(s.tuition) === 0) return true
      if (s.type_name && (s.type_name.includes('公办') || s.type_name.includes('公立'))) return true
      if (s.type_name && (s.type_name.includes('民办') || s.type_name.includes('私立'))) return false
      return true
    }).length,
    privateSchools: schoolList.value.filter(s => {
      if (Number(s.is_public) === 0) return true
      if (s.nature === '民办') return true
      if (s.type === 4) return true
      if (s.type_name && (s.type_name.includes('民办') || s.type_name.includes('私立'))) return true
      return false
    }).length,
    keySchools: schoolList.value.filter(s => {
      if (s.is_key !== undefined && s.is_key !== null && (Number(s.is_key) === 1 || s.is_key === true)) return true
      if (s.isKey !== undefined && s.isKey !== null && s.isKey === true) return true
      if (s.type !== undefined && s.type !== null && Number(s.type) === 2) return true
      const tn = getTypeName(s)
      if (tn === '重点高中') return true
      if (s.type_name && (s.type_name.includes('重点') || s.type_name.includes('一级'))) return true
      if (s.level && (s.level.includes('一级') || s.level.includes('重点') || s.level.includes('示范'))) return true
      return false
    }).length
  }
  localStats.value = stats
  sharedStore.updateStatistics(stats)
  eventBus.emit(Events.STATISTICS_UPDATED, stats)
}

const handleSearch = () => {
  currentPage.value = 1
  if (searchForm.name) {
    sharedStore.addSearchHistory(searchForm.name)
    eventBus.emit(Events.SEARCH_PERFORMED, searchForm.name)
  }
  fetchSchoolList()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.city = ''
  searchForm.type = 0
  searchForm.nature = ''
  searchForm.minScore = null
  searchForm.maxScore = null
  sortBy.value = 'default'
  currentPage.value = 1
  sharedStore.clearSelected()
  eventBus.emit(Events.SELECTION_CLEARED)
  fetchSchoolList()
}

const filterByCity = (city: string) => {
  searchForm.city = searchForm.city === city ? '' : city
  currentPage.value = 1
  fetchSchoolList()
}

const filterByNature = (nature: string) => {
  searchForm.nature = searchForm.nature === nature ? '' : nature
  currentPage.value = 1
  fetchSchoolList()
}

const viewDetails = (school: School) => {
  sharedStore.addBrowsingHistory(school.id, school.name)
  eventBus.emit(Events.SCHOOL_VIEWED, { id: school.id, name: school.name })
  sharedStore.setTransferData('currentSchool', school)
  router.push(`/school/${school.id}`)
}

const compareSchools = () => {
  if (sharedStore.selectedCount < 2) {
    ElMessage.warning('请至少选择2所学校进行对比')
    return
  }
  sharedStore.setTransferData('compareSchools', sharedStore.selectedSchools)
  router.push(`/compare?ids=${sharedStore.selectedSchools.join(',')}`)
}

const clearSelection = () => {
  sharedStore.clearSelected()
  eventBus.emit(Events.SELECTION_CLEARED)
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchSchoolList()
}

onMounted(() => {
  fetchSchoolList()
})
</script>

<style scoped>
.school-page {
  padding: var(--wx-spacing-lg);
  background: var(--wx-bg);
  min-height: 100%;
}

/* 搜索栏 */
.search-bar {
  margin-bottom: var(--wx-spacing-md);
  max-width: 600px;
}

/* 筛选标签 */
.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
  margin-bottom: var(--wx-spacing-lg);
}

.filter-chip {
  display: inline-block;
  padding: 4px 14px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-bg-white);
  border: 1px solid var(--wx-border-light);
  color: var(--wx-text-secondary);
  font-size: var(--wx-font-size-sm);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
  user-select: none;
}

.filter-chip:hover {
  background: var(--wx-bg-hover);
  color: var(--wx-text-primary);
}

.filter-chip.active {
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  border-color: var(--wx-primary);
}

.filter-chip.reset {
  color: var(--wx-danger);
  border-color: var(--wx-danger);
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--wx-spacing-md);
  margin-bottom: var(--wx-spacing-lg);
}

.stat-card {
  text-align: center;
  padding: var(--wx-spacing-lg);
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--wx-text-primary);
  margin-bottom: 4px;
}

.stat-card .stat-label {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--wx-spacing-md);
  padding: var(--wx-spacing-sm) 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
}

.sort-label {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
}

.sort-select {
  padding: 4px 8px;
  border: 1px solid var(--wx-border-light);
  border-radius: var(--wx-radius-sm);
  background: var(--wx-bg-white);
  color: var(--wx-text-primary);
  font-size: var(--wx-font-size-sm);
  font-family: var(--wx-font-family);
  outline: none;
  cursor: pointer;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
}

.list-count {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
}

/* 加载状态 */
.loading-wrap {
  padding: var(--wx-spacing-md) 0;
}

/* 列表项右侧 */
.item-right {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
  flex-shrink: 0;
}

.view-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

.score-tag {
  color: var(--wx-primary);
  font-weight: 500;
}

/* 头像样式 */
.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: var(--wx-radius-sm);
  object-fit: cover;
}

.avatar-text {
  font-size: 18px;
  font-weight: 600;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--wx-spacing-md);
}

.empty-title {
  font-size: var(--wx-font-size-lg);
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-sm);
}

.empty-desc {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
  margin-bottom: var(--wx-spacing-lg);
}

.empty-desc span {
  display: block;
  margin-bottom: 4px;
}

/* 分页 */
.pagination-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--wx-spacing-lg);
  padding: var(--wx-spacing-xl) 0;
}

.page-btn {
  padding: 6px 16px;
  border: 1px solid var(--wx-border);
  border-radius: var(--wx-radius-sm);
  background: var(--wx-bg-white);
  color: var(--wx-text-primary);
  font-size: var(--wx-font-size-sm);
  font-family: var(--wx-font-family);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
}

.page-btn:hover:not(:disabled) {
  background: var(--wx-bg-hover);
  border-color: var(--wx-primary);
  color: var(--wx-primary);
}

.page-btn:disabled {
  color: var(--wx-text-muted);
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--wx-spacing-sm);
  }
}

@media (max-width: 480px) {
  .stats-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>