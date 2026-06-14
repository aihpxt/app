<template>
  <div class="smart-assistant">
    <!-- 左侧聊天面板 -->
    <div class="chat-container">
      <!-- 顶部栏 -->
      <div class="chat-header">
        <div class="header-left">
          <div class="assistant-avatar">🤖</div>
          <div class="assistant-info">
            <h3>智能助手</h3>
            <p class="status" :class="{ online: isOnline }">
              <span class="status-dot"></span>
              {{ isOnline ? '在线' : '离线' }}
            </p>
          </div>
        </div>
        <div class="header-right">
          <el-button size="small" @click="clearChat" class="wx-btn-text">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
          <el-button size="small" @click="showSettings = true" class="wx-btn-text">
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 快捷问题 -->
      <div class="quick-questions">
        <div class="section-title">💡 快速提问</div>
        <div class="quick-tags">
          <span
            v-for="tag in quickTags"
            :key="tag.label"
            class="quick-tag"
            @click="sendQuickQuestion(tag.label)"
          >
            {{ tag.emoji }} {{ tag.label }}
          </span>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="chat-messages" ref="chatContainer">
        <div v-if="messages.length === 0 && !isLoading" class="empty-chat">
          <div class="empty-icon">💬</div>
          <h3>智能助手随时为您服务</h3>
          <p>有什么问题都可以问我，我会尽力帮助您！</p>
        </div>

        <template v-for="message in messages" :key="message.id">
          <div class="chat-message" :class="message.isSelf ? 'mine' : 'other'">
            <div class="msg-avatar">
              {{ message.isSelf ? '👤' : '🤖' }}
            </div>
            <div class="msg-content-wrapper">
              <div class="msg-bubble">
                <!-- 文本消息 -->
                <template v-if="message.type === 'text'">
                  <p>{{ message.content }}</p>
                </template>
                <!-- 卡片消息 -->
                <template v-else-if="message.type === 'card'">
                  <div class="info-card">
                    <div class="card-title">{{ message.data.title }}</div>
                    <div class="card-content">{{ message.data.content }}</div>
                    <div v-if="message.data.link" class="card-link">
                      <a :href="message.data.link" target="_blank">
                        <el-icon><Link /></el-icon>
                        查看详情
                      </a>
                    </div>
                  </div>
                </template>
                <!-- 列表消息 -->
                <template v-else-if="message.type === 'list'">
                  <ul class="answer-list">
                    <li v-for="(item, index) in message.data.items" :key="index">
                      <span class="list-number">{{ Number(index) + 1 }}</span>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </template>
                <!-- 图表消息 -->
                <template v-else-if="message.type === 'chart'">
                  <div class="mini-chart">
                    <div class="chart-title">{{ message.data.title }}</div>
                    <div class="chart-bars">
                      <div
                        v-for="(bar, index) in message.data.bars"
                        :key="index"
                        class="chart-bar-wrapper"
                      >
                        <div class="bar-label">{{ bar.label }}</div>
                        <div class="bar-container">
                          <div
                            class="bar-fill"
                            :style="{ width: bar.value + '%', background: bar.color }"
                          ></div>
                        </div>
                        <div class="bar-value">{{ bar.value }}%</div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
              <div class="msg-time">{{ formatTime(message.time) }}</div>
            </div>
          </div>
        </template>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-indicator">
          <span class="typing-dots">
            <span></span><span></span><span></span>
          </span>
          <span>正在思考...</span>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <textarea
            v-model="inputMessage"
            placeholder="输入您的问题..."
            @keydown="handleKeydown"
            :disabled="isLoading"
            rows="1"
          ></textarea>
        </div>
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="!inputMessage.trim() || isLoading"
        >
          <el-icon><Promotion /></el-icon>
        </button>
      </div>
    </div>

    <!-- 右侧功能菜单 -->
    <div class="function-menu">
      <div class="menu-header">
        <h3>🎯 功能入口</h3>
      </div>
      <div class="menu-items">
        <div
          v-for="feature in features"
          :key="feature.id"
          class="menu-item"
          @click="handleFeatureClick(feature)"
        >
          <div class="feature-icon">{{ feature.icon }}</div>
          <div class="feature-info">
            <div class="feature-title">{{ feature.title }}</div>
            <div class="feature-desc">{{ feature.description }}</div>
          </div>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 设置弹窗 -->
    <el-dialog title="助手设置" v-model="showSettings" width="400px">
      <div class="settings-content">
        <div class="setting-item">
          <span>自动回复</span>
          <el-switch :value="autoReply" @change="toggleAutoReply" />
        </div>
        <div class="setting-item">
          <span>语音输入</span>
          <el-switch :value="voiceInput" @change="toggleVoiceInput" />
        </div>
        <div class="setting-item">
          <span>深色模式</span>
          <el-switch :value="darkMode" @change="toggleDarkMode" />
        </div>
        <div class="setting-item">
          <span>回复速度</span>
          <el-select v-model="responseSpeed" placeholder="请选择">
            <el-option label="快速" value="fast" />
            <el-option label="正常" value="normal" />
            <el-option label="详细" value="detailed" />
          </el-select>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import {
  Delete, Setting, Link, Promotion, ArrowRight
} from '@element-plus/icons-vue'
import { apiClient } from '../api'

