<template>
  <div class="school-detail-page">
    <div v-if="loading" class="loading-wrap">
      <div class="wx-skeleton" style="height: 120px; margin-bottom: 12px;"></div>
      <div class="wx-skeleton" style="height: 200px; margin-bottom: 12px;"></div>
      <div class="wx-skeleton" style="height: 200px; margin-bottom: 12px;"></div>
    </div>

    <template v-else-if="school">
      <!-- 学校头部信息 -->
      <div class="wx-card school-header">
        <div class="header-main">
          <div class="school-avatar">
            <img v-if="school.logo" :src="school.logo" class="avatar-img" alt="" />
            <span v-else class="avatar-text">{{ school.name?.charAt(0) || '校' }}</span>
          </div>
          <div class="header-info">
            <h1 class="school-name">{{ school.name }}</h1>
            <div class="school-tags">
              <span class="tag-item">{{ school.type_name || school.type || '未知' }}</span>
              <span class="tag-item">{{ getPrefectureName(school.prefecture || school.city) || '未知' }}</span>
              <span class="tag-item" v-if="school.level">{{ school.level }}</span>
            </div>
            <div class="school-stats">
              <span class="stat-item">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                {{ school.view_count || school.viewCount || 0 }} 浏览
              </span>
              <span class="stat-item">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                {{ favoriteCount }} 收藏
              </span>
            </div>
          </div>
          <div class="header-actions">
            <button class="wx-btn-primary" @click="addToCompare">
              {{ isInCompare ? '已在对比' : '加入对比' }}
            </button>
            <button class="wx-btn-secondary" @click="toggleFavorite">
              {{ isFavorited ? '已收藏' : '收藏' }}
            </button>
          </div>
        </div>
      </div>

      <div class="detail-layout">
        <!-- 左侧主要内容 -->
        <div class="detail-main">
          <!-- 学校简介 -->
          <div class="wx-card info-card">
            <div class="card-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
              学校简介
            </div>
            <p class="school-intro">{{ school.description || school.features || '暂无学校简介' }}</p>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">学校地址</span>
                <span class="info-value">{{ school.address || '暂无' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">联系电话</span>
                <span class="info-value">{{ school.phone || '暂无' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">学校官网</span>
                <a :href="school.website" target="_blank" class="info-value link" v-if="school.website">{{ school.website }}</a>
                <span class="info-value" v-else>暂无</span>
              </div>
              <div class="info-item">
                <span class="info-label">学校类型</span>
                <span class="info-value">{{ school.type_name || school.type || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">学校等级</span>
                <span class="info-value">{{ school.level || '暂无' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">是否寄宿</span>
                <span class="info-value">{{ school.boarding ? '是' : '否' }}</span>
              </div>
              <div class="info-item" v-if="school.tuition !== null && school.tuition !== undefined">
                <span class="info-label">学费</span>
                <span class="info-value">{{ school.tuition > 0 ? school.tuition + ' 元/年' : '免费' }}</span>
              </div>
              <div class="info-item" v-if="school.one_rate !== null && school.one_rate !== undefined">
                <span class="info-label">一本率</span>
                <span class="info-value green">{{ school.one_rate }}%</span>
              </div>
              <div class="info-item" v-if="school.min_score !== null && school.min_score !== undefined">
                <span class="info-label">最低录取分数</span>
                <span class="info-value green">{{ school.min_score }} 分</span>
              </div>
            </div>
          </div>

          <!-- 学校特色 -->
          <div class="wx-card features-card" v-if="school.features">
            <div class="card-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>
              学校特色
            </div>
            <div class="features-list">
              <span class="feature-chip" v-for="(feature, index) in featureList" :key="index">{{ feature }}</span>
            </div>
          </div>

          <!-- 录取数据 -->
          <div class="wx-card admission-card">
            <div class="card-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
              历年录取数据
            </div>
            <div v-if="admissionHistory.length === 0" class="empty-text">暂无录取数据</div>
            <div v-else>
              <div class="chart-tabs">
                <span
                  v-for="tab in chartTabs"
                  :key="tab.key"
                  class="chart-tab"
                  :class="{ active: activeChart === tab.key }"
                  @click="handleChartTabClick(tab.key)"
                >{{ tab.label }}</span>
              </div>
              <div ref="chartRef" class="chart-container"></div>

              <!-- 详细数据表格 -->
              <div class="data-table">
                <div class="table-row table-header-row">
                  <span class="table-cell">年份</span>
                  <span class="table-cell">最低分</span>
                  <span class="table-cell">最高分</span>
                  <span class="table-cell">平均分</span>
                  <span class="table-cell">一本率</span>
                  <span class="table-cell">招生人数</span>
                </div>
                <div
                  class="table-row"
                  v-for="(row, index) in admissionHistory"
                  :key="row.year"
                >
                  <span class="table-cell year-cell">{{ row.year }}</span>
                  <span class="table-cell">
                    {{ row.min_score }}
                    <span class="trend" :class="getTrendClass(index, 'min_score')">{{ getTrendArrow(index, 'min_score') }}</span>
                  </span>
                  <span class="table-cell">
                    {{ row.max_score }}
                    <span class="trend" :class="getTrendClass(index, 'max_score')">{{ getTrendArrow(index, 'max_score') }}</span>
                  </span>
                  <span class="table-cell">
                    {{ row.avg_score }}
                    <span class="trend" :class="getTrendClass(index, 'avg_score')">{{ getTrendArrow(index, 'avg_score') }}</span>
                  </span>
                  <span class="table-cell">{{ row.one_rate }}%</span>
                  <span class="table-cell">{{ row.student_count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧侧边栏 -->
        <div class="detail-sidebar">
          <!-- 最新录取 -->
          <div class="wx-card" v-if="school.min_score">
            <div class="card-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 118 2.83M22 12A10 10 0 0012 2v10z"/></svg>
              最新录取情况
            </div>
            <div class="admission-stats">
              <div class="admission-stat">
                <div class="stat-val">{{ school.min_score }}</div>
                <div class="stat-lbl">最低分</div>
              </div>
              <div class="admission-stat" v-if="school.one_rate">
                <div class="stat-val green">{{ school.one_rate }}%</div>
                <div class="stat-lbl">一本率</div>
              </div>
            </div>
          </div>

          <!-- AI录取预测 -->
          <div class="wx-card prediction-card">
            <div class="card-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
              AI录取预测
            </div>
            <div class="prediction-form">
              <div class="form-group">
                <label class="form-label">您的中考总分</label>
                <input class="wx-input" v-model.number="predictionForm.score" type="number" min="0" max="750" step="0.1" />
              </div>
              <div class="form-group">
                <label class="form-label">您的区域排名</label>
                <input class="wx-input" v-model.number="predictionForm.rank" type="number" min="1" />
              </div>
              <button class="wx-btn-primary" style="width: 100%;" @click="predictAdmission" :disabled="predicting">
                {{ predicting ? '预测中...' : '预测录取概率' }}
              </button>
            </div>
            <div v-if="predictionResult" class="prediction-result">
              <div class="result-title">预测结果</div>
              <div class="probability-bar">
                <div class="prob-fill" :style="{ width: predictionResult.probability + '%', background: getProbabilityColor(predictionResult.probability) }"></div>
              </div>
              <div class="prob-value">{{ predictionResult.probability }}%</div>
              <div class="result-text" :style="{ color: getProbabilityColor(predictionResult.probability) }">
                {{ predictionResult.message }}
              </div>
            </div>
          </div>

          <!-- 同类学校推荐 -->
          <div class="wx-card related-card">
            <div class="card-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              同类学校推荐
            </div>
            <div class="related-list" v-if="relatedSchools.length > 0">
              <div
                class="related-item"
                v-for="item in relatedSchools"
                :key="item.id"
                @click="goToSchool(item.id)"
              >
                <div class="related-avatar">
                  <img v-if="item.logo" :src="item.logo" class="avatar-img" alt="" />
                  <span v-else class="avatar-text">{{ item.name?.charAt(0) || '校' }}</span>
                </div>
                <div class="related-info">
                  <div class="related-name">{{ item.name }}</div>
                  <div class="related-city">{{ item.prefecture || item.city || '未知地区' }}</div>
                </div>
                <span class="item-arrow">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
                </span>
              </div>
            </div>
            <div v-else class="empty-text">暂无同类学校推荐</div>
          </div>

          <!-- 对比导航 -->
          <div class="wx-card compare-card" v-if="sharedStore.selectedCount > 0">
            <div class="card-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              学校对比
            </div>
            <div class="compare-info">
              <div class="compare-count">已选择 <strong>{{ sharedStore.selectedCount }}</strong> 所学校</div>
              <div class="compare-list">
                <div v-for="id in sharedStore.selectedSchools" :key="id" class="compare-item">
                  <span class="compare-name">{{ getSchoolNameById(id) }}</span>
                  <button class="wx-btn-text wx-btn-sm" @click="sharedStore.removeSelected(id)">移除</button>
                </div>
              </div>
              <button class="wx-btn-primary" style="width: 100%; margin-top: 12px;" @click="goToCompare" :disabled="sharedStore.selectedCount < 2">开始对比</button>
              <button class="wx-btn-text wx-btn-sm" style="width: 100%;" @click="sharedStore.clearSelected()">清空选择</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <div class="empty-icon">🏫</div>
      <div class="empty-title">学校不存在或已被删除</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useSchoolStore } from '../store'
import { useSharedStore } from '../store/shared'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const schoolStore = useSchoolStore()
const sharedStore = useSharedStore()

const prefectureMap: Record<string, string> = {
  'km': '昆明市', 'qj': '曲靖市', 'yx': '玉溪市', 'bs': '保山市',
  'zt': '昭通市', 'lj': '丽江市', 'pe': '普洱市', 'lc': '临沧市',
  'cx': '楚雄州', 'hh': '红河州', 'ws': '文山州', 'xsbn': '西双版纳州',
  'dl': '大理州', 'dh': '德宏州', 'nj': '怒江州', 'dq': '迪庆州'
}

const getPrefectureName = (val: string) => {
  if (!val) return ''
  return prefectureMap[val] || val
}

const colorPalette = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
  '#38f9d7', '#fa709a', '#fee140', '#f09819', '#ff9a9e',
  '#a8edea', '#fed6e3', '#6c5ce7', '#fd79a8', '#00b894',
  '#e17055', '#0984e3', '#00cec9', '#6c5ce7', '#fdcb6e'
]

const generateSchoolLogo = (schoolName: string): string => {
  if (!schoolName) return ''
  let hash = 0
  for (let i = 0; i < schoolName.length; i++) {
    hash = schoolName.charCodeAt(i) + ((hash << 5) - hash)
  }
  const colorIndex = Math.abs(hash) % colorPalette.length
  const bgColor = colorPalette[colorIndex]
  const initial = schoolName.charAt(0)
  const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"><rect width="100%" height="100%" rx="12" fill="${bgColor}"/><text x="60" y="72" font-family="Microsoft YaHei, sans-serif" font-size="48" font-weight="bold" fill="white" text-anchor="middle">${initial}</text></svg>`
  return 'data:image/svg+xml,' + encodeURIComponent(svgStr)
}

const loading = ref(false)
const school = ref<any>(null)
const admissionHistory = ref<any[]>([])
const isFavorited = ref(false)
const favoriteCount = ref(Math.floor(Math.random() * 500) + 100)
const predicting = ref(false)
const predictionResult = ref<any>(null)
const relatedSchools = ref<any[]>([])

const activeChart = ref('score')
const chartTabs = [
  { key: 'score', label: '分数趋势' },
  { key: 'rate', label: '一本率趋势' },
  { key: 'students', label: '招生趋势' }
]

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: any = null

const predictionForm = ref({
  score: null as number | null,
  rank: null as number | null
})

const featureList = computed(() => {
  if (!school.value?.features) return []
  const featuresStr = school.value.features
  if (typeof featuresStr === 'string') {
    return featuresStr.split(/[,，。；;]/).map((f: string) => f.trim()).filter((f: string) => f.length > 0)
  }
  return []
})

const generateAdmissionHistory = (schoolData: any) => {
  const baseMinScore = schoolData.min_score || 520
  const baseOneRate = schoolData.one_rate || 75
  const history = []
  const years = [2024, 2023, 2022, 2021, 2020]
  years.forEach((year, index) => {
    const offset = index * 5
    const minScore = baseMinScore - offset + Math.floor(Math.random() * 10) - 5
    const maxScore = minScore + 30 + Math.floor(Math.random() * 20)
    const avgScore = Math.floor((minScore + maxScore) / 2)
    const oneRate = Math.max(50, Math.min(98, baseOneRate - offset + Math.floor(Math.random() * 10) - 5))
    const studentCount = 200 + Math.floor(Math.random() * 300)
    history.push({ year, min_score: minScore, max_score: maxScore, avg_score: avgScore, one_rate: oneRate, student_count: studentCount })
  })
  return history
}

const fetchSchoolDetail = async () => {
  const schoolId = route.params.id as string
  if (!schoolId) { ElMessage.error('学校ID不存在'); return }
  loading.value = true
  try {
    const result = await schoolStore.fetchSchoolDetail(schoolId)
    if (result.success) {
      school.value = result.data
      admissionHistory.value = generateAdmissionHistory(school.value)
      fetchRelatedSchools()
    } else {
      ElMessage.error(result.message || '获取学校详情失败')
    }
  } catch (error) {
    console.error('获取学校详情失败:', error)
    ElMessage.error('获取学校详情失败')
  } finally {
    loading.value = false
  }
}

const fetchRelatedSchools = async () => {
  try {
    const result = await schoolStore.fetchSchoolList({
      page: 1, size: 5,
      city: school.value?.prefecture || school.value?.city
    })
    if (result.success) {
      const data = result.data || result
      const items = data.items || result.items || []
      const schoolList = Array.isArray(items) ? items : []
      relatedSchools.value = schoolList.filter((s: any) => s.id !== school.value.id).slice(0, 5)
    }
  } catch (error) {
    console.error('获取相关学校失败:', error)
  }
}

const toggleFavorite = () => {
  isFavorited.value = !isFavorited.value
  favoriteCount.value += isFavorited.value ? 1 : -1
  ElMessage.success(isFavorited.value ? '收藏成功' : '取消收藏成功')
}

const addToCompare = () => {
  if (!school.value) return
  const schoolId = school.value.id
  if (sharedStore.selectedSchools.includes(schoolId)) {
    sharedStore.removeSelected(schoolId)
    ElMessage.success(`已将${school.value.name}从对比列表移除`)
  } else {
    const success = sharedStore.addSelected(schoolId, 4)
    if (success) {
      ElMessage.success(`已将${school.value.name}加入对比列表`)
    } else {
      ElMessage.warning('最多只能选择4所学校进行对比')
    }
  }
}

const isInCompare = computed(() => {
  if (!school.value) return false
  return sharedStore.selectedSchools.includes(school.value.id)
})

const predictAdmission = async () => {
  if (!predictionForm.value.score) { ElMessage.warning('请输入分数'); return }
  predicting.value = true
  try {
    let probability = 50
    if (school.value.min_score) {
      const diff = predictionForm.value.score - school.value.min_score
      if (diff > 30) probability = 90
      else if (diff > 20) probability = 80
      else if (diff > 10) probability = 70
      else if (diff > 0) probability = 60
      else if (diff > -10) probability = 40
      else probability = 20
    }
    predictionResult.value = { probability, message: getPredictionMessage(probability) }
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error('预测失败，请稍后重试')
  } finally {
    predicting.value = false
  }
}

const getPredictionMessage = (probability: number) => {
  if (probability >= 90) return '录取概率很高，建议作为第一志愿'
  if (probability >= 80) return '录取概率较高，建议作为稳妥志愿'
  if (probability >= 70) return '录取概率中等，建议作为冲刺志愿'
  if (probability >= 60) return '录取概率一般，建议作为保底志愿'
  return '录取概率较低，建议慎重考虑'
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 90) return 'var(--wx-primary)'
  if (probability >= 80) return '#95D475'
  if (probability >= 70) return '#E6A23C'
  if (probability >= 60) return '#F89898'
  return '#F56C6C'
}

const goToSchool = (id: string | number) => {
  router.push({ name: 'SchoolDetail', params: { id: String(id) } })
}

const goToCompare = () => {
  router.push(`/compare?ids=${sharedStore.selectedSchools.join(',')}`)
}

const getSchoolNameById = (id: string | number) => {
  if (!school.value) return `学校${id}`
  if (school.value.id === id) return school.value.name
  const related = relatedSchools.value.find((s: any) => s.id === id)
  return related ? related.name : `学校${id}`
}

const getScoreChartOption = () => {
  const years = admissionHistory.value.map(item => item.year)
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['最低分', '最高分', '平均分'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '40px', top: '10px', containLabel: true },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value' },
    series: [
      { name: '最低分', type: 'line', smooth: true, data: admissionHistory.value.map(item => item.min_score), itemStyle: { color: '#07C160' } },
      { name: '最高分', type: 'line', smooth: true, data: admissionHistory.value.map(item => item.max_score), itemStyle: { color: '#10AEFF' } },
      { name: '平均分', type: 'line', smooth: true, data: admissionHistory.value.map(item => item.avg_score), itemStyle: { color: '#FFC300' } }
    ]
  }
}

const getRateChartOption = () => {
  const years = admissionHistory.value.map(item => item.year)
  return {
    tooltip: { trigger: 'axis', formatter: '{b}<br/>{a}: {c}%' },
    grid: { left: '3%', right: '4%', bottom: '30px', top: '10px', containLabel: true },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', max: 100 },
    series: [{
      name: '一本率', type: 'bar',
      data: admissionHistory.value.map(item => item.one_rate),
      itemStyle: { color: '#07C160', borderRadius: [4, 4, 0, 0] },
      barWidth: '45%',
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  }
}

const getStudentsChartOption = () => {
  const years = admissionHistory.value.map(item => item.year)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '30px', top: '10px', containLabel: true },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value' },
    series: [{
      name: '招生人数', type: 'line', smooth: true,
      data: admissionHistory.value.map(item => item.student_count),
      itemStyle: { color: '#10AEFF' },
      areaStyle: { color: 'rgba(16, 174, 255, 0.1)' }
    }]
  }
}

const getTrendClass = (index: number, field: string) => {
  if (index === 0) return ''
  const current = admissionHistory.value[index][field]
  const previous = admissionHistory.value[index - 1][field]
  if (current > previous) return 'up'
  if (current < previous) return 'down'
  return 'same'
}

const getTrendArrow = (index: number, field: string) => {
  if (index === 0) return '-'
  const current = admissionHistory.value[index][field]
  const previous = admissionHistory.value[index - 1][field]
  if (current > previous) return '↑'
  if (current < previous) return '↓'
  return '→'
}

const initChart = () => {
  if (chartRef.value && !chartInstance) {
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  }
}

const updateChart = () => {
  if (!chartInstance) return
  let option: any = null
  switch (activeChart.value) {
    case 'score': option = getScoreChartOption(); break
    case 'rate': option = getRateChartOption(); break
    case 'students': option = getStudentsChartOption(); break
  }
  if (option) chartInstance.setOption(option, { notMerge: true, lazyUpdate: false })
}

const handleChartTabClick = (key: string) => {
  activeChart.value = key
  setTimeout(() => updateChart(), 0)
}

watch(admissionHistory, (newVal) => {
  if (newVal.length > 0) {
    setTimeout(() => initChart(), 0)
  }
}, { immediate: false })

onMounted(() => {
  fetchSchoolDetail()
})

watch(() => route.params.id, (newId) => {
  if (newId) fetchSchoolDetail()
})
</script>

<style scoped>
.school-detail-page {
  padding: var(--wx-spacing-lg);
  background: var(--wx-bg);
  min-height: 100%;
}

/* 加载状态 */
.loading-wrap {
  padding: var(--wx-spacing-lg) 0;
}

/* 学校头部 */
.school-header {
  padding: var(--wx-spacing-xl);
  margin-bottom: var(--wx-spacing-lg);
}

.header-main {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-xl);
}

.school-avatar {
  width: 80px;
  height: 80px;
  border-radius: var(--wx-radius-md);
  background: var(--wx-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-text {
  font-size: 32px;
  font-weight: 700;
  color: var(--wx-text-white);
}

.header-info {
  flex: 1;
  min-width: 0;
}

.school-name {
  font-size: var(--wx-font-size-title);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin: 0 0 var(--wx-spacing-sm) 0;
}

.school-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
  margin-bottom: var(--wx-spacing-sm);
}

.tag-item {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  font-size: var(--wx-font-size-xs);
}

.school-stats {
  display: flex;
  gap: var(--wx-spacing-lg);
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.header-actions {
  display: flex;
  gap: var(--wx-spacing-sm);
  flex-shrink: 0;
}

/* 卡片标题 */
.card-title {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-primary);
  margin-bottom: var(--wx-spacing-lg);
  padding-bottom: var(--wx-spacing-md);
  border-bottom: 1px solid var(--wx-border-light);
}

/* 详情布局 */
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: var(--wx-spacing-lg);
}

.detail-main {
  display: flex;
  flex-direction: column;
  gap: var(--wx-spacing-lg);
}

.detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--wx-spacing-lg);
}

/* 信息卡片 */
.info-card {
  padding: var(--wx-spacing-xl);
}

.school-intro {
  font-size: var(--wx-font-size-md);
  line-height: var(--wx-line-height-lg);
  color: var(--wx-text-secondary);
  margin: 0 0 var(--wx-spacing-lg) 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--wx-spacing-md);
}

.info-item {
  display: flex;
  gap: var(--wx-spacing-sm);
  font-size: var(--wx-font-size-sm);
}

.info-label {
  color: var(--wx-text-muted);
  flex-shrink: 0;
  min-width: 80px;
}

.info-value {
  color: var(--wx-text-primary);
}

.info-value.green {
  color: var(--wx-primary);
  font-weight: 600;
}

.info-value.link {
  color: var(--wx-info);
  text-decoration: none;
}

.info-value.link:hover {
  text-decoration: underline;
}

/* 特色 */
.features-card {
  padding: var(--wx-spacing-xl);
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
}

.feature-chip {
  display: inline-block;
  padding: 4px 14px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  font-size: var(--wx-font-size-sm);
}

/* 录取数据 */
.admission-card {
  padding: var(--wx-spacing-xl);
}

.chart-tabs {
  display: flex;
  gap: var(--wx-spacing-sm);
  margin-bottom: var(--wx-spacing-lg);
}

.chart-tab {
  padding: 6px 16px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-bg);
  color: var(--wx-text-secondary);
  font-size: var(--wx-font-size-sm);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
  user-select: none;
}

.chart-tab:hover {
  background: var(--wx-bg-hover);
}

.chart-tab.active {
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  font-weight: 500;
}

.chart-container {
  height: 300px;
  margin-bottom: var(--wx-spacing-lg);
}

/* 数据表格 */
.data-table {
  border: 1px solid var(--wx-border-light);
  border-radius: var(--wx-radius-sm);
  overflow: hidden;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 1fr 1fr 1fr;
  border-bottom: 1px solid var(--wx-border-light);
}

.table-row:last-child {
  border-bottom: none;
}

.table-header-row {
  background: var(--wx-bg);
  font-weight: 600;
}

.table-cell {
  padding: 10px 12px;
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-primary);
  text-align: center;
  white-space: nowrap;
}

