<template>
  <div class="data-visualization-page">
    <!-- 页面加载动画 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-orb">
          <div class="orb-core"></div>
          <div class="orb-ring orb-ring-1"></div>
          <div class="orb-ring orb-ring-2"></div>
          <div class="orb-ring orb-ring-3"></div>
        </div>
        <div class="loading-text">
          <span class="loading-char" v-for="(char, index) in loadingText" :key="index" :style="{ animationDelay: index * 0.1 + 's' }">
            {{ char }}
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          <div class="progress-glow"></div>
        </div>
        <div class="loading-dots">
          <span class="dot" v-for="i in 5" :key="i" :style="{ animationDelay: i * 0.2 + 's' }"></span>
        </div>
      </div>
    </div>

    <div class="page-header animate-fadeInUp">
      <div class="header-bg"></div>
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">📊</span>
          <span>数据分析中心</span>
        </h1>
        <p class="page-subtitle">全面了解学习情况，科学制定提升计划</p>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value">{{ chartCount }}</span>
            <span class="stat-label">分析维度</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">{{ recommendationCount }}</span>
            <span class="stat-label">智能建议</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">实时</span>
            <span class="stat-label">数据更新</span>
          </div>
        </div>
      </div>
    </div>

    <div class="visualization-container">
      <el-card class="control-card animate-slideUp">
        <el-form :model="formData" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="分析类型">
                <el-select v-model="formData.analysisType" @change="loadAnalysis">
                  <el-option label="综合分析" value="comprehensive" />
                  <el-option label="成绩趋势" value="trend" />
                  <el-option label="科目分析" value="subject" />
                  <el-option label="目标对比" value="comparison" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="时间范围">
                <el-select v-model="formData.timeRange" @change="loadAnalysis">
                  <el-option label="最近3次考试" value="3" />
                  <el-option label="最近5次考试" value="5" />
                  <el-option label="最近10次考试" value="10" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="显示维度">
                <el-select v-model="formData.dimension" @change="loadAnalysis">
                  <el-option label="全部维度" value="all" />
                  <el-option label="仅成绩分析" value="score" />
                  <el-option label="仅目标对比" value="target" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item>
                <el-button type="primary" @click="loadAnalysis" :loading="loading">
                  <el-icon><RefreshLeft /></el-icon>
                  生成分析
                </el-button>
                <el-button @click="exportReport" :disabled="!visualizationData">
                  <el-icon><Download /></el-icon>
                  导出报告
                </el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>正在生成分析报告...</p>
      </div>

      <div v-else-if="visualizationData" class="charts-content">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>{{ visualizationData.scoreTrend.title }}</h3>
              <el-tag type="primary">趋势分析</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="scoreTrendChart" class="chart"></div>
            <div class="chart-analysis">
              <el-alert
                :title="visualizationData.scoreTrend.analysis"
                type="success"
                :closable="false"
                show-icon
              />
            </div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>{{ visualizationData.subjectAnalysis.title }}</h3>
              <el-tag type="warning">科目分析</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="subjectAnalysisChart" class="chart"></div>
            <div class="chart-analysis">
              <el-alert
                :title="visualizationData.subjectAnalysis.analysis"
                type="warning"
                :closable="false"
                show-icon
              />
            </div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>{{ visualizationData.schoolComparison.title }}</h3>
              <el-tag type="success">目标对比</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="schoolComparisonChart" class="chart"></div>
            <div class="chart-analysis">
              <el-alert
                :title="visualizationData.schoolComparison.analysis"
                type="info"
                :closable="false"
                show-icon
              />
            </div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>{{ visualizationData.progressAnalysis.title }}</h3>
              <el-tag type="danger">进度分析</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="progressAnalysisChart" class="chart"></div>
            <div class="chart-analysis">
              <el-alert
                :title="visualizationData.progressAnalysis.analysis"
                type="error"
                :closable="false"
                show-icon
              />
            </div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>学校排名</h3>
              <el-tag type="primary">云南省重点高中</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="schoolRankingChart" class="chart"></div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>成绩分布</h3>
              <el-tag type="warning">各科成绩区间</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="scoreDistributionChart" class="chart"></div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>学习时长分析</h3>
              <el-tag type="success">日均学习时间</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="studyTimeChart" class="chart"></div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>错题分析</h3>
              <el-tag type="danger">知识点掌握情况</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="errorAnalysisChart" class="chart"></div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>学科对比分析</h3>
              <el-tag type="primary">各科成绩对比</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="subjectComparisonChart" class="chart"></div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>模拟考试分析</h3>
              <el-tag type="warning">历次模拟成绩趋势</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="mockExamChart" class="chart"></div>
            <div class="exam-summary">
              <div class="summary-item">
                <div class="summary-value">5</div>
                <div class="summary-label">模拟考试次数</div>
              </div>
              <div class="summary-item">
                <div class="summary-value">585</div>
                <div class="summary-label">平均分</div>
              </div>
              <div class="summary-item">
                <div class="summary-value">+25</div>
                <div class="summary-label">进步幅度</div>
              </div>
              <div class="summary-item">
                <div class="summary-value">89%</div>
                <div class="summary-label">完成率</div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>学校录取趋势分析</h3>
              <el-tag type="info">近五年分数线变化</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="admissionTrendChart" class="chart"></div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>志愿填报成功率分析</h3>
              <el-tag type="success">志愿策略评估</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="volunteerSuccessChart" class="chart"></div>
            <div class="success-summary">
              <div class="success-item high">
                <div class="success-icon">✅</div>
                <div class="success-info">
                  <div class="success-rate">75%</div>
                  <div class="success-label">第一志愿成功率</div>
                </div>
              </div>
              <div class="success-item medium">
                <div class="success-icon">📊</div>
                <div class="success-info">
                  <div class="success-rate">92%</div>
                  <div class="success-label">服从调剂成功率</div>
                </div>
              </div>
              <div class="success-item low">
                <div class="success-icon">⚠️</div>
                <div class="success-info">
                  <div class="success-rate">8%</div>
                  <div class="success-label">滑档风险</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>学科对比分析</h3>
              <el-tag type="info">各科成绩对比</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <SubjectCompareChart />
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>模拟考试分析</h3>
              <el-tag type="primary">历次考试记录</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <ExamAnalysisChart />
          </div>
        </el-card>

        <el-card class="recommendation-card">
          <template #header>
            <div class="card-header">
              <h3>学习建议</h3>
              <el-tag type="primary">智能推荐</el-tag>
            </div>
          </template>
          <div class="recommendation-list">
            <div
              v-for="(recommendation, idx) in visualizationData.recommendations"
              :key="recommendation.title"
              class="recommendation-item"
            >
              <div class="recommendation-number">{{ idx + 1 }}</div>
              <div class="recommendation-content">
                <h4>{{ recommendation.title }}</h4>
                <p>{{ recommendation.content }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <div v-else class="empty-state">
        <el-empty description="暂无数据分析数据，请点击上方按钮生成分析报告" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshLeft, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { aiApi } from '@/api'
import { useSharedStore, eventBus, Events } from '../store/shared'
import SubjectCompareChart from '../components/SubjectCompareChart.vue'
import ExamAnalysisChart from '../components/ExamAnalysisChart.vue'

interface ChartDataset {
  label: string
  data: number[]
  borderColor: string
  backgroundColor: string
}

interface ScoreTrendData {
  title: string
  analysis: string
  data: {
    labels: string[]
    datasets: ChartDataset[]
  }
}

interface SubjectAnalysisData {
  title: string
  analysis: string
  data: {
    labels: string[]
    datasets: ChartDataset[]
  }
}

interface SchoolComparisonData {
  title: string
  analysis: string
  data: {
    labels: string[]
    datasets: ChartDataset[]
  }
}

interface ProgressAnalysisData {
  title: string
  analysis: string
  data: Record<string, { current: number; target: number; progress: number }>
}

interface Recommendation {
  title: string
  content: string
}

interface VisualizationData {
  scoreTrend: ScoreTrendData
  subjectAnalysis: SubjectAnalysisData
  schoolComparison: SchoolComparisonData
  progressAnalysis: ProgressAnalysisData
  recommendations: Recommendation[]
}

const loading = ref(false)
const isLoading = ref(true)
const loadingProgress = ref(0)
const loadingText = ref('正在分析数据...')
const visualizationData = ref<VisualizationData | null>(null)
const sharedStore = useSharedStore()

// 页面统计数据
const chartCount = ref(12)
const recommendationCount = ref(6)

// 从共享状态获取统计数据（用于后续扩展）
// const statistics = computed(() => sharedStore.statistics)

const formData = ref({
  analysisType: 'comprehensive',
  timeRange: '3',
  dimension: 'all'
})

const scoreTrendChart = ref<HTMLElement | null>(null)
const subjectAnalysisChart = ref<HTMLElement | null>(null)
const schoolComparisonChart = ref<HTMLElement | null>(null)
const progressAnalysisChart = ref<HTMLElement | null>(null)
const schoolRankingChart = ref<HTMLElement | null>(null)
const scoreDistributionChart = ref<HTMLElement | null>(null)
const studyTimeChart = ref<HTMLElement | null>(null)
const errorAnalysisChart = ref<HTMLElement | null>(null)
const subjectComparisonChart = ref<HTMLElement | null>(null)
const mockExamChart = ref<HTMLElement | null>(null)
const admissionTrendChart = ref<HTMLElement | null>(null)
const volunteerSuccessChart = ref<HTMLElement | null>(null)

let scoreTrendChartInstance: echarts.ECharts | null = null
let subjectAnalysisChartInstance: echarts.ECharts | null = null
let schoolComparisonChartInstance: echarts.ECharts | null = null
let progressAnalysisChartInstance: echarts.ECharts | null = null
let schoolRankingChartInstance: echarts.ECharts | null = null
let scoreDistributionChartInstance: echarts.ECharts | null = null
let studyTimeChartInstance: echarts.ECharts | null = null
let errorAnalysisChartInstance: echarts.ECharts | null = null
let subjectComparisonChartInstance: echarts.ECharts | null = null
let mockExamChartInstance: echarts.ECharts | null = null
let admissionTrendChartInstance: echarts.ECharts | null = null
let volunteerSuccessChartInstance: echarts.ECharts | null = null

// 当前选中的考试（用于图表联动）
const selectedExamIndex = ref(-1)

const generateMockData = (): VisualizationData => {
  const timeRange = parseInt(formData.value.timeRange)
  const labels = Array.from({ length: timeRange }, (_, i) => `第${timeRange - i}次考试`)
  
  const subjects = ['语文', '数学', '英语', '物理', '化学', '生物']
  const schoolNames = ['云师大附中', '昆一中', '昆三中', '昆八中', '云大附中']
  const schoolScores = [690, 680, 670, 660, 655]
  const userScores = [635, 642, 658, 648, 665]

  return {
    scoreTrend: {
      title: '成绩趋势分析',
      analysis: '整体成绩呈现上升趋势，最近一次考试进步明显，建议继续保持学习节奏。',
      data: {
        labels,
        datasets: [
          {
            label: '总分',
            data: [620, 635, 648, 652, 668].slice(-timeRange),
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.3)'
          },
          {
            label: '目标分数',
            data: Array(timeRange).fill(680),
            borderColor: '#67C23A',
            backgroundColor: 'rgba(103, 194, 58, 0.1)'
          }
        ]
      }
    },
    subjectAnalysis: {
      title: '科目综合分析',
      analysis: '数学和物理表现优异，语文和英语仍有提升空间，建议加强阅读理解和写作训练。',
      data: {
        labels: subjects,
        datasets: [
          {
            label: '当前成绩',
            data: [108, 118, 112, 98, 88, 85],
            borderColor: '#409EFF',
            backgroundColor: 'rgba(64, 158, 255, 0.5)'
          },
          {
            label: '目标成绩',
            data: [115, 125, 120, 105, 95, 92],
            borderColor: '#67C23A',
            backgroundColor: 'rgba(103, 194, 58, 0.3)'
          }
        ]
      }
    },
    schoolComparison: {
      title: '目标学校对比',
      analysis: '当前成绩与云师大附中仍有差距，建议重点提升薄弱科目，争取在中考中取得更好成绩。',
      data: {
        labels: schoolNames,
        datasets: [
          {
            label: '录取分数线',
            data: schoolScores,
            borderColor: '#E6A23C',
            backgroundColor: 'rgba(230, 162, 60, 0.8)'
          },
          {
            label: '我的成绩',
            data: userScores,
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.8)'
          }
        ]
      }
    },
    progressAnalysis: {
      title: '学习进度分析',
      analysis: '整体学习进度已完成78%，建议在剩余时间内重点突破薄弱环节。',
      data: {
        '语文': { current: 85, target: 95, progress: 89 },
        '数学': { current: 92, target: 98, progress: 94 },
        '英语': { current: 82, target: 95, progress: 86 },
        '物理': { current: 88, target: 95, progress: 93 },
        '化学': { current: 78, target: 90, progress: 87 },
        '生物': { current: 80, target: 90, progress: 89 }
      }
    },
    recommendations: [
      {
        title: '加强语文阅读理解',
        content: '建议每天阅读一篇课外文章，积累词汇和表达方式，提高阅读理解能力。'
      },
      {
        title: '数学错题整理',
        content: '建立错题本，定期回顾错题，分析错误原因，避免重复犯错。'
      },
      {
        title: '英语听力训练',
        content: '每天坚持听英语听力材料，提高听力理解能力和口语表达能力。'
      },
      {
        title: '物理公式复习',
        content: '系统复习物理公式，理解公式的应用场景，加强计算题练习。'
      },
      {
        title: '化学实验复习',
        content: '回顾化学实验原理和操作步骤，理解实验现象背后的化学原理。'
      },
      {
        title: '调整学习节奏',
        content: '合理安排学习时间，保证充足睡眠，保持良好的学习状态。'
      }
    ]
  }
}