interface Message {
  id: number
  content: string
  time: number
  isSelf: boolean
  type: 'text' | 'card' | 'list' | 'chart'
  data?: any
}

interface Feature {
  id: string
  icon: string
  title: string
  description: string
  action: string
}

const inputMessage = ref('')
const messages = ref<Message[]>([])
const isLoading = ref(false)
const isOnline = ref(true)
const showSettings = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const currentSessionId = ref<number | null>(null)

const autoReply = ref(true)
const voiceInput = ref(false)
const darkMode = ref(true)
const responseSpeed = ref('normal')

const quickTags = [
  { label: '中考政策', emoji: '📋' },
  { label: '学校推荐', emoji: '🏫' },
  { label: '学习计划', emoji: '📅' },
  { label: '成绩分析', emoji: '📊' },
  { label: '志愿填报', emoji: '✏️' },
  { label: '心理健康', emoji: '💚' },
  { label: '时间管理', emoji: '⏰' },
  { label: '学科辅导', emoji: '📚' }
]

const features = [
  {
    id: 'policy',
    icon: '📋',
    title: '政策查询',
    description: '查询最新中考政策和录取规则',
    action: 'policy'
  },
  {
    id: 'school',
    icon: '🏫',
    title: '学校对比',
    description: '对比分析各学校的优势特点',
    action: 'school'
  },
  {
    id: 'study',
    icon: '📅',
    title: '学习计划',
    description: '制定个性化学习计划',
    action: 'study'
  },
  {
    id: 'analysis',
    icon: '📊',
    title: '成绩分析',
    description: '深入分析学习成绩数据',
    action: 'analysis'
  },
  {
    id: 'volunteer',
    icon: '✏️',
    title: '志愿填报',
    description: '智能推荐志愿填报方案',
    action: 'volunteer'
  },
  {
    id: 'mental',
    icon: '💚',
    title: '心理辅导',
    description: '提供心理疏导和建议',
    action: 'mental'
  }
]

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  return `${hour}:${minute}`
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage: Message = {
    id: Date.now(),
    content: inputMessage.value,
    time: Date.now(),
    isSelf: true,
    type: 'text'
  }

  messages.value.push(userMessage)
  const question = inputMessage.value
  inputMessage.value = ''
  isLoading.value = true

  scrollToBottom()

  // 保存用户消息到后端
  if (currentSessionId.value) {
    try {
      await apiClient.post('/chat/messages', {
        session_id: currentSessionId.value,
        role: 'user',
        content: userMessage.content
      })
    } catch (error) {
      console.error('保存消息失败:', error)
    }
  }

  await getAIResponse(question)
}

const sendQuickQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

