<template>
  <div class="exam-analysis-chart">
    <!-- 考试信息概览 -->
    <div class="exam-overview">
      <div class="overview-card">
        <div class="overview-icon">📝</div>
        <div class="overview-info">
          <div class="overview-value">{{ examCount }}</div>
          <div class="overview-label">考试次数</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon">📊</div>
        <div class="overview-info">
          <div class="overview-value">{{ averageScore }}</div>
          <div class="overview-label">平均分数</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon">📈</div>
        <div class="overview-info">
          <div class="overview-value" :class="improvement >= 0 ? 'positive' : 'negative'">
            {{ improvement >= 0 ? '+' : '' }}{{ improvement }}
          </div>
          <div class="overview-label">总体进步</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon">🎯</div>
        <div class="overview-info">
          <div class="overview-value">{{ achievementRate }}%</div>
          <div class="overview-label">目标达成率</div>
        </div>
      </div>
    </div>

    <!-- 图表切换 -->
    <div class="chart-tabs">
      <el-tabs v-model="activeTab" @change="updateChart">
        <el-tab-pane label="成绩趋势" name="trend" />
        <el-tab-pane label="各科对比" name="subjects" />
        <el-tab-pane label="排名变化" name="ranking" />
      </el-tabs>
    </div>

    <!-- 图表容器 -->
    <div ref="chartRef" class="chart"></div>

    <!-- 考试详情列表 -->
    <div class="exam-list">
      <div class="list-title">📋 考试记录详情</div>
      <div class="list-container">
        <div 
          v-for="(exam, index) in examHistory" 
          :key="exam.id"
          class="exam-item"
          :class="{ active: selectedExam === exam.id }"
          @click="selectExam(exam.id)"
        >
          <div class="exam-rank">
            <span class="rank-badge" :class="getRankClass(exam.rank)">第{{ index + 1 }}次</span>
          </div>
          <div class="exam-info">
            <div class="exam-name">{{ exam.name }}</div>
            <div class="exam-date">{{ exam.date }}</div>
          </div>
          <div class="exam-score">
            <div class="score-value" :class="getScoreClass(exam.score)">{{ exam.score }}</div>
            <div class="score-label">总分</div>
          </div>
          <div class="exam-ranking">
            <div class="ranking-value">{{ exam.rank }}名</div>
            <div class="ranking-label">年级排名</div>
          </div>
          <div class="exam-trend">
            <span :class="exam.trend >= 0 ? 'up' : 'down'">
              {{ exam.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(exam.trend) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析报告 -->
    <div class="analysis-report">
      <div class="report-title">📊 考试分析报告</div>
      <div class="report-content">
        <div class="report-section">
          <h4>总体表现</h4>
          <p>{{ overallAnalysis }}</p>
        </div>
        <div class="report-section">
          <h4>优势科目</h4>
          <ul>
            <li v-for="subject in strongSubjects" :key="subject">{{ subject }}</li>
          </ul>
        </div>
        <div class="report-section">
          <h4>薄弱科目</h4>
          <ul>
            <li v-for="subject in weakSubjects" :key="subject">{{ subject }}</li>
          </ul>
        </div>
        <div class="report-section">
          <h4>改进建议</h4>
          <ol>
            <li v-for="(suggestion, index) in improvementSuggestions" :key="index">{{ suggestion }}</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

interface ExamRecord {
  id: number
  name: string
  date: string
  score: number
  rank: number
  trend: number
  subjects: { name: string; score: number; full: number }[]
}

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const activeTab = ref('trend')
const selectedExam = ref<number | null>(null)

const examHistory = ref<ExamRecord[]>([
  {
    id: 1,
    name: '一模考试',
    date: '2026-03-15',
    score: 560,
    rank: 120,
    trend: 0,
    subjects: [
      { name: '语文', score: 98, full: 120 },
      { name: '数学', score: 105, full: 120 },
      { name: '英语', score: 102, full: 120 },
      { name: '物理', score: 85, full: 100 },
      { name: '化学', score: 80, full: 100 },
      { name: '生物', score: 90, full: 100 }
    ]
  },
  {
    id: 2,
    name: '二模考试',
    date: '2026-04-05',
    score: 575,
    rank: 115,
    trend: -5,
    subjects: [
      { name: '语文', score: 102, full: 120 },
      { name: '数学', score: 110, full: 120 },
      { name: '英语', score: 105, full: 120 },
      { name: '物理', score: 88, full: 100 },
      { name: '化学', score: 85, full: 100 },
      { name: '生物', score: 85, full: 100 }
    ]
  },
  {
    id: 3,
    name: '三模考试',
    date: '2026-04-25',
    score: 568,
    rank: 108,
    trend: -7,
    subjects: [
      { name: '语文', score: 105, full: 120 },
      { name: '数学', score: 108, full: 120 },
      { name: '英语', score: 108, full: 120 },
      { name: '物理', score: 82, full: 100 },
      { name: '化学', score: 80, full: 100 },
      { name: '生物', score: 85, full: 100 }
    ]
  },
  {
    id: 4,
    name: '四模考试',
    date: '2026-05-10',
    score: 582,
    rank: 95,
    trend: -13,
    subjects: [
      { name: '语文', score: 108, full: 120 },
      { name: '数学', score: 115, full: 120 },
      { name: '英语', score: 110, full: 120 },
      { name: '物理', score: 90, full: 100 },
      { name: '化学', score: 85, full: 100 },
      { name: '生物', score: 74, full: 100 }
    ]
  },
  {
    id: 5,
    name: '五模考试',
    date: '2026-05-20',
    score: 585,
    rank: 88,
    trend: -7,
    subjects: [
      { name: '语文', score: 108, full: 120 },
      { name: '数学', score: 118, full: 120 },
      { name: '英语', score: 112, full: 120 },
      { name: '物理', score: 98, full: 100 },
      { name: '化学', score: 88, full: 100 },
      { name: '生物', score: 69, full: 100 }
    ]
  }
])

const examCount = computed(() => examHistory.value.length)

const averageScore = computed(() => {
  const total = examHistory.value.reduce((sum, exam) => sum + exam.score, 0)
  return Math.round(total / examHistory.value.length)
})

const improvement = computed(() => {
  if (examHistory.value.length < 2) return 0
  const first = examHistory.value[0].score
  const last = examHistory.value[examHistory.value.length - 1].score
  return last - first
})

const achievementRate = computed(() => {
  const target = 600
  const latest = examHistory.value[examHistory.value.length - 1].score
  return Math.round((latest / target) * 100)
})

const overallAnalysis = computed(() => {
  const latest = examHistory.value[examHistory.value.length - 1]
  const avgRank = Math.round(examHistory.value.reduce((sum, e) => sum + e.rank, 0) / examHistory.value.length)
  
  if (latest.rank < avgRank) {
    return `最近一次考试表现优秀，总分${latest.score}分，排名${latest.rank}名，相比之前有明显进步。继续保持这个势头！`
  } else {
    return `最近一次考试总分${latest.score}分，排名${latest.rank}名。建议分析薄弱环节，针对性提升。`
  }
})

const strongSubjects = computed(() => {
  const latest = examHistory.value[examHistory.value.length - 1]
  return latest.subjects
    .filter(s => s.score / s.full >= 0.9)
    .map(s => s.name)
})

const weakSubjects = computed(() => {
  const latest = examHistory.value[examHistory.value.length - 1]
  return latest.subjects
    .filter(s => s.score / s.full < 0.75)
    .map(s => s.name)
})

const improvementSuggestions = computed(() => {
  const suggestions = []
  const latest = examHistory.value[examHistory.value.length - 1]
  
  if (weakSubjects.value.length > 0) {
    suggestions.push(`重点关注${weakSubjects.value.join('、')}科目的复习，这些科目提升空间较大。`)
  }
  
  const math = latest.subjects.find(s => s.name === '数学')
  if (math && math.score < 115) {
    suggestions.push('数学成绩接近目标，建议加强压轴题练习，冲击更高分数。')
  }
  
  const english = latest.subjects.find(s => s.name === '英语')
  if (english && english.score < 115) {
    suggestions.push('英语建议加强听力和写作训练，提升综合能力。')
  }
  
  suggestions.push('保持良好的学习节奏，合理安排作息时间。')
  
  return suggestions
})

const getRankClass = (rank: number) => {
  if (rank <= 100) return 'top'
  if (rank <= 150) return 'medium'
  return 'low'
}

const getScoreClass = (score: number) => {
  if (score >= 580) return 'high'
  if (score >= 550) return 'medium'
  return 'low'
}

const selectExam = (id: number) => {
  selectedExam.value = id
}

const initChart = () => {
  nextTick(() => {
    if (!chartRef.value) return
    
    if (chartInstance) {
      chartInstance.dispose()
    }

    chartInstance = echarts.init(chartRef.value)
    updateChart()

    window.addEventListener('resize', () => {
      chartInstance?.resize()
    })
  })
}

const updateChart = () => {
  if (!chartInstance) return

  const exams = examHistory.value
  const names = exams.map(e => e.name)
  const scores = exams.map(e => e.score)
  const ranks = exams.map(e => e.rank)

  let option: echarts.EChartsOption

  switch (activeTab.value) {
    case 'trend':
      option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e4e7ed',
          textStyle: { color: '#303133' },
          formatter: (params: unknown) => {
            const p = params as { seriesName: string; value: number; axisValue: string }[]
            const exam = exams.find(e => e.name === p[0].axisValue)
            if (!exam) return ''
            return `${exam.name}<br/>总分: ${exam.score}分<br/>排名: ${exam.rank}名`
          }
        },
        legend: {
          data: ['总分', '目标分数'],
          textStyle: { color: '#909399' },
          top: 10
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: names,
          axisLabel: { color: '#606266', fontSize: 12 },
          axisLine: { lineStyle: { color: '#e4e7ed' } }
        },
        yAxis: {
          type: 'value',
          name: '分数',
          min: 500,
          max: 650,
          nameTextStyle: { color: '#909399' },
          axisLabel: { color: '#909399' },
          axisLine: { lineStyle: { color: '#e4e7ed' } },
          splitLine: { lineStyle: { color: '#f2f6fc' } }
        },
        series: [
          {
            name: '总分',
            type: 'line',
            data: scores,
            smooth: true,
            lineStyle: { color: '#667eea', width: 3 },
            itemStyle: { color: '#667eea' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                { offset: 1, color: 'rgba(102, 126, 234, 0)' }
              ])
            },
            symbol: 'circle',
            symbolSize: 10
          },
          {
            name: '目标分数',
            type: 'line',
            data: Array(exams.length).fill(600),
            lineStyle: { color: '#F56C6C', width: 2, type: 'dashed' },
            symbol: 'none'
          }
        ]
      }
      break

    case 'subjects':
      const latestExam = exams[exams.length - 1]
      const subjectNames = latestExam.subjects.map(s => s.name)
      const subjectScores = latestExam.subjects.map(s => s.score)
      const subjectTargets = latestExam.subjects.map(s => Math.round(s.full * 0.95))

      option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e4e7ed',
          textStyle: { color: '#303133' }
        },
        legend: {
          data: ['当前成绩', '目标成绩'],
          textStyle: { color: '#909399' },
          top: 10
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: subjectNames,
          axisLabel: { color: '#606266' },
          axisLine: { lineStyle: { color: '#e4e7ed' } }
        },
        yAxis: {
          type: 'value',
          name: '分数',
          min: 0,
          max: 130,
          nameTextStyle: { color: '#909399' },
          axisLabel: { color: '#909399' },
          axisLine: { lineStyle: { color: '#e4e7ed' } },
          splitLine: { lineStyle: { color: '#f2f6fc' } }
        },
        series: [
          {
            name: '当前成绩',
            type: 'bar',
            data: subjectScores,
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
            data: subjectTargets,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#10b981' },
                { offset: 1, color: '#34d399' }
              ]),
              borderRadius: [4, 4, 0, 0],
              opacity: 0.6
            }
          }
        ]
      }
      break

    case 'ranking':
      option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e4e7ed',
          textStyle: { color: '#303133' },
          formatter: (params: unknown) => {
            const p = params as { seriesName: string; value: number; axisValue: string }[]
            const exam = exams.find(e => e.name === p[0].axisValue)
            if (!exam) return ''
            return `${exam.name}<br/>排名: ${exam.rank}名<br/>较上次: ${exam.trend >= 0 ? '↑' : '↓'}${Math.abs(exam.trend)}`
          }
        },
        legend: {
          data: ['年级排名'],
          textStyle: { color: '#909399' },
          top: 10
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: names,
          axisLabel: { color: '#606266', fontSize: 12 },
          axisLine: { lineStyle: { color: '#e4e7ed' } }
        },
        yAxis: {
          type: 'value',
          name: '排名',
          min: 0,
          max: 150,
          inverse: true,
          nameTextStyle: { color: '#909399' },
          axisLabel: { color: '#909399' },
          axisLine: { lineStyle: { color: '#e4e7ed' } },
          splitLine: { lineStyle: { color: '#f2f6fc' } }
        },
        series: [
          {
            name: '年级排名',
            type: 'line',
            data: ranks,
            smooth: true,
            lineStyle: { color: '#10b981', width: 3 },
            itemStyle: { color: '#10b981' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
                { offset: 1, color: 'rgba(16, 185, 129, 0)' }
              ])
            },
            symbol: 'circle',
            symbolSize: 10
          }
        ]
      }
      break

    default:
      option = {}
  }

  chartInstance.setOption(option)
}