const loadAnalysis = async () => {
  loading.value = true
  isLoading.value = true
  loadingProgress.value = 0
  
  // 模拟加载进度
  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += Math.random() * 15
    }
  }, 200)

  try {
    const response = await aiApi.getDataVisualizationAnalysis({
      studentId: '',
      analysisType: formData.value.analysisType,
      timeRange: formData.value.timeRange
    })

    if (response.success && response.data) {
      visualizationData.value = response.data as VisualizationData
    } else {
      visualizationData.value = generateMockData()
    }

    loadingProgress.value = 100
    clearInterval(progressInterval)
    
    await nextTick()
    setTimeout(() => {
      isLoading.value = false
      initCharts()
    }, 300)
    
    ElMessage.success('数据分析完成')
  } catch (error) {
    console.error('加载数据分析失败:', error)
    loadingProgress.value = 100
    clearInterval(progressInterval)
    visualizationData.value = generateMockData()
    await nextTick()
    setTimeout(() => {
      isLoading.value = false
      initCharts()
    }, 300)
    ElMessage.warning('使用模拟数据展示')
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  if (!visualizationData.value) return

  initScoreTrendChart()
  initSubjectAnalysisChart()
  initSchoolComparisonChart()
  initProgressAnalysisChart()
  initSchoolRankingChart()
  initScoreDistributionChart()
  initStudyTimeChart()
  initErrorAnalysisChart()
  initSubjectComparisonChart()
  initMockExamChart()
  initAdmissionTrendChart()
  initVolunteerSuccessChart()
}