const getAIResponse = async (question: string) => {
  try {
    const response = await apiClient.post('/ai/chat', {
      message: question,
      session_id: currentSessionId.value
    })

    if (response.data && response.data.success) {
      const aiResponse = response.data.data

      let assistantMessage: Message = {
        id: Date.now(),
        content: aiResponse.content || '',
        time: Date.now(),
        isSelf: false,
        type: 'text'
      }

      if (aiResponse.type === 'card') {
        assistantMessage.type = 'card'
        assistantMessage.data = aiResponse.data
      } else if (aiResponse.type === 'list') {
        assistantMessage.type = 'list'
        assistantMessage.data = aiResponse.data
      } else if (aiResponse.type === 'chart') {
        assistantMessage.type = 'chart'
        assistantMessage.data = aiResponse.data
      }

      messages.value.push(assistantMessage)

      if (currentSessionId.value) {
        try {
          await apiClient.post('/chat/messages', {
            session_id: currentSessionId.value,
            role: 'assistant',
            content: JSON.stringify(aiResponse)
          })
        } catch (error) {
          console.error('保存回复失败:', error)
        }
      }
    } else {
      await simulateResponse(question)
      return
    }
  } catch (error) {
    console.error('获取AI响应失败:', error)
    await simulateResponse(question)
    return
  }

  isLoading.value = false
  scrollToBottom()
}

const simulateResponse = async (question: string) => {
  await new Promise(resolve => setTimeout(resolve, 1500))

  let response: Message

  if (question.includes('中考政策') || question.includes('政策')) {
    response = {
      id: Date.now(),
      content: '',
      time: Date.now(),
      isSelf: false,
      type: 'card',
      data: {
        title: '2024年云南省中考政策要点',
        content: '1. 总分750分，考试科目包括语文、数学、英语、物理、化学、道德与法治、历史、体育。\n2. 普通高中录取采用平行志愿模式。\n3. 少数民族考生可享受加分政策。\n4. 特长生招生比例不超过5%。',
        link: '/policy'
      }
    }
  } else if (question.includes('学校') || question.includes('推荐')) {
    response = {
      id: Date.now(),
      content: '',
      time: Date.now(),
      isSelf: false,
      type: 'list',
      data: {
        items: [
          '云南师范大学附属中学 - 重点中学，升学率高',
          '昆明市第一中学 - 历史悠久，师资雄厚',
          '曲靖市第一中学 - 教学质量优异',
          '玉溪市第一中学 - 校园环境优美',
          '红河州第一中学 - 近年崛起的名校'
        ]
      }
    }
  } else if (question.includes('学习计划') || question.includes('计划')) {
    response = {
      id: Date.now(),
      content: '',
      time: Date.now(),
      isSelf: false,
      type: 'chart',
      data: {
        title: '每日学习时间分配建议',
        bars: [
          { label: '语文', value: 20, color: '#ef4444' },
          { label: '数学', value: 25, color: '#3b82f6' },
          { label: '英语', value: 20, color: '#10b981' },
          { label: '物理', value: 15, color: '#f59e0b' },
          { label: '其他', value: 20, color: '#8b5cf6' }
        ]
      }
    }
  } else if (question.includes('成绩') || question.includes('分析')) {
    response = {
      id: Date.now(),
      content: '',
      time: Date.now(),
      isSelf: false,
      type: 'card',
      data: {
        title: '成绩分析报告',
        content: '根据您最近的模拟考试成绩分析：\n\n📈 优势科目：数学（92分）、物理（88分）\n\n⚠️ 需要加强：英语听力、语文作文\n\n💡 建议：每天增加30分钟听力练习，每周写一篇作文',
        link: '/analysis'
      }
    }
  } else if (question.includes('志愿') || question.includes('填报')) {
    response = {
      id: Date.now(),
      content: '志愿填报需要综合考虑以下因素：\n\n1. 您的模拟考试成绩排名\n2. 各学校往年录取分数线\n3. 您的兴趣爱好和未来规划\n4. 家庭所在地和交通情况\n\n建议使用我们的志愿填报工具进行智能分析！',
      time: Date.now(),
      isSelf: false,
      type: 'text'
    }
  } else if (question.includes('心理') || question.includes('压力')) {
    response = {
      id: Date.now(),
      content: '面对中考压力，我有一些建议：\n\n1. 合理安排作息，保证充足睡眠\n2. 适当运动，放松身心\n3. 与家人朋友沟通交流\n4. 制定合理的学习目标，不要给自己太大压力\n\n记住，您不是一个人在战斗！💪',
      time: Date.now(),
      isSelf: false,
      type: 'text'
    }
  } else {
    response = {
      id: Date.now(),
      content: '感谢您的提问！我来帮您解答。\n\n关于您问的"' + question + '"，这是一个很好的问题。\n\n根据我的知识库，为您提供以下信息：\n\n- 如果您想了解中考政策，可以点击左侧的「政策查询」\n- 如果您想了解学校信息，可以点击「学校对比」\n- 如果需要学习建议，我可以帮您制定学习计划\n\n请问您还有其他问题吗？',
      time: Date.now(),
      isSelf: false,
      type: 'text'
    }
  }

  messages.value.push(response)
  isLoading.value = false
  scrollToBottom()
}

