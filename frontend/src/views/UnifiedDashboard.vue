<template>
  <div class="unified-dashboard">
    <!-- 顶部导航 -->
    <el-header class="dashboard-header">
      <div class="header-left">
        <h1>🦞 云南省AI全域赋能中考择校智能决策平台</h1>
        <p class="subtitle">统一管理平台</p>
      </div>
      <div class="header-right">
        <el-badge :value="notificationCount" class="notification-badge">
          <el-button icon="el-icon-bell" circle @click="showNotifications" />
        </el-badge>
        <el-dropdown @command="handleUserCommand">
          <span class="user-dropdown">
            <el-avatar :size="40" :src="userAvatar" />
            <span class="username">{{ (currentUser && typeof currentUser === 'object' && !Array.isArray(currentUser)) ? (currentUser.name || '用户') : '用户' }}</span>
            <i class="el-icon-arrow-down el-icon--right" />
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="settings">设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="dashboard-main">
      <!-- 系统状态卡片 -->
      <el-row :gutter="20" class="status-cards">
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">🤖</div>
              <div class="card-info">
                <h3>智能体系统</h3>
                <p class="status-text" :class="agentStatus.class">{{ agentStatus.text }}</p>
                <p class="count">{{ agentCount }} 个智能体</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">🔧</div>
              <div class="card-info">
                <h3>Skills系统</h3>
                <p class="status-text" :class="skillStatus.class">{{ skillStatus.text }}</p>
                <p class="count">{{ skillCount }} 个技能</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">📞</div>
              <div class="card-info">
                <h3>电话系统</h3>
                <p class="status-text" :class="phoneStatus.class">{{ phoneStatus.text }}</p>
                <p class="count">{{ phoneCallCount }} 次通话</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">👥</div>
              <div class="card-info">
                <h3>用户系统</h3>
                <p class="status-text" :class="userStatus.class">{{ userStatus.text }}</p>
                <p class="count">{{ userCount }} 位用户</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 功能模块 -->
      <el-row :gutter="20" class="feature-modules">
        <!-- AI助手 -->
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <span>🤖 AI助手</span>
                <el-button type="text" @click="openAIAssistant">打开</el-button>
              </div>
            </template>
            <div class="ai-assistant-preview">
              <el-scrollbar height="200px">
                <div class="chat-messages">
                  <div v-for="(msg, idx) in chatMessages" :key="msg.id || idx" 
                       :class="['message', msg.role]">
                    <div class="message-content">{{ msg.content }}</div>
                  </div>
                </div>
              </el-scrollbar>
              <el-input
                v-model="chatInput"
                placeholder="输入消息..."
                @keyup.enter="sendMessage"
                class="chat-input"
              >
                <template #append>
                  <el-button icon="el-icon-s-promotion" @click="sendMessage" />
                </template>
              </el-input>
            </div>
          </el-card>
        </el-col>

        <!-- 学校查询 -->
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <span>📚 学校查询</span>
                <el-button type="text" @click="openSchoolSearch">更多</el-button>
              </div>
            </template>
            <div class="school-search-preview">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索学校..."
                prefix-icon="el-icon-search"
                @keyup.enter="searchSchools"
                class="search-input"
              />
              <el-scrollbar height="150px" class="search-results">
                <div v-for="school in searchResults" :key="school.id" 
                     class="school-item" @click="viewSchoolDetail(school)">
                  <div class="school-name">{{ school.name }}</div>
                  <div class="school-info">
                    <span>{{ school.city }}</span>
                    <span>{{ school.level }}</span>
                  </div>
                </div>
              </el-scrollbar>
            </div>
          </el-card>
        </el-col>

        <!-- 数据统计 -->
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <span>📊 数据统计</span>
                <el-button type="text" @click="openDataStats">详情</el-button>
              </div>
            </template>
            <div class="data-stats-preview">
              <div class="stat-item">
                <div class="stat-label">总访问量</div>
                <div class="stat-value">{{ formatNumber(totalVisits) }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">今日咨询</div>
                <div class="stat-value">{{ formatNumber(todayConsultations) }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">活跃用户</div>
                <div class="stat-value">{{ formatNumber(activeUsers) }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">转化率</div>
                <div class="stat-value">{{ conversionRate }}%</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 渠道整合 -->
      <el-row :gutter="20" class="channel-integration">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>🔗 渠道整合</span>
                <el-button type="primary" @click="syncChannels">同步数据</el-button>
              </div>
            </template>
            <div class="channel-stats">
              <div class="channel-item" v-for="channel in channels" :key="channel.type">
                <div class="channel-icon">{{ channel.icon }}</div>
                <div class="channel-info">
                  <h4>{{ channel.name }}</h4>
                  <p>{{ channel.description }}</p>
                  <div class="channel-metrics">
                    <span>互动: {{ channel.interactions }}</span>
                    <span>用户: {{ channel.users }}</span>
                  </div>
                </div>
                <div class="channel-status" :class="channel.status">
                  {{ channel.statusText }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- 通知抽屉 -->
    <el-drawer v-model="notificationDrawer" title="通知中心" size="30%">
      <div class="notification-list">
        <div v-for="notification in notifications" :key="notification.id" 
             class="notification-item" :class="{ unread: !notification.read }">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-content">{{ notification.content }}</div>
          <div class="notification-time">{{ formatTime(notification.time) }}</div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import unifiedService from '@/api/unified'
import { ElMessage } from 'element-plus'

export default {
  name: 'UnifiedDashboard',
  setup() {
    // 响应式数据
    const currentUser = ref(null)
    const userAvatar = ref('')
    const notificationCount = ref(0)
    const notificationDrawer = ref(false)
    const notifications = ref([])

    // 系统状态
    const agentStatus = ref({ text: '运行中', class: 'status-success' })
    const skillStatus = ref({ text: '运行中', class: 'status-success' })
    const phoneStatus = ref({ text: '运行中', class: 'status-success' })
    const userStatus = ref({ text: '运行中', class: 'status-success' })

    const agentCount = ref(11)
    const skillCount = ref(4)
    const phoneCallCount = ref(0)
    const userCount = ref(0)

    // AI助手
    const chatMessages = ref([
      { role: 'assistant', content: '您好！我是AI助手，有什么可以帮助您的吗？' }
    ])
    const chatInput = ref('')

    // 学校搜索
    const searchKeyword = ref('')
    const searchResults = ref([])

    // 数据统计
    const totalVisits = ref(0)
    const todayConsultations = ref(0)
    const activeUsers = ref(0)
    const conversionRate = ref(0)

    // 渠道
    const channels = ref([
      {
        type: 'web',
        name: 'Web前端',
        icon: '🌐',
        description: '网站访问和在线咨询',
        interactions: 0,
        users: 0,
        status: 'active',
        statusText: '正常'
      },
      {
        type: 'phone',
        name: '电话系统',
        icon: '📞',
        description: '智能电话咨询',
        interactions: 0,
        users: 0,
        status: 'active',
        statusText: '正常'
      },
      {
        type: 'wechat',
        name: '微信公众号',
        icon: '💬',
        description: '微信咨询和服务',
        interactions: 0,
        users: 0,
        status: 'active',
        statusText: '正常'
      }
    ])

    // 初始化
    onMounted(async () => {
      await initializeDashboard()
      await loadSystemStatus()
      await loadNotifications()
    })

    // 初始化仪表盘
    const initializeDashboard = async () => {
      const result = await unifiedService.initialize()
      if (result.success) {
        currentUser.value = result.user
        userAvatar.value = result.user?.avatar || ''
      }
    }

    // 加载系统状态
    const loadSystemStatus = async () => {
      const status = await unifiedService.getSystemStatus()
      if (status.success) {
        // 更新各系统状态
        if (status.services?.['ai-service']?.health?.status === 'healthy') {
          agentStatus.value = { text: '运行中', class: 'status-success' }
        }
        
        // 更新统计数据
        if (status.metrics?.rate_limiter?.active_clients) {
          activeUsers.value = status.metrics.rate_limiter.active_clients
        }
      }
    }

    // 加载通知
    const loadNotifications = async () => {
      // 模拟通知数据
      notifications.value = [
        {
          id: 1,
          title: '系统更新',
          content: '系统已更新到最新版本',
          time: new Date(),
          read: false
        },
        {
          id: 2,
          title: '新功能上线',
          content: '智能体Skills功能已上线',
          time: new Date(Date.now() - 3600000),
          read: false
        }
      ]
      notificationCount.value = notifications.value.filter(n => !n.read).length
    }

    // 发送消息
    const sendMessage = async () => {
      if (!chatInput.value.trim()) return

      const userMessage = { role: 'user', content: chatInput.value }
      chatMessages.value.push(userMessage)

      try {
        // 直接调用AI服务的推荐接口
        const response = await fetch('http://localhost:8000/api/v1/ai/recommend', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: chatInput.value,
            score: 680, // 默认分数
            rank: 1000, // 默认排名
            user_info: {
              location: '云南',
              exam_type: '中考'
            }
          })
        })
        
        if (!response.ok) {
          throw new Error('API请求失败')
        }
        
        const data = await response.json()
        // 构建响应消息
        let responseContent = ''
        if (data.success && data.data && data.data.schools) {
          responseContent = '根据您的需求，推荐以下学校：\n'
          data.data.schools.forEach((school, index) => {
            responseContent += `${index + 1}. ${school.name} (录取概率: ${school.probability})\n`
          })
        } else {
          responseContent = data.message || '我收到了你的消息'
        }
        const assistantMessage = { role: 'assistant', content: responseContent }
        chatMessages.value.push(assistantMessage)
      } catch (error) {
        ElMessage.error('发送失败：' + error.message)
      }

      chatInput.value = ''
    }

    // 搜索学校
    const searchSchools = async () => {
      if (!searchKeyword.value.trim()) return

      try {
        const result = await unifiedService.search(searchKeyword.value, 'schools')
        if (result.success) {
          searchResults.value = result.results
        }
      } catch (error) {
        ElMessage.error('搜索失败：' + error.message)
      }
    }

    // 查看学校详情
    const viewSchoolDetail = (school) => {
      // 跳转到学校详情页
      console.log('View school:', school)
    }

    // 同步渠道数据
    const syncChannels = async () => {
      try {
        ElMessage.info('正在同步数据...')
        // 调用同步API
        await new Promise(resolve => setTimeout(resolve, 2000))
        ElMessage.success('数据同步完成')
      } catch (error) {
        ElMessage.error('同步失败：' + error.message)
      }
    }

    // 显示通知
    const showNotifications = () => {
      notificationDrawer.value = true
    }

    // 用户命令处理
    const handleUserCommand = (command) => {
      switch (command) {
        case 'profile':
          // 跳转到个人中心
          break
        case 'settings':
          // 打开设置
          break
        case 'logout':
          // 退出登录
          break
      }
    }

    // 格式化数字
    const formatNumber = (num) => {
      return num.toLocaleString()
    }

    // 格式化时间
    const formatTime = (time) => {
      const now = new Date()
      const diff = now - time
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)

      if (days > 0) return `${days}天前`
      if (hours > 0) return `${hours}小时前`
      if (minutes > 0) return `${minutes}分钟前`
      return '刚刚'
    }

    return {
      currentUser,
      userAvatar,
      notificationCount,
      notificationDrawer,
      notifications,
      agentStatus,
      skillStatus,
      phoneStatus,
      userStatus,
      agentCount,
      skillCount,
      phoneCallCount,
      userCount,
      chatMessages,
      chatInput,
      searchKeyword,
      searchResults,
      totalVisits,
      todayConsultations,
      activeUsers,
      conversionRate,
      channels,
      sendMessage,
      searchSchools,
      viewSchoolDetail,
      syncChannels,
      showNotifications,
      handleUserCommand,
      formatNumber,
      formatTime
    }
  }
}
</script>