const initScoreTrendChart = () => {
  if (!scoreTrendChart.value) return
  
  if (scoreTrendChartInstance) {
    scoreTrendChartInstance.dispose()
  }

  scoreTrendChartInstance = echarts.init(scoreTrendChart.value)
  const chartData = visualizationData.value!.scoreTrend.data

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' }
    },
    legend: {
      data: chartData.datasets.map(d => d.label),
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.labels,
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: {
      type: 'value',
      name: '分数',
      nameTextStyle: { color: '#909399' },
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      splitLine: { lineStyle: { color: '#f2f6fc' } }
    },
    series: chartData.datasets.map(dataset => ({
      name: dataset.label,
      type: 'line',
      data: dataset.data,
      smooth: true,
      itemStyle: {
        color: dataset.borderColor
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: dataset.backgroundColor },
          { offset: 1, color: 'rgba(255, 255, 255, 0)' }
        ])
      },
      emphasis: {
        focus: 'series'
      }
    }))
  }

  scoreTrendChartInstance.setOption(option)
  
  // 添加点击事件实现图表联动
  scoreTrendChartInstance.on('click', (params: unknown) => {
    const p = params as { dataIndex: number }
    handleExamClick(p.dataIndex)
  })
}

const initSubjectAnalysisChart = () => {
  if (!subjectAnalysisChart.value) return
  
  if (subjectAnalysisChartInstance) {
    subjectAnalysisChartInstance.dispose()
  }

  subjectAnalysisChartInstance = echarts.init(subjectAnalysisChart.value)
  const chartData = visualizationData.value!.subjectAnalysis.data

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' }
    },
    legend: {
      data: chartData.datasets.map(d => d.label),
      textStyle: { color: '#909399' }
    },
    radar: {
      indicator: chartData.labels.map(label => ({ name: label, max: 130 })),
      shape: 'polygon',
      splitNumber: 4,
      axisName: { color: '#909399' },
      splitLine: { lineStyle: { color: '#e4e7ed' } },
      splitArea: { areaStyle: { color: ['rgba(102, 126, 234, 0.05)', 'rgba(102, 126, 234, 0.1)'] } },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    series: [{
      type: 'radar',
      data: chartData.datasets.map(dataset => ({
        value: dataset.data,
        name: dataset.label,
        itemStyle: {
          color: dataset.borderColor
        },
        areaStyle: {
          color: dataset.backgroundColor
        }
      }))
    }]
  }

  subjectAnalysisChartInstance.setOption(option)
}

const initSchoolComparisonChart = () => {
  if (!schoolComparisonChart.value) return
  
  if (schoolComparisonChartInstance) {
    schoolComparisonChartInstance.dispose()
  }

  schoolComparisonChartInstance = echarts.init(schoolComparisonChart.value)
  const chartData = visualizationData.value!.schoolComparison.data

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' }
    },
    legend: {
      data: chartData.datasets.map(d => d.label),
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.labels,
      axisLabel: { color: '#909399', rotate: 30 },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: {
      type: 'value',
      name: '分数',
      nameTextStyle: { color: '#909399' },
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      splitLine: { lineStyle: { color: '#f2f6fc' } }
    },
    series: chartData.datasets.map(dataset => ({
      name: dataset.label,
      type: 'bar',
      data: dataset.data,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: dataset.backgroundColor },
          { offset: 1, color: dataset.borderColor }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }))
  }

  schoolComparisonChartInstance.setOption(option)
}