const handleFeatureClick = (feature: Feature) => {
  if (feature.action === 'policy') {
    sendQuickQuestion('中考政策')
  } else if (feature.action === 'school') {
    sendQuickQuestion('推荐一些好的高中')
  } else if (feature.action === 'study') {
    sendQuickQuestion('制定学习计划')
  } else if (feature.action === 'analysis') {
    sendQuickQuestion('分析我的成绩')
  } else if (feature.action === 'volunteer') {
    sendQuickQuestion('志愿填报建议')
  } else if (feature.action === 'mental') {
    sendQuickQuestion('缓解学习压力')
  }
}

const toggleAutoReply = () => {
  autoReply.value = !autoReply.value
}

const toggleVoiceInput = () => {
  voiceInput.value = !voiceInput.value
}

const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
}

const clearChat = () => {
  messages.value = []
  const welcomeMessage: Message = {
    id: Date.now(),
    content: '您好！我是您的智能助手，很高兴为您服务。\n\n我可以帮您：\n• 查询中考政策和录取信息\n• 推荐合适的学校\n• 制定个性化学习计划\n• 分析学习成绩\n• 提供志愿填报建议\n\n有什么问题尽管问我吧！',
    time: Date.now(),
    isSelf: false,
    type: 'text'
  }
  messages.value.push(welcomeMessage)
}

const createChatSession = async () => {
  try {
    const response = await apiClient.post('/chat/sessions', {
      user_id: 'default_user'
    })
    if (response.data && response.data.success) {
      currentSessionId.value = response.data.data.session_id
      console.log('创建聊天会话成功，ID:', currentSessionId.value)
    }
  } catch (error) {
    console.error('创建会话失败:', error)
  }
}

onMounted(() => {
  createChatSession()

  const welcomeMessage: Message = {
    id: Date.now(),
    content: '您好！我是您的智能助手，很高兴为您服务。\n\n我可以帮您：\n• 查询中考政策和录取信息\n• 推荐合适的学校\n• 制定个性化学习计划\n• 分析学习成绩\n• 提供志愿填报建议\n\n有什么问题尽管问我吧！',
    time: Date.now(),
    isSelf: false,
    type: 'text'
  }
  messages.value.push(welcomeMessage)
})

onUnmounted(() => {
  // 组件卸载时可以保存会话状态
})
</script>

<style scoped>
/* ==================== 整体布局 ==================== */
.smart-assistant {
  display: flex;
  height: 100%;
  background: var(--wx-bg);
}

/* ==================== 聊天容器 ==================== */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--wx-bg);
  min-width: 0;
  border-right: 1px solid var(--wx-border-light);
}

/* ==================== 顶部栏 ==================== */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--wx-spacing-xl);
  height: 56px;
  background: var(--wx-bg-white);
  border-bottom: 1px solid var(--wx-border-light);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-md);
}

.assistant-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--wx-radius-sm);
  background: var(--wx-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.assistant-info h3 {
  margin: 0;
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-text-primary);
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  margin: 2px 0 0;
}

.status.online {
  color: var(--wx-primary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--wx-bg-active);
}

