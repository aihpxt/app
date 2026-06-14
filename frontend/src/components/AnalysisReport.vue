<template>
  <div class="analysis-report">
    <!-- 报告头部 -->
    <div class="report-header">
      <div class="header-info">
        <h1>📊 个性化学习分析报告</h1>
        <p>生成时间：{{ currentDate }}</p>
      </div>
      <div class="header-actions">
        <el-button size="small" @click="refreshReport">
          <el-icon><Refresh /></el-icon>
          刷新报告
        </el-button>
        <el-button size="small" type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>
    
    <!-- 总体概览 -->
    <div class="overview-section">
      <div class="section-title">
        <el-icon><PieChart /></el-icon>
        <span>学习概览</span>
      </div>
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon blue">📚</div>
          <div class="card-content">
            <div class="card-value">{{ overview.totalHours }}</div>
            <div class="card-label">累计学习时长(小时)</div>
          </div>
          <div class="card-trend" :class="overview.hoursTrend > 0 ? 'up' : 'down'">
            {{ overview.hoursTrend > 0 ? '↑' : '↓' }} {{ Math.abs(overview.hoursTrend) }}%
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon green">✅</div>
          <div class="card-content">
            <div class="card-value">{{ overview.completedTasks }}</div>
            <div class="card-label">已完成任务数</div>
          </div>
          <div class="card-trend" :class="overview.tasksTrend > 0 ? 'up' : 'down'">
            {{ overview.tasksTrend > 0 ? '↑' : '↓' }} {{ Math.abs(overview.tasksTrend) }}%
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon orange">🔥</div>
          <div class="card-content">
            <div class="card-value">{{ overview.streakDays }}</div>
            <div class="card-label">连续学习天数</div>
          </div>
          <div class="card-trend" :class="overview.streakTrend > 0 ? 'up' : 'down'">
            {{ overview.streakTrend > 0 ? '↑' : '↓' }} {{ Math.abs(overview.streakTrend) }}%
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon purple">🎯</div>
          <div class="card-content">
            <div class="card-value">{{ overview.goalProgress }}%</div>
            <div class="card-label">目标完成进度</div>
          </div>
          <div class="card-trend" :class="overview.goalTrend > 0 ? 'up' : 'down'">
            {{ overview.goalTrend > 0 ? '↑' : '↓' }} {{ Math.abs(overview.goalTrend) }}%
          </div>
        </div>
      </div>
    </div>
    
    <!-- 学科分析 -->
    <div class="subject-section">
      <div class="section-title">
        <el-icon><DataLine /></el-icon>
        <span>学科成绩分析</span>
      </div>
      <div class="subject-grid">
        <div class="subject-chart">
          <div class="chart-header">
            <h3>各科成绩对比</h3>
            <el-select v-model="subjectPeriod" class="period-select">
              <el-option label="最近一次" value="latest" />
              <el-option label="近3次" value="recent" />
              <el-option label="全部" value="all" />
            </el-select>
          </div>
          <div class="bar-chart-container">
            <div 
              v-for="subject in subjectData" 
              :key="subject.name"
              class="bar-item"
            >
              <div class="bar-label">{{ subject.name }}</div>
              <div class="bar-track">
                <div 
                  class="bar-fill" 
                  :style="{ width: subject.score + '%', background: subject.color }"
                ></div>
              </div>
              <div class="bar-score">{{ subject.score }}分</div>
            </div>
          </div>
        </div>
        
        <div class="subject-stats">
          <div class="stat-card">
            <div class="stat-title">📈 优势科目</div>
            <div class="stat-content">
              <div v-for="subject in strongSubjects" :key="subject.name" class="subject-tag">
                <span class="tag-color" :style="{ background: subject.color }"></span>
                {{ subject.name }} - {{ subject.score }}分
              </div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-title">⚠️ 需要加强</div>
            <div class="stat-content">
              <div v-for="subject in weakSubjects" :key="subject.name" class="subject-tag">
                <span class="tag-color" :style="{ background: subject.color }"></span>
                {{ subject.name }} - {{ subject.score }}分
              </div>
            </div>
          </div>
          <div class="stat-card suggestion-card">
            <div class="stat-title">💡 学习建议</div>
            <div class="suggestion-list">
              <div v-for="(suggestion, index) in suggestions" :key="index" class="suggestion-item">
                <span class="suggestion-num">{{ index + 1 }}</span>
                <span>{{ suggestion }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 学习时间分析 -->
    <div class="time-section">
      <div class="section-title">
        <el-icon><Clock /></el-icon>
        <span>学习时间分布</span>
      </div>
      <div class="time-grid">
        <div class="time-chart">
          <h3>每日学习时段分布</h3>
          <div class="time-bars">
            <div 
              v-for="(hour, index) in timeDistribution" 
              :key="index"
              class="time-bar-wrapper"
            >
              <div class="time-bar-label">{{ hour.label }}</div>
              <div class="time-bar-container">
                <div 
                  class="time-bar-fill" 
                  :style="{ height: hour.value + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        <div class="time-summary">
          <div class="summary-card">
            <div class="summary-value">{{ mostActiveTime }}</div>
            <div class="summary-label">最活跃时段</div>
          </div>
          <div class="summary-card">
            <div class="summary-value">{{ dailyAverage }}小时</div>
            <div class="summary-label">日均学习时长</div>
          </div>
          <div class="summary-card">
            <div class="summary-value">{{ weeklyDays }}天</div>
            <div class="summary-label">每周学习天数</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 考试分析 -->
    <div class="exam-section">
      <div class="section-title">
        <el-icon><Document /></el-icon>
        <span>模拟考试分析</span>
      </div>
      <div class="exam-content">
        <div class="exam-chart">
          <h3>成绩趋势</h3>
          <div class="line-chart">
            <svg viewBox="0 0 600 200" class="line-svg">
              <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.3" />
                  <stop offset="100%" style="stop-color:#764ba2;stop-opacity:0.3" />
                </linearGradient>
              </defs>
              <path :d="areaPath" fill="url(#lineGradient)" />
              <path :d="linePath" fill="none" stroke="url(#lineGradient)" stroke-width="3" />
              <circle 
                v-for="(point, index) in chartPoints" 
                :key="index"
                :cx="point.x" 
                :cy="point.y" 
                r="6" 
                fill="#667eea"
                class="chart-point"
              />
            </svg>
            <div class="chart-labels">
              <span v-for="(label, index) in examLabels" :key="index">{{ label }}</span>
            </div>
          </div>
        </div>
        
        <div class="exam-details">
          <div class="detail-item">
            <span class="detail-label">最高分</span>
            <span class="detail-value high">{{ examStats.highest }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">最低分</span>
            <span class="detail-value low">{{ examStats.lowest }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">平均分</span>
            <span class="detail-value">{{ examStats.average }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">进步幅度</span>
            <span class="detail-value" :class="examStats.improvement > 0 ? 'high' : 'low'">
              {{ examStats.improvement > 0 ? '+' : '' }}{{ examStats.improvement }}分
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错题分析 -->
    <div class="mistakes-section">
      <div class="section-title">
        <el-icon><CircleClose /></el-icon>
        <span>错题分析</span>
      </div>
      <div class="mistakes-content">
        <div class="mistakes-stats">
          <div class="mistake-stat-item">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <div class="stat-value">{{ mistakeStats.total }}</div>
              <div class="stat-label">总错题数</div>
            </div>
          </div>
          <div class="mistake-stat-item">
            <div class="stat-icon">🔄</div>
            <div class="stat-info">
              <div class="stat-value">{{ mistakeStats.reviewed }}</div>
              <div class="stat-label">已复习</div>
            </div>
          </div>
          <div class="mistake-stat-item">
            <div class="stat-icon">📚</div>
            <div class="stat-info">
              <div class="stat-value">{{ mistakeStats.toReview }}</div>
              <div class="stat-label">待复习</div>
            </div>
          </div>
        </div>
        
        <div class="mistakes-chart">
          <h4>错题学科分布</h4>
          <div class="donut-chart">
            <svg viewBox="0 0 200 200" class="donut-svg">
              <circle 
                v-for="(segment, index) in mistakeSegments" 
                :key="index"
                cx="100" 
                cy="100" 
                r="70"
                fill="none"
                :stroke="segment.color"
                stroke-width="30"
                :stroke-dasharray="segment.dashArray"
                :stroke-dashoffset="segment.offset"
                :transform="segment.transform"
                class="donut-segment"
              />
            </svg>
            <div class="donut-center">
              <div class="center-value">{{ mistakeStats.total }}</div>
              <div class="center-label">错题</div>
            </div>
          </div>
          <div class="donut-legend">
            <div v-for="item in mistakeLegend" :key="item.name" class="legend-item">
              <span class="legend-color" :style="{ background: item.color }"></span>
              <span class="legend-name">{{ item.name }}</span>
              <span class="legend-value">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 学习建议 -->
    <div class="suggestions-section">
      <div class="section-title">
        <el-icon><Star /></el-icon>
        <span>综合建议</span>
      </div>
      <div class="suggestions-content">
        <div class="suggestion-card" v-for="(item, index) in comprehensiveSuggestions" :key="index">
          <div class="suggestion-icon">{{ item.icon }}</div>
          <div class="suggestion-body">
            <div class="suggestion-title">{{ item.title }}</div>
            <div class="suggestion-text">{{ item.content }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, Download, PieChart, DataLine, Clock, 
  Document, CircleClose, Star 
} from '@element-plus/icons-vue'

interface SubjectData {
  name: string
  score: number
  color: string
}

interface ExamPoint {
  x: number
  y: number
}

const currentDate = ref('')
const subjectPeriod = ref('latest')

const overview = ref({
  totalHours: 156,
  hoursTrend: 12,
  completedTasks: 89,
  tasksTrend: 8,
  streakDays: 15,
  streakTrend: 20,
  goalProgress: 73,
  goalTrend: 5
})

const subjectData = ref<SubjectData[]>([
  { name: '语文', score: 85, color: '#ef4444' },
  { name: '数学', score: 92, color: '#3b82f6' },
  { name: '英语', score: 88, color: '#10b981' },
  { name: '物理', score: 86, color: '#f59e0b' },
  { name: '化学', score: 80, color: '#8b5cf6' },
  { name: '生物', score: 78, color: '#ec4899' },
  { name: '历史', score: 88, color: '#06b6d4' },
  { name: '地理', score: 84, color: '#14b8a6' },
  { name: '政治', score: 82, color: '#a855f7' }
])

const timeDistribution = ref([
  { label: '6点', value: 5 },
  { label: '8点', value: 35 },
  { label: '10点', value: 45 },
  { label: '12点', value: 20 },
  { label: '14点', value: 50 },
  { label: '16点', value: 65 },
  { label: '18点', value: 30 },
  { label: '20点', value: 80 },
  { label: '22点', value: 40 }
])

const examScores = ref([485, 502, 498, 520, 515, 538])
const examLabels = ref(['月考1', '月考2', '期中', '月考3', '月考4', '期末'])

const mistakeStats = ref({
  total: 156,
  reviewed: 98,
  toReview: 58
})

const mistakeSubjects = ref([
  { name: '数学', count: 45, color: '#3b82f6' },
  { name: '物理', count: 32, color: '#f59e0b' },
  { name: '英语', count: 28, color: '#10b981' },
  { name: '化学', count: 25, color: '#8b5cf6' },
  { name: '语文', count: 26, color: '#ef4444' }
])

const mostActiveTime = computed(() => {
  const max = timeDistribution.value.reduce((prev, curr) => 
    prev.value > curr.value ? prev : curr
  )
  return max.label
})

const dailyAverage = computed(() => {
  return (overview.value.totalHours / 30).toFixed(1)
})

const weeklyDays = computed(() => 6)

const strongSubjects = computed(() => {
  return [...subjectData.value].sort((a, b) => b.score - a.score).slice(0, 3)
})

const weakSubjects = computed(() => {
  return [...subjectData.value].sort((a, b) => a.score - b.score).slice(0, 3)
})

const suggestions = computed(() => {
  const weak = weakSubjects.value
  const suggestions = []
  if (weak.length > 0) {
    suggestions.push(`重点加强${weak[0].name}学科的学习，当前成绩${weak[0].score}分`)
    if (weak.length > 1) {
      suggestions.push(`其次关注${weak[1].name}学科，建议每天多花30分钟练习`)
    }
  }
  suggestions.push('保持良好的学习习惯，继续保持15天的连续学习记录')
  suggestions.push('错题复习进度良好，继续坚持每天复习错题')
  return suggestions
})

const examStats = computed(() => ({
  highest: Math.max(...examScores.value),
  lowest: Math.min(...examScores.value),
  average: Math.round(examScores.value.reduce((a, b) => a + b, 0) / examScores.value.length),
  improvement: examScores.value[examScores.value.length - 1] - examScores.value[0]
}))

const chartPoints = computed((): ExamPoint[] => {
  const maxScore = 600
  const width = 600
  const height = 200
  const padding = 40
  
  return examScores.value.map((score, index) => ({
    x: padding + (index * (width - 2 * padding)) / (examScores.value.length - 1),
    y: height - padding - (score / maxScore) * (height - 2 * padding)
  }))
})

const linePath = computed(() => {
  if (chartPoints.value.length === 0) return ''
  return chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

const areaPath = computed(() => {
  if (chartPoints.value.length === 0) return ''
  const points = chartPoints.value
  const lastX = points[points.length - 1].x
  const firstX = points[0].x
  const height = 200
  const padding = 40
  return `${linePath.value} L ${lastX} ${height - padding} L ${firstX} ${height - padding} Z`
})

const mistakeSegments = computed(() => {
  const total = mistakeSubjects.value.reduce((sum, s) => sum + s.count, 0)
  let offset = 0
  const circumference = 2 * Math.PI * 70
  
  return mistakeSubjects.value.map((subject, _index) => {
    const percentage = subject.count / total
    const dashArray = `${percentage * circumference} ${circumference}`
    const currentOffset = -offset
    offset += percentage * circumference
    
    return {
      color: subject.color,
      dashArray,
      offset: currentOffset,
      transform: `rotate(-90 100 100)`
    }
  })
})

const mistakeLegend = computed(() => mistakeSubjects.value)

const comprehensiveSuggestions = ref([
  {
    icon: '🎯',
    title: '目标设定',
    content: '根据您的学习情况，建议设定明确的学习目标。数学和物理是您的优势学科，可以挑战更高难度的题目；英语和化学需要加强练习。'
  },
  {
    icon: '⏰',
    title: '时间管理',
    content: '您的学习高峰期在晚上8点左右，建议在这个时间段安排重点科目学习。注意劳逸结合，保证充足睡眠。'
  },
  {
    icon: '📚',
    title: '错题复习',
    content: '错题复习进度良好（62.8%已复习），建议继续坚持每天复习10-15道错题，巩固薄弱知识点。'
  },
  {
    icon: '📈',
    title: '成绩趋势',
    content: '近期成绩呈上升趋势，相比第一次月考进步了53分！继续保持这个势头，相信您在中考中一定能取得好成绩！'
  }
])

const refreshReport = () => {
  ElMessage.info('报告已刷新')
}

const exportReport = () => {
  ElMessage.success('报告导出成功')
}

onMounted(() => {
  const now = new Date()
  currentDate.value = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`
})
</script>

<style scoped>
.analysis-report {
  padding: 24px;
  background: #0f0f23;
  min-height: 100vh;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-info h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-info p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.overview-card {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.3s;
}

.overview-card:hover {
  transform: translateY(-4px);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-icon.blue {
  background: rgba(59, 130, 246, 0.2);
}

.card-icon.green {
  background: rgba(16, 185, 129, 0.2);
}

.card-icon.orange {
  background: rgba(245, 158, 11, 0.2);
}

.card-icon.purple {
  background: rgba(139, 92, 246, 0.2);
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.card-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.card-trend {
  font-size: 14px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 20px;
}

.card-trend.up {
  color: #10b981;
  background: rgba(16, 185, 129, 0.15);
}

.card-trend.down {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.15);
}

.subject-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}

.subject-chart {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.period-select {
  width: 120px;
}

.bar-chart-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 60px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.bar-track {
  flex: 1;
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
}

.bar-score {
  width: 60px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  text-align: right;
}

.subject-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 20px;
}

.stat-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 14px;
}

.subject-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.subject-tag:last-child {
  margin-bottom: 0;
}

.tag-color {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.suggestion-card {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.suggestion-item {
  display: flex;
  gap: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.suggestion-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #f59e0b;
  flex-shrink: 0;
}

.time-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}

.time-chart {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 24px;
}

.time-chart h3 {
  margin: 0 0 24px 0;
  font-size: 16px;
  font-weight: 600;
}

.time-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 180px;
}

.time-bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.time-bar-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.time-bar-container {
  width: 32px;
  height: 140px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.time-bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  transition: height 0.5s ease;
}

.time-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-card {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.summary-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.exam-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}

.exam-chart {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 24px;
}

.exam-chart h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
}

.line-chart {
  position: relative;
}

.line-svg {
  width: 100%;
  height: 200px;
}

.chart-point {
  cursor: pointer;
  transition: r 0.2s;
}

.chart-point:hover {
  r: 8;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 40px;
  margin-top: 12px;
}

.chart-labels span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.exam-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}

.detail-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.detail-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.detail-value.high {
  color: #10b981;
}

.detail-value.low {
  color: #ef4444;
}

.mistakes-content {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 20px;
}

.mistakes-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mistake-stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}

.stat-icon {
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.mistakes-chart {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 40px;
}

.mistakes-chart h4 {
  position: absolute;
  top: 24px;
  left: 24px;
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.donut-chart {
  position: relative;
  width: 200px;
  height: 200px;
}

.donut-svg {
  width: 100%;
  height: 100%;
}

.donut-segment {
  transition: opacity 0.3s;
}

.donut-segment:hover {
  opacity: 0.8;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.center-value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
}

.center-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.donut-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-name {
  flex: 1;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.legend-value {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.suggestions-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.suggestion-card {
  display: flex;
  gap: 16px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.suggestion-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.suggestion-body {
  flex: 1;
}

.suggestion-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.suggestion-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .subject-grid, .time-grid, .exam-content {
    grid-template-columns: 1fr;
  }
  
  .suggestions-content {
    grid-template-columns: 1fr;
  }
  
  .mistakes-content {
    grid-template-columns: 1fr;
  }
  
  .mistakes-chart {
    flex-direction: column;
  }
}
</style>