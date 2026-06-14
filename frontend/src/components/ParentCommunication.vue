<template>
  <div class="parent-communication">
    <!-- 消息列表 -->
    <div class="message-list">
      <div class="list-header">
        <h3>👨‍👩‍👧 家校沟通</h3>
        <el-button size="small" type="primary" @click="showNewMessageModal = true">
          <el-icon><ChatDotRound /></el-icon>
          发送消息
        </el-button>
      </div>
      
      <div class="tabs-container">
        <el-tabs v-model="activeTab" class="communication-tabs">
          <el-tab-pane label="全部" name="all">
            <div class="conversation-list">
              <div 
                v-for="conversation in allConversations" 
                :key="conversation.id"
                class="conversation-item"
                :class="{ active: selectedConversation?.id === conversation.id }"
                @click="selectConversation(conversation)"
              >
                <div class="avatar-wrapper">
                  <div class="avatar" :style="{ background: conversation.avatarColor }">
                    {{ conversation.avatar }}
                  </div>
                  <span v-if="conversation.unreadCount > 0" class="unread-badge">{{ conversation.unreadCount }}</span>
                </div>
                <div class="conversation-info">
                  <div class="conversation-title">{{ conversation.name }}</div>
                  <div class="conversation-preview">{{ conversation.lastMessage }}</div>
                </div>
                <div class="conversation-meta">
                  <div class="message-time">{{ formatTime(conversation.lastTime) }}</div>
                  <span v-if="conversation.type === 'parent'" class="type-badge parent">家长</span>
                  <span v-else class="type-badge teacher">老师</span>
                </div>
              </div>
              <div v-if="allConversations.length === 0" class="empty-state">
                <el-empty description="暂无消息" />
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="家长消息" name="parent">
            <div class="conversation-list">
              <div 
                v-for="conversation in parentConversations" 
                :key="conversation.id"
                class="conversation-item"
                :class="{ active: selectedConversation?.id === conversation.id }"
                @click="selectConversation(conversation)"
              >
                <div class="avatar-wrapper">
                  <div class="avatar" :style="{ background: conversation.avatarColor }">
                    {{ conversation.avatar }}
                  </div>
                  <span v-if="conversation.unreadCount > 0" class="unread-badge">{{ conversation.unreadCount }}</span>
                </div>
                <div class="conversation-info">
                  <div class="conversation-title">{{ conversation.name }}</div>
                  <div class="conversation-preview">{{ conversation.lastMessage }}</div>
                </div>
                <div class="conversation-meta">
                  <div class="message-time">{{ formatTime(conversation.lastTime) }}</div>
                </div>
              </div>
              <div v-if="parentConversations.length === 0" class="empty-state">
                <el-empty description="暂无家长消息" />
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="老师消息" name="teacher">
            <div class="conversation-list">
              <div 
                v-for="conversation in teacherConversations" 
                :key="conversation.id"
                class="conversation-item"
                :class="{ active: selectedConversation?.id === conversation.id }"
                @click="selectConversation(conversation)"
              >
                <div class="avatar-wrapper">
                  <div class="avatar" :style="{ background: conversation.avatarColor }">
                    {{ conversation.avatar }}
                  </div>
                  <span v-if="conversation.unreadCount > 0" class="unread-badge">{{ conversation.unreadCount }}</span>
                </div>
                <div class="conversation-info">
                  <div class="conversation-title">{{ conversation.name }}</div>
                  <div class="conversation-preview">{{ conversation.lastMessage }}</div>
                </div>
                <div class="conversation-meta">
                  <div class="message-time">{{ formatTime(conversation.lastTime) }}</div>
                </div>
              </div>
              <div v-if="teacherConversations.length === 0" class="empty-state">
                <el-empty description="暂无老师消息" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    
    <!-- 聊天窗口 -->
    <div class="chat-window">
      <div v-if="selectedConversation" class="chat-content">
        <div class="chat-header">
          <div class="header-info">
            <div class="avatar" :style="{ background: selectedConversation.avatarColor }">
              {{ selectedConversation.avatar }}
            </div>
            <div class="header-text">
              <div class="chat-title">{{ selectedConversation.name }}</div>
              <div class="chat-subtitle">
                <span v-if="selectedConversation.type === 'parent'">家长</span>
                <span v-else>{{ selectedConversation.subject }}</span>
              </div>
            </div>
          </div>
          <div class="header-actions">
            <el-button size="small" @click="toggleMute">
              <el-icon><component :is="isMuted ? BellFilled : Bell" /></el-icon>
              {{ isMuted ? '取消静音' : '静音' }}
            </el-button>
            <el-button size="small" @click="showConversationSettings = true">
              <el-icon><Setting /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="message-container" ref="messageContainer">
          <div 
            v-for="message in currentMessages" 
            :key="message.id"
            class="message-item"
            :class="{ self: message.isSelf }"
          >
            <div class="message-avatar" :style="{ background: message.isSelf ? '#667eea' : selectedConversation.avatarColor }">
              {{ message.isSelf ? '我' : selectedConversation.avatar }}
            </div>
            <div class="message-content">
              <div class="message-bubble" :class="{ self: message.isSelf }">
                {{ message.content }}
              </div>
              <div class="message-time">{{ formatTime(message.time) }}</div>
            </div>
          </div>
          <div v-if="currentMessages.length === 0" class="empty-chat">
            <el-empty description="开始聊天吧" />
          </div>
        </div>
        
        <div class="chat-input">
          <el-input 
            v-model="inputMessage" 
            placeholder="输入消息..."
            class="message-input"
            @keyup.enter="sendMessage"
          />
          <div class="input-actions">
            <el-button size="small"><el-icon><Paperclip /></el-icon></el-button>
            <el-button size="small"><el-icon><User /></el-icon></el-button>
            <el-button size="small" type="primary" @click="sendMessage">发送</el-button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-chat-window">
        <div class="empty-content">
          <div class="empty-icon">💬</div>
          <h3>选择一个对话开始聊天</h3>
          <p>与家长或老师进行沟通交流</p>
        </div>
      </div>
    </div>
    
    <!-- 发送新消息弹窗 -->
    <el-dialog title="发送新消息" v-model="showNewMessageModal" width="400px">
      <div class="form-item">
        <label>选择收件人类型</label>
        <el-select v-model="newMessage.type" placeholder="请选择">
          <el-option label="家长" value="parent" />
          <el-option label="老师" value="teacher" />
        </el-select>
      </div>
      <div class="form-item">
        <label>收件人姓名</label>
        <el-input v-model="newMessage.name" placeholder="请输入姓名" />
      </div>
      <div class="form-item" v-if="newMessage.type === 'teacher'">
        <label>学科</label>
        <el-select v-model="newMessage.subject" placeholder="请选择学科">
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
      </div>
      <div class="form-item">
        <label>消息内容</label>
        <textarea v-model="newMessage.content" placeholder="请输入消息内容" rows="4" class="el-textarea" />
      </div>
      <template #footer>
        <el-button @click="showNewMessageModal = false">取消</el-button>
        <el-button type="primary" @click="sendNewMessage">发送</el-button>
      </template>
    </el-dialog>
    
    <!-- 对话设置弹窗 -->
    <el-dialog title="对话设置" v-model="showConversationSettings" width="400px">
      <div class="settings-item">
        <span>消息通知</span>
        <el-switch :value="!isMuted" @change="toggleMute" />
      </div>
      <div class="settings-item">
        <span>置顶对话</span>
        <el-switch :value="isPinned" @change="togglePin" />
      </div>
      <div class="settings-item">
        <span>免打扰时间</span>
        <el-time-picker v-model="doNotDisturbTime" range format="HH:mm" />
      </div>
      <template #footer>
        <el-button @click="showConversationSettings = false">关闭</el-button>
        <el-button type="danger" @click="deleteConversation">删除对话</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { 
  ChatDotRound, Bell, BellFilled, Setting, 
  Paperclip, User 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { apiClient } from '../api'

interface Conversation {
  id: number
  name: string
  avatar: string
  avatarColor: string
  type: 'parent' | 'teacher'
  subject?: string
  lastMessage: string
  lastTime: number
  unreadCount: number
}

interface Message {
  id: number
  content: string
  time: number
  isSelf: boolean
}

interface NewMessage {
  type: 'parent' | 'teacher'
  name: string
  subject: string
  content: string
}

const activeTab = ref('all')
const selectedConversation = ref<Conversation | null>(null)
const inputMessage = ref('')
const isMuted = ref(false)
const isPinned = ref(false)
const doNotDisturbTime = ref<Date[]>([])
const showNewMessageModal = ref(false)
const showConversationSettings = ref(false)
const messageContainer = ref<HTMLElement | null>(null)

const newMessage = ref<NewMessage>({
  type: 'parent',
  name: '',
  subject: '',
  content: ''
})

const conversations = ref<Conversation[]>([
  {
    id: 1,
    name: '张小明家长',
    avatar: '张',
    avatarColor: '#f59e0b',
    type: 'parent',
    lastMessage: '老师您好，请问小明最近学习情况怎么样？',
    lastTime: Date.now() - 3600000,
    unreadCount: 2
  },
  {
    id: 2,
    name: '李老师',
    avatar: '李',
    avatarColor: '#10b981',
    type: 'teacher',
    subject: '数学',
    lastMessage: '明天的模拟考试记得提醒孩子准备好文具',
    lastTime: Date.now() - 7200000,
    unreadCount: 0
  },
  {
    id: 3,
    name: '王芳家长',
    avatar: '王',
    avatarColor: '#ef4444',
    type: 'parent',
    lastMessage: '收到，谢谢老师的关心！',
    lastTime: Date.now() - 14400000,
    unreadCount: 1
  },
  {
    id: 4,
    name: '陈老师',
    avatar: '陈',
    avatarColor: '#8b5cf6',
    type: 'teacher',
    subject: '英语',
    lastMessage: '下周将进行听力测试，请提前准备',
    lastTime: Date.now() - 21600000,
    unreadCount: 0
  },
  {
    id: 5,
    name: '刘伟家长',
    avatar: '刘',
    avatarColor: '#06b6d4',
    type: 'parent',
    lastMessage: '好的，我们会督促孩子复习的',
    lastTime: Date.now() - 28800000,
    unreadCount: 0
  }
])

const messagesMap = ref<Record<number, Message[]>>({
  1: [
    { id: 1, content: '家长您好，小明最近学习状态不错，进步明显！', time: Date.now() - 7200000, isSelf: false },
    { id: 2, content: '太好了，谢谢老师！', time: Date.now() - 7000000, isSelf: true },
    { id: 3, content: '老师您好，请问小明最近学习情况怎么样？', time: Date.now() - 3600000, isSelf: false },
    { id: 4, content: '小明最近在数学方面进步很大，特别是函数部分', time: Date.now() - 3500000, isSelf: true },
    { id: 5, content: '真的吗？太好了！我们在家也会继续督促他', time: Date.now() - 3400000, isSelf: false }
  ],
  2: [
    { id: 1, content: '李老师好，孩子最近数学学习有什么需要注意的吗？', time: Date.now() - 10800000, isSelf: false },
    { id: 2, content: '最近主要是函数部分需要加强练习', time: Date.now() - 10700000, isSelf: true },
    { id: 3, content: '明天的模拟考试记得提醒孩子准备好文具', time: Date.now() - 7200000, isSelf: false }
  ],
  3: [
    { id: 1, content: '王芳同学这次月考成绩有所下滑，需要多加关注', time: Date.now() - 17200000, isSelf: true },
    { id: 2, content: '收到，谢谢老师的关心！', time: Date.now() - 14400000, isSelf: false }
  ],
  4: [
    { id: 1, content: '下周将进行听力测试，请提前准备', time: Date.now() - 21600000, isSelf: false }
  ],
  5: [
    { id: 1, content: '刘伟最近作业完成情况不太好，需要督促', time: Date.now() - 32400000, isSelf: true },
    { id: 2, content: '好的，我们会督促孩子复习的', time: Date.now() - 28800000, isSelf: false }
  ]
})

const allConversations = computed(() => {
  return [...conversations.value].sort((a, b) => b.lastTime - a.lastTime)
})

const parentConversations = computed(() => {
  return conversations.value
    .filter(c => c.type === 'parent')
    .sort((a, b) => b.lastTime - a.lastTime)
})

const teacherConversations = computed(() => {
  return conversations.value
    .filter(c => c.type === 'teacher')
    .sort((a, b) => b.lastTime - a.lastTime)
})

const currentMessages = computed(() => {
  if (!selectedConversation.value) return []
  return messagesMap.value[selectedConversation.value.id] || []
})

const formatTime = (timestamp: number) => {
  const now = Date.now()
  const diff = now - timestamp
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  const date = new Date(timestamp)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  
  return `${month}月${day}日 ${hour}:${minute}`
}

const selectConversation = (conversation: Conversation) => {
  selectedConversation.value = conversation
  conversation.unreadCount = 0
  
  nextTick(() => {
    scrollToBottom()
  })
}

const scrollToBottom = () => {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || !selectedConversation.value) return
  
  const message: Message = {
    id: Date.now(),
    content: inputMessage.value,
    time: Date.now(),
    isSelf: true
  }
  
  // 发送到后端
  try {
    await apiClient.post('/messages/send', {
      conversation_id: selectedConversation.value.id,
      content: inputMessage.value,
      sender_type: 'teacher'
    })
  } catch (error) {
    console.error('发送消息失败:', error)
  }
  
  if (!messagesMap.value[selectedConversation.value.id]) {
    messagesMap.value[selectedConversation.value.id] = []
  }
  
  messagesMap.value[selectedConversation.value.id].push(message)
  selectedConversation.value.lastMessage = inputMessage.value
  selectedConversation.value.lastTime = Date.now()
  
  inputMessage.value = ''
  
  nextTick(() => {
    scrollToBottom()
  })
}