.status.online .status-dot {
  background: var(--wx-primary);
}

.header-right {
  display: flex;
  gap: var(--wx-spacing-sm);
}

.wx-btn-text {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  border-radius: var(--wx-radius-sm);
  color: var(--wx-text-secondary);
  font-size: var(--wx-font-size-sm);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
}

.wx-btn-text:hover {
  background: var(--wx-bg-hover);
  color: var(--wx-text-primary);
}

/* ==================== 快捷问题 ==================== */
.quick-questions {
  padding: var(--wx-spacing-md) var(--wx-spacing-xl);
  border-bottom: 1px solid var(--wx-border-light);
  flex-shrink: 0;
}

.section-title {
  font-size: var(--wx-font-size-sm);
  font-weight: 500;
  color: var(--wx-text-secondary);
  margin-bottom: var(--wx-spacing-sm);
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
}

.quick-tag {
  cursor: pointer;
  background: var(--wx-bg);
  border: 1px solid var(--wx-border-light);
  padding: 4px 12px;
  border-radius: var(--wx-radius-round);
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
  transition: all var(--wx-transition-fast);
  user-select: none;
}

.quick-tag:hover {
  background: var(--wx-primary-light);
  border-color: var(--wx-primary);
  color: var(--wx-primary);
}

/* ==================== 消息列表 ==================== */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--wx-spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--wx-spacing-lg);
}

/* ==================== 消息样式 ==================== */
.chat-message {
  display: flex;
  gap: var(--wx-spacing-sm);
  max-width: 70%;
  animation: wx-slide-up 0.25s ease;
}

.chat-message.mine {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.chat-message .msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--wx-radius-sm);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.chat-message.mine .msg-avatar {
  background: var(--wx-primary);
  color: var(--wx-text-white);
}

.chat-message.other .msg-avatar {
  background: var(--wx-bg-active);
  color: var(--wx-text-secondary);
}

