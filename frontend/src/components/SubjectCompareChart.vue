<template>
  <div class="subject-compare-chart">
    <!-- 学科选择器 -->
    <div class="subject-selector">
      <el-tag 
        v-for="subject in subjects" 
        :key="subject.name"
        :class="{ active: selectedSubjects.includes(subject.name) }"
        @click="toggleSubject(subject.name)"
      >
        {{ subject.name }}
      </el-tag>
      <el-button size="small" @click="selectAll">全选</el-button>
      <el-button size="small" @click="clearSelection">清空</el-button>
    </div>

    <!-- 图表容器 -->
    <div ref="chartRef" class="chart"></div>

    <!-- 数据详情 -->
    <div class="data-details">
      <div class="detail-title">📊 学科详情</div>
      <div class="detail-grid">
        <div 
          v-for="subject in filteredSubjects" 
          :key="subject.name" 
          class="detail-card"
        >
          <div class="detail-header">
            <span class="detail-icon">{{ subject.icon }}</span>
            <span class="detail-name">{{ subject.name }}</span>
          </div>
          <div class="detail-body">
            <div class="detail-row">
              <span class="detail-label">当前成绩</span>
              <span class="detail-value score">{{ subject.current }}/{{ subject.full }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">目标成绩</span>
              <span class="detail-value target">{{ subject.target }}/{{ subject.full }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">差距</span>
              <span class="detail-value gap" :class="subject.gap >= 0 ? 'positive' : 'negative'">
                {{ subject.gap >= 0 ? '+' : '' }}{{ subject.gap }}
              </span>
            </div>
            <div class="detail-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill current" 
                  :style="{ width: (subject.current / subject.full * 100) + '%' }"
                  :title="`当前: ${subject.current}/${subject.full}`"
                ></div>
                <div 
                  class="progress-fill target" 
                  :style="{ width: (subject.target / subject.full * 100) + '%' }"
                  :title="`目标: ${subject.target}/${subject.full}`"
                ></div>
              </div>
              <div class="progress-legend">
                <span class="legend-item"><span class="legend-dot current"></span> 当前</span>
                <span class="legend-item"><span class="legend-dot target"></span> 目标</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 学习建议 -->
    <div class="suggestions">
      <div class="suggestion-title">💡 学习建议</div>
      <div class="suggestion-list">
        <div 
          v-for="(suggestion, index) in suggestions" 
          :key="index" 
          class="suggestion-item"
        >
          <span class="suggestion-number">{{ index + 1 }}</span>
          <div class="suggestion-content">
            <div class="suggestion-subject">{{ suggestion.subject }}</div>
            <div class="suggestion-text">{{ suggestion.text }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

interface Subject {
  name: string
  icon: string
  current: number
  target: number
  full: number
  rank: number
  gap: number
}

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const subjects = ref<Subject[]>([
  { name: '语文', icon: '📖', current: 108, target: 115, full: 120, rank: 85, gap: 7 },
  { name: '数学', icon: '🧮', current: 118, target: 120, full: 120, rank: 95, gap: 2 },
  { name: '英语', icon: '🔤', current: 112, target: 118, full: 120, rank: 90, gap: 6 },
  { name: '物理', icon: '⚡', current: 98, target: 100, full: 100, rank: 88, gap: 2 },
  { name: '化学', icon: '🧪', current: 88, target: 95, full: 100, rank: 75, gap: 7 },
  { name: '生物', icon: '🧬', current: 85, target: 92, full: 100, rank: 80, gap: 7 }
])

const selectedSubjects = ref(['语文', '数学', '英语', '物理', '化学', '生物'])

const filteredSubjects = computed(() => {
  return subjects.value.filter(s => selectedSubjects.value.includes(s.name))
})

const suggestions = computed(() => {
  const sorted = [...subjects.value].sort((a, b) => b.gap - a.gap)
  return sorted.slice(0, 3).map(s => ({
    subject: s.name,
    text: getSuggestion(s.name, s.gap)
  }))
})

const getSuggestion = (subject: string, gap: number): string => {
  const suggestions: Record<string, string> = {
    '语文': gap > 5 
      ? '建议加强阅读理解和写作训练，每天坚持阅读课外文章积累素材。'
      : '成绩良好，建议保持，可适当增加课外阅读提升综合素养。',
    '数学': gap > 5
      ? '建议整理错题本，重点突破薄弱知识点，加强综合题练习。'
      : '成绩优秀，建议挑战更高难度题目，保持领先优势。',
    '英语': gap > 5
      ? '建议每天坚持听力训练，积累词汇量，加强语法学习。'
      : '成绩良好，建议多进行英语阅读和写作练习。',
    '物理': gap > 5
      ? '建议系统复习物理公式，加强实验题和计算题练习。'
      : '成绩优秀，建议深入理解物理概念，提升分析能力。',
    '化学': gap > 5
      ? '建议重点复习化学反应方程式，加强实验操作理解。'
      : '成绩良好，建议多做综合题，提高知识整合能力。',
    '生物': gap > 5
      ? '建议加强生物学概念记忆，多做图表分析题。'
      : '成绩良好，建议关注生物实验和科学探究能力提升。'
  }
  return suggestions[subject] || '继续保持，稳步提升！'
}

const toggleSubject = (name: string) => {
  const index = selectedSubjects.value.indexOf(name)
  if (index > -1) {
    if (selectedSubjects.value.length > 1) {
      selectedSubjects.value.splice(index, 1)
    }
  } else {
    selectedSubjects.value.push(name)
  }
}

const selectAll = () => {
  selectedSubjects.value = subjects.value.map(s => s.name)
}

const clearSelection = () => {
  if (selectedSubjects.value.length > 1) {
    selectedSubjects.value = [subjects.value[0].name]
  }
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
  if (!chartInstance || filteredSubjects.value.length === 0) return

  const data = filteredSubjects.value
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133' },
      axisPointer: { type: 'cross', crossStyle: { color: '#999' } },
      formatter: (params: unknown) => {
        const p = params as { seriesName: string; value: number; axisValue: string; marker: string }[]
        const subject = data.find(s => s.name === p[0].axisValue)
        if (!subject) return ''
        let result = `<div style="font-weight: bold; margin-bottom: 8px;">${subject.icon} ${subject.name}</div>`
        p.forEach(item => {
          result += `${item.marker} ${item.seriesName}: ${item.value}/${subject.full}<br/>`
        })
        result += `<br/>排名百分位: ${subject.rank}%`
        return result
      }
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
      data: data.map(s => s.name),
      axisPointer: { type: 'shadow' },
      axisLabel: { 
        color: '#606266', 
        fontSize: 14,
        fontWeight: 500
      },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '分数',
      min: 0,
      max: 130,
      interval: 30,
      nameTextStyle: { color: '#909399', fontSize: 13 },
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      splitLine: { lineStyle: { color: '#f2f6fc', type: 'dashed' } }
    },
    series: [
      {
        name: '当前成绩',
        type: 'bar',
        barWidth: '35%',
        data: data.map(s => s.current),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        emphasis: {
          itemStyle: {
            shadowColor: 'rgba(102, 126, 234, 0.5)',
            shadowBlur: 10
          }
        },
        label: {
          show: true,
          position: 'top',
          color: '#667eea',
          fontWeight: 'bold',
          fontSize: 12,
          formatter: '{c}'
        }
      },
      {
        name: '目标成绩',
        type: 'bar',
        barWidth: '35%',
        data: data.map(s => s.target),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#34d399' }
          ]),
          borderRadius: [6, 6, 0, 0],
          opacity: 0.7
        },
        emphasis: {
          itemStyle: {
            shadowColor: 'rgba(16, 185, 129, 0.5)',
            shadowBlur: 10
          }
        },
        label: {
          show: true,
          position: 'top',
          color: '#10b981',
          fontWeight: 'bold',
          fontSize: 12,
          formatter: '{c}'
        }
      }
    ],
    animationDuration: 1000,
    animationEasing: 'cubicOut'
  }

  chartInstance.setOption(option)
}