watch(activeTab, () => {
  updateChart()
})

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.exam-analysis-chart {
  padding: 20px;
}

.exam-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.overview-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.overview-info {
  flex: 1;
}

.overview-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.overview-value.positive {
  color: #10b981;
}

.overview-value.negative {
  color: #ef4444;
}

.overview-label {
  font-size: 12px;
  color: #6b7280;
}

.chart-tabs {
  margin-bottom: 20px;
}

.chart {
  height: 350px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.exam-list {
  margin-bottom: 24px;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.list-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exam-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.exam-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.exam-item.active {
  border-left: 4px solid #667eea;
}

.exam-rank {
  flex-shrink: 0;
}

.rank-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.rank-badge.top {
  background: #d1fae5;
  color: #059669;
}

.rank-badge.medium {
  background: #fef3c7;
  color: #d97706;
}

.rank-badge.low {
  background: #fee2e2;
  color: #dc2626;
}

.exam-info {
  flex: 1;
}

.exam-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.exam-date {
  font-size: 13px;
  color: #6b7280;
}

.exam-score {
  text-align: center;
  min-width: 70px;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
}

.score-value.high {
  color: #10b981;
}

.score-value.medium {
  color: #3b82f6;
}

.score-value.low {
  color: #f59e0b;
}

.score-label {
  font-size: 12px;
  color: #6b7280;
}

.exam-ranking {
  text-align: center;
  min-width: 80px;
}

.ranking-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.ranking-label {
  font-size: 12px;
  color: #6b7280;
}

.exam-trend {
  font-size: 16px;
  font-weight: 600;
}

.exam-trend .up {
  color: #10b981;
}

.exam-trend .down {
  color: #ef4444;
}

.analysis-report {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.report-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.report-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.report-section {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
}

.report-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.report-section p {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

.report-section ul,
.report-section ol {
  margin: 0;
  padding-left: 20px;
}

.report-section li {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.8;
}

@media (max-width: 768px) {
  .exam-analysis-chart {
    padding: 12px;
  }

  .exam-overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .overview-card {
    padding: 12px;
  }

  .overview-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .overview-value {
    font-size: 20px;
  }

  .chart {
    height: 280px;
  }

  .exam-item {
    flex-wrap: wrap;
    gap: 12px;
  }

  .exam-info {
    flex: 1;
  }

  .exam-score,
  .exam-ranking {
    min-width: 60px;
  }

  .score-value,
  .ranking-value {
    font-size: 16px;
  }

  .report-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .report-section {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .exam-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .overview-card {
    padding: 10px;
  }

  .overview-icon {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .overview-value {
    font-size: 18px;
  }

  .chart {
    height: 240px;
  }

  .exam-item {
    padding: 12px;
    gap: 8px;
  }

  .exam-name {
    font-size: 14px;
  }

  .exam-date {
    font-size: 12px;
  }

  .score-value {
    font-size: 16px;
  }

  .ranking-value {
    font-size: 14px;
  }

  .exam-trend {
    font-size: 14px;
  }

  .report-title,
  .list-title {
    font-size: 15px;
  }

  .report-section h4 {
    font-size: 13px;
  }

  .report-section p,
  .report-section li {
    font-size: 12px;
  }
}

@media (max-width: 360px) {
  .exam-overview {
    grid-template-columns: 1fr;
  }

  .chart {
    height: 200px;
  }
}
</style>