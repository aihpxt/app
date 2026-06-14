<template>
  <div class="goal-manager">
    <!-- 目标统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon active-icon">🎯</div>
        <div class="stat-info">
          <div class="stat-value">{{ activeGoals }}</div>
          <div class="stat-label">进行中目标</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon completed-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ completedGoals }}</div>
          <div class="stat-label">已完成目标</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon overdue-icon">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ overdueGoals }}</div>
          <div class="stat-label">即将到期</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon avg-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ averageProgress }}%</div>
          <div class="stat-label">平均进度</div>
        </div>
      </div>
    </div>

    <div class="goal-section">
      <div class="section-header">
        <h3 class="section-title">🎯 学习目标管理</h3>
        <el-button size="small" type="primary" @click="showGoalModal = true">
          <el-icon><Plus /></el-icon>
          添加目标
        </el-button>
      </div>
      
      <div class="goal-filter">
        <el-tabs v-model="activeFilter">
          <el-tab-pane label="全部" name="all" />
          <el-tab-pane label="进行中" name="active" />
          <el-tab-pane label="已完成" name="completed" />
          <el-tab-pane label="即将到期" name="overdue" />
        </el-tabs>
      </div>
      
      <div class="goal-cards">
        <div 
          v-for="goal in filteredGoals" 
          :key="goal.id" 
          class="goal-card"
          :class="{ 
            completed: goal.completed, 
            overdue: isGoalOverdue(goal) && !goal.completed,
            'almost-due': isAlmostDue(goal) && !goal.completed && !isGoalOverdue(goal)
          }"
        >
          <div class="goal-header">
            <div class="goal-icon-wrapper">
              <span class="goal-icon">{{ goal.type === 'score' ? '📊' : '🏫' }}</span>
              <div v-if="isAlmostDue(goal) && !goal.completed" class="due-indicator">
                <el-icon class="clock-icon"><Clock /></el-icon>
              </div>
            </div>
            <div class="goal-info">
              <div class="goal-title-row">
                <h4 class="goal-title">{{ goal.title }}</h4>
                <div class="goal-badges">
                  <el-tag :type="getGoalTagType(goal)" size="small">
                    {{ getGoalStatusText(goal) }}
                  </el-tag>
                  <el-tag v-if="isGoalOverdue(goal)" type="danger" size="small">已逾期</el-tag>
                  <el-tag v-else-if="isAlmostDue(goal)" type="warning" size="small">即将到期</el-tag>
                </div>
              </div>
              <p class="goal-subtitle">{{ goal.description }}</p>
            </div>
          </div>
          
          <div class="goal-progress-section">
            <div class="progress-header">
              <span class="progress-label">完成进度</span>
              <span class="progress-text" :style="{ color: getProgressColor(goal.progress) }">
                {{ goal.progress }}%
              </span>
            </div>
            <div class="progress-bar-container">
              <div 
                class="progress-fill" 
                :style="{ 
                  width: goal.progress + '%',
                  background: getProgressGradient(goal.progress)
                }"
              >
                <div v-if="goal.progress > 0 && goal.progress < 100" class="progress-glow"></div>
              </div>
            </div>
          </div>
          
          <div class="goal-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>目标日期：{{ formatDate(goal.targetDate) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Aim /></el-icon>
              <span>{{ goal.type === 'score' ? '目标分数' : '目标学校' }}：{{ goal.target }}</span>
            </div>
            <div v-if="goal.progress > 0 && !goal.completed" class="meta-item">
              <el-icon><TrendCharts /></el-icon>
              <span>今日进度 +{{ goal.dailyProgress || 0 }}%</span>
            </div>
          </div>
          
          <div class="goal-actions">
            <el-button size="small" @click="adjustProgress(goal)">
              <el-icon><Plus /></el-icon>
              调整进度
            </el-button>
            <el-button size="small" @click="editGoal(goal)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteGoal(goal.id)">删除</el-button>
          </div>
        </div>
        
        <div v-if="filteredGoals.length === 0" class="empty-goals">
          <el-empty description="暂无学习目标" />
          <el-button type="primary" @click="showGoalModal = true">立即设置目标</el-button>
        </div>
      </div>
    </div>
    
    <!-- 目标设置弹窗 -->
    <el-dialog title="设置学习目标" v-model="showGoalModal" width="500px">
      <el-form :model="goalForm" :rules="goalRules" ref="goalFormRef" label-width="100px">
        <el-form-item label="目标类型" prop="type">
          <el-select v-model="goalForm.type">
            <el-option label="分数目标" value="score" />
            <el-option label="学校目标" value="school" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标标题" prop="title">
          <el-input v-model="goalForm.title" placeholder="例如：中考总分达到680分" />
        </el-form-item>
        
        <el-form-item label="目标值" prop="target">
          <el-input v-model="goalForm.target" :placeholder="goalForm.type === 'score' ? '例如：680分' : '例如：云南师范大学附属中学'" />
        </el-form-item>
        
        <el-form-item label="截止日期" prop="targetDate">
          <el-date-picker v-model="goalForm.targetDate" type="date" :min-date="new Date()" />
        </el-form-item>
        
        <el-form-item label="描述">
          <textarea v-model="goalForm.description" rows="2" class="goal-textarea" placeholder="请描述你的目标..." />
        </el-form-item>
        
        <el-form-item label="初始进度">
          <el-slider v-model="goalForm.progress" :min="0" :max="100" :step="5" />
          <span class="progress-value">{{ goalForm.progress }}%</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showGoalModal = false">取消</el-button>
        <el-button type="primary" @click="saveGoal">保存</el-button>
      </template>
    </el-dialog>

    <!-- 进度调整弹窗 -->
    <el-dialog title="调整目标进度" v-model="showAdjustModal" width="400px">
      <div class="adjust-form">
        <div class="current-progress">
          <span class="label">当前进度</span>
          <span class="value">{{ adjustingGoal?.progress || 0 }}%</span>
        </div>
        <el-form-item label="调整进度">
          <el-slider v-model="adjustProgressValue" :min="0" :max="100" :step="1" />
          <div class="adjust-buttons">
            <el-button size="small" @click="adjustProgressValue = Math.max(0, adjustProgressValue - 10)">-10%</el-button>
            <span class="adjust-value">{{ adjustProgressValue }}%</span>
            <el-button size="small" @click="adjustProgressValue = Math.min(100, adjustProgressValue + 10)">+10%</el-button>
          </div>
        </el-form-item>
        <el-form-item label="进度备注">
          <textarea v-model="progressNote" rows="2" placeholder="记录本次进度调整的原因..." />
        </el-form-item>
      </div>
      
      <template #footer>
        <el-button @click="showAdjustModal = false">取消</el-button>
        <el-button type="primary" @click="confirmAdjustProgress">确认调整</el-button>
      </template>
    </el-dialog>

    <!-- 目标完成庆祝动画 -->
    <transition name="celebration">
      <div v-if="showCelebration" class="celebration-overlay">
        <div class="celebration-content">
          <div class="celebration-icon">🎉</div>
          <h2>恭喜完成目标！</h2>
          <p>{{ celebrationGoal }}</p>
          <div class="celebration-particles">
            <span v-for="i in 20" :key="i" class="particle" :style="{ animationDelay: i * 0.1 + 's' }">✨</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, Calendar, Aim, TrendCharts, Clock } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface LearningGoal {
  id: number
  type: 'score' | 'school'
  title: string
  description: string
  target: string
  targetDate: string
  progress: number
  dailyProgress: number
  completed: boolean
  createdAt: string
}