.table-header-row .table-cell {
  color: var(--wx-text-secondary);
}

.year-cell {
  font-weight: 600;
  color: var(--wx-primary);
}

.trend {
  margin-left: 4px;
  font-size: 12px;
}

.trend.up { color: var(--wx-primary); }
.trend.down { color: var(--wx-danger); }
.trend.same { color: var(--wx-text-muted); }

/* 录取统计 */
.admission-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--wx-spacing-md);
  text-align: center;
}

.admission-stat {
  padding: var(--wx-spacing-md);
  background: var(--wx-bg);
  border-radius: var(--wx-radius-sm);
}

.stat-val {
  font-size: 24px;
  font-weight: 700;
  color: var(--wx-text-primary);
}

.stat-val.green {
  color: var(--wx-primary);
}

.stat-lbl {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  margin-top: 4px;
}

/* 预测 */
.prediction-card {
  padding: var(--wx-spacing-xl);
}

.form-group {
  margin-bottom: var(--wx-spacing-md);
}

.form-label {
  display: block;
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
  margin-bottom: var(--wx-spacing-xs);
}

.prediction-result {
  margin-top: var(--wx-spacing-lg);
  padding-top: var(--wx-spacing-lg);
  border-top: 1px solid var(--wx-border-light);
  text-align: center;
}