const initProgressAnalysisChart = () => {
  if (!progressAnalysisChart.value) return
  
  if (progressAnalysisChartInstance) {
    progressAnalysisChartInstance.dispose()
  }

  progressAnalysisChartInstance = echarts.init(progressAnalysisChart.value)
  const chartData = visualizationData.value!.progressAnalysis.data

  const subjects = Object.keys(chartData)
  const currentData = subjects.map(subject => chartData[subject].current)
  const targetData = subjects.map(subject => chartData[subject].target)
  const progressData = subjects.map(subject => chartData[subject].progress)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' }
    },
    legend: {
      data: ['当前成绩', '目标分数', '完成度'],
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: subjects,
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '分数',
        position: 'left',
        nameTextStyle: { color: '#909399' },
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { lineStyle: { color: '#f2f6fc' } }
      },
      {
        type: 'value',
        name: '完成度(%)',
        position: 'right',
        nameTextStyle: { color: '#909399' },
        max: 100,
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '当前成绩',
        type: 'bar',
        data: currentData,
        itemStyle: {
          color: '#409EFF',
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '目标分数',
        type: 'bar',
        data: targetData,
        itemStyle: {
          color: '#67C23A',
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '完成度',
        type: 'line',
        yAxisIndex: 1,
        data: progressData,
        itemStyle: {
          color: '#E6A23C'
        },
        lineStyle: {
          width: 3
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }

  progressAnalysisChartInstance.setOption(option)
}

const initSchoolRankingChart = () => {
  if (!schoolRankingChart.value) return
  
  if (schoolRankingChartInstance) {
    schoolRankingChartInstance.dispose()
  }

  schoolRankingChartInstance = echarts.init(schoolRankingChart.value)

  const schoolData = [
    { name: '云南省第一中学', type: '重点高中', city: '昆明市', score: 680, change: 0, students: 12580, rank: 1 },
    { name: '昆明市第二中学', type: '重点高中', city: '昆明市', score: 675, change: -1, students: 11250, rank: 2 },
    { name: '曲靖市第一中学', type: '重点高中', city: '曲靖市', score: 670, change: 1, students: 9860, rank: 3 },
    { name: '玉溪市第一中学', type: '重点高中', city: '玉溪市', score: 665, change: 0, students: 8750, rank: 4 },
    { name: '昆明市第三中学', type: '重点高中', city: '昆明市', score: 660, change: -1, students: 8200, rank: 5 },
    { name: '昆明市第八中学', type: '重点高中', city: '昆明市', score: 658, change: 1, students: 7680, rank: 6 },
    { name: '红河州第一中学', type: '重点高中', city: '红河州', score: 655, change: 0, students: 7200, rank: 7 },
    { name: '大理州第一中学', type: '重点高中', city: '大理州', score: 650, change: -1, students: 6850, rank: 8 }
  ]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.98)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133', fontSize: 14 },
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const p = params as { axisValue: string; marker: string; seriesName: string; value: number }[]
        const school = schoolData.find(s => s.name === p[0].axisValue)
        if (!school) return ''
        const changeIcon = school.change > 0 ? '↑' : school.change < 0 ? '↓' : '—'
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; font-size: 16px; color: #303133; margin-bottom: 8px;">${school.name}</div>
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <div><span style="color: #909399;">学校类型：</span>${school.type}</div>
              <div><span style="color: #909399;">所在地区：</span>${school.city}</div>
              <div><span style="color: #909399;">录取分数线：</span><span style="font-weight: bold; color: #667eea;">${school.score}分</span></div>
              <div><span style="color: #909399;">排名变化：</span><span style="${school.change > 0 ? 'color: #67C23A' : school.change < 0 ? 'color: #F56C6C' : 'color: #909399'}">${changeIcon} ${Math.abs(school.change)}</span></div>
              <div><span style="color: #909399;">在校人数：</span>${school.students.toLocaleString()}人</div>
            </div>
          </div>
        `
      }
    },
    legend: {
      data: ['录取分数线', '排名'],
      textStyle: { color: '#606266', fontSize: 13 },
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '25%',
      top: '15%',
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: schoolData.map(s => s.name),
      axisLabel: { 
        color: '#404040', 
        fontSize: 13, 
        fontWeight: 500,
        rotate: 45,
        margin: 20,
        interval: 0,
        formatter: (value: string) => {
          return value.length > 6 ? value.slice(0, 6) + '...' : value
        }
      },
      axisLine: { lineStyle: { color: '#e4e7ed', width: 2 } },
      axisTick: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        name: '录取分数线',
        position: 'left',
        nameTextStyle: { color: '#606266', fontSize: 13, fontWeight: 500 },
        axisLabel: { color: '#606266', fontSize: 12 },
        axisLine: { lineStyle: { color: '#e4e7ed', width: 2 } },
        splitLine: { lineStyle: { color: '#f5f7fa', type: 'dashed' } },
        min: 620,
        max: 700
      },
      {
        type: 'value',
        name: '排名',
        position: 'right',
        nameTextStyle: { color: '#606266', fontSize: 13, fontWeight: 500 },
        max: 10,
        min: 1,
        inverse: true,
        axisLabel: { color: '#606266', fontSize: 12 },
        axisLine: { lineStyle: { color: '#e4e7ed', width: 2 } },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '录取分数线',
        type: 'bar',
        data: schoolData.map(s => s.score),
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [6, 6, 0, 0],
          shadowColor: 'rgba(102, 126, 234, 0.3)',
          shadowBlur: 10,
          shadowOffsetY: 5
        },
        emphasis: {
          itemStyle: {
            shadowColor: 'rgba(102, 126, 234, 0.5)',
            shadowBlur: 15
          }
        },
        label: {
          show: true,
          position: 'top',
          color: '#667eea',
          fontWeight: 'bold',
          fontSize: 12,
          formatter: '{c}分'
        }
      },
      {
        name: '排名',
        type: 'line',
        yAxisIndex: 1,
        data: schoolData.map(s => s.rank),
        itemStyle: {
          color: '#F56C6C'
        },
        lineStyle: {
          width: 3,
          type: 'dashed'
        },
        symbol: 'circle',
        symbolSize: 10,
        emphasis: {
          scale: 1.5,
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(245, 108, 108, 0.5)'
          }
        }
      }
    ]
  }

  schoolRankingChartInstance.setOption(option)
  
  schoolRankingChartInstance.on('mouseover', (params: unknown) => {
    const p = params as { dataIndex: number }
    schoolRankingChartInstance?.dispatchAction({
      type: 'highlight',
      seriesIndex: 0,
      dataIndex: p.dataIndex
    })
  })
  
  schoolRankingChartInstance.on('mouseout', () => {
    schoolRankingChartInstance?.dispatchAction({
      type: 'downplay',
      seriesIndex: 0
    })
  })
}

const initScoreDistributionChart = () => {
  if (!scoreDistributionChart.value) return
  
  if (scoreDistributionChartInstance) {
    scoreDistributionChartInstance.dispose()
  }

  scoreDistributionChartInstance = echarts.init(scoreDistributionChart.value)

  const subjectData = [
    { name: '语文', value: 108, max: 120 },
    { name: '数学', value: 118, max: 120 },
    { name: '英语', value: 112, max: 120 },
    { name: '物理', value: 98, max: 100 },
    { name: '化学', value: 88, max: 100 },
    { name: '生物', value: 85, max: 100 }
  ]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' },
      formatter: (params: unknown) => {
        const p = params as { name: string; value: number; data: { max: number } }
        const rate = ((p.value / p.data.max) * 100).toFixed(1)
        return `${p.name}<br/>分数: ${p.value}/${p.data.max}<br/>占比: ${rate}%`
      }
    },
    series: [
      {
        name: '成绩分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}',
          color: '#909399'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true,
          lineStyle: { color: '#e4e7ed' }
        },
        data: subjectData.map((item, index) => ({
          value: item.value,
          name: item.name,
          max: item.max,
          itemStyle: {
            color: [
              '#667eea',
              '#67C23A',
              '#E6A23C',
              '#F56C6C',
              '#909399',
              '#409EFF'
            ][index]
          }
        }))
      }
    ]
  }

  scoreDistributionChartInstance.setOption(option)
}

// 学习时长分析图表
const initStudyTimeChart = () => {
  if (!studyTimeChart.value) return
  
  if (studyTimeChartInstance) {
    studyTimeChartInstance.dispose()
  }

  studyTimeChartInstance = echarts.init(studyTimeChart.value)

  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const studyTime = [4.5, 5.2, 4.8, 5.5, 4.0, 6.5, 7.2]
  const recommendedTime = Array(7).fill(6)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' },
      formatter: (params: unknown) => {
        const p = params as { axisValue: string; marker: string; seriesName: string; value: number }[]
        return `${p[0].axisValue}<br/>${p[0].marker}${p[0].seriesName}: ${p[0].value}小时<br/>${p[1].marker}${p[1].seriesName}: ${p[1].value}小时`
      }
    },
    legend: {
      data: ['实际学习时长', '推荐学习时长'],
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: days,
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: {
      type: 'value',
      name: '小时',
      nameTextStyle: { color: '#909399' },
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      splitLine: { lineStyle: { color: '#f2f6fc' } }
    },
    series: [
      {
        name: '实际学习时长',
        type: 'bar',
        data: studyTime,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '推荐学习时长',
        type: 'line',
        data: recommendedTime,
        smooth: true,
        lineStyle: {
          color: '#67C23A',
          type: 'dashed',
          width: 2
        },
        symbol: 'none'
      }
    ]
  }

  studyTimeChartInstance.setOption(option)
}

// 错题分析图表
const initErrorAnalysisChart = () => {
  if (!errorAnalysisChart.value) return
  
  if (errorAnalysisChartInstance) {
    errorAnalysisChartInstance.dispose()
  }

  errorAnalysisChartInstance = echarts.init(errorAnalysisChart.value)

  const knowledgePoints = ['函数与导数', '三角函数', '立体几何', '概率统计', '解析几何', '数列', '不等式', '向量']
  const errorRates = [15, 8, 22, 12, 28, 18, 10, 5]
  const masteryLevels = ['掌握中', '已掌握', '需加强', '掌握中', '薄弱', '掌握中', '已掌握', '已掌握']

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' },
      formatter: (params: unknown) => {
        const p = params as [{ axisValue: string; value: number }]
        const mastery = masteryLevels[knowledgePoints.indexOf(p[0].axisValue)]
        return `${p[0].axisValue}<br/>错误率: ${p[0].value}%<br/>掌握程度: ${mastery}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '错误率(%)',
      nameTextStyle: { color: '#909399' },
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      splitLine: { lineStyle: { color: '#f2f6fc' } }
    },
    yAxis: {
      type: 'category',
      data: knowledgePoints,
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    series: [
      {
        type: 'bar',
        data: errorRates.map((rate, index) => ({
          value: rate,
          itemStyle: {
            color: rate > 20 ? '#F56C6C' : rate > 15 ? '#E6A23C' : '#67C23A',
            borderRadius: [0, 4, 4, 0]
          },
          label: {
            show: true,
            position: 'right',
            formatter: `${masteryLevels[index]}`,
            color: '#909399',
            fontSize: 11
          }
        })),
        barWidth: '60%'
      }
    ]
  }

  errorAnalysisChartInstance.setOption(option)
}

