<template>
  <div class="progress-tracker">
    <div class="progress-section">
      <div class="section-header">
        <h3 class="section-title">📈 学习进度追踪</h3>
        <div class="time-filter">
          <el-select v-model="timeRange" @change="loadProgress">
            <el-option label="今日" value="today" />
            <el-option label="本周" value="week" />
            <el-option label="本月" value="month" />
          </el-select>
        </div>
      </div>
      
      <!-- 统计概览 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon bg-blue">📚</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalHours.toFixed(1) }}</div>
            <div class="stat-label">学习时长 (小时)</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-green">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completedTasks }}</div>
            <div class="stat-label">完成任务数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-purple">🎯</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.goalProgress }}%</div>
            <div class="stat-label">目标完成度</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-orange">🔥</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.streak }}</div>
            <div class="stat-label">连续学习天数</div>
          </div>
        </div>
      </div>
      
      <!-- 学习时长图表 -->
      <div class="chart-section">
        <h4 class="chart-title">学习时长趋势</h4>
        <div ref="timeChartRef" class="chart-container"></div>
      </div>
      
      <!-- 学科分布 -->
      <div class="chart-section">
        <h4 class="chart-title">学科学习分布</h4>
        <div ref="subjectChartRef" class="chart-container"></div>
      </div>
      
      <!-- 任务列表 -->
      <div class="task-section">
        <div class="task-header">
          <h4 class="task-title">📋 学习任务</h4>
          <el-button size="small" type="primary" @click="showTaskModal = true">
            <el-icon><Plus /></el-icon>
            添加任务
          </el-button>
        </div>
        
        <div class="task-list">
          <div 
            v-for="task in tasks" 
            :key="task.id" 
            class="task-item"
            :class="{ completed: task.completed }"
            @click="toggleTask(task)"
          >
            <div class="task-checkbox">
              <el-icon v-if="task.completed"><Check /></el-icon>
            </div>
            <div class="task-content">
              <div class="task-title">{{ task.title }}</div>
              <div class="task-meta">
                <span class="task-subject">{{ task.subject }}</span>
                <span class="task-time">{{ task.time }}</span>
              </div>
            </div>
            <div class="task-priority" :class="task.priority">
              {{ getPriorityText(task.priority) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加任务弹窗 -->
    <el-dialog title="添加学习任务" v-model="showTaskModal" width="450px">
      <el-form :model="taskForm" label-width="80px">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.title" placeholder="例如：完成数学模拟试卷" />
        </el-form-item>
        
        <el-form-item label="学科" required>
          <el-select v-model="taskForm.subject">
            <el-option label="语文" value="语文" />
            <el-option label="数学" value="数学" />
            <el-option label="英语" value="英语" />
            <el-option label="物理" value="物理" />
            <el-option label="化学" value="化学" />
            <el-option label="生物" value="生物" />
            <el-option label="历史" value="历史" />
            <el-option label="地理" value="地理" />
            <el-option label="政治" value="政治" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="预计时间" required>
          <el-input v-model="taskForm.time" placeholder="例如：1小时30分钟" />
        </el-form-item>
        
        <el-form-item label="优先级" required>
          <el-select v-model="taskForm.priority">
            <el-option label="紧急" value="high" />
            <el-option label="中等" value="medium" />
            <el-option label="普通" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showTaskModal = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { Plus, Check } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const timeRange = ref('week')
const showTaskModal = ref(false)
const timeChartRef = ref(null)
const subjectChartRef = ref(null)
let timeChart = null
let subjectChart = null

const stats = reactive({
  totalHours: 28.5,
  completedTasks: 15,
  goalProgress: 72,
  streak: 12
})

const tasks = ref([])

const taskForm = reactive({
  title: '',
  subject: '数学',
  time: '',
  priority: 'medium'
})

const loadProgress = () => {
  if (timeRange.value === 'today') {
    stats.totalHours = 4.5
    stats.completedTasks = 3
    stats.goalProgress = 25
  } else if (timeRange.value === 'week') {
    stats.totalHours = 28.5
    stats.completedTasks = 15
    stats.goalProgress = 72
  } else {
    stats.totalHours = 98.5
    stats.completedTasks = 52
    stats.goalProgress = 85
  }
  updateCharts()
}

const loadTasks = () => {
  const stored = localStorage.getItem('learningTasks')
  if (stored) {
    tasks.value = JSON.parse(stored)
  } else {
    tasks.value = [
      { id: 1, title: '完成数学模拟试卷', subject: '数学', time: '1小时30分钟', priority: 'high', completed: true },
      { id: 2, title: '背诵英语单词50个', subject: '英语', time: '30分钟', priority: 'medium', completed: true },
      { id: 3, title: '复习物理力学章节', subject: '物理', time: '1小时', priority: 'high', completed: false },
      { id: 4, title: '做化学实验题', subject: '化学', time: '45分钟', priority: 'medium', completed: false },
      { id: 5, title: '语文阅读理解练习', subject: '语文', time: '1小时', priority: 'low', completed: false }
    ]
    saveTasks()
  }
}

const saveTasks = () => {
  localStorage.setItem('learningTasks', JSON.stringify(tasks.value))
}

const saveTask = () => {
  if (!taskForm.title) return
  
  tasks.value.push({
    id: Date.now(),
    ...taskForm,
    completed: false
  })
  
  saveTasks()
  showTaskModal.value = false
  resetForm()
}

const toggleTask = (task) => {
  task.completed = !task.completed
  saveTasks()
  updateStats()
}

const updateStats = () => {
  stats.completedTasks = tasks.value.filter(t => t.completed).length
}

const resetForm = () => {
  taskForm.title = ''
  taskForm.subject = '数学'
  taskForm.time = ''
  taskForm.priority = 'medium'
}

const getPriorityText = (priority) => {
  const map = { high: '紧急', medium: '中等', low: '普通' }
  return map[priority] || '普通'
}

const initCharts = () => {
  nextTick(() => {
    if (timeChartRef.value) {
      timeChart = echarts.init(timeChartRef.value)
    }
    if (subjectChartRef.value) {
      subjectChart = echarts.init(subjectChartRef.value)
    }
    updateCharts()
  })
}

const updateCharts = () => {
  const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const dailyHours = [3.5, 4.2, 2.8, 5.1, 4.8, 4.5, 3.6]
  
  if (timeChart) {
    timeChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: weekDays },
      yAxis: { type: 'value', name: '小时' },
      series: [{
        type: 'bar',
        data: dailyHours,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        }
      }]
    })
  }
  
  const subjects = ['数学', '英语', '物理', '化学', '语文', '其他']
  const subjectHours = [8.5, 6.2, 5.1, 4.3, 3.2, 1.2]
  
  if (subjectChart) {
    subjectChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0, left: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '40%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 16, fontWeight: 'bold' }
        },
        data: subjects.map((name, index) => ({
          value: subjectHours[index],
          name,
          itemStyle: {
            color: ['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280'][index]
          }
        }))
      }]
    })
  }
}

