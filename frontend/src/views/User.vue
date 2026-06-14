<template>
  <div class="user-page">
    <!-- 通知提醒悬浮窗 -->
    <transition name="slide-fade">
      <div v-if="showNotificationPanel" class="notification-panel" @click="showNotificationPanel = false">
        <div class="notification-content" @click.stop>
          <div class="notification-header">
            <h3>📢 通知提醒</h3>
            <el-button size="small" @click="showNotificationPanel = false">关闭</el-button>
          </div>
          <div class="notification-list">
            <div 
              v-for="notification in notifications" 
              :key="notification.id" 
              class="notification-item"
              :class="notification.type"
            >
              <div class="notification-icon">{{ notification.icon }}</div>
              <div class="notification-body">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-desc">{{ notification.description }}</div>
                <div class="notification-time">{{ notification.time }}</div>
              </div>
              <div class="notification-action">
                <el-button size="small" @click="handleNotificationAction(notification)">
                  {{ notification.actionText }}
                </el-button>
              </div>
            </div>
            <div v-if="notifications.length === 0" class="empty-notifications">
              <el-empty description="暂无通知" />
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="header-top">
          <div class="header-title">
            <h1 class="page-title">个人中心</h1>
            <p class="page-desc">管理你的个人信息和系统设置</p>
          </div>
          <div class="header-actions">
            <div class="notification-badge" @click="showNotificationPanel = true">
              <el-icon class="bell-icon"><Bell /></el-icon>
              <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
            </div>
          </div>
        </div>
        
        <!-- 今日提醒 -->
        <div class="daily-reminder" v-if="todayReminders.length > 0">
          <div class="reminder-header">
            <el-icon class="reminder-icon"><Clock /></el-icon>
            <span>今日待办</span>
            <span class="reminder-count">{{ todayReminders.length }} 项</span>
          </div>
          <div class="reminder-list">
            <div 
              v-for="reminder in todayReminders" 
              :key="reminder.id" 
              class="reminder-item"
              :class="{ completed: reminder.completed }"
              @click="toggleReminderComplete(reminder)"
            >
              <div class="reminder-checkbox">
                <el-icon v-if="reminder.completed"><Check /></el-icon>
              </div>
              <div class="reminder-content">
                <div class="reminder-title">{{ reminder.title }}</div>
                <div class="reminder-meta">{{ reminder.time }} · {{ reminder.subject }}</div>
              </div>
              <div class="reminder-priority" :class="reminder.priority">
                {{ reminder.priority === 'high' ? '紧急' : reminder.priority === 'medium' ? '中等' : '普通' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="profile-card card">
            <div class="profile-header">
              <div class="avatar-wrapper">
                <img :src="userInfo.avatar" alt="用户头像" class="avatar">
                <div class="avatar-edit" @click="uploadAvatar">
                  <el-icon class="edit-icon"><Camera /></el-icon>
                </div>
              </div>
              <div class="user-info">
                <h2 class="user-name">{{ userInfo.name }}</h2>
                <p class="user-email">{{ userInfo.email }}</p>
              </div>
            </div>
            <div class="profile-stats">
              <div class="stat" @click="activeMenu = 'learning'">
                <span class="stat-value">{{ userStats.practices }}</span>
                <span class="stat-label">演练次数</span>
              </div>
              <div class="stat" @click="activeMenu = 'favorites'">
                <span class="stat-value">{{ userStats.schools }}</span>
                <span class="stat-label">收藏学校</span>
              </div>
              <div class="stat" @click="activeMenu = 'learning'">
                <span class="stat-value">{{ userStats.plans }}</span>
                <span class="stat-label">保存方案</span>
              </div>
            </div>
            <!-- 快捷操作 -->
            <div class="quick-actions">
              <el-button type="primary" size="small" @click="activeMenu = 'profile'">
                <el-icon><Edit /></el-icon>
                编辑资料
              </el-button>
              <el-button size="small" @click="exportData">
                <el-icon><Download /></el-icon>
                导出数据
              </el-button>
            </div>
          </div>

          <div class="menu-card card">
            <div class="section-title">
              <el-icon><List /></el-icon>
              <span>功能导航</span>
            </div>
            <el-menu :default-active="activeMenu" class="user-menu">
              <el-menu-item index="profile" @click="activeMenu = 'profile'">
                <el-icon><User /></el-icon>
                <span>个人信息</span>
              </el-menu-item>
              <el-menu-item index="learning" @click="activeMenu = 'learning'">
                <el-icon><Book /></el-icon>
                <span>学习记录</span>
              </el-menu-item>
              <el-menu-item index="goals" @click="activeMenu = 'goals'">
                <el-icon><Aim /></el-icon>
                <span>学习目标</span>
              </el-menu-item>
              <el-menu-item index="plans" @click="activeMenu = 'plans'">
                <el-icon><Calendar /></el-icon>
                <span>学习计划</span>
              </el-menu-item>
              <el-menu-item index="favorites" @click="activeMenu = 'favorites'">
                <el-icon><Star /></el-icon>
                <span>收藏管理</span>
              </el-menu-item>
              <el-menu-item index="settings" @click="activeMenu = 'settings'">
                <el-icon><Setting /></el-icon>
                <span>系统设置</span>
              </el-menu-item>
            </el-menu>
          </div>
        </el-col>

        <el-col :xs="24" :md="16">
          <div v-if="activeMenu === 'profile'" class="content-card card">
            <div class="section-title">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </div>
            <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="120px">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="editForm.name" placeholder="请输入姓名" />
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="editForm.email" type="email" placeholder="请输入邮箱" />
              </el-form-item>
              <el-form-item label="手机号码" prop="phone">
                <el-input v-model="editForm.phone" placeholder="请输入手机号码" />
              </el-form-item>
              <el-form-item label="所在地区" prop="region">
                <el-select v-model="editForm.region" placeholder="请选择地区">
                  <el-option label="昆明市" value="昆明市" />
                  <el-option label="曲靖市" value="曲靖市" />
                  <el-option label="玉溪市" value="玉溪市" />
                  <el-option label="保山市" value="保山市" />
                  <el-option label="昭通市" value="昭通市" />
                  <el-option label="丽江市" value="丽江市" />
                  <el-option label="普洱市" value="普洱市" />
                  <el-option label="临沧市" value="临沧市" />
                </el-select>
              </el-form-item>
              <el-form-item label="学校" prop="school">
                <el-input v-model="editForm.school" placeholder="请输入所在学校" />
              </el-form-item>
              <el-form-item label="年级" prop="grade">
                <el-select v-model="editForm.grade" placeholder="请选择年级">
                  <el-option label="初一" value="初一" />
                  <el-option label="初二" value="初二" />
                  <el-option label="初三" value="初三" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveProfile" :loading="saving">保存修改</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div v-if="activeMenu === 'learning'" class="content-card card">
            <div class="section-title">
              <el-icon><Book /></el-icon>
              <span>学习记录</span>
            </div>
            <div class="learning-tabs">
              <el-tabs v-model="activeTab">
                <el-tab-pane label="模拟演练" name="practice">
                  <div class="tab-content">
                    <div class="practice-summary">
                      <div class="summary-item">
                        <span class="summary-value">{{ practiceRecords.length }}</span>
                        <span class="summary-label">演练次数</span>
                      </div>
                      <div class="summary-item">
                        <span class="summary-value">{{ totalStrategies }}</span>
                        <span class="summary-label">策略使用</span>
                      </div>
                    </div>
                    <el-table :data="practiceRecords" style="width: 100%" border>
                      <el-table-column prop="date" label="日期" width="150" />
                      <el-table-column prop="times" label="演练次数" width="100" />
                      <el-table-column prop="strategies" label="使用策略">
                        <template #default="scope">
                          <div class="strategy-tags">
                            <el-tag 
                              v-for="(strategy, index) in scope.row.strategies.split(',')" 
                              :key="index"
                              :type="getStrategyTag(strategy.trim())"
                              size="small"
                            >
                              {{ strategy.trim() }}
                            </el-tag>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column prop="score" label="预估分数" width="120">
                        <template #default="scope">
                          <span :class="getScoreClass(scope.row.score)">{{ scope.row.score }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="actions" label="操作" width="120">
                        <template #default="scope">
                          <el-button type="primary" size="small" @click="viewPractice(scope.row.id)">
                            查看
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="分数记录" name="score">
                  <div class="tab-content">
                    <div class="score-chart">
                      <div ref="scoreChart" class="chart-mini"></div>
                    </div>
                    <el-table :data="scoreRecords" style="width: 100%" border>
                      <el-table-column prop="date" label="日期" width="150" />
                      <el-table-column prop="score" label="分数" width="100">
                        <template #default="scope">
                          <span :class="getScoreClass(scope.row.score)">{{ scope.row.score }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="rank" label="排名" width="100" />
                      <el-table-column prop="subjects" label="科目" />
                      <el-table-column prop="improve" label="进步" width="100">
                        <template #default="scope">
                          <span :class="scope.row.improve >= 0 ? 'positive' : 'negative'">
                            {{ scope.row.improve >= 0 ? '+' : '' }}{{ scope.row.improve }}
                          </span>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="浏览记录" name="browse">
                  <el-table :data="userBrowseRecords" style="width: 100%" border>
                    <el-table-column prop="date" label="日期" width="150" />
                    <el-table-column prop="type" label="类型" width="100">
                      <template #default="scope">
                        <el-tag :type="getTypeTag(scope.row.type)">{{ scope.row.type }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="title" label="标题" />
                    <el-table-column prop="actions" label="操作" width="120">
                      <template #default="scope">
                        <el-button type="primary" size="small" @click="viewRecord(scope.row)">
                          查看
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>

          <!-- 学习目标管理 -->
          <div v-if="activeMenu === 'goals'" class="content-card card">
            <GoalManager />
          </div>

          <!-- 学习计划管理 -->
          <div v-if="activeMenu === 'plans'" class="content-card card">
            <ProgressTracker />
          </div>

          <div v-if="activeMenu === 'favorites'" class="content-card card">
            <div class="section-title">
              <el-icon><Star /></el-icon>
              <span>收藏管理</span>
              <el-button size="small" @click="goToCompare" :disabled="favoriteSchools.length < 2">
                批量对比 ({{ favoriteSchools.length }})
              </el-button>
            </div>
            <div class="favorites-grid">
              <div v-for="item in favoriteSchools" :key="item.id" class="favorite-card">
                <div class="favorite-header">
                  <div class="favorite-icon">
                    <el-icon><MapPin /></el-icon>
                  </div>
                  <div class="favorite-badge">{{ item.type }}</div>
                </div>
                <div class="favorite-body">
                  <h3 class="favorite-name">{{ item.name }}</h3>
                  <p class="favorite-location">{{ item.city }} · {{ item.district }}</p>
                  <div class="favorite-stats">
                    <span class="stat-item">{{ item.minScore }}分</span>
                    <span class="stat-divider">|</span>
                    <span class="stat-item">{{ item.oneRate }}%一本率</span>
                  </div>
                </div>
                <div class="favorite-footer">
                  <el-button size="small" @click="goToSchoolDetail(item.id)">查看详情</el-button>
                  <el-button size="small" text @click="removeFavorite(item.id)">取消收藏</el-button>
                </div>
              </div>
            </div>
            <div v-if="favoriteSchools.length === 0" class="empty-favorites">
              <el-empty description="暂无收藏的学校" />
              <el-button type="primary" @click="goToSchoolList">去浏览学校</el-button>
            </div>
          </div>

          <div v-if="activeMenu === 'settings'" class="content-card card">
            <div class="section-title">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </div>
            <el-form :model="settingsForm" label-width="150px">
              <el-form-item label="通知提醒">
                <div class="form-row">
                  <el-switch v-model="settingsForm.notifications" />
                  <span class="form-hint">接收系统通知和消息提醒</span>
                </div>
              </el-form-item>
              <el-form-item label="邮件提醒">
                <div class="form-row">
                  <el-switch v-model="settingsForm.emailNotifications" />
                  <span class="form-hint">重要消息发送到邮箱</span>
                </div>
              </el-form-item>
              <el-form-item label="深色模式">
                <div class="form-row">
                  <el-switch v-model="settingsForm.darkMode" />
                  <span class="form-hint">切换深色/浅色主题</span>
                </div>
              </el-form-item>
              <el-form-item label="默认页面">
                <el-select v-model="settingsForm.defaultPage" placeholder="请选择默认页面">
                  <el-option label="首页" value="home" />
                  <el-option label="仪表盘" value="dashboard" />
                  <el-option label="学校查询" value="school" />
                  <el-option label="志愿填报" value="volunteer" />
                </el-select>
              </el-form-item>
              <el-form-item label="语言">
                <el-select v-model="settingsForm.language" placeholder="请选择语言">
                  <el-option label="中文" value="zh" />
                  <el-option label="English" value="en" />
                </el-select>
              </el-form-item>
              <el-form-item label="数据清理">
                <div class="form-row">
                  <el-button type="danger" @click="clearCache">清除缓存</el-button>
                  <span class="form-hint">清除本地缓存数据，不会影响服务器数据</span>
                </div>
              </el-form-item>
              <el-form-item label="数据导出">
                <div class="form-row">
                  <el-button @click="exportData">导出数据</el-button>
                  <span class="form-hint">导出个人学习数据和收藏信息</span>
                </div>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveSettings" :loading="savingSettings">保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Grid as Book, Star, Setting, List, Search as MapPin, Camera, Edit, Download, Aim, Calendar, Check, Clock, Bell
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useSharedStore, eventBus, Events } from '../store/shared'
import GoalManager from '../components/GoalManager.vue'
import ProgressTracker from '../components/ProgressTracker.vue'

interface UserInfo {
  name: string
  email: string
  avatar: string
}

interface PracticeRecord {
  id: number
  date: string
  times: number
  strategies: string
  score: number
}

interface ScoreRecord {
  id: number
  date: string
  score: number
  rank: number
  subjects: string
  improve: number
}

interface BrowseRecord {
  id: number
  date: string
  type: string
  title: string
  url?: string
}

interface FavoriteSchool {
  id: number
  name: string
  city: string
  district: string
  type: string
  minScore: number
  oneRate: number
}

interface LearningGoal {
  id: number
  title: string
  description: string
  targetScore: number
  deadline: string
  progress: number
  status: 'active' | 'completed' | 'overdue'
}

interface StudyPlan {
  id: number
  title: string
  subject: string
  date: string
  time: string
  duration: number
  completed: boolean
}

const router = useRouter()
const sharedStore = useSharedStore()
const activeMenu = ref('profile')
const activeTab = ref('practice')
const saving = ref(false)
const savingSettings = ref(false)
const editFormRef = ref<InstanceType<typeof import('element-plus')['ElForm']> | null>(null)
const scoreChart = ref<HTMLElement | null>(null)
let scoreChartInstance: echarts.ECharts | null = null

const userInfo = reactive<UserInfo>({
  name: '张同学',
  email: 'student@example.com',
  avatar: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=friendly%20asian%20high%20school%20student%20portrait%20professional%20photo&image_size=square'
})

// 用户统计数据（从共享状态获取）
const userStats = computed(() => ({
  practices: 12,
  schools: 8,
  plans: sharedStore.favoriteCount
}))

// 从共享状态获取浏览历史
const userBrowseRecords = computed(() => {
  return sharedStore.browsingHistory.map((item, index) => ({
    id: index + 1,
    date: new Date(item.timestamp).toLocaleDateString('zh-CN'),
    type: '学校',
    title: item.name,
    url: `/school/${item.id}`
  }))
})

// 学习目标数据
const learningGoals = ref<LearningGoal[]>([
  {
    id: 1,
    title: '中考总分突破600分',
    description: '通过系统复习和模拟训练，在中考中取得600分以上的成绩',
    targetScore: 600,
    deadline: '2024-06-20',
    progress: 75,
    status: 'active'
  },
  {
    id: 2,
    title: '数学单科达到110分',
    description: '重点突破函数和几何难点，提高数学成绩',
    targetScore: 110,
    deadline: '2024-06-20',
    progress: 85,
    status: 'active'
  },
  {
    id: 3,
    title: '英语听力专项提升',
    description: '每天坚持听力练习，提高英语听力水平',
    targetScore: 25,
    deadline: '2024-05-30',
    progress: 100,
    status: 'completed'
  },
  {
    id: 4,
    title: '物理实验操作满分',
    description: '熟悉所有实验操作步骤，争取实验考试满分',
    targetScore: 20,
    deadline: '2024-05-15',
    progress: 60,
    status: 'overdue'
  }
])

// 学习目标统计
// @ts-ignore - 预留功能
const _completedGoals = computed(() => learningGoals.value.filter(g => g.status === 'completed').length)
// @ts-ignore - 预留功能
const _activeGoals = computed(() => learningGoals.value.filter(g => g.status === 'active').length)
// @ts-ignore - 预留功能
const _overdueGoals = computed(() => learningGoals.value.filter(g => g.status === 'overdue').length)

// 学习计划数据
const studyPlans = ref<StudyPlan[]>([
  { id: 1, title: '数学函数复习', subject: '数学', date: '2024-05-20', time: '08:00-09:30', duration: 90, completed: true },
  { id: 2, title: '英语阅读理解', subject: '英语', date: '2024-05-20', time: '10:00-11:30', duration: 90, completed: false },
  { id: 3, title: '物理电学专题', subject: '物理', date: '2024-05-20', time: '14:00-15:30', duration: 90, completed: false },
  { id: 4, title: '化学方程式背诵', subject: '化学', date: '2024-05-21', time: '08:00-09:00', duration: 60, completed: false },
  { id: 5, title: '语文古诗文默写', subject: '语文', date: '2024-05-21', time: '10:00-11:00', duration: 60, completed: false },
  { id: 6, title: '历史近代史复习', subject: '历史', date: '2024-05-22', time: '08:00-09:30', duration: 90, completed: false },
  { id: 7, title: '地理气候专题', subject: '地理', date: '2024-05-22', time: '14:00-15:30', duration: 90, completed: false },
  { id: 8, title: '生物遗传专题', subject: '生物', date: '2024-05-23', time: '08:00-09:30', duration: 90, completed: false },
])

const planFilter = ref('all')
// @ts-ignore - 预留功能
const _showAddGoalModal = ref(false)
// @ts-ignore - 预留功能
const _showAddPlanModal = ref(false)
const currentWeekOffset = ref(0)

// 通知和提醒相关
const showNotificationPanel = ref(false)

interface Notification {
  id: number
  type: 'success' | 'warning' | 'danger' | 'info'
  icon: string
  title: string
  description: string
  time: string
  actionText: string
  action?: () => void
}

interface Reminder {
  id: number
  title: string
  subject: string
  time: string
  priority: 'high' | 'medium' | 'low'
  completed: boolean
}

const notifications = ref<Notification[]>([
  {
    id: 1,
    type: 'warning',
    icon: '⚠️',
    title: '学习目标即将到期',
    description: '您的"物理实验操作满分"目标还有3天到期，请尽快完成！',
    time: '5分钟前',
    actionText: '查看',
    action: () => { activeMenu.value = 'goals' }
  },
  {
    id: 2,
    type: 'success',
    icon: '✅',
    title: '学习计划已完成',
    description: '恭喜！您已完成今日的"数学函数复习"计划',
    time: '1小时前',
    actionText: '继续',
    action: () => { activeMenu.value = 'plans' }
  },
  {
    id: 3,
    type: 'info',
    icon: '📊',
    title: '模拟考试分析已更新',
    description: '最新模拟考试分析报告已生成，快来查看您的进步情况！',
    time: '3小时前',
    actionText: '查看报告',
    action: () => { router.push('/data-visualization') }
  },
  {
    id: 4,
    type: 'danger',
    icon: '🔥',
    title: '薄弱知识点提醒',
    description: '您的解析几何知识点掌握程度较低，建议加强练习！',
    time: '昨天',
    actionText: '去练习',
    action: () => { ElMessage.info('练习功能开发中...') }
  }
])

const todayReminders = ref<Reminder[]>([
  { id: 1, title: '数学函数复习', subject: '数学', time: '08:00-09:30', priority: 'high', completed: true },
  { id: 2, title: '英语阅读理解', subject: '英语', time: '10:00-11:30', priority: 'high', completed: false },
  { id: 3, title: '物理电学专题', subject: '物理', time: '14:00-15:30', priority: 'medium', completed: false },
  { id: 4, title: '复习错题本', subject: '全科', time: '19:00-20:00', priority: 'low', completed: false }
])

const unreadCount = computed(() => notifications.value.length)

// 切换提醒完成状态
const toggleReminderComplete = (reminder: Reminder) => {
  reminder.completed = !reminder.completed
  if (reminder.completed) {
    ElMessage.success(`已完成: ${reminder.title}`)
  }
}

// 处理通知操作
const handleNotificationAction = (notification: Notification) => {
  showNotificationPanel.value = false
  if (notification.action) {
    notification.action()
  }
}

// 检查目标进度并推送提醒
const checkGoalProgress = () => {
  const today = new Date()
  learningGoals.value.forEach(goal => {
    const deadline = new Date(goal.deadline)
    const daysRemaining = Math.ceil((deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    
    if (daysRemaining > 0 && daysRemaining <= 7 && goal.progress < 100 && goal.status === 'active') {
      const existingNotification = notifications.value.find(n => n.title.includes(goal.title))
      if (!existingNotification) {
        notifications.value.unshift({
          id: Date.now(),
          type: 'warning',
          icon: '⏰',
          title: `目标即将到期`,
          description: `"${goal.title}"还有${daysRemaining}天到期，当前进度${goal.progress}%`,
          time: '刚刚',
          actionText: '查看',
          action: () => { activeMenu.value = 'goals' }
        })
      }
    }
  })
}

// 检查学习计划并推送提醒
const checkStudyPlans = () => {
  const now = new Date()
  const currentHour = now.getHours()
  const currentMinute = now.getMinutes()
  
  studyPlans.value.forEach(plan => {
    if (!plan.completed) {
      const [startTime] = plan.time.split('-')
      const [hour, minute] = startTime.split(':').map(Number)
      
      const diffMinutes = (hour - currentHour) * 60 + (minute - currentMinute)
      if (diffMinutes > 0 && diffMinutes <= 15) {
        notifications.value.unshift({
          id: Date.now(),
          type: 'info',
          icon: '📚',
          title: '学习计划即将开始',
          description: `${plan.subject} - ${plan.title} 将在${diffMinutes}分钟后开始`,
          time: '刚刚',
          actionText: '前往',
          action: () => { activeMenu.value = 'plans' }
        })
      }
    }
  })
}

const editForm = reactive({
  name: '张同学',
  email: 'student@example.com',
  phone: '13800138000',
  region: '昆明市',
  school: '昆明市第一中学',
  grade: '初三'
})

const editRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  region: [{ required: true, message: '请选择地区', trigger: 'change' }],
  school: [{ required: true, message: '请输入所在学校', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }]
}

const settingsForm = reactive({
  notifications: true,
  emailNotifications: true,
  darkMode: false,
  defaultPage: 'home',
  language: 'zh'
})

const practiceRecords = ref<PracticeRecord[]>([
  { id: 1, date: '2026-01-15', times: 3, strategies: '保守型, 均衡型', score: 655 },
  { id: 2, date: '2026-01-10', times: 5, strategies: '均衡型, 激进型', score: 648 },
  { id: 3, date: '2026-01-05', times: 3, strategies: '激进型, 均衡型', score: 642 }
])

const scoreRecords = ref<ScoreRecord[]>([
  { id: 1, date: '2026-01-12', score: 650, rank: 120, subjects: '语文, 数学, 英语, 物理, 化学, 体育', improve: 8 },
  { id: 2, date: '2026-01-08', score: 642, rank: 150, subjects: '语文, 数学, 英语, 物理, 化学, 体育', improve: 7 },
  { id: 3, date: '2026-01-01', score: 635, rank: 180, subjects: '语文, 数学, 英语, 物理, 化学, 体育', improve: 0 }
])

const favoriteSchools = ref<FavoriteSchool[]>([
  { id: 1, name: '云南师范大学附属中学', city: '昆明市', district: '呈贡区', type: '省级示范', minScore: 690, oneRate: 95 },
  { id: 2, name: '昆明市第一中学', city: '昆明市', district: '五华区', type: '省级示范', minScore: 680, oneRate: 92 },
  { id: 3, name: '昆明市第三中学', city: '昆明市', district: '呈贡区', type: '省级示范', minScore: 670, oneRate: 88 },
  { id: 4, name: '云南大学附属中学', city: '昆明市', district: '盘龙区', type: '省级示范', minScore: 655, oneRate: 86 }
])

const totalStrategies = computed(() => {
  return practiceRecords.value.reduce((sum, record) => sum + record.times, 0)
})

// 头像上传
const uploadAvatar = () => {
  ElMessageBox.confirm(
    '请选择头像来源',
    '上传头像',
    {
      confirmButtonText: '使用随机头像',
      cancelButtonText: '取消',
      type: 'info',
      showClose: false
    }
  ).then(() => {
    const prompts = [
      'friendly asian high school student portrait professional photo',
      'young asian student headshot smiling',
      'professional student portrait photo',
      'asian teenager portrait studio photo'
    ]
    const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)]
    userInfo.avatar = `https://neeko-copilot.bytedance.net/api/text_to_image?prompt=${encodeURIComponent(randomPrompt)}&image_size=square`
    ElMessage.success('头像更新成功！')
  }).catch(() => {})
}

const saveProfile = () => {
  editFormRef.value?.validate((valid) => {
    if (valid) {
      saving.value = true
      setTimeout(() => {
        userInfo.name = editForm.name
        userInfo.email = editForm.email
        saving.value = false
        ElMessage.success('个人信息保存成功！')
      }, 1000)
    }
  })
}

const resetForm = () => {
  editFormRef.value?.resetFields()
}

const saveSettings = () => {
  savingSettings.value = true
  setTimeout(() => {
    // 使用共享状态保存偏好设置
    sharedStore.updatePreferences({
      theme: settingsForm.darkMode ? 'dark' : 'light',
      language: settingsForm.language === 'zh' ? 'zh-CN' : 'en',
      notifications: settingsForm.notifications
    })
    
    // 触发偏好设置更新事件
    eventBus.emit(Events.PREFERENCES_UPDATED, { ...settingsForm })
    
    savingSettings.value = false
    ElMessage.success('设置保存成功！')
  }, 1000)
}

const clearCache = () => {
  ElMessageBox.confirm('确定要清除缓存吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 清除浏览历史和搜索历史
    sharedStore.browsingHistory = []
    localStorage.removeItem('browsingHistory')
    sharedStore.searchHistory = []
    localStorage.removeItem('searchHistory')
    
    setTimeout(() => {
      ElMessage.success('缓存已清除！')
    }, 500)
  })
}

const exportData = () => {
  // 使用共享状态导出数据
  const data = {
    userInfo,
    practiceRecords: practiceRecords.value,
    scoreRecords: scoreRecords.value,
    favoriteSchools: favoriteSchools.value,
    browsingHistory: sharedStore.browsingHistory,
    searchHistory: sharedStore.searchHistory,
    preferences: sharedStore.preferences,
    exportTime: new Date().toLocaleString()
  }
  const content = JSON.stringify(data, null, 2)
  const blob = new Blob([content], { type: 'application/json;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `个人数据_${new Date().toLocaleDateString()}.json`
  link.click()
  ElMessage.success('数据导出成功！')
}

const viewPractice = (_id: number) => {
  ElMessage.info('查看演练记录功能开发中...')
}

const viewRecord = (record: BrowseRecord) => {
  if (record.url) {
    router.push(record.url)
  } else {
    ElMessage.info('查看记录功能开发中...')
  }
}

const goToSchoolDetail = (id: number) => {
  router.push(`/school/detail/${id}`)
}

const goToSchoolList = () => {
  router.push('/school')
}

const goToCompare = () => {
  const ids = favoriteSchools.value.map(s => s.id).join(',')
  router.push(`/compare?ids=${ids}`)
}

// 学习目标管理方法
// @ts-ignore - 预留功能
const _getGoalStatus = (status: string) => {
// @ts-ignore - 预留功能
  return status === 'completed' ? 'success' : status === 'overdue' ? 'danger' : 'primary'
}
// @ts-ignore - 预留功能
const _getGoalColor = (status: string) => {
// @ts-ignore - 预留功能
  return status === 'completed' ? '#67C23A' : status === 'overdue' ? '#F56C6C' : '#409EFF'
}
// @ts-ignore - 预留功能
const _getGoalTagType = (status: string) => {
// @ts-ignore - 预留功能
  return status === 'completed' ? 'success' : status === 'overdue' ? 'danger' : 'primary'
}
// @ts-ignore - 预留功能
const _getGoalStatusText = (status: string) => {
// @ts-ignore - 预留功能
  return status === 'completed' ? '已完成' : status === 'overdue' ? '已逾期' : '进行中'
}
// @ts-ignore - 预留功能
const _getGoalProgressColor = (progress: number) => {
// @ts-ignore - 预留功能
  if (progress >= 100) return '#67C23A'
  if (progress >= 60) return '#409EFF'
  if (progress >= 30) return '#E6A23C'
  return '#F56C6C'
}
// @ts-ignore - 预留功能
const _isGoalOverdue = (goal: LearningGoal) => {
// @ts-ignore - 预留功能
  return new Date(goal.deadline) < new Date() && goal.status !== 'completed'
}
// @ts-ignore - 预留功能
const _editGoal = (goal: LearningGoal) => {
// @ts-ignore - 预留功能
  ElMessage.info(`编辑目标: ${goal.title}`)
}
// @ts-ignore - 预留功能
const _deleteGoal = (id: number) => {
  ElMessageBox.confirm('确定要删除这个目标吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = learningGoals.value.findIndex(g => g.id === id)
    if (index > -1) {
      learningGoals.value.splice(index, 1)
      ElMessage.success('目标已删除')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 学习计划管理方法
const weekDays = computed(() => {
  const days = []
  const today = new Date()
  const startOfWeek = new Date(today)
  startOfWeek.setDate(today.getDate() - today.getDay() + 1 + currentWeekOffset.value * 7)
  
  const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek)
    date.setDate(startOfWeek.getDate() + i)
    const todayDate = new Date().toDateString()
    days.push({
      name: dayNames[i],
      day: date.getDate(),
      date: date.toISOString().split('T')[0],
      isToday: date.toDateString() === todayDate
    })
  }
  return days
})

// @ts-ignore - 预留功能
const _currentWeekRange = computed(() => {
// @ts-ignore - 预留功能
  if (weekDays.value.length === 0) return ''
  const start = weekDays.value[0]
  const end = weekDays.value[6]
  return `${start.date} - ${end.date}`
})

// @ts-ignore - 预留功能
const _prevWeek = () => {
// @ts-ignore - 预留功能
  currentWeekOffset.value--
}

// @ts-ignore - 预留功能
const _nextWeek = () => {
// @ts-ignore - 预留功能
  currentWeekOffset.value++
}

// @ts-ignore - 预留功能
const _getPlansForDay = (date: string) => {
// @ts-ignore - 预留功能
  return studyPlans.value.filter(p => p.date === date)
}

// @ts-ignore - 预留功能
const _isPlanOverdue = (plan: StudyPlan) => {
// @ts-ignore - 预留功能
  return new Date(plan.date) < new Date()
}

// @ts-ignore - 预留功能
const _togglePlanComplete = (plan: StudyPlan) => {
// @ts-ignore - 预留功能
  plan.completed = !plan.completed
  ElMessage.success(plan.completed ? '计划已完成！' : '已取消完成')
}

// @ts-ignore - 预留功能
const _filteredPlans = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  const weekStart = weekDays.value[0]?.date || today
  const weekEnd = weekDays.value[6]?.date || today
  
  return studyPlans.value.filter(plan => {
    if (planFilter.value === 'today') {
      return plan.date === today
    } else if (planFilter.value === 'week') {
      return plan.date >= weekStart && plan.date <= weekEnd
    } else if (planFilter.value === 'month') {
      const month = new Date().getMonth()
      return new Date(plan.date).getMonth() === month
    }
    return true
  })
})

// @ts-ignore - 预留功能
const _editPlan = (plan: StudyPlan) => {
// @ts-ignore - 预留功能
  ElMessage.info(`编辑计划: ${plan.title}`)
}

// @ts-ignore - 预留功能
const _deletePlan = (id: number) => {
  ElMessageBox.confirm('确定要删除这个计划吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = studyPlans.value.findIndex(p => p.id === id)
    if (index > -1) {
      studyPlans.value.splice(index, 1)
      ElMessage.success('计划已删除')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

const removeFavorite = (id: number) => {
  const index = favoriteSchools.value.findIndex(item => item.id === id)
  if (index > -1) {
    favoriteSchools.value.splice(index, 1)
    ElMessage.success('已取消收藏')
  }
}

const getScoreClass = (score: number) => {
  if (score >= 650) return 'score-high'
  if (score >= 600) return 'score-medium'
  return 'score-low'
}

const getStrategyTag = (strategy: string): 'primary' | 'warning' | 'success' | 'info' | undefined => {
  const tags: Record<string, 'primary' | 'warning' | 'success' | 'info'> = {
    '保守型': 'info',
    '均衡型': 'primary',
    '激进型': 'warning'
  }
  return tags[strategy] || 'info'
}

const getTypeTag = (type: string): 'primary' | 'warning' | 'success' | 'info' | undefined => {
  const tags: Record<string, 'primary' | 'warning' | 'success' | 'info'> = {
    '学校': 'primary',
    '政策': 'warning',
    '资源': 'success',
    '新闻': 'info'
  }
  return tags[type]
}

const initScoreChart = () => {
  if (!scoreChart.value) return
  
  if (scoreChartInstance) {
    scoreChartInstance.dispose()
  }

  scoreChartInstance = echarts.init(scoreChart.value)
  const data = scoreRecords.value

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      textStyle: { color: '#303133' }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLabel: { color: '#909399', rotate: 30 },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: {
      type: 'value',
      min: 600,
      axisLabel: { color: '#909399' },
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      splitLine: { lineStyle: { color: '#f2f6fc' } }
    },
    series: [{
      name: '分数',
      type: 'line',
      data: data.map(d => d.score),
      smooth: true,
      itemStyle: { color: '#667eea' },
      lineStyle: { width: 3 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
          { offset: 1, color: 'rgba(255, 255, 255, 0)' }
        ])
      }
    }]
  }

  scoreChartInstance.setOption(option)
}

onMounted(() => {
  // 检查目标进度和学习计划提醒
  checkGoalProgress()
  checkStudyPlans()
  
  nextTick(() => {
    if (activeMenu.value === 'learning' && activeTab.value === 'score') {
      initScoreChart()
    }
  })
})
</script>

<style scoped>
.user-page {
  min-height: 100%;
  background: var(--bg-secondary);
}

/* 通知面板 */
.notification-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.notification-content {
  width: 90%;
  max-width: 480px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  max-height: 80vh;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.notification-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.notification-list {
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border-left: 4px solid transparent;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.notification-item.warning {
  border-left-color: #E6A23C;
}

.notification-item.success {
  border-left-color: #67C23A;
}

.notification-item.danger {
  border-left-color: #F56C6C;
}

.notification-item.info {
  border-left-color: #409EFF;
}

.notification-item:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateX(5px);
}

.notification-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.notification-body {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.notification-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  font-size: 12px;
  color: var(--text-muted);
}

.notification-action {
  flex-shrink: 0;
}

.empty-notifications {
  padding: 40px 20px;
  text-align: center;
}

/* 页面头部 */
.page-header {
  background: var(--primary-gradient);
  color: #fff;
  padding: 48px 0;
  margin-bottom: 32px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-title {
  flex: 1;
}

.header-actions {
  flex-shrink: 0;
}

.notification-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  cursor: pointer;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.notification-badge:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

.bell-icon {
  font-size: 20px;
  color: #fff;
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: #F56C6C;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 今日提醒 */
.daily-reminder {
  margin-top: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.reminder-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.reminder-icon {
  font-size: 18px;
}

.reminder-header span {
  font-size: 16px;
  font-weight: 600;
}

.reminder-count {
  margin-left: auto;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.reminder-item:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateX(5px);
}

.reminder-item.completed {
  opacity: 0.6;
}

.reminder-checkbox {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.reminder-item.completed .reminder-checkbox {
  background: #67C23A;
  border-color: #67C23A;
}

.reminder-checkbox .el-icon {
  color: #fff;
  font-size: 14px;
}

.reminder-content {
  flex: 1;
  min-width: 0;
}

.reminder-title {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 4px;
}

.reminder-meta {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.reminder-priority {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.reminder-priority.high {
  background: rgba(245, 108, 108, 0.2);
  color: #F56C6C;
}

.reminder-priority.medium {
  background: rgba(230, 162, 60, 0.2);
  color: #E6A23C;
}

.reminder-priority.low {
  background: rgba(103, 194, 58, 0.2);
  color: #67C23A;
}

/* 过渡动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #fff;
}

.page-desc {
  font-size: 16px;
  opacity: 0.9;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
  backdrop-filter: blur(10px);
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-title .el-icon {
  font-size: 22px;
  color: #667eea;
}

.profile-card {
  text-align: center;
}

.profile-header {
  margin-bottom: 32px;
}

.avatar-wrapper {
  position: relative;
  width: 110px;
  height: 110px;
  margin: 0 auto 24px;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
  transition: transform 0.3s ease;
}

.avatar-wrapper:hover .avatar {
  transform: scale(1.05);
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transform: translateY(10px);
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
  border: 2px solid #fff;
}

.avatar-wrapper:hover .avatar-edit {
  opacity: 1;
  transform: translateY(0);
}

.edit-icon {
  font-size: 14px;
  color: #fff;
}

.user-name {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.user-email {
  color: var(--text-secondary);
  font-size: 14px;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.stat {
  text-align: center;
  cursor: pointer;
  padding: 12px;
  border-radius: 12px;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.stat:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 6px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.user-menu {
  background: transparent;
  border: none;
}

.user-menu :deep(.el-menu-item) {
  height: 56px;
  line-height: 56px;
  font-size: 15px;
  margin-bottom: 8px;
  border-radius: 12px;
  transition: color 0.3s, background-color 0.3s, box-shadow 0.3s;
  color: var(--text-secondary);
  background: transparent;
}

.user-menu :deep(.el-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
  color: var(--text-primary);
}

.user-menu :deep(.el-menu-item.is-active) {
  background: var(--primary-gradient);
  color: #fff;
}

.content-card {
  min-height: 500px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.form-hint {
  font-size: 14px;
  color: var(--text-muted);
}

.learning-tabs {
  margin-top: 20px;
}

.learning-tabs :deep(.el-tabs__item) {
  color: var(--text-secondary);
}

.learning-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.learning-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-color);
}

.learning-tabs :deep(.el-tabs__active-bar) {
  background: var(--primary-gradient);
}

.tab-content {
  margin-top: 20px;
}

.practice-summary {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
  padding: 20px 28px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.summary-item {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.summary-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.score-chart {
  margin-bottom: 24px;
}

.chart-mini {
  width: 100%;
  height: 200px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.high-score {
  color: #67C23A;
  font-weight: 600;
}

.medium-score {
  color: #E6A23C;
  font-weight: 600;
}

.low-score {
  color: #F56C6C;
  font-weight: 600;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.favorite-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  transition: color 0.3s, background-color 0.3s, box-shadow 0.3s;
}

.favorite-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
}

.favorite-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.favorite-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.favorite-badge {
  font-size: 12px;
  padding: 5px 12px;
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15) 0%, rgba(95, 209, 126, 0.15) 100%);
  color: #67C23A;
  border-radius: 20px;
  font-weight: 500;
}

.favorite-body {
  margin-bottom: 16px;
}

.favorite-name {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.favorite-location {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.favorite-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-divider {
  color: var(--border-color);
}

.favorite-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.empty-favorites {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

:deep(.el-form-item__label) {
  color: var(--text-secondary);
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  box-shadow: none;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__inner) {
  color: var(--text-primary);
}

:deep(.el-input__inner::placeholder) {
  color: var(--text-muted);
}

:deep(.el-select .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
}

:deep(.el-select-dropdown) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
}

:deep(.el-select-dropdown__item) {
  color: var(--text-secondary);
}

:deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.15);
}

:deep(.el-select-dropdown__item.selected) {
  color: #667eea;
}

:deep(.el-button--primary) {
  background: var(--primary-gradient);
  border: none;
  border-radius: 12px;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

:deep(.el-button--default) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 12px;
}

:deep(.el-button--default:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

:deep(.el-button--text) {
  color: var(--text-muted);
}

:deep(.el-button--text:hover) {
  color: #F56C6C;
}

:deep(.el-switch.is-checked .el-switch__core) {
  background: var(--primary-gradient);
  border-color: transparent;
}

:deep(.el-table) {
  background: #ffffff;
  color: #1a1a2e;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

:deep(.el-table th.el-table__cell) {
  background: #f5f5f7;
  color: #1a1a2e;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
  font-weight: 600;
  font-size: 14px;
  padding: 16px 12px;
  text-align: left;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  padding: 14px 12px;
  font-size: 14px;
  color: #1a1a2e;
  background: #ffffff;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell) {
  background: rgba(102, 126, 234, 0.08);
}

:deep(.el-table__body tr) {
  transition: background-color 0.2s ease;
}

:deep(.el-table__body tr:nth-child(even)) {
  background: #fafafa;
}

:deep(.el-table__body tr:nth-child(odd)) {
  background: #ffffff;
}

.strategy-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 表格按钮样式优化 */
:deep(.el-table .el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 12px;
  transition: all 0.2s ease;
}

:deep(.el-table .el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 分数显示优化 */
.score-high {
  color: #67C23A;
  font-weight: 600;
}

.score-medium {
  color: #E6A23C;
  font-weight: 600;
}

.score-low {
  color: #F56C6C;
  font-weight: 600;
}

/* 排名显示优化 */
.rank-top {
  color: #67C23A;
  font-weight: 600;
}

.rank-medium {
  color: #E6A23C;
  font-weight: 600;
}

/* 进步显示优化 */
.positive {
  color: #67C23A;
  font-weight: 600;
}

.negative {
  color: #F56C6C;
  font-weight: 600;
}

:deep(.el-empty__description) {
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .page-header {
    padding: 32px 0;
  }

  .page-title {
    font-size: 28px;
  }

  .container {
    padding: 0 16px;
  }

  .profile-stats {
    flex-direction: column;
    gap: 16px;
  }

  .stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
  }

  .stat-value {
    font-size: 24px;
  }

  .stat-label {
    font-size: 14px;
  }

  .favorites-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .card {
    padding: 20px;
  }

  .practice-summary {
    flex-direction: column;
    gap: 16px;
  }

  .summary-item {
    justify-content: space-between;
  }

  .daily-reminder {
    padding: 16px;
  }

  .reminder-item {
    padding: 12px;
    gap: 10px;
  }

  .reminder-title {
    font-size: 14px;
  }

  .header-top {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .notification-badge {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 24px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .page-desc {
    font-size: 14px;
  }

  .container {
    padding: 0 12px;
  }

  .card {
    padding: 16px;
  }

  .profile-card {
    padding: 20px 16px;
  }

  .avatar-wrapper {
    width: 80px;
    height: 80px;
    margin-bottom: 16px;
  }

  .user-name {
    font-size: 18px;
  }

  .user-email {
    font-size: 13px;
  }

  .stat {
    padding: 10px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .quick-actions {
    flex-direction: column;
    gap: 8px;
  }

  .quick-actions el-button {
    width: 100%;
  }

  .menu-card {
    padding: 16px;
  }

  .user-menu :deep(.el-menu-item) {
    height: 48px;
    line-height: 48px;
    font-size: 14px;
  }

  .section-title {
    font-size: 16px;
  }

  .learning-tabs :deep(.el-tabs__item) {
    font-size: 13px;
  }

  .chart-mini {
    height: 160px;
  }

  .favorites-grid {
    gap: 10px;
  }

  .favorite-card {
    padding: 14px;
  }

  .favorite-name {
    font-size: 15px;
  }

  .favorite-stats {
    flex-direction: column;
    gap: 4px;
  }

  .stat-divider {
    display: none;
  }

  .favorite-footer {
    flex-direction: column;
    gap: 8px;
  }

  .favorite-footer el-button {
    width: 100%;
  }

  .daily-reminder {
    padding: 12px;
  }

  .reminder-header {
    gap: 8px;
  }

  .reminder-item {
    padding: 10px;
    gap: 8px;
  }

  .reminder-title {
    font-size: 13px;
  }

  .reminder-meta {
    font-size: 12px;
  }

  .reminder-checkbox {
    width: 20px;
    height: 20px;
  }

  .notification-panel {
    padding: 16px;
  }

  .notification-content {
    padding: 16px;
  }

  .notification-item {
    padding: 12px;
    gap: 12px;
  }

  .notification-title {
    font-size: 14px;
  }

  .notification-desc {
    font-size: 12px;
  }

  :deep(.el-form-item__label) {
    font-size: 13px;
  }

  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}

@media (max-width: 360px) {
  .page-title {
    font-size: 22px;
  }

  .container {
    padding: 0 8px;
  }

  .card {
    padding: 12px;
  }

  .profile-card {
    padding: 16px 12px;
  }

  .avatar-wrapper {
    width: 70px;
    height: 70px;
  }

  .stat-value {
    font-size: 20px;
  }

  .user-menu :deep(.el-menu-item) {
    height: 44px;
    line-height: 44px;
    font-size: 13px;
    padding: 0 12px;
  }

  .favorites-grid {
    gap: 8px;
  }

  .favorite-card {
    padding: 12px;
  }

  :deep(.el-table) {
    font-size: 11px;
  }

  :deep(.el-table td),
  :deep(.el-table th) {
    padding: 6px 4px;
  }
}
</style>