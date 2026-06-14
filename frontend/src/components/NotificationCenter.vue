<template>
  <div class="notification-center">
    <!-- 通知面板 -->
    <transition name="slide-fade">
      <div v-if="showPanel" class="notification-panel" @click.self="showPanel = false">
        <div class="panel-content">
          <div class="panel-header">
            <h3>🔔 通知中心</h3>
            <div class="header-actions">
              <el-button size="small" @click="markAllRead">全部已读</el-button>
              <el-button size="small" @click="showPanel = false">关闭</el-button>
            </div>
          </div>
          
          <div class="notification-tabs">
            <el-tabs v-model="activeTab" class="notification-tabs-inner">
              <el-tab-pane label="全部" name="all">
                <div class="notification-list">
                  <div 
                    v-for="notification in allNotifications" 
                    :key="notification.id" 
                    class="notification-item"
                    :class="{ read: notification.read, unread: !notification.read }"
                    @click="markAsRead(notification)"
                  >
                    <div class="notification-icon" :class="notification.type">
                      {{ getIcon(notification.type) }}
                    </div>
                    <div class="notification-body">
                      <div class="notification-title">{{ notification.title }}</div>
                      <div class="notification-desc">{{ notification.description }}</div>
                      <div class="notification-time">{{ formatTime(notification.time) }}</div>
                    </div>
                    <div class="notification-badge" v-if="!notification.read"></div>
                  </div>
                  <div v-if="allNotifications.length === 0" class="empty-notifications">
                    <el-empty description="暂无通知" />
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="学习提醒" name="reminder">
                <div class="notification-list">
                  <div 
                    v-for="notification in reminderNotifications" 
                    :key="notification.id" 
                    class="notification-item"
                    :class="{ read: notification.read }"
                    @click="markAsRead(notification)"
                  >
                    <div class="notification-icon reminder">📅</div>
                    <div class="notification-body">
                      <div class="notification-title">{{ notification.title }}</div>
                      <div class="notification-desc">{{ notification.description }}</div>
                      <div class="notification-time">{{ formatTime(notification.time) }}</div>
                    </div>
                    <div class="notification-badge" v-if="!notification.read"></div>
                  </div>
                  <div v-if="reminderNotifications.length === 0" class="empty-notifications">
                    <el-empty description="暂无学习提醒" />
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="系统通知" name="system">
                <div class="notification-list">
                  <div 
                    v-for="notification in systemNotifications" 
                    :key="notification.id" 
                    class="notification-item"
                    :class="{ read: notification.read }"
                    @click="markAsRead(notification)"
                  >
                    <div class="notification-icon system">📢</div>
                    <div class="notification-body">
                      <div class="notification-title">{{ notification.title }}</div>
                      <div class="notification-desc">{{ notification.description }}</div>
                      <div class="notification-time">{{ formatTime(notification.time) }}</div>
                    </div>
                    <div class="notification-badge" v-if="!notification.read"></div>
                  </div>
                  <div v-if="systemNotifications.length === 0" class="empty-notifications">
                    <el-empty description="暂无系统通知" />
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="目标进度" name="progress">
                <div class="notification-list">
                  <div 
                    v-for="notification in progressNotifications" 
                    :key="notification.id" 
                    class="notification-item"
                    :class="{ read: notification.read }"
                    @click="markAsRead(notification)"
                  >
                    <div class="notification-icon progress">🎯</div>
                    <div class="notification-body">
                      <div class="notification-title">{{ notification.title }}</div>
                      <div class="notification-desc">{{ notification.description }}</div>
                      <div class="notification-time">{{ formatTime(notification.time) }}</div>
                    </div>
                    <div class="notification-badge" v-if="!notification.read"></div>
                  </div>
                  <div v-if="progressNotifications.length === 0" class="empty-notifications">
                    <el-empty description="暂无进度通知" />
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </transition>
    
    <!-- 悬浮通知 -->
    <transition-group name="notification-float">
      <div 
        v-for="toast in floatingToasts" 
        :key="toast.id" 
        class="floating-toast"
        :class="toast.type"
      >
        <div class="toast-icon">{{ getIcon(toast.type) }}</div>
        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-desc">{{ toast.description }}</div>
        </div>
        <div class="toast-close" @click="removeToast(toast.id)">✕</div>
      </div>
    </transition-group>
    
    <!-- 通知按钮 -->
    <div class="notification-button" @click="showPanel = true">
      <el-icon class="bell-icon"><Bell /></el-icon>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Bell } from '@element-plus/icons-vue'