// 学科对比分析图表
const initSubjectComparisonChart = () => {
  if (!subjectComparisonChart.value) return
  
  if (subjectComparisonChartInstance) {
    subjectComparisonChartInstance.dispose()
  }

  subjectComparisonChartInstance = echarts.init(subjectComparisonChart.value)

  const subjects = ['语文', '数学', '英语', '物理', '化学', '生物']
  const scores = [108, 118, 112, 98, 88, 85]
  const targets = [110, 115, 115, 100, 95, 90]
  const rankings = [85, 95, 90, 88, 75, 80]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' },
      axisPointer: { type: 'cross', crossStyle: { color: '#999' } }
    },
    legend: {
      data: ['当前成绩', '目标成绩', '排名百分位'],
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: subjects,
      axisPointer: { type: 'shadow' },
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '分数',
        min: 0,
        max: 120,
        interval: 30,
        nameTextStyle: { color: '#909399' },
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { lineStyle: { color: '#f2f6fc' } }
      },
      {
        type: 'value',
        name: '排名%',
        min: 0,
        max: 100,
        interval: 25,
        nameTextStyle: { color: '#909399' },
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '当前成绩',
        type: 'bar',
        data: scores,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '目标成绩',
        type: 'bar',
        data: targets,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#67C23A' },
            { offset: 1, color: '#85CE61' }
          ]),
          borderRadius: [4, 4, 0, 0],
          opacity: 0.6
        }
      },
      {
        name: '排名百分位',
        type: 'line',
        yAxisIndex: 1,
        data: rankings,
        smooth: true,
        lineStyle: { color: '#F56C6C', width: 3 },
        itemStyle: { color: '#F56C6C' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0)' }
          ])
        }
      }
    ]
  }

  subjectComparisonChartInstance.setOption(option)
}

