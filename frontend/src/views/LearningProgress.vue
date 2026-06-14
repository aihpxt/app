<template>
  <div class="learning-progress-page">
    <div class="page-header">
      <h1 class="page-title">📊 学习进度跟踪</h1>
      <p class="page-subtitle">记录学习轨迹，分析学习效果</p>
      <div class="header-stats">
        <div class="stat-badge">
          <span class="badge-value">{{ streakDays }}</span>
          <span class="badge-label">连续学习天数</span>
        </div>
        <div class="stat-badge">
          <span class="badge-value">{{ totalHours }}</span>
          <span class="badge-label">累计学习小时</span>
        </div>
        <div class="stat-badge">
          <span class="badge-value">{{ completedTasks }}</span>
          <span class="badge-label">完成任务数</span>
        </div>
      </div>
    </div>

    <div class="progress-container">
      <!-- 总体进度卡片 -->
      <el-card class="overall-progress-card">
        <template #header>
          <div class="card-header">
            <h3>🎯 总体学习进度</h3>
            <el-tag type="primary" size="small">{{ overallProgress }}%</el-tag>
          </div>
        </template>
        <div class="overall-progress">
          <div class="progress-ring-container">
            <svg class="progress-ring" viewBox="0 0 100 100">
              <circle class="progress-ring-bg" cx="50" cy="50" r="45" />
              <circle 
                class="progress-ring-fill" 
                cx="50" cy="50" r="45"
                :style="{ strokeDasharray: `${overallProgress * 2.83} 283` }"
              />
              <text class="progress-ring-text" x="50" y="55">{{ overallProgress }}%</text>
            </svg>
          </div>
          <div class="overall-stats">
            <div class="stat-item">
              <el-icon class="stat-icon blue"><Timer /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ totalHours }}</div>
                <div class="stat-label">学习时长 (小时)</div>
              </div>
            </div>
            <div class="stat-item">
              <el-icon class="stat-icon green"><Check /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ completedTasks }}/{{ totalTasks }}</div>
                <div class="stat-label">完成任务</div>
              </div>
            </div>
            <div class="stat-item">
              <el-icon class="stat-icon purple"><TrendCharts /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ subjectCount }}</div>
                <div class="stat-label">学习科目</div>
              </div>
            </div>
            <div class="stat-item">
              <el-icon class="stat-icon orange"><Flag /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ streakDays }}</div>
                <div class="stat-label">连续天数</div>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <div class="row-cards">
        <!-- 科目进度卡片 -->
        <el-card class="subjects-progress-card">
          <template #header>
            <div class="card-header">
              <h3>📚 科目学习进度</h3>
              <el-tag type="info" size="small">{{ subjects.length }} 个科目</el-tag>
            </div>
          </template>
          <div class="subjects-list">
            <div
              v-for="subject in subjects"
              :key="subject.name"
              class="subject-item"
            >
              <div class="subject-header">
                <div class="subject-info">
                  <span class="subject-icon">{{ subject.icon }}</span>
                  <div class="subject-name-wrapper">
                    <h4 class="subject-name">{{ subject.name }}</h4>
                    <span class="subject-hours">{{ subject.completedHours }}/{{ subject.totalHours }} 小时</span>
                  </div>
                </div>
                <el-tag :type="getSubjectTagType(subject.progress)" size="small">{{ subject.progress }}%</el-tag>
              </div>
              <div class="subject-progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: subject.progress + '%' }"
                  :class="getProgressClass(subject.progress)"
                ></div>
              </div>
              <div class="subject-details">
                <div class="strengths-weaknesses">
                  <div class="strengths">
                    <span class="label">优势：</span>
                    <el-tag v-for="strength in subject.strengths" :key="strength" size="small" type="success">
                      {{ strength }}
                    </el-tag>
                  </div>
                  <div class="weaknesses">
                    <span class="label">薄弱：</span>
                    <el-tag v-for="weakness in subject.weaknesses" :key="weakness" size="small" type="danger">
                      {{ weakness }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 学习目标卡片 -->
        <el-card class="learning-goals-card">
          <template #header>
            <div class="card-header">
              <h3>🎯 学习目标</h3>
              <el-button type="primary" size="small" @click="showAddGoalModal = true">
                <el-icon><Plus /></el-icon> 添加目标
              </el-button>
            </div>
          </template>
          <div class="goals-list">
            <div
              v-for="goal in learningGoals"
              :key="goal.id"
              class="goal-item"
              :class="{ completed: goal.completed, overdue: goal.overdue }"
            >
              <div class="goal-header">
                <div class="goal-status-icon">
                  <el-icon v-if="goal.completed"><CircleCheck /></el-icon>
                  <el-icon v-else-if="goal.overdue"><CircleClose /></el-icon>
                  <el-icon v-else><Aim /></el-icon>
                </div>
                <div class="goal-info">
                  <h4 class="goal-title">{{ goal.title }}</h4>
                  <div class="goal-meta">
                    <span class="goal-target">目标：{{ goal.target }}</span>
                    <span class="goal-deadline">
                      <el-icon><Calendar /></el-icon>
                      {{ goal.deadline }}
                    </span>
                  </div>
                </div>
                <el-tag :type="goal.completed ? 'success' : goal.overdue ? 'danger' : 'warning'" size="small">
                  {{ goal.completed ? '已完成' : goal.overdue ? '已逾期' : '进行中' }}
                </el-tag>
              </div>
              <div class="goal-progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: goal.progress + '%' }"
                  :class="getProgressClass(goal.progress)"
                ></div>
                <span class="progress-text">{{ goal.progress }}%</span>
              </div>
              <p class="goal-description">{{ goal.description }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 学习分析卡片 -->
      <el-card class="learning-analytics-card">
        <template #header>
          <div class="card-header">
            <h3>📈 学习分析</h3>
            <div class="analytics-tabs">
              <el-tabs v-model="activeTab" type="card">
                <el-tab-pane label="学习趋势" name="trend"></el-tab-pane>
                <el-tab-pane label="时间分布" name="time"></el-tab-pane>
                <el-tab-pane label="科目分析" name="subject"></el-tab-pane>
                <el-tab-pane label="学习习惯" name="habits"></el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </template>
        
        <div class="analytics-content">
          <!-- 学习趋势 -->
          <div v-if="activeTab === 'trend'" class="tab-content">
            <div class="chart-row">
              <div class="chart-item">
                <h4>学习时长趋势</h4>
                <div ref="timeTrendChart" class="chart-container"></div>
              </div>
              <div class="chart-item">
                <h4>任务完成趋势</h4>
                <div ref="taskTrendChart" class="chart-container"></div>
              </div>
            </div>
            <div class="chart-row">
              <div class="chart-item full-width">
                <h4>测试成绩趋势</h4>
                <div ref="scoreTrendChart" class="chart-container-wide"></div>
              </div>
            </div>
          </div>

          <!-- 时间分布 -->
          <div v-if="activeTab === 'time'" class="tab-content">
            <div class="chart-row">
              <div class="chart-item">
                <h4>每日学习时段分布</h4>
                <div ref="hourDistributionChart" class="chart-container"></div>
              </div>
              <div class="chart-item">
                <h4>每周学习天数分布</h4>
                <div ref="weekDayChart" class="chart-container"></div>
              </div>
            </div>
            <div class="chart-row">
              <div class="chart-item full-width">
                <h4>月度学习时长统计</h4>
                <div ref="monthlyChart" class="chart-container-wide"></div>
              </div>
            </div>
          </div>

          <!-- 科目分析 -->
          <div v-if="activeTab === 'subject'" class="tab-content">
            <div class="chart-row">
              <div class="chart-item">
                <h4>科目学习时长占比</h4>
                <div ref="subjectPieChart" class="chart-container"></div>
              </div>
              <div class="chart-item">
                <h4>科目成绩对比</h4>
                <div ref="subjectBarChart" class="chart-container"></div>
              </div>
            </div>
            <div class="chart-row">
              <div class="chart-item full-width">
                <h4>科目学习进度对比</h4>
                <div ref="subjectProgressChart" class="chart-container-wide"></div>
              </div>
            </div>
          </div>

          <!-- 学习习惯 -->
          <div v-if="activeTab === 'habits'" class="tab-content">
            <div class="habits-grid">
              <div class="habit-card">
                <div class="habit-icon blue">⏰</div>
                <div class="habit-info">
                  <div class="habit-value">{{ habits.averageDailyHours }}小时</div>
                  <div class="habit-label">平均每日学习时间</div>
                </div>
              </div>
              <div class="habit-card">
                <div class="habit-icon green">📅</div>
                <div class="habit-info">
                  <div class="habit-value">{{ habits.mostProductiveDay }}</div>
                  <div class="habit-label">最高效学习日</div>
                </div>
              </div>
              <div class="habit-card">
                <div class="habit-icon purple">🕐</div>
                <div class="habit-info">
                  <div class="habit-value">{{ habits.mostProductiveTime }}</div>
                  <div class="habit-label">最高效学习时段</div>
                </div>
              </div>
              <div class="habit-card">
                <div class="habit-icon orange">📊</div>
                <div class="habit-info">
                  <div class="habit-value">{{ habits.totalLearningDays }}天</div>
                  <div class="habit-label">总学习天数</div>
                </div>
              </div>
              <div class="habit-card">
                <div class="habit-icon red">🔥</div>
                <div class="habit-info">
                  <div class="habit-value">{{ habits.consecutiveDays }}天</div>
                  <div class="habit-label">连续学习天数</div>
                </div>
              </div>
              <div class="habit-card">
                <div class="habit-icon cyan">✅</div>
                <div class="habit-info">
                  <div class="habit-value">{{ habits.completionRate }}%</div>
                  <div class="habit-label">任务完成率</div>
                </div>
              </div>
            </div>
            <div class="recommendations-section">
              <h4>💡 学习建议</h4>
              <ul class="recommendations-list">
                <li v-for="(rec, index) in recommendations" :key="index" class="recommendation-item">
                  <span class="recommendation-number">{{ index + 1 }}</span>
                  <span class="recommendation-text">{{ rec }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 最近活动卡片 -->
      <el-card class="recent-activities-card">
        <template #header>
          <div class="card-header">
            <h3>📝 最近学习活动</h3>
            <el-tag type="info" size="small">{{ recentActivities.length }} 条记录</el-tag>
          </div>
        </template>
        <el-timeline mode="start">
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :type="getActivityType(activity.type)"
            :timestamp="activity.time"
          >
            <div class="activity-card">
              <div class="activity-header">
                <el-icon :size="18"><component :is="getActivityIcon(activity.type)" /></el-icon>
                <span class="activity-title">{{ activity.title }}</span>
                <el-tag size="small" :type="getSubjectTagTypeByName(activity.subject)">{{ activity.subject }}</el-tag>
              </div>
              <div class="activity-details">
                <span v-if="activity.type === 'learning'" class="duration">
                  <el-icon><Timer /></el-icon> {{ activity.duration }} 分钟
                </span>
                <span v-else-if="activity.type === 'test'" class="score">
                  <el-icon><DataAnalysis /></el-icon> {{ activity.score }}/{{ activity.totalScore }} 分
                  <span v-if="activity.improve" class="improve" :class="activity.improve >= 0 ? 'positive' : 'negative'">
                    ({{ activity.improve >= 0 ? '+' : '' }}{{ activity.improve }})
                  </span>
                </span>
                <span v-else-if="activity.type === 'goal'" class="goal-status">
                  <el-icon><Aim /></el-icon> {{ activity.goalStatus }}
                </span>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <!-- 添加目标弹窗 -->
    <el-dialog title="添加学习目标" v-model="showAddGoalModal" width="500px">
      <el-form :model="newGoal" label-width="100px">
        <el-form-item label="目标标题" required>
          <el-input v-model="newGoal.title" placeholder="例如：中考总分达到680分" />
        </el-form-item>
        <el-form-item label="目标值" required>
          <el-input v-model="newGoal.target" placeholder="例如：680分" />
        </el-form-item>
        <el-form-item label="截止日期" required>
          <el-date-picker v-model="newGoal.deadline" type="date" />
        </el-form-item>
        <el-form-item label="目标描述">
          <textarea v-model="newGoal.description" rows="2" class="el-textarea" placeholder="描述你的目标..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddGoalModal = false">取消</el-button>
        <el-button type="primary" @click="addGoal">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Timer, Check, TrendCharts, Calendar, DataAnalysis, Plus,
  Aim, Reading, Edit, Histogram, Flag
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const activeTab = ref('trend')
const showAddGoalModal = ref(false)

// 时间趋势图表引用
const timeTrendChart = ref(null)
const taskTrendChart = ref(null)
const scoreTrendChart = ref(null)
const hourDistributionChart = ref(null)
const weekDayChart = ref(null)
const monthlyChart = ref(null)
const subjectPieChart = ref(null)
const subjectBarChart = ref(null)
const subjectProgressChart = ref(null)

let chartInstances = []

// 新目标表单
const newGoal = reactive({
  title: '',
  target: '',
  deadline: '',
  description: ''
})

// 统计数据
const streakDays = ref(12)
const totalHours = ref(156.5)
const completedTasks = ref(148)
const totalTasks = ref(165)
const overallProgress = computed(() => Math.round((completedTasks.value / totalTasks.value) * 100))
const subjectCount = ref(9)

// 科目数据
const subjects = ref([
  { name: '语文', icon: '📖', completedHours: 28, totalHours: 35, progress: 80, strengths: ['阅读理解', '作文'], weaknesses: ['文言文'] },
  { name: '数学', icon: '🧮', completedHours: 32, totalHours: 40, progress: 80, strengths: ['代数', '几何'], weaknesses: ['函数综合'] },
  { name: '英语', icon: '🔤', completedHours: 25, totalHours: 30, progress: 83, strengths: ['阅读理解', '语法'], weaknesses: ['听力'] },
  { name: '物理', icon: '⚛️', completedHours: 18, totalHours: 25, progress: 72, strengths: ['力学'], weaknesses: ['电学', '电磁'] },
  { name: '化学', icon: '🧪', completedHours: 15, totalHours: 20, progress: 75, strengths: ['有机化学'], weaknesses: ['实验题'] },
  { name: '生物', icon: '🧬', completedHours: 12, totalHours: 15, progress: 80, strengths: ['遗传学'], weaknesses: ['生态学'] },
  { name: '历史', icon: '📜', completedHours: 10, totalHours: 15, progress: 67, strengths: ['近代史'], weaknesses: ['古代史'] },
  { name: '地理', icon: '🌍', completedHours: 10, totalHours: 15, progress: 67, strengths: ['自然地理'], weaknesses: ['人文地理'] },
  { name: '政治', icon: '📚', completedHours: 6, totalHours: 10, progress: 60, strengths: ['经济'], weaknesses: ['哲学'] }
])

// 学习目标数据
const learningGoals = ref([
  { id: 1, title: '中考总分突破650分', target: '650分', deadline: '2026-06-20', progress: 85, description: '通过系统复习和模拟训练，在中考中取得650分以上的成绩', completed: false, overdue: false },
  { id: 2, title: '数学单科达到115分', target: '115分', deadline: '2026-06-20', progress: 78, description: '重点突破函数和几何难点，提高数学成绩', completed: false, overdue: false },
  { id: 3, title: '英语听力专项提升', target: '听力满分30分', deadline: '2026-05-30', progress: 100, description: '每天坚持听力练习，提高英语听力水平', completed: true, overdue: false },
  { id: 4, title: '物理实验操作满分', target: '20分', deadline: '2026-05-15', progress: 60, description: '熟悉所有实验操作步骤，争取实验考试满分', completed: false, overdue: true }
])

// 学习习惯数据
const habits = reactive({
  averageDailyHours: 4.5,
  mostProductiveDay: '星期六',
  mostProductiveTime: '晚上 19:00-21:00',
  totalLearningDays: 86,
  consecutiveDays: 12,
  completionRate: 89
})

// 学习建议
const recommendations = ref([
  '数学函数部分需要加强练习，建议每天做2道函数综合题',
  '物理电学部分薄弱，建议观看相关教学视频并做专项练习',
  '学习时间安排合理，继续保持每天4-5小时的学习时长',
  '周末可以适当增加学习时间，建议安排模拟考试',
  '注意劳逸结合，保证充足睡眠，提高学习效率'
])

// 最近活动数据
const recentActivities = ref([
  { id: 1, type: 'test', title: '完成数学模拟试卷', subject: '数学', time: '今天 14:30', score: 108, totalScore: 120, improve: 3 },
  { id: 2, type: 'learning', title: '复习物理力学章节', subject: '物理', time: '今天 10:00', duration: 90 },
  { id: 3, type: 'learning', title: '英语阅读理解练习', subject: '英语', time: '今天 09:00', duration: 60 },
  { id: 4, type: 'goal', title: '更新学习目标进度', subject: '目标管理', time: '昨天 20:00', goalStatus: '数学目标完成80%' },
  { id: 5, type: 'test', title: '完成英语听力测试', subject: '英语', time: '昨天 16:00', score: 26, totalScore: 30, improve: 2 },
  { id: 6, type: 'learning', title: '化学方程式背诵', subject: '化学', time: '昨天 14:00', duration: 45 },
  { id: 7, type: 'learning', title: '语文古诗文默写', subject: '语文', time: '昨天 10:00', duration: 60 },
  { id: 8, type: 'test', title: '物理单元测试', subject: '物理', time: '前天 15:00', score: 85, totalScore: 100, improve: -2 }
])

// 获取科目标签类型
const getSubjectTagType = (progress: number) => {
  if (progress >= 80) return 'success'
  if (progress >= 60) return 'warning'
  return 'danger'
}

const getSubjectTagTypeByName = (name: string) => {
  const subject = subjects.value.find(s => s.name === name)
  return subject ? getSubjectTagType(subject.progress) : 'info'
}

// 获取进度样式类
const getProgressClass = (progress: number) => {
  if (progress >= 80) return 'high'
  if (progress >= 60) return 'medium'
  return 'low'
}

// 获取活动类型
const getActivityType = (type: string): "" | "primary" | "success" | "warning" | "info" | "danger" => {
  const types: Record<string, "primary" | "success" | "warning" | "info" | "danger"> = {
    learning: 'primary',
    test: 'success',
    goal: 'warning'
  }
  return types[type] || 'info'
}

// 获取活动图标
const getActivityIcon = (type: string) => {
  const icons: Record<string, any> = { learning: Reading, test: Histogram, goal: Aim }
  return icons[type] || Edit
}

// 添加目标
const addGoal = () => {
  if (!newGoal.title || !newGoal.target || !newGoal.deadline) {
    ElMessage.error('请填写完整信息')
    return
  }
  
  learningGoals.value.push({
    id: Date.now(),
    title: newGoal.title,
    target: newGoal.target,
    deadline: newGoal.deadline,
    description: newGoal.description,
    progress: 0,
    completed: false,
    overdue: false
  })
  
  showAddGoalModal.value = false
  newGoal.title = ''
  newGoal.target = ''
  newGoal.deadline = ''
  newGoal.description = ''
  
  ElMessage.success('目标添加成功')
}

// 初始化图表
const initCharts = () => {
  nextTick(() => {
    // 学习时长趋势
    if (timeTrendChart.value) {
      const chart = echarts.init(timeTrendChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
        yAxis: { type: 'value', name: '小时' },
        series: [{
          type: 'line',
          smooth: true,
          data: [3.5, 4.2, 2.8, 5.1, 4.8, 6.5, 5.6],
          lineStyle: { width: 3, color: '#667eea' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#667eea40' },
              { offset: 1, color: '#667eea05' }
            ])
          }
        }]
      })
    }

    // 任务完成趋势
    if (taskTrendChart.value) {
      const chart = echarts.init(taskTrendChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: ['第1周', '第2周', '第3周', '第4周'] },
        yAxis: { type: 'value', name: '完成数' },
        series: [{
          type: 'bar',
          data: [28, 32, 45, 43],
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#10b981' },
              { offset: 1, color: '#34d399' }
            ])
          }
        }]
      })
    }

    // 测试成绩趋势
    if (scoreTrendChart.value) {
      const chart = echarts.init(scoreTrendChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 0, left: 'center' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: ['第一次模拟', '三月月考', '第二次模拟', '四月月考', '第三次模拟'] },
        yAxis: { type: 'value', name: '分数' },
        series: [
          { name: '总分', type: 'line', smooth: true, data: [580, 605, 628, 645, 658], color: '#667eea' },
          { name: '数学', type: 'line', smooth: true, data: [102, 105, 108, 112, 110], color: '#10b981' },
          { name: '英语', type: 'line', smooth: true, data: [98, 102, 105, 108, 110], color: '#f59e0b' },
          { name: '物理', type: 'line', smooth: true, data: [72, 75, 78, 82, 85], color: '#ef4444' }
        ]
      })
    }

    // 每日时段分布
    if (hourDistributionChart.value) {
      const chart = echarts.init(hourDistributionChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: ['6-8', '8-10', '10-12', '12-14', '14-16', '16-18', '18-20', '20-22'] },
        yAxis: { type: 'value', name: '学习天数' },
        series: [{
          type: 'bar',
          data: [5, 28, 32, 15, 35, 38, 42, 30],
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#8b5cf6' },
              { offset: 1, color: '#a78bfa' }
            ])
          }
        }]
      })
    }

    // 每周学习天数
    if (weekDayChart.value) {
      const chart = echarts.init(weekDayChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data: [
            { value: 86, name: '周一', itemStyle: { color: '#667eea' } },
            { value: 82, name: '周二', itemStyle: { color: '#10b981' } },
            { value: 78, name: '周三', itemStyle: { color: '#f59e0b' } },
            { value: 84, name: '周四', itemStyle: { color: '#ef4444' } },
            { value: 80, name: '周五', itemStyle: { color: '#8b5cf6' } },
            { value: 86, name: '周六', itemStyle: { color: '#06b6d4' } },
            { value: 82, name: '周日', itemStyle: { color: '#ec4899' } }
          ]
        }]
      })
    }

    // 月度学习时长
    if (monthlyChart.value) {
      const chart = echarts.init(monthlyChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月'] },
        yAxis: { type: 'value', name: '学习时长(小时)' },
        series: [{
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 10,
          data: [28, 35, 42, 38, 41],
          lineStyle: { width: 3, color: '#667eea' },
          itemStyle: { color: '#667eea', borderWidth: 2, borderColor: '#fff' }
        }]
      })
    }

    // 科目学习占比
    if (subjectPieChart.value) {
      const chart = echarts.init(subjectPieChart.value)
      chartInstances.push(chart)
      const subjectColors = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#6b7280', '#06b6d4', '#84cc16']
      chart.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, left: 'center', itemGap: 10 },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '40%'],
          data: subjects.value.map((s, i) => ({
            value: s.completedHours,
            name: s.name,
            itemStyle: { color: subjectColors[i] }
          }))
        }]
      })
    }

    // 科目成绩对比
    if (subjectBarChart.value) {
      const chart = echarts.init(subjectBarChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: ['语文', '数学', '英语', '物理', '化学', '生物'] },
        yAxis: { type: 'value', name: '分数', max: 120 },
        series: [{
          type: 'bar',
          data: [98, 108, 105, 85, 72, 42],
          itemStyle: { borderRadius: [4, 4, 0, 0] }
        }]
      })
    }

    // 科目进度对比
    if (subjectProgressChart.value) {
      const chart = echarts.init(subjectProgressChart.value)
      chartInstances.push(chart)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 0, left: 'center' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: subjects.value.map(s => s.name) },
        yAxis: { type: 'value', name: '进度(%)', max: 100 },
        series: [{
          name: '学习进度',
          type: 'bar',
          data: subjects.value.map(s => s.progress),
          itemStyle: { borderRadius: [4, 4, 0, 0] }
        }]
      })
    }

    // 窗口大小变化时调整图表
    window.addEventListener('resize', () => {
      chartInstances.forEach(chart => chart.resize())
    })
  })
}