interface Notification {
  id: number
  type: 'reminder' | 'system' | 'progress' | 'info'
  title: string
  description: string
  time: number
  read: boolean
}

interface FloatingToast {
  id: number
  type: string
  title: string
  description: string
}

const showPanel = ref(false)
const activeTab = ref('all')
const notifications = ref<Notification[]>([])
const floatingToasts = ref<FloatingToast[]>([])
const sentNotifications = ref<Set<string>>(new Set()) // 用于记录已发送的通知
let notificationId = 1
let toastId = 1

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const allNotifications = computed(() => {
  return [...notifications.value].sort((a, b) => b.time - a.time)
})

const reminderNotifications = computed(() => {
  return notifications.value.filter(n => n.type === 'reminder').sort((a, b) => b.time - a.time)
})

const systemNotifications = computed(() => {
  return notifications.value.filter(n => n.type === 'system').sort((a, b) => b.time - a.time)
})

const progressNotifications = computed(() => {
  return notifications.value.filter(n => n.type === 'progress').sort((a, b) => b.time - a.time)
})

const getIcon = (type: string) => {
  const icons: Record<string, string> = {
    reminder: '📅',
    system: '📢',
    progress: '🎯',
    info: 'ℹ️'
  }
  return icons[type] || '📄'
}

const formatTime = (timestamp: number) => {
  const now = Date.now()
  const diff = now - timestamp
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  const date = new Date(timestamp)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const markAsRead = (notification: Notification) => {
  notification.read = true
  saveNotifications()
}

const markAllRead = () => {
  notifications.value.forEach(n => n.read = true)
  saveNotifications()
}

const removeToast = (id: number) => {
  floatingToasts.value = floatingToasts.value.filter(t => t.id !== id)
}

const addNotification = (type: Notification['type'], title: string, description: string) => {
  const notification: Notification = {
    id: notificationId++,
    type,
    title,
    description,
    time: Date.now(),
    read: false
  }
  
  notifications.value.push(notification)
  saveNotifications()
  
  // 显示悬浮通知
  if (type !== 'system' || notifications.value.filter(n => n.type === 'system').length <= 5) {
    showFloatingToast(type, title, description)
  }
}

const showFloatingToast = (type: string, title: string, description: string) => {
  const toast: FloatingToast = {
    id: toastId++,
    type,
    title,
    description
  }
  
  floatingToasts.value.push(toast)
  
  setTimeout(() => {
    removeToast(toast.id)
  }, 5000)
}

const saveNotifications = () => {
  localStorage.setItem('notifications', JSON.stringify(notifications.value))
}

const loadNotifications = () => {
  const saved = localStorage.getItem('notifications')
  if (saved) {
    try {
      notifications.value = JSON.parse(saved)
      notificationId = Math.max(...notifications.value.map(n => n.id), 1) + 1
    } catch {
      notifications.value = []
    }
  }
}

const checkDailyReminders = () => {
  const now = new Date()
  const hour = now.getHours()
  const minute = now.getMinutes()
  
  // 早上8点提醒学习
  if (hour === 8 && minute === 0) {
    addNotification('reminder', '📚 学习时间到', '早上好！今天也要加油学习哦！')
  }
  
  // 中午12点提醒休息
  if (hour === 12 && minute === 0) {
    addNotification('reminder', '🌞 午休时间', '辛苦了一上午，好好休息一下吧！')
  }
  
  // 下午2点提醒继续学习
  if (hour === 14 && minute === 0) {
    addNotification('reminder', '📖 继续学习', '下午好！继续加油，距离目标更近一步！')
  }
  
  // 晚上9点提醒总结
  if (hour === 21 && minute === 0) {
    addNotification('reminder', '📝 今日总结', '今天学习得怎么样？记得做个总结哦！')
  }
}

const checkGoalProgress = () => {
  // 模拟检查目标进度
  const goals = [
    { id: 1, title: '数学冲刺', progress: 75, target: 100 },
    { id: 2, title: '英语听力', progress: 60, target: 100 },
    { id: 3, title: '物理实验', progress: 95, target: 100 }
  ]
  
  goals.forEach(goal => {
    if (goal.progress >= 90 && goal.progress < 100) {
      // 生成唯一的通知标识符
      const notificationKey = `goal_progress_${goal.id}`
      // 检查是否已经发送过相同的通知
      if (!sentNotifications.value.has(notificationKey)) {
        addNotification('progress', `🎯 ${goal.title}即将完成`, `当前进度: ${goal.progress}%，继续加油！`)
        sentNotifications.value.add(notificationKey)
      }
    }
  })
}

let reminderInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadNotifications()
  
  // 初始化一些示例通知
  if (notifications.value.length === 0) {
    notifications.value = [
      { id: notificationId++, type: 'reminder', title: '📅 今日学习计划', description: '记得完成数学函数专题学习', time: Date.now() - 3600000, read: false },
      { id: notificationId++, type: 'progress', title: '🎯 目标进度更新', description: '数学冲刺目标已完成75%', time: Date.now() - 7200000, read: false },
      { id: notificationId++, type: 'system', title: '📢 系统更新', description: '已更新学校数据库，新增10所学校信息', time: Date.now() - 14400000, read: true },
      { id: notificationId++, type: 'reminder', title: '📚 学习提醒', description: '明天有模拟考试，记得复习', time: Date.now() - 21600000, read: true },
      { id: notificationId++, type: 'progress', title: '🎯 目标达成', description: '物理实验复习目标已完成！', time: Date.now() - 28800000, read: true }
    ]
    saveNotifications()
  }
  
  // 每分钟检查一次提醒
  reminderInterval = setInterval(() => {
    checkDailyReminders()
    checkGoalProgress()
  }, 60000)
})