// 模拟考试分析图表
const initMockExamChart = () => {
  if (!mockExamChart.value) return
  
  if (mockExamChartInstance) {
    mockExamChartInstance.dispose()
  }

  mockExamChartInstance = echarts.init(mockExamChart.value)

  const exams = ['一模', '二模', '三模', '四模', '五模']
  const totalScores = [560, 575, 568, 582, 585]
  const rankPositions = [120, 115, 108, 95, 88]
  const targetScore = Array(5).fill(600)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' },
      formatter: (params: unknown) => {
        const p = params as { seriesName: string; value: number; axisValue: string; marker?: string }[]
        let result = `${p[0].axisValue}<br/>`
        p.forEach(item => {
          const colorMap: Record<string, string> = {
            '总分': '#409EFF',
            '年级排名': '#67C23A',
            '目标分数': '#F56C6C'
          }
          const color = colorMap[item.seriesName] || '#909399'
          result += `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:6px;"></span>${item.seriesName}: ${item.value}`
          if (item.seriesName === '总分') result += '分'
          if (item.seriesName === '年级排名') result += '名'
          result += '<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['总分', '年级排名', '目标分数'],
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: exams,
      axisLabel: { color: '#909399', fontSize: 14 },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '分数',
        min: 500,
        max: 650,
        interval: 50,
        nameTextStyle: { color: '#909399' },
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { lineStyle: { color: '#f2f6fc' } }
      },
      {
        type: 'value',
        name: '排名',
        min: 0,
        max: 150,
        interval: 30,
        inverse: true,
        nameTextStyle: { color: '#909399' },
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '总分',
        type: 'line',
        data: totalScores,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0)' }
          ])
        },
        symbol: 'circle',
        symbolSize: 10
      },
      {
        name: '年级排名',
        type: 'line',
        yAxisIndex: 1,
        data: rankPositions,
        smooth: true,
        lineStyle: { color: '#67C23A', width: 3, type: 'dashed' },
        itemStyle: { color: '#67C23A' },
        symbol: 'diamond',
        symbolSize: 10
      },
      {
        name: '目标分数',
        type: 'line',
        data: targetScore,
        lineStyle: {
          color: '#F56C6C',
          width: 2,
          type: 'dashed'
        },
        itemStyle: { color: '#F56C6C' },
        symbol: 'none'
      }
    ]
  }

  mockExamChartInstance.setOption(option)
}

// 学校录取趋势分析图表
const initAdmissionTrendChart = () => {
  if (!admissionTrendChart.value) return
  
  if (admissionTrendChartInstance) {
    admissionTrendChartInstance.dispose()
  }

  admissionTrendChartInstance = echarts.init(admissionTrendChart.value)

  const years = ['2021', '2022', '2023', '2024', '2025']
  const schoolA = [655, 662, 668, 672, 678]
  const schoolB = [648, 655, 660, 665, 670]
  const schoolC = [640, 645, 652, 658, 662]
  const avgLine = [648, 654, 660, 665, 670]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' }
    },
    legend: {
      data: ['师大附中', '昆一中', '昆三中', '平均分数线'],
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: years,
      axisLabel: { color: '#909399', fontSize: 12 },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: {
      type: 'value',
      name: '分数线',
      min: 630,
      max: 690,
      nameTextStyle: { color: '#909399' },
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      splitLine: { lineStyle: { color: '#f2f6fc' } }
    },
    series: [
      {
        name: '师大附中',
        type: 'line',
        data: schoolA,
        smooth: true,
        lineStyle: { color: '#E6A23C', width: 3 },
        itemStyle: { color: '#E6A23C' },
        symbol: 'circle',
        symbolSize: 8
      },
      {
        name: '昆一中',
        type: 'line',
        data: schoolB,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        itemStyle: { color: '#409EFF' },
        symbol: 'circle',
        symbolSize: 8
      },
      {
        name: '昆三中',
        type: 'line',
        data: schoolC,
        smooth: true,
        lineStyle: { color: '#67C23A', width: 3 },
        itemStyle: { color: '#67C23A' },
        symbol: 'circle',
        symbolSize: 8
      },
      {
        name: '平均分数线',
        type: 'line',
        data: avgLine,
        smooth: true,
        lineStyle: { color: '#F56C6C', width: 2, type: 'dashed' },
        itemStyle: { color: '#F56C6C' },
        symbol: 'none'
      }
    ]
  }

  admissionTrendChartInstance.setOption(option)
}