const sendNewMessage = async () => {
  if (!newMessage.value.name || !newMessage.value.content) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  // 发送到后端
  try {
    const response = await apiClient.post('/messages/conversation', {
      name: newMessage.value.name,
      type: newMessage.value.type,
      subject: newMessage.value.type === 'teacher' ? newMessage.value.subject : undefined,
      content: newMessage.value.content
    })
    
    if (response.data && response.data.success) {
      const colors = ['#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899']
      const color = colors[Math.floor(Math.random() * colors.length)]
      const avatar = newMessage.value.name.charAt(0)
      
      const conversation: Conversation = {
        id: response.data.data.conversation_id || Date.now(),
        name: newMessage.value.name,
        avatar,
        avatarColor: color,
        type: newMessage.value.type,
        subject: newMessage.value.type === 'teacher' ? newMessage.value.subject : undefined,
        lastMessage: newMessage.value.content,
        lastTime: Date.now(),
        unreadCount: 0
      }
      
      conversations.value.unshift(conversation)
      messagesMap.value[conversation.id] = [{
        id: Date.now(),
        content: newMessage.value.content,
        time: Date.now(),
        isSelf: true
      }]
      
      showNewMessageModal.value = false
      newMessage.value = { type: 'parent', name: '', subject: '', content: '' }
      
      ElMessage.success('消息发送成功')
    }
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error('发送失败，请稍后重试')
  }
}