.msg-content-wrapper {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-message.mine .msg-content-wrapper {
  align-items: flex-end;
}

.chat-message.other .msg-content-wrapper {
  align-items: flex-start;
}

.chat-message .msg-bubble {
  position: relative;
  padding: 10px var(--wx-spacing-md);
  border-radius: var(--wx-radius-sm);
  font-size: var(--wx-font-size-md);
  line-height: var(--wx-line-height);
  word-break: break-word;
}

.chat-message.mine .msg-bubble {
  background: var(--wx-primary);
  color: var(--wx-text-white);
  border-top-right-radius: 2px;
}

.chat-message.other .msg-bubble {
  background: var(--wx-bg-white);
  color: var(--wx-text-primary);
  border-top-left-radius: 2px;
  box-shadow: var(--wx-shadow-sm);
}

.chat-message .msg-time {
  font-size: 11px;
  color: var(--wx-text-muted);
  margin-top: 4px;
}

.msg-bubble p {
  margin: 0;
  white-space: pre-line;
}

/* ==================== 卡片消息 ==================== */
.info-card {
  padding: 4px 0;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}

.card-content {
  font-size: 13px;
  white-space: pre-line;
  line-height: 1.7;
  opacity: 0.9;
}

.card-link {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.mine .card-link {
  border-top-color: rgba(255, 255, 255, 0.2);
}

.card-link a {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}

.other .card-link a {
  color: var(--wx-primary);
}

.mine .card-link a {
  color: var(--wx-text-white);
}

/* ==================== 列表消息 ==================== */
.answer-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.answer-list li {
  padding: 6px 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.answer-list li:first-child {
  padding-top: 0;
}

.answer-list li:last-child {
  padding-bottom: 0;
}

.list-number {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.other .list-number {
  background: var(--wx-primary);
  color: var(--wx-text-white);
}

.mine .list-number {
  background: rgba(255, 255, 255, 0.3);
  color: var(--wx-text-white);
}

/* ==================== 图表消息 ==================== */
.mini-chart {
  padding: 4px 0;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.chart-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chart-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-label {
  width: 36px;
  font-size: 12px;
  flex-shrink: 0;
}

.other .bar-label {
  color: var(--wx-text-secondary);
}

.bar-container {
  flex: 1;
  height: 10px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 5px;
  overflow: hidden;
}

.mine .bar-container {
  background: rgba(255, 255, 255, 0.2);
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.bar-value {
  width: 36px;
  font-size: 12px;
  text-align: right;
  flex-shrink: 0;
}

.other .bar-value {
  color: var(--wx-text-secondary);
}

/* ==================== 加载/空状态 ==================== */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: var(--wx-spacing-md) 0;
}

.loading-indicator span {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: var(--wx-text-muted);
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: var(--wx-spacing-lg);
}

.empty-chat h3 {
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-sm);
}

.empty-chat p {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-muted);
}

/* ==================== 输入区域 ==================== */
.chat-input-area {
  padding: var(--wx-spacing-md) var(--wx-spacing-xl);
  background: var(--wx-bg-white);
  border-top: 1px solid var(--wx-border-light);
  display: flex;
  gap: var(--wx-spacing-md);
  align-items: flex-end;
  flex-shrink: 0;
}

.chat-input-area .input-wrapper {
  flex: 1;
}

.chat-input-area textarea {
  width: 100%;
  min-height: 40px;
  max-height: 120px;
  padding: 10px var(--wx-spacing-md);
  border: 1px solid var(--wx-border);
  border-radius: var(--wx-radius-sm);
  background: var(--wx-bg);
  color: var(--wx-text-primary);
  font-size: var(--wx-font-size-md);
  font-family: var(--wx-font-family);
  outline: none;
  resize: none;
  transition: border-color var(--wx-transition-fast);
  box-sizing: border-box;
  line-height: var(--wx-line-height);
}

.chat-input-area textarea:focus {
  border-color: var(--wx-border-focus);
}

.chat-input-area textarea::placeholder {
  color: var(--wx-text-placeholder);
}

.chat-input-area textarea:disabled {
  background: var(--wx-bg);
  color: var(--wx-text-muted);
  cursor: not-allowed;
}

.chat-input-area .send-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--wx-radius-sm);
  background: var(--wx-primary);
  color: var(--wx-text-white);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: background var(--wx-transition-fast);
  flex-shrink: 0;
}

.chat-input-area .send-btn:hover {
  background: var(--wx-primary-hover);
}

.chat-input-area .send-btn:disabled {
  background: var(--wx-bg-active);
  color: var(--wx-text-muted);
  cursor: not-allowed;
}

/* ==================== 右侧功能菜单 ==================== */
.function-menu {
  width: 240px;
  padding: var(--wx-spacing-xl);
  flex-shrink: 0;
}

.menu-header h3 {
  margin: 0 0 var(--wx-spacing-lg) 0;
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-text-primary);
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: var(--wx-spacing-sm);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-md);
  padding: 12px;
  background: var(--wx-bg-white);
  border-radius: var(--wx-radius-sm);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
  border: 1px solid var(--wx-border-light);
}

.menu-item:hover {
  background: var(--wx-primary-light);
  border-color: var(--wx-primary);
}

.feature-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--wx-radius-sm);
  background: var(--wx-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.feature-info {
  flex: 1;
  min-width: 0;
}

.feature-title {
  font-size: var(--wx-font-size-md);
  font-weight: 500;
  color: var(--wx-text-primary);
  margin-bottom: 2px;
}

.feature-desc {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow {
  color: var(--wx-text-muted);
  flex-shrink: 0;
}

/* ==================== 设置弹窗 ==================== */
.settings-content {
  padding: 10px 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--wx-border-light);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item span {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-primary);
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .chat-message {
    max-width: 85%;
  }

  .function-menu {
    display: none;
  }

  .chat-header {
    padding: 0 var(--wx-spacing-md);
  }

  .chat-messages {
    padding: var(--wx-spacing-md);
  }

  .quick-questions {
    padding: var(--wx-spacing-md);
  }

  .chat-input-area {
    padding: var(--wx-spacing-sm) var(--wx-spacing-md);
  }
}

@media (max-width: 480px) {
  .chat-message {
    max-width: 90%;
  }
}
</style>