// 志愿填报成功率分析图表
const initVolunteerSuccessChart = () => {
  if (!volunteerSuccessChart.value) return
  
  if (volunteerSuccessChartInstance) {
    volunteerSuccessChartInstance.dispose()
  }

  volunteerSuccessChartInstance = echarts.init(volunteerSuccessChart.value)

  const categories = ['第一志愿', '第二志愿', '第三志愿', '调剂志愿']
  const successRates = [75, 15, 8, 2]
  const riskLevels = [15, 25, 40, 60]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' },
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['成功率', '风险等级'],
      textStyle: { color: '#909399' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#909399', fontSize: 12 },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '成功率(%)',
        min: 0,
        max: 100,
        nameTextStyle: { color: '#909399' },
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { lineStyle: { color: '#f2f6fc' } }
      },
      {
        type: 'value',
        name: '风险(%)',
        min: 0,
        max: 100,
        nameTextStyle: { color: '#909399' },
        axisLabel: { color: '#909399' },
        axisLine: { lineStyle: { color: '#e4e7ed' } },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '成功率',
        type: 'bar',
        data: successRates.map((rate, index) => ({
          value: rate,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: index === 0 ? '#67C23A' : index === 1 ? '#409EFF' : '#E6A23C' },
              { offset: 1, color: index === 0 ? '#85CE61' : index === 1 ? '#67B8F7' : '#F0C78A' }
            ]),
            borderRadius: [4, 4, 0, 0]
          }
        }))
      },
      {
        name: '风险等级',
        type: 'line',
        yAxisIndex: 1,
        data: riskLevels,
        smooth: true,
        lineStyle: { color: '#F56C6C', width: 3 },
        itemStyle: { color: '#F56C6C' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0)' }
          ])
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }

  volunteerSuccessChartInstance.setOption(option)
}

// 图表联动：点击考试时更新所有图表高亮
const handleExamClick = (examIndex: number) => {
  selectedExamIndex.value = examIndex
  
  // 更新所有图表的高亮状态
  updateChartsHighlight(examIndex)
  
  ElMessage.info(`已选择第 ${examIndex + 1} 次考试，其他图表已联动更新`)
}

// 更新图表高亮状态
const updateChartsHighlight = (examIndex: number) => {
  // 更新成绩趋势图高亮
  if (scoreTrendChartInstance) {
    scoreTrendChartInstance.dispatchAction({
      type: 'highlight',
      seriesIndex: 0,
      dataIndex: examIndex
    })
  }
  
  // 更新科目分析图高亮（显示对应考试的科目数据）
  if (subjectAnalysisChartInstance) {
    subjectAnalysisChartInstance.dispatchAction({
      type: 'highlight',
      seriesIndex: 0,
      dataIndex: 0
    })
  }
  
  // 更新学校对比图高亮
  if (schoolComparisonChartInstance) {
    schoolComparisonChartInstance.dispatchAction({
      type: 'highlight',
      seriesIndex: 0,
      dataIndex: examIndex
    })
  }
}

// 导出报告（支持多种格式）
const exportReport = () => {
  if (!visualizationData.value) return

  ElMessageBox.confirm(
    '请选择导出格式',
    '导出报告',
    {
      confirmButtonText: 'JSON 格式',
      cancelButtonText: 'CSV 格式',
      type: 'info',
      showClose: false
    }
  ).then(() => {
    exportToJSON()
  }).catch(() => {
    exportToCSV()
  })
}

