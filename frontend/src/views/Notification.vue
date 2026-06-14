<template>
  <div class="notification-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">消息通知</h1>
        <p class="page-desc">查看系统通知、政策更新和活动提醒</p>
      </div>
    </div>

    <div class="container">
      <!-- 统计信息 -->
      <div class="notification-stats card">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon unread">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ unreadCount }}</div>
                <div class="stat-label">未读消息</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon total">
                <el-icon><Message /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ notificationList.length }}</div>
                <div class="stat-label">总消息数</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 操作按钮 -->
      <div class="notification-actions">
        <el-button type="primary" @click="markAllRead" :disabled="unreadCount === 0">
          <el-icon><Check /></el-icon>全部已读
        </el-button>
        <el-button @click="refreshNotifications">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </div>

      <!-- 通知列表 -->
      <div class="notification-list">
        <el-empty v-if="notificationList.length === 0" description="暂无通知" />
        <el-card
          v-for="notification in notificationList"
          :key="notification.id"
          class="notification-card"
          :class="{ 'unread': !notification.isRead }"
          shadow="hover"
        >
          <div class="notification-header">
            <div class="notification-title">
              <el-tag :type="getNotificationType(notification.type)" size="small">
                {{ getNotificationTypeLabel(notification.type) }}
              </el-tag>
              <span class="title-text">{{ notification.title }}</span>
            </div>
            <div class="notification-time">
              {{ formatTime(notification.createTime) }}
            </div>
          </div>
          <div class="notification-content">
            {{ notification.content }}
          </div>
          <div class="notification-actions">
            <el-button
              v-if="!notification.isRead"
              type="primary"
              size="small"
              @click="markAsRead(notification.id)"
            >
              标记为已读
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteNotification(notification.id)"
            >
              删除
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell, Message, Check, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8001'

const notificationList = ref([])
const unreadCount = ref(0)
const loading = ref(false)

const getNotificationType = (type) => {
  const typeMap = {
    'system': '',
    'policy': 'success',
    'volunteer': 'warning',
    'event': 'info',
    'recommend': 'danger'
  }
  return typeMap[type] || ''
}

const getNotificationTypeLabel = (type) => {
  const labelMap = {
    'system': '系统通知',
    'policy': '政策更新',
    'volunteer': '志愿提醒',
    'event': '活动通知',
    'recommend': '推荐消息'
  }
  return labelMap[type] || '系统通知'
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/notification/list`)
    if (response.data.success) {
      notificationList.value = response.data.data || []
      await fetchUnreadCount()
    }
  } catch (error) {
    console.error('获取通知列表失败:', error)
    ElMessage.error('获取通知列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const fetchUnreadCount = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/notification/unread-count`)
    if (response.data.success) {
      unreadCount.value = response.data.data.count || 0
    }
  } catch (error) {
    console.error('获取未读消息数量失败:', error)
  }
}

const markAsRead = async (notificationId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/notification/${notificationId}/read`)
    if (response.data.success) {
      const notification = notificationList.value.find(n => n.id === notificationId)
      if (notification) {
        notification.isRead = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      ElMessage.success('标记为已读成功')
    }
  } catch (error) {
    console.error('标记为已读失败:', error)
    ElMessage.error('标记为已读失败，请稍后重试')
  }
}

const markAllRead = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/notification/read-all`)
    if (response.data.success) {
      notificationList.value.forEach(n => n.isRead = true)
      unreadCount.value = 0
      ElMessage.success('全部标记为已读成功')
    }
  } catch (error) {
    console.error('全部标记为已读失败:', error)
    ElMessage.error('全部标记为已读失败，请稍后重试')
  }
}

const deleteNotification = async (notificationId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await axios.delete(`${API_BASE_URL}/api/notification/${notificationId}`)
    if (response.data.success) {
      const index = notificationList.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        const notification = notificationList.value[index]
        if (!notification.isRead) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
        notificationList.value.splice(index, 1)
      }
      ElMessage.success('删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除通知失败:', error)
      ElMessage.error('删除通知失败，请稍后重试')
    }
  }
}

const refreshNotifications = () => {
  fetchNotifications()
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notification-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 0;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.page-desc {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.notification-stats {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 15px;
}

.stat-icon.unread {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.notification-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.notification-card {
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.notification-card.unread {
  border-left: 4px solid #667eea;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.notification-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-text {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.notification-content {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.notification-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .stat-item {
    padding: 15px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .notification-actions {
    flex-direction: column;
  }
  
  .notification-actions .el-button {
    width: 100%;
  }
}
</style>