const toggleMute = () => {
  isMuted.value = !isMuted.value
}

const togglePin = () => {
  isPinned.value = !isPinned.value
}

const deleteConversation = () => {
  if (!selectedConversation.value) return
  
  conversations.value = conversations.value.filter(
    c => c.id !== selectedConversation.value?.id
  )
  delete messagesMap.value[selectedConversation.value.id]
  selectedConversation.value = null
  showConversationSettings.value = false
  
  ElMessage.success('对话已删除')
}

watch(selectedConversation, () => {
  nextTick(() => {
    scrollToBottom()
  })
})
</script>

<style scoped>
.parent-communication {
  display: flex;
  height: 100%;
  background: #0f0f23;
}

.message-list {
  width: 380px;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.tabs-container {
  flex: 1;
  overflow: hidden;
}

.communication-tabs {
  height: 100%;
}

.conversation-list {
  padding: 12px;
  max-height: calc(100% - 40px);
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.conversation-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.conversation-item.active {
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.unread-badge {
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
  padding: 0 5px;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.conversation-preview {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-meta {
  text-align: right;
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}

.type-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}

.type-badge.parent {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.type-badge.teacher {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.chat-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.message-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-item.self {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}

.message-content {
  max-width: 60%;
}

.message-bubble {
  background: rgba(255, 255, 255, 0.1);
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
  color: #fff;
}

.message-bubble.self {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 6px;
}

.message-item.self .message-time {
  text-align: right;
}

.empty-chat {
  padding: 60px 20px;
  text-align: center;
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 12px;
  align-items: center;
}

.message-input {
  flex: 1;
}

.input-actions {
  display: flex;
  gap: 8px;
}

.empty-chat-window {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.empty-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
}

.settings-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.settings-item:last-child {
  border-bottom: none;
}

.settings-item span {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}
</style>