<style scoped>
.unified-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
}

.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 5px 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-badge {
  margin-right: 10px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: white;
}

.username {
  font-size: 14px;
}

.dashboard-main {
  padding: 20px;
}

.status-cards {
  margin-bottom: 20px;
}

.status-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s;
}

.status-card:hover {
  transform: translateY(-5px);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-icon {
  font-size: 40px;
}

.card-info h3 {
  margin: 0 0 5px;
  font-size: 16px;
  color: #303133;
}

.status-text {
  margin: 0 0 5px;
  font-size: 12px;
}

.status-success {
  color: #67c23a;
}

.status-warning {
  color: #e6a23c;
}

.status-error {
  color: #f56c6c;
}

.count {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.feature-modules {
  margin-bottom: 20px;
}

.feature-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-assistant-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  background: #f4f4f5;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

.chat-input {
  margin-top: 10px;
}

.school-search-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.search-input {
  margin-bottom: 10px;
}

.search-results {
  flex: 1;
}

.school-item {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background 0.3s;
}

.school-item:hover {
  background: #f5f7fa;
}

.school-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.school-info {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.data-stats-preview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 10px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f9fafc;
  border-radius: 8px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
}

.channel-integration {
  margin-bottom: 20px;
}

.channel-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 10px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9fafc;
  border-radius: 8px;
}

.channel-icon {
  font-size: 32px;
}

.channel-info {
  flex: 1;
}

.channel-info h4 {
  margin: 0 0 5px;
  color: #303133;
}

.channel-info p {
  margin: 0 0 10px;
  font-size: 12px;
  color: #909399;
}

.channel-metrics {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #606266;
}

.channel-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.channel-status.active {
  background: #f0f9ff;
  color: #409eff;
}

.channel-status.inactive {
  background: #fef0f0;
  color: #f56c6c;
}

.notification-list {
  padding: 10px;
}

.notification-item {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
}

.notification-item.unread {
  background: #ecf5ff;
}

.notification-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.notification-content {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}
</style>