onUnmounted(() => {
  if (reminderInterval) {
    clearInterval(reminderInterval)
  }
})

defineExpose({ addNotification })
</script>

<style scoped>
.notification-center {
  position: relative;
}

.notification-button {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  z-index: 1000;
  transition: transform 0.3s, box-shadow 0.3s;
}

.notification-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
}

.bell-icon {
  font-size: 24px;
  color: #fff;
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  background: #ef4444;
  color: #fff;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

.notification-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.panel-content {
  background: #1a1a32;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.notification-tabs {
  padding: 16px;
}

.notification-tabs-inner {
  --el-tabs-header-height: 40px;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: background 0.3s;
}

.notification-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.notification-item.read {
  opacity: 0.7;
}

.notification-item.unread {
  background: rgba(102, 126, 234, 0.15);
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.notification-icon.reminder {
  background: rgba(245, 158, 11, 0.2);
}

.notification-icon.system {
  background: rgba(59, 130, 246, 0.2);
}

.notification-icon.progress {
  background: rgba(16, 185, 129, 0.2);
}

.notification-body {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.notification-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.notification-badge {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  flex-shrink: 0;
}

.empty-notifications {
  padding: 40px 20px;
  text-align: center;
}

/* 悬浮通知 */
.floating-toast {
  position: fixed;
  top: 100px;
  right: 24px;
  background: #1a1a32;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
  max-width: 400px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  z-index: 10000;
  border-left: 4px solid;
}

.floating-toast.reminder {
  border-left-color: #f59e0b;
}

.floating-toast.system {
  border-left-color: #3b82f6;
}

.floating-toast.progress {
  border-left-color: #10b981;
}

.toast-icon {
  font-size: 24px;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.toast-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toast-close {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 4px;
}

.toast-close:hover {
  color: #fff;
}

/* 动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: opacity 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
}

.notification-float-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.notification-float-leave-active {
  transition: all 0.3s ease;
}

.notification-float-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.notification-float-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

.notification-float-move {
  transition: transform 0.3s ease;
}
</style>