watch(selectedSubjects, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.subject-compare-chart {
  padding: 20px;
}

.subject-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
  align-items: center;
}

.subject-selector el-tag {
  padding: 6px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
}

.subject-selector el-tag:hover {
  transform: translateY(-2px);
}

.subject-selector el-tag.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-color: transparent;
}

.subject-selector el-button {
  margin-left: auto;
}

.chart {
  height: 350px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.data-details {
  margin-bottom: 24px;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.detail-icon {
  font-size: 20px;
}

.detail-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 13px;
  color: #6b7280;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
}

.detail-value.score {
  color: #667eea;
}

.detail-value.target {
  color: #10b981;
}

.detail-value.gap.positive {
  color: #10b981;
}

.detail-value.gap.negative {
  color: #ef4444;
}

.detail-progress {
  margin-top: 8px;
}

.progress-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  position: relative;
  overflow: visible;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  position: absolute;
  top: 0;
  left: 0;
  transition: width 0.5s ease;
}

.progress-fill.current {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  z-index: 2;
}

.progress-fill.target {
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.3) 0%, rgba(52, 211, 153, 0.3) 100%);
  z-index: 1;
}

.progress-legend {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.current {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.legend-dot.target {
  background: #10b981;
  opacity: 0.7;
}

.suggestions {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.suggestion-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.suggestion-number {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
}

.suggestion-subject {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.suggestion-text {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .subject-compare-chart {
    padding: 12px;
  }

  .subject-selector {
    flex-wrap: wrap;
    gap: 6px;
  }

  .subject-selector el-tag {
    padding: 5px 12px;
    font-size: 12px;
  }

  .subject-selector el-button {
    margin-left: 0;
    margin-top: 8px;
  }

  .chart {
    height: 280px;
  }

  .detail-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .detail-card {
    padding: 12px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .detail-name {
    font-size: 14px;
  }

  .suggestions {
    padding: 16px;
  }

  .suggestion-item {
    padding: 10px;
    gap: 10px;
  }

  .suggestion-number {
    width: 20px;
    height: 20px;
    font-size: 12px;
  }

  .suggestion-text {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .subject-selector {
    gap: 4px;
  }

  .subject-selector el-tag {
    padding: 4px 10px;
    font-size: 11px;
  }

  .chart {
    height: 240px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .detail-card {
    padding: 10px;
  }

  .detail-icon {
    font-size: 16px;
  }

  .detail-name {
    font-size: 13px;
  }

  .detail-label {
    font-size: 12px;
  }

  .detail-value {
    font-size: 13px;
  }

  .suggestions {
    padding: 12px;
  }

  .suggestion-title {
    font-size: 15px;
  }

  .suggestion-item {
    padding: 8px;
    gap: 8px;
  }

  .suggestion-number {
    width: 18px;
    height: 18px;
    font-size: 11px;
  }

  .suggestion-subject {
    font-size: 13px;
  }

  .suggestion-text {
    font-size: 11px;
  }
}

@media (max-width: 360px) {
  .chart {
    height: 200px;
  }

  .progress-legend {
    flex-direction: column;
    gap: 4px;
  }

  .legend-item {
    font-size: 11px;
  }
}
</style>