onMounted(() => {
  loadTasks()
  initCharts()
  
  window.addEventListener('resize', () => {
    timeChart?.resize()
    subjectChart?.resize()
  })
})

watch(timeRange, () => {
  loadProgress()
})
</script>

<style scoped>
.progress-tracker {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.time-filter {
  width: 120px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.bg-blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.stat-icon.bg-green {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.stat-icon.bg-purple {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
}

.stat-icon.bg-orange {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.chart-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px 0;
}

.chart-container {
  height: 250px;
}

.task-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-item:hover {
  background: #f3f4f6;
}

.task-item.completed {
  opacity: 0.6;
}

.task-item.completed .task-title {
  text-decoration: line-through;
}

.task-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-item.completed .task-checkbox {
  background: #10b981;
  border-color: #10b981;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 14px;
  color: #1f2937;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  gap: 12px;
}

.task-subject {
  font-size: 12px;
  color: #6b7280;
  padding: 2px 8px;
  background: #e5e7eb;
  border-radius: 4px;
}

.task-time {
  font-size: 12px;
  color: #6b7280;
}

.task-priority {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.task-priority.high {
  background: #fee2e2;
  color: #dc2626;
}

.task-priority.medium {
  background: #fef3c7;
  color: #d97706;
}

.task-priority.low {
  background: #d1fae5;
  color: #059669;
}
</style>