onMounted(() => {
  initCharts()
})
</script>

<style scoped>
.learning-progress-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #fff;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.header-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.stat-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 30px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.badge-value {
  font-size: 28px;
  font-weight: 700;
}

.badge-label {
  font-size: 12px;
  opacity: 0.8;
}

.progress-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.row-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 1200px) {
  .row-cards {
    grid-template-columns: 1fr;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

/* 总体进度 */
.overall-progress-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.overall-progress-card .card-header h3,
.overall-progress-card .el-tag {
  color: #fff;
}

.overall-progress-card .el-tag {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.overall-progress {
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 20px 0;
}

.progress-ring-container {
  flex-shrink: 0;
}

.progress-ring {
  width: 150px;
  height: 150px;
}

.progress-ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.2);
  stroke-width: 8;
}

.progress-ring-fill {
  fill: none;
  stroke: #fff;
  stroke-width: 8;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
  transition: stroke-dasharray 0.5s ease;
}

.progress-ring-text {
  fill: #fff;
  font-size: 24px;
  font-weight: 600;
  text-anchor: middle;
}

.overall-stats {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
}

.stat-icon {
  font-size: 24px;
}

.stat-icon.blue { color: #93c5fd; }
.stat-icon.green { color: #86efac; }
.stat-icon.purple { color: #c4b5fd; }
.stat-icon.orange { color: #fcd34d; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
}

.stat-label {
  font-size: 13px;
  opacity: 0.8;
}

/* 科目进度 */
.subjects-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.subject-item {
  padding: 20px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
}

.subject-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.subject-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.subject-icon {
  font-size: 24px;
}

.subject-name-wrapper {
  display: flex;
  flex-direction: column;
}

.subject-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.subject-hours {
  font-size: 13px;
  color: #6b7280;
}

.subject-progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-fill.high { background: linear-gradient(90deg, #10b981, #34d399); }
.progress-fill.medium { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.progress-fill.low { background: linear-gradient(90deg, #f59e0b, #fbbf24); }

.strengths-weaknesses {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.strengths, .weaknesses {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.label {
  font-size: 12px;
  color: #6b7280;
}

/* 学习目标 */
.goals-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.goal-item {
  padding: 20px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  position: relative;
}

.goal-item.completed {
  opacity: 0.7;
}

.goal-item.overdue {
  border-color: #ef4444;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.goal-status-icon {
  font-size: 20px;
  margin-right: 10px;
}

.goal-info {
  flex: 1;
}

.goal-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.goal-meta {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #6b7280;
}

.goal-target {
  padding: 2px 8px;
  background: #e5e7eb;
  border-radius: 4px;
}

.goal-progress-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  min-width: 45px;
  text-align: right;
}

.goal-description {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

/* 学习分析 */
.analytics-tabs {
  flex: 1;
  margin-left: 20px;
}

.analytics-content {
  padding-top: 20px;
}

.tab-content {
  min-height: 400px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-item {
  background: #f9fafb;
  border-radius: 10px;
  padding: 20px;
}

.chart-item h4 {
  margin: 0 0 15px 0;
  font-size: 15px;
  font-weight: 600;
}

.chart-item.full-width {
  grid-column: 1 / -1;
}

.chart-container {
  height: 200px;
}

.chart-container-wide {
  height: 250px;
}

/* 学习习惯 */
.habits-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 25px;
}

@media (max-width: 900px) {
  .habits-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .habits-grid {
    grid-template-columns: 1fr;
  }
}

.habit-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 10px;
}

.habit-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.habit-icon.blue { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
.habit-icon.green { background: linear-gradient(135deg, #d1fae5, #a7f3d0); }
.habit-icon.purple { background: linear-gradient(135deg, #ede9fe, #ddd6fe); }
.habit-icon.orange { background: linear-gradient(135deg, #fef3c7, #fde68a); }
.habit-icon.red { background: linear-gradient(135deg, #fee2e2, #fecaca); }
.habit-icon.cyan { background: linear-gradient(135deg, #cffafe, #a5f3fc); }

.habit-info {
  flex: 1;
}

.habit-value {
  font-size: 20px;
  font-weight: 600;
  color: #374151;
}

.habit-label {
  font-size: 13px;
  color: #6b7280;
}

/* 学习建议 */
.recommendations-section {
  background: #fef3c7;
  border-radius: 10px;
  padding: 20px;
}

.recommendations-section h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
}

.recommendations-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.recommendation-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px dashed #fbbf24;
}

.recommendation-item:last-child {
  border-bottom: none;
}

.recommendation-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #f59e0b;
  color: #fff;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.recommendation-text {
  font-size: 14px;
  color: #78350f;
  line-height: 1.5;
}

/* 最近活动 */
.activity-card {
  background: #f9fafb;
  padding: 15px;
  border-radius: 8px;
}

.activity-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.activity-title {
  font-weight: 500;
  color: #374151;
}

.activity-details {
  font-size: 13px;
  color: #6b7280;
}

.duration, .score {
  display: flex;
  align-items: center;
  gap: 5px;
}

.improve {
  margin-left: 10px;
  font-weight: 600;
}

.improve.positive { color: #10b981; }
.improve.negative { color: #ef4444; }
</style>