const exportToJSON = () => {
  const reportData = {
    title: '学习数据分析报告',
    generatedAt: new Date().toLocaleString('zh-CN'),
    analysisType: formData.value.analysisType,
    timeRange: formData.value.timeRange,
    data: visualizationData.value
  }

  const content = JSON.stringify(reportData, null, 2)
  const blob = new Blob([content], { type: 'application/json;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `学习分析报告_${new Date().toLocaleDateString()}.json`
  link.click()

  ElMessage.success('JSON报告导出成功')
}

const exportToCSV = () => {
  if (!visualizationData.value) return

  let csvContent = '数据类型,项目,数值\n'
  
  // 导出成绩趋势数据
  const trendData = visualizationData.value.scoreTrend.data
  trendData.labels.forEach((label: string, index: number) => {
    trendData.datasets.forEach((dataset: ChartDataset) => {
      csvContent += `成绩趋势,${dataset.label}-${label},${dataset.data[index]}\n`
    })
  })

  // 导出科目分析数据
  const subjectData = visualizationData.value.subjectAnalysis.data
  subjectData.labels.forEach((label: string, index: number) => {
    subjectData.datasets.forEach((dataset: ChartDataset) => {
      csvContent += `科目分析,${dataset.label}-${label},${dataset.data[index]}\n`
    })
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `学习分析报告_${new Date().toLocaleDateString()}.csv`
  link.click()

  ElMessage.success('CSV报告导出成功')
}

const handleResize = () => {
  scoreTrendChartInstance?.resize()
  subjectAnalysisChartInstance?.resize()
  schoolComparisonChartInstance?.resize()
  progressAnalysisChartInstance?.resize()
  schoolRankingChartInstance?.resize()
  scoreDistributionChartInstance?.resize()
  studyTimeChartInstance?.resize()
  errorAnalysisChartInstance?.resize()
  subjectComparisonChartInstance?.resize()
  mockExamChartInstance?.resize()
  admissionTrendChartInstance?.resize()
  volunteerSuccessChartInstance?.resize()
}

// 事件处理函数
const handleStatisticsUpdated = (data?: unknown) => {
  console.log('统计数据更新:', data)
  // 可以在这里更新相关的图表或统计展示
}

const handleSchoolViewed = (data?: unknown) => {
  console.log('学校被查看:', data)
  // 可以在这里更新相关的分析数据
}

const handleSearchPerformed = (data?: unknown) => {
  console.log('搜索执行:', data)
  // 可以在这里更新搜索相关的分析
}

onMounted(() => {
  // 启动加载动画
  setTimeout(() => {
    loadAnalysis()
  }, 500)
  
  window.addEventListener('resize', handleResize)
  
  // 注册事件监听
  eventBus.on(Events.STATISTICS_UPDATED, handleStatisticsUpdated)
  eventBus.on(Events.SCHOOL_VIEWED, handleSchoolViewed)
  eventBus.on(Events.SEARCH_PERFORMED, handleSearchPerformed)
  
  // 初始化共享状态
  sharedStore.initFromStorage()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  scoreTrendChartInstance?.dispose()
  subjectAnalysisChartInstance?.dispose()
  schoolComparisonChartInstance?.dispose()
  progressAnalysisChartInstance?.dispose()
  schoolRankingChartInstance?.dispose()
  scoreDistributionChartInstance?.dispose()
  studyTimeChartInstance?.dispose()
  errorAnalysisChartInstance?.dispose()
  subjectComparisonChartInstance?.dispose()
  mockExamChartInstance?.dispose()
  admissionTrendChartInstance?.dispose()
  volunteerSuccessChartInstance?.dispose()
  
  // 取消事件监听
  eventBus.off(Events.STATISTICS_UPDATED, handleStatisticsUpdated)
  eventBus.off(Events.SCHOOL_VIEWED, handleSchoolViewed)
  eventBus.off(Events.SEARCH_PERFORMED, handleSearchPerformed)
})
</script>

<style scoped>
.data-visualization-page {
  padding: 0;
  min-height: 100%;
  background: var(--bg-secondary);
}

/* 加载动画 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #080810 0%, #1a1a32 50%, #252540 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.5s ease, visibility 0.5s ease;
}

.loading-overlay.fade-out {
  opacity: 0;
  visibility: hidden;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.loading-orb {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.orb-core {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: orbPulse 2s ease-in-out;
  box-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
}

.orb-ring {
  position: absolute;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 50%;
  animation: orbRing 3s linear;
}

.orb-ring-1 {
  width: 70px;
  height: 70px;
  animation-delay: 0s;
}

.orb-ring-2 {
  width: 90px;
  height: 90px;
  animation-delay: -1s;
}

.orb-ring-3 {
  width: 110px;
  height: 110px;
  animation-delay: -2s;
}

@keyframes orbPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 30px rgba(102, 126, 234, 0.5); }
  50% { transform: scale(1.2); box-shadow: 0 0 50px rgba(102, 126, 234, 0.8); }
}

@keyframes orbRing {
  0% { transform: rotate(0deg); opacity: 1; }
  50% { opacity: 0.5; }
  100% { transform: rotate(360deg); opacity: 1; }
}

.loading-text {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  display: flex;
  gap: 4px;
}

.loading-char {
  display: inline-block;
  animation: charBounce 0.6s ease-in-out;
  color: #667eea;
}

@keyframes charBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.loading-progress {
  width: 250px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: progressShimmer 2s;
}

.progress-glow {
  position: absolute;
  top: -10px;
  left: 0;
  right: 0;
  height: 26px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
  filter: blur(10px);
  animation: glowMove 2s;
}

@keyframes progressShimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes glowMove {
  0% { transform: translateX(-50%); }
  100% { transform: translateX(50%); }
}

.loading-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: dotBounce 1s ease-in-out;
}

@keyframes dotBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

/* 页面头部 */
.page-header {
  position: relative;
  text-align: center;
  margin-bottom: 30px;
  padding: 60px 0;
  border-radius: 0 0 32px 32px;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--primary-gradient);
  background-size: 400% 400%;
  animation: gradientShift 15s ease;
}

.header-bg::before {
  content: '';
  position: absolute;
  top: 0;
  left: -50%;
  width: 200%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shine 3s ease-in-out;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes shine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.header-content {
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 42px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.title-icon {
  font-size: 48px;
  animation: floatIcon 3s ease-in-out;
}

@keyframes floatIcon {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
}

.page-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 30px;
}

.header-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
}

.visualization-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 40px;
}

.control-card {
  margin-bottom: 30px;
  border-radius: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  padding: 24px;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.control-card:hover {
  box-shadow: var(--shadow-md);
  border-color: rgba(102, 126, 234, 0.2);
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
}

.loading-overlay p {
  margin-top: 20px;
  color: var(--text-secondary);
}

.charts-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  border-radius: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  overflow: hidden;
  transition: box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-gradient);
  transform: scaleX(0);
  transition: transform 0.4s ease;
}

.chart-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(102, 126, 234, 0.3);
}

.chart-card:hover::before {
  transform: scaleX(1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
}

.chart {
  width: 100%;
  height: 320px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.chart:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.2);
}

.chart-analysis {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.chart-analysis:hover {
  background: rgba(102, 126, 234, 0.08);
}

.recommendation-card {
  grid-column: span 2;
  border-radius: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.recommendation-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
  padding: 8px;
}

.recommendation-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  align-items: flex-start;
  border: 1px solid var(--border-color);
  transition: box-shadow 0.35s cubic-bezier(0.4, 0, 0.2, 1), transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.recommendation-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--primary-gradient);
  transform: scaleY(0);
  transition: transform 0.35s ease;
}

.recommendation-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.recommendation-item:hover::before {
  transform: scaleY(1);
}

.recommendation-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.recommendation-item:hover .recommendation-number {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.recommendation-content {
  flex: 1;
  min-width: 0;
}

.recommendation-content h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
}

.recommendation-content p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-state {
  padding: 100px 0;
  text-align: center;
}

@media (max-width: 1200px) {
  .charts-content {
    grid-template-columns: 1fr;
  }

  .recommendation-card {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .charts-content {
    grid-template-columns: 1fr;
  }

  .recommendation-list {
    grid-template-columns: 1fr;
  }

  .chart {
    height: 300px;
  }

  .page-title {
    font-size: 24px;
  }
}

:deep(.el-card) {
  background: transparent;
  border: none;
}

:deep(.el-form-item__label) {
  color: var(--text-secondary);
}

:deep(.el-select__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  box-shadow: none;
}

:deep(.el-select__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.el-select__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
}

:deep(.el-select__placeholder) {
  color: var(--text-muted);
}

:deep(.el-select__input) {
  color: var(--text-primary);
}

:deep(.el-select-dropdown) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
}

:deep(.el-select-dropdown__item) {
  color: var(--text-secondary);
  border-radius: 8px;
  margin: 4px;
}

:deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.15);
  color: var(--text-primary);
}

:deep(.el-button--primary) {
  background: var(--primary-gradient);
  border: none;
  border-radius: 12px;
  padding: 0 20px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  transition: box-shadow 0.3s, transform 0.3s, border-color 0.3s, opacity 0.3s;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.el-button) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-primary);
  border-radius: 12px;
  padding: 0 20px;
  height: 44px;
  font-size: 15px;
  transition: box-shadow 0.3s, transform 0.3s, border-color 0.3s, opacity 0.3s;
}

:deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.4);
}

:deep(.el-button:disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

:deep(.el-alert) {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

:deep(.el-alert__title) {
  color: var(--text-secondary);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>