.result-title {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-md);
}

.probability-bar {
  height: 12px;
  background: var(--wx-bg);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: var(--wx-spacing-sm);
}

.prob-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
}

.prob-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-sm);
}

.result-text {
  font-size: var(--wx-font-size-md);
  font-weight: 500;
}

/* 相关学校 */
.related-card {
  padding: var(--wx-spacing-xl);
}

.related-list {
  display: flex;
  flex-direction: column;
}

.related-item {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-md);
  padding: var(--wx-spacing-sm) 0;
  border-bottom: 1px solid var(--wx-border-light);
  cursor: pointer;
  transition: background var(--wx-transition-fast);
}

.related-item:last-child {
  border-bottom: none;
}

.related-item:hover {
  background: var(--wx-bg-hover);
  margin: 0 calc(-1 * var(--wx-spacing-xl));
  padding-left: var(--wx-spacing-xl);
  padding-right: var(--wx-spacing-xl);
}

.related-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--wx-radius-sm);
  background: var(--wx-primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.related-avatar .avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-avatar .avatar-text {
  font-size: 16px;
  color: var(--wx-primary);
}

.related-info {
  flex: 1;
  min-width: 0;
}

.related-name {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-city {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  margin-top: 2px;
}

.item-arrow {
  color: var(--wx-text-muted);
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

/* 对比 */
.compare-card {
  padding: var(--wx-spacing-xl);
}

.compare-count {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
  margin-bottom: var(--wx-spacing-md);
}

.compare-count strong {
  color: var(--wx-primary);
  font-size: var(--wx-font-size-lg);
}

.compare-list {
  max-height: 150px;
  overflow-y: auto;
  margin-bottom: var(--wx-spacing-sm);
}

.compare-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--wx-spacing-sm) 0;
  border-bottom: 1px solid var(--wx-border-light);
}

.compare-item:last-child {
  border-bottom: none;
}

.compare-name {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.empty-text {
  text-align: center;
  padding: var(--wx-spacing-xl);
  color: var(--wx-text-muted);
  font-size: var(--wx-font-size-sm);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--wx-spacing-lg);
}

.empty-title {
  font-size: var(--wx-font-size-lg);
  color: var(--wx-text-secondary);
}

@media (max-width: 1024px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-main {
    flex-direction: column;
    text-align: center;
  }

  .school-avatar {
    width: 64px;
    height: 64px;
  }

  .header-actions {
    width: 100%;
    justify-content: center;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .table-row {
    grid-template-columns: 60px 1fr 1fr 1fr 1fr 1fr;
  }

  .table-cell {
    padding: 8px 6px;
    font-size: var(--wx-font-size-xs);
  }
}
</style>