const goals = ref<LearningGoal[]>([])
const showGoalModal = ref(false)
const showAdjustModal = ref(false)
const showCelebration = ref(false)
const celebrationGoal = ref('')
const editingId = ref<number | null>(null)
const activeFilter = ref('all')
const adjustingGoal = ref<LearningGoal | null>(null)
const adjustProgressValue = ref(0)
const progressNote = ref('')

const goalFormRef = ref<InstanceType<typeof import('element-plus')['ElForm']> | null>(null)

const goalForm = reactive({
  type: 'score' as 'score' | 'school',
  title: '',
  target: '',
  targetDate: '',
  description: '',
  progress: 0
})

const goalRules = {
  type: [{ required: true, message: '请选择目标类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入目标标题', trigger: 'blur' }],
  target: [{ required: true, message: '请输入目标值', trigger: 'blur' }],
  targetDate: [{ required: true, message: '请选择截止日期', trigger: 'change' }]
}

const loadGoals = () => {
  const stored = localStorage.getItem('learningGoals')
  if (stored) {
    goals.value = JSON.parse(stored)
  } else {
    goals.value = [
      {
        id: 1,
        type: 'score',
        title: '中考总分目标',
        description: '争取在2026年中考中取得优异成绩',
        target: '680分',
        targetDate: '2026-06-20',
        progress: 75,
        dailyProgress: 2,
        completed: false,
        createdAt: '2026-01-01'
      },
      {
        id: 2,
        type: 'school',
        title: '目标学校',
        description: '努力考上理想的高中',
        target: '云南师范大学附属中学',
        targetDate: '2026-07-20',
        progress: 80,
        dailyProgress: 1,
        completed: false,
        createdAt: '2026-01-05'
      },
      {
        id: 3,
        type: 'score',
        title: '数学单科目标',
        description: '提高数学成绩',
        target: '115分',
        targetDate: '2026-06-20',
        progress: 65,
        dailyProgress: 3,
        completed: false,
        createdAt: '2026-01-10'
      },
      {
        id: 4,
        type: 'score',
        title: '英语听力专项',
        description: '每天坚持听力练习',
        target: '28分',
        targetDate: '2026-05-30',
        progress: 100,
        dailyProgress: 0,
        completed: true,
        createdAt: '2026-02-01'
      }
    ]
    saveGoals()
  }
}

const saveGoals = () => {
  localStorage.setItem('learningGoals', JSON.stringify(goals.value))
}

const activeGoals = computed(() => goals.value.filter(g => !g.completed && !isGoalOverdue(g)).length)
const completedGoals = computed(() => goals.value.filter(g => g.completed).length)
const overdueGoals = computed(() => goals.value.filter(g => isGoalOverdue(g) && !g.completed).length)
const averageProgress = computed(() => {
  const active = goals.value.filter(g => !g.completed)
  if (active.length === 0) return 0
  return Math.round(active.reduce((sum, g) => sum + g.progress, 0) / active.length)
})

const filteredGoals = computed(() => {
  switch (activeFilter.value) {
    case 'active':
      return goals.value.filter(g => !g.completed && !isGoalOverdue(g))
    case 'completed':
      return goals.value.filter(g => g.completed)
    case 'overdue':
      return goals.value.filter(g => isGoalOverdue(g) && !g.completed)
    default:
      return goals.value
  }
})

const saveGoal = () => {
  if (!goalFormRef.value) return
  
  goalFormRef.value.validate((valid) => {
    if (!valid) return
    
    if (editingId.value) {
      const index = goals.value.findIndex(g => g.id === editingId.value)
      if (index !== -1) {
        goals.value[index] = {
          ...goals.value[index],
          type: goalForm.type,
          title: goalForm.title,
          target: goalForm.target,
          targetDate: goalForm.targetDate,
          description: goalForm.description,
          progress: goalForm.progress
        }
        ElMessage.success('目标更新成功')
      }
    } else {
      goals.value.push({
        id: Date.now(),
        type: goalForm.type,
        title: goalForm.title,
        target: goalForm.target,
        targetDate: goalForm.targetDate,
        description: goalForm.description,
        progress: goalForm.progress,
        dailyProgress: 0,
        completed: false,
        createdAt: new Date().toISOString().split('T')[0]
      })
      ElMessage.success('目标添加成功')
      
      checkGoalReminders()
    }
    
    saveGoals()
    showGoalModal.value = false
    editingId.value = null
    resetForm()
  })
}

const editGoal = (goal: LearningGoal) => {
  editingId.value = goal.id
  goalForm.type = goal.type
  goalForm.title = goal.title
  goalForm.target = goal.target
  goalForm.targetDate = goal.targetDate
  goalForm.description = goal.description
  goalForm.progress = goal.progress
  showGoalModal.value = true
}

const deleteGoal = (id: number) => {
  ElMessageBox.confirm('确定要删除这个目标吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    goals.value = goals.value.filter(g => g.id !== id)
    saveGoals()
    ElMessage.success('目标已删除')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

const resetForm = () => {
  goalForm.type = 'score'
  goalForm.title = ''
  goalForm.target = ''
  goalForm.targetDate = ''
  goalForm.description = ''
  goalForm.progress = 0
}

const adjustProgress = (goal: LearningGoal) => {
  adjustingGoal.value = goal
  adjustProgressValue.value = goal.progress
  progressNote.value = ''
  showAdjustModal.value = true
}

const confirmAdjustProgress = () => {
  if (!adjustingGoal.value) return
  
  const oldProgress = adjustingGoal.value.progress
  const newProgress = adjustProgressValue.value
  const diff = newProgress - oldProgress
  
  adjustingGoal.value.progress = newProgress
  adjustingGoal.value.dailyProgress = Math.max(0, diff)
  
  if (newProgress >= 100 && !adjustingGoal.value.completed) {
    adjustingGoal.value.completed = true
    celebrationGoal.value = adjustingGoal.value.title
    showCelebration.value = true
    setTimeout(() => {
      showCelebration.value = false
    }, 3000)
    ElMessage.success(`🎉 恭喜完成目标：${adjustingGoal.value.title}`)
  } else if (diff > 0) {
    ElMessage.success(`进度更新成功！+${diff}%`)
  }
  
  saveGoals()
  showAdjustModal.value = false
  adjustingGoal.value = null
}

const getProgressColor = (progress: number) => {
  if (progress >= 80) return '#10b981'
  if (progress >= 50) return '#3b82f6'
  if (progress >= 30) return '#f59e0b'
  return '#ef4444'
}

const getProgressGradient = (progress: number) => {
  if (progress >= 80) return 'linear-gradient(90deg, #10b981 0%, #34d399 100%)'
  if (progress >= 50) return 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)'
  if (progress >= 30) return 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)'
  return 'linear-gradient(90deg, #ef4444 0%, #f87171 100%)'
}

const formatDate = (date: string) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

const isGoalOverdue = (goal: LearningGoal) => {
  return new Date(goal.targetDate) < new Date() && !goal.completed
}

const isAlmostDue = (goal: LearningGoal) => {
  const today = new Date()
  const deadline = new Date(goal.targetDate)
  const daysRemaining = Math.ceil((deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  return daysRemaining > 0 && daysRemaining <= 7 && !goal.completed
}

const getGoalTagType = (goal: LearningGoal) => {
  if (goal.completed) return 'success'
  if (isGoalOverdue(goal)) return 'danger'
  if (isAlmostDue(goal)) return 'warning'
  return 'primary'
}

const getGoalStatusText = (goal: LearningGoal) => {
  if (goal.completed) return '已完成'
  if (isGoalOverdue(goal)) return '已逾期'
  return '进行中'
}

const checkGoalReminders = () => {
  const today = new Date()
  
  goals.value.forEach(goal => {
    if (goal.completed) return
    
    const deadline = new Date(goal.targetDate)
    const daysRemaining = Math.ceil((deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    
    if (daysRemaining === 3 && goal.progress < 80) {
      ElMessage.warning(`⚠️ 目标「${goal.title}」还有3天到期，当前进度${goal.progress}%`)
    } else if (daysRemaining === 1 && goal.progress < 100) {
      ElMessage.warning(`⚠️ 目标「${goal.title}」明天到期，请尽快完成！`)
    }
  })
}

onMounted(() => {
  loadGoals()
  checkGoalReminders()
  
  setInterval(checkGoalReminders, 24 * 60 * 60 * 1000)
})

watch(goals, () => {
  saveGoals()
}, { deep: true })
</script>

<style scoped>
.goal-manager {
  padding: 20px;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

.active-icon {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.completed-icon {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.overdue-icon {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.avg-icon {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
}

.stat-info {
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.goal-filter {
  margin-bottom: 20px;
}

.goal-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.goal-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border-left: 4px solid #e5e7eb;
}

.goal-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.goal-card.completed {
  border-left-color: #10b981;
  opacity: 0.85;
}

.goal-card.overdue {
  border-left-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fff 100%);
}

.goal-card.almost-due {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fff 100%);
}

.goal-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.goal-icon-wrapper {
  position: relative;
}

.goal-icon {
  font-size: 32px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
}

.due-indicator {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: #f59e0b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.clock-icon {
  font-size: 10px;
  color: #fff;
}

.goal-info {
  flex: 1;
}

.goal-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.goal-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.goal-badges {
  display: flex;
  gap: 6px;
}

.goal-subtitle {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  line-height: 1.5;
}

.goal-progress-section {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 13px;
  color: #6b7280;
}

.progress-text {
  font-size: 16px;
  font-weight: 700;
}

.progress-bar-container {
  height: 10px;
  background: #e5e7eb;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease, background 0.3s ease;
  position: relative;
}

.progress-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 30%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4));
  animation: glow 2s infinite;
}

@keyframes glow {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

.goal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
  padding: 4px 8px;
  background: #f3f4f6;
  border-radius: 4px;
}

.goal-actions {
  display: flex;
  gap: 8px;
}

.empty-goals {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
}

.goal-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s ease;
}

.goal-textarea:focus {
  border-color: #409eff;
}

.adjust-form {
  padding: 10px;
}

.current-progress {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.current-progress .label {
  font-size: 14px;
  color: #6b7280;
}

.current-progress .value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.adjust-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
}

.adjust-value {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  min-width: 60px;
  text-align: center;
}

.progress-value {
  margin-left: 12px;
  font-weight: 600;
  color: #667eea;
}

.celebration-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.celebration-content {
  background: #fff;
  border-radius: 20px;
  padding: 40px 60px;
  text-align: center;
  animation: bounceIn 0.5s ease;
  position: relative;
}

@keyframes bounceIn {
  0% { transform: scale(0.5); opacity: 0; }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}

.celebration-icon {
  font-size: 64px;
  margin-bottom: 16px;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.celebration-content h2 {
  font-size: 24px;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.celebration-content p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.celebration-particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  font-size: 20px;
  animation: floatUp 3s infinite;
  opacity: 0;
}

@keyframes floatUp {
  0% {
    opacity: 1;
    transform: translateY(100%) rotate(0deg);
  }
  100% {
    opacity: 0;
    transform: translateY(-200%) rotate(360deg);
  }
}

.particle:nth-child(odd) { left: 20%; }
.particle:nth-child(even) { left: 40%; }
.particle:nth-child(3n) { left: 60%; }
.particle:nth-child(4n) { left: 80%; }

@media (max-width: 768px) {
  .goal-manager {
    padding: 12px;
  }

  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .stat-value {
    font-size: 20px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .goal-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .goal-card {
    padding: 16px;
  }

  .goal-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .goal-icon {
    width: 40px;
    height: 40px;
    font-size: 24px;
  }

  .goal-title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .goal-title {
    font-size: 15px;
  }

  .goal-meta {
    flex-wrap: wrap;
    gap: 8px;
  }

  .meta-item {
    font-size: 11px;
    padding: 3px 6px;
  }

  .goal-actions {
    flex-wrap: wrap;
    gap: 6px;
  }

  .empty-goals {
    padding: 24px;
  }

  .celebration-content {
    padding: 24px 32px;
  }

  .celebration-icon {
    font-size: 48px;
  }

  .celebration-content h2 {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card {
    padding: 10px;
  }

  .stat-icon {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }

  .goal-card {
    padding: 12px;
  }

  .goal-icon {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }

  .goal-title {
    font-size: 14px;
  }

  .goal-subtitle {
    font-size: 12px;
  }

  .goal-actions el-button {
    padding: 6px 10px;
    font-size: 12px;
  }

  .celebration-content {
    padding: 20px 24px;
  }

  .celebration-icon {
    font-size: 40px;
  }

  .celebration-content h2 {
    font-size: 18px;
  }

  .celebration-content p {
    font-size: 14px;
  }
}

@media (max-width: 360px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }

  .goal-badges {
    flex-wrap: wrap;
  }

  .goal-badges el-tag {
    margin-bottom: 4px;
  }
}
</style>