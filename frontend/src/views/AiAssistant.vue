<template>
  <div class="chat-page">
    <!-- 侧边栏 - 历史对话 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="createNewChat">
          <el-icon><Plus /></el-icon>
          <span v-if="!sidebarCollapsed">新建对话</span>
        </button>
        <button class="toggle-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </button>
      </div>

      <div class="chat-list" v-if="!sidebarCollapsed">
        <div class="list-header">
          <span>历史对话</span>
        </div>
        <div class="chat-items">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="chat-item"
            :class="{ active: currentSessionId === session.id }"
            @click="loadSession(session)"
          >
            <el-icon><ChatDotRound /></el-icon>
            <span class="chat-title">{{ session.title }}</span>
            <button class="delete-btn" @click.stop="deleteSession(session.id)">
              <el-icon><Delete /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主聊天区域 -->
    <main class="chat-container">
      <!-- 顶部标题栏 -->
      <div class="chat-header">
        <div class="header-left">
          <span class="logo-icon">🦐</span>
          <span class="logo-text">小龙虾择校</span>
        </div>
        <div class="header-right">
          <button class="func-toggle-btn" @click="showFuncPanel = !showFuncPanel" :class="{ active: showFuncPanel }">
            <el-icon><Grid /></el-icon>
          </button>
          <span class="user-info" v-if="isLoggedIn && userInfo && typeof userInfo === 'object' && !Array.isArray(userInfo)">
            <el-avatar :size="28" :src="userInfo.avatar || defaultAvatar" />
            <span class="username">{{ userInfo.nickname || '用户' }}</span>
          </span>
          <el-button v-else size="small" type="primary" @click="goLogin">登录</el-button>
        </div>
      </div>

      <!-- 聊天主体 -->
      <div class="chat-body">
        <div class="chat-messages" ref="messagesContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-area">
            <div class="welcome-icon">🦐</div>
            <h2>你好！我是小龙虾择校助手</h2>
            <p>我可以帮助你了解中考政策、学校选择、志愿填报等问题</p>
          </div>

          <!-- 消息列表 -->
          <template v-for="msg in displayedMessages" :key="msg.id">
            <div class="chat-message" :class="msg.role === 'user' ? 'mine' : 'other'">
              <div class="msg-avatar">
                <span v-if="msg.role === 'user'">👤</span>
                <span v-else>🦐</span>
              </div>
              <div class="msg-content-wrapper">
                <div class="msg-bubble">
                  <div v-if="msg.role === 'user'">{{ msg.content }}</div>
                  <div v-else>
                    <div v-html="msg.displayContent"></div>
                    <div v-if="msg.loading" class="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
                <div class="msg-time">{{ formatMessageTime(msg) }}</div>
              </div>
            </div>
          </template>
        </div>

        <!-- 快捷功能面板 -->
        <Transition name="slide-fade">
          <aside v-if="showFuncPanel" class="func-panel">
            <div class="func-header">
              <span class="func-title">快捷功能</span>
              <button class="close-btn" @click="showFuncPanel = false">
                <el-icon><Close /></el-icon>
              </button>
            </div>
            <div class="func-grid">
              <div
                v-for="item in quickFunctions"
                :key="item.name"
                class="func-card"
                @click="handleFuncClick(item)"
              >
                <div class="func-icon">{{ item.icon }}</div>
                <div class="func-info">
                  <div class="func-name">{{ item.name }}</div>
                  <div class="func-desc">{{ item.desc }}</div>
                </div>
              </div>
            </div>
          </aside>
        </Transition>
      </div>

      <!-- 微信风格输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <textarea
            v-model="inputMessage"
            placeholder="输入你的问题..."
            :disabled="loading"
            @keydown="handleKeydown"
            ref="inputTextarea"
            rows="1"
          ></textarea>
        </div>
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="!inputMessage.trim() || loading"
        >
          <el-icon v-if="!loading"><Promotion /></el-icon>
          <el-icon v-else class="animate-spin"><Loading /></el-icon>
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Fold, Expand, ChatDotRound, Delete, Promotion, Grid, Close, Loading } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useUserStore } from '@/store'
import { useSchoolStore } from '@/store'
import { aiServiceApi } from '@/api'
import { schoolApi } from '@/api'

marked.setOptions({ breaks: true, gfm: true })

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const schoolStore = useSchoolStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const sidebarCollapsed = ref(false)
const showFuncPanel = ref(false)
const sessions = ref([])
const currentSessionId = ref(null)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const inputTextarea = ref(null)
const sessionId = ref(null)
const streamingMessageId = ref(null)
const schoolListLoaded = ref(false)

const quickFunctions = [
  { icon: '📊', name: '分数线查询', desc: '查询学校录取分数线', question: '师大附中录取分数线是多少？' },
  { icon: '🏫', name: '学校推荐', desc: '根据条件推荐学校', question: '昆明户籍可以报考哪些学校？' },
  { icon: '🎯', name: '估分择校', desc: '根据估分推荐学校', question: '估分680分推荐什么学校？' },
  { icon: '📝', name: '志愿填报', desc: '志愿填报技巧指导', question: '志愿填报有什么技巧？' },
  { icon: '📚', name: '学校对比', desc: '对比不同学校信息', question: '师大附中和昆一中哪个好？' },
  { icon: '💡', name: '政策解读', desc: '中考政策解读分析', question: '2026年中考政策有什么变化？' },
  { icon: '📅', name: '学习计划', desc: '制定个性化学习计划', question: '如何制定中考复习计划？' },
  { icon: '📈', name: '成绩分析', desc: '分析成绩并提供建议', question: '我的成绩如何提高？' },
  { icon: '🧠', name: '学习方法', desc: '推荐有效的学习方法', question: '有哪些有效的中考复习方法？' },
  { icon: '🏠', name: '学校环境', desc: '了解学校校园环境', question: '昆三中的校园环境怎么样？' },
  { icon: '👨‍🏫', name: '师资力量', desc: '了解学校师资情况', question: '云师大附中的师资力量如何？' },
  { icon: '💰', name: '学费收费', desc: '查询学校收费标准', question: '民办高中的收费标准是多少？' },
  { icon: '🚗', name: '交通情况', desc: '了解学校交通情况', question: '昆一中的交通方便吗？' },
  { icon: '🍽️', name: '食宿条件', desc: '了解学校食宿条件', question: '师大附中的宿舍条件怎么样？' },
  { icon: '🎉', name: '社团活动', desc: '了解学校社团活动', question: '昆八中有哪些社团活动？' },
  { icon: '📞', name: '联系咨询', desc: '获取学校联系方式', question: '如何联系云大附中？' },
]

const messageCache = ref(new Map())
const scrollTimeout = ref(null)

const displayedMessages = computed(() => {
  return messages.value.map(msg => ({
    ...msg,
    displayContent: msg.role === 'assistant' && msg.content ? marked.parse(msg.content) : msg.content
  }))
})

const formatMessageTime = (msg) => {
  const date = new Date(msg.timestamp || Date.now())
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  return `${hour}:${minute}`
}

const scrollToBottom = () => {
  if (scrollTimeout.value) clearTimeout(scrollTimeout.value)
  scrollTimeout.value = setTimeout(() => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  }, 50)
}

const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2, 9)

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// ==================== 学校数据库查询 ====================

const getSchoolFromDB = async (schoolName) => {
  try {
    if (!schoolListLoaded.value) {
      await schoolStore.fetchSchoolList({ page: 1, size: 100 })
      schoolListLoaded.value = true
    }

    const schools = schoolStore.getSchoolList
    const lowerName = schoolName.toLowerCase()

    if (!Array.isArray(schools)) {
      console.warn('schoolStore.getSchoolList 不是数组:', schools)
      return null
    }

    for (const school of schools) {
      const schoolNameLower = (school.name || '').toLowerCase()
      if (schoolNameLower.includes(lowerName) || lowerName.includes(schoolNameLower)) {
        return school
      }
    }

    return null
  } catch (error) {
    console.error('查询学校数据库失败:', error)
    return null
  }
}

const generateSchoolResponse = (school) => {
  const isPublic = school.is_public === 1 || school.nature === '公办' || school.tuition === 0

  let response = `**${school.name}** 🏛️\n\n【基本信息】\n`

  if (school.type_name || school.type) {
    response += `- **类型**：${school.type_name || (school.type === 2 ? '重点高中' : school.type === 4 ? '民办学校' : '普通高中')}\n`
  }

  response += `- **性质**：${isPublic ? '公办' : '民办'}\n`

  if (school.level) {
    response += `- **等级**：${school.level}\n`
  }

  if (school.prefecture || school.city) {
    const prefectureMap = {
      'km': '昆明市', 'qj': '曲靖市', 'yx': '玉溪市', 'bs': '保山市',
      'zt': '昭通市', 'lj': '丽江市', 'pe': '普洱市', 'lc': '临沧市',
      'cx': '楚雄州', 'hh': '红河州', 'ws': '文山州', 'xsbn': '西双版纳州',
      'dl': '大理州', 'dh': '德宏州', 'nj': '怒江州', 'dq': '迪庆州'
    }
    const location = prefectureMap[school.prefecture] || school.prefecture || school.city
    response += `- **地区**：${location}\n`
  }

  if (school.address) {
    response += `- **地址**：${school.address}\n`
  }

  if (school.phone) {
    response += `- **电话**：${school.phone}\n`
  }

  response += '\n【录取情况】\n'

  if (school.min_score) {
    response += `- **录取分数线**：约${school.min_score}分\n`
  }

  if (school.one_rate) {
    response += `- **一本率**：${school.one_rate}%\n`
  }

  if (school.min_rank) {
    response += `- **最低排名**：约${school.min_rank}名\n`
  }

  if (school.tuition !== undefined && school.tuition !== null) {
    response += `- **学费**：${school.tuition === 0 ? '免费（公办）' : `${school.tuition}元/学期`}\n`
  }

  if (school.boarding !== undefined) {
    response += `- **住宿**：${school.boarding === 1 ? '提供' : '不提供'}\n`
  }

  if (school.features) {
    response += '\n【学校特色】\n'
    const features = school.features
    if (Array.isArray(features)) {
      features.forEach(f => response += `- ${f}\n`)
    } else if (typeof features === 'string') {
      response += `- ${features}\n`
    }
  }

  if (school.description) {
    response += '\n【学校简介】\n'
    response += school.description
  }

  response += '\n如需更详细的信息，可以访问学校详情页查看！'

  return response
}

// ==================== 发送消息 ====================

const sendMessage = async () => {
  const content = inputMessage.value.trim()
  if (!content || loading.value) return

  const cachedResponse = messageCache.value.get(content)
  if (cachedResponse && !cachedResponse.includes('未能获取') && !cachedResponse.includes('处理失败')) {
    const userMsg = { id: generateId(), role: 'user', content, loading: false, error: false, timestamp: Date.now() }
    messages.value.push(userMsg)
    inputMessage.value = ''
    scrollToBottom()
    setTimeout(() => {
      const aiMsg = { id: generateId(), role: 'assistant', content: cachedResponse, loading: false, error: false, timestamp: Date.now() }
      messages.value.push(aiMsg)
      scrollToBottom()
    }, 100)
    return
  }

  const userMsg = { id: generateId(), role: 'user', content, loading: false, error: false, timestamp: Date.now() }
  messages.value.push(userMsg)
  inputMessage.value = ''
  scrollToBottom()

  const aiMsg = { id: generateId(), role: 'assistant', content: '', loading: true, error: false, timestamp: Date.now() }
  messages.value.push(aiMsg)
  streamingMessageId.value = aiMsg.id
  loading.value = true

  try {
    const schoolNames = extractSchoolNames(content)
    let dbResponse = null

    if (schoolNames.length > 0) {
      for (const name of schoolNames) {
        const school = await getSchoolFromDB(name)
        if (school) {
          dbResponse = generateSchoolResponse(school)
          break
        }
      }
    }

    if (dbResponse) {
      const msg = messages.value.find(m => m.id === streamingMessageId.value)
      if (msg) {
        msg.loading = false
        msg.content = dbResponse
        messageCache.value.set(content, dbResponse)
      }
      if (isLoggedIn.value) {
        setTimeout(() => saveCurrentSession(), 0)
      }
    } else {
      await aiServiceApi.openclawChat({ message: content, context: {}, session_id: sessionId.value }, (chunk, responseData) => {
        const msg = messages.value.find(m => m.id === streamingMessageId.value)
        if (msg) {
          msg.content += chunk
        }
        scrollToBottom()
        if (responseData && responseData.session_id) {
          sessionId.value = responseData.session_id
        }
      })
      const msg = messages.value.find(m => m.id === streamingMessageId.value)
      if (msg) {
        msg.loading = false
        if (!msg.content) {
          msg.content = getOfflineResponse(content)
        } else {
          messageCache.value.set(content, msg.content)
        }
      }
      if (isLoggedIn.value) {
        setTimeout(() => saveCurrentSession(), 0)
      }
    }
  } catch (error) {
    console.error('AI服务调用失败:', error)
    const schoolNames = extractSchoolNames(content)
    let dbResponse = null

    if (schoolNames.length > 0) {
      for (const name of schoolNames) {
        const school = await getSchoolFromDB(name)
        if (school) {
          dbResponse = generateSchoolResponse(school)
          break
        }
      }
    }

    const offlineResponse = dbResponse || getOfflineResponse(content)
    const msg = messages.value.find(m => m.id === streamingMessageId.value)
    if (msg) {
      msg.error = false
      msg.loading = false
      await streamOfflineResponse(msg, offlineResponse)
    }
  } finally {
    loading.value = false
    streamingMessageId.value = null
    scrollToBottom()
  }
}

const extractSchoolNames = (content) => {
  const schoolKeywords = [
    '中学', '高中', '一中', '二中', '三中', '四中', '五中',
    '附中', '实验', '民族', '师范', '大学', '学院', '职业'
  ]

  const names = []
  const parts = content.split(/[，。！？、\s]+/)

  for (const part of parts) {
    for (const keyword of schoolKeywords) {
      const idx = part.indexOf(keyword)
      if (idx !== -1) {
        const name = part.substring(0, idx + keyword.length)
        if (name.length >= 2) {
          names.push(name.trim())
        }
      }
    }
  }

  return [...new Set(names)]
}

const streamOfflineResponse = async (msg, text) => {
  for (let i = 0; i < text.length; i++) {
    msg.content += text.charAt(i)
    await new Promise(r => setTimeout(r, 15 + Math.random() * 15))
    scrollToBottom()
  }
}

// ==================== 离线响应 ====================

const getOfflineResponse = (content) => {
  const q = content.toLowerCase()

  if (q.includes('云南师范大学附属中学') || q.includes('师大附中')) {
    return `**云南师范大学附属中学** 🏛️\n\n【基本信息】\n- **性质**：公办\n- **等级**：一级一等\n- **地址**：昆明市高新区洪源路36号\n- **电话**：0871-68215819\n\n【办学特色】\n- 云南省顶尖高中，清北录取人数常年全省第一\n- 百年名校，师资力量雄厚\n- 设有创新班、竞赛班，面向全省招收优秀学生\n\n【录取情况】\n- **录取分数线**：约685分（2025年参考）\n- **一本率**：98%\n- **2026年计划招生**：800人（统招600人，定向200人）\n\n【学校特色】\n- 历史悠久，底蕴深厚\n- 学科竞赛成绩突出\n- 社团活动丰富`
  }

  if (q.includes('昆明市第一中学') || q.includes('昆一中')) {
    return `**昆明市第一中学** 🏛️\n\n【基本信息】\n- **性质**：公办\n- **等级**：一级一等\n- **地址**：昆明市五华区西昌路233号\n- **电话**：0871-65324879\n\n【办学特色】\n- 百年名校，创办于1905年\n- 云南省首批一级一等完全中学\n- 教学严谨，学风优良\n\n【录取情况】\n- **录取分数线**：约678分（2025年参考）\n- **一本率**：95%\n- **2026年计划招生**：900人\n\n【学校特色】\n- 历史悠久，文化底蕴深厚\n- 体育、艺术特长生招生\n- 社团活动丰富多样`
  }

  if (q.includes('腾冲一中') || q.includes('腾冲第一中学')) {
    return `**腾冲市第一中学** 🏛️\n\n【基本信息】\n- **性质**：公办\n- **等级**：一级一等\n- **地址**：腾冲市腾越街道\n- **所属地区**：保山市腾冲市\n\n【办学特色】\n- 滇西地区知名重点中学\n- 办学历史悠久，文化底蕴深厚\n- 注重学生全面发展\n\n【录取情况】\n- **录取分数线**：约630分（2025年参考）\n- **一本率**：约80%\n\n【学校特色】\n- 优美的校园环境\n- 丰富的课外活动\n- 优秀的师资队伍`
  }

  if (q.includes('保山天成') || q.includes('天成中学')) {
    return `**保山天成中学** 🏛️\n\n【基本信息】\n- **性质**：民办\n- **地址**：保山市隆阳区\n- **所属地区**：保山市隆阳区\n\n【办学特色】\n- 现代化民办中学\n- 小班化教学模式\n- 注重个性化培养\n\n【录取情况】\n- **录取分数线**：约580分（2025年参考）\n- **收费标准**：民办收费，具体请咨询学校\n\n【学校特色】\n- 优质的硬件设施\n- 特色课程丰富\n- 寄宿制管理`
  }

  if (q.includes('保山') && (q.includes('好高中') || q.includes('高中') || q.includes('学校'))) {
    return `**保山市优质高中推荐** 🏛️\n\n【一级一等高中】\n1. **腾冲市第一中学**\n   - 录取分数线：约630分\n   - 一本率：约80%\n   - 特色：历史悠久，滇西名校\n\n2. **保山市第一中学**\n   - 录取分数线：约610分\n   - 一本率：约75%\n   - 特色：市级重点，师资雄厚\n\n【一级二等高中】\n3. **隆阳区第一中学**\n   - 录取分数线：约580分\n   - 一本率：约60%\n\n4. **施甸县第一中学**\n   - 录取分数线：约560分\n   - 一本率：约55%\n\n【民办高中】\n5. **保山天成中学**\n   - 录取分数线：约580分\n   - 特色：民办优质教育\n\n建议根据您的估分和户籍所在地选择合适的学校。`
  }

  const prefectureMap = {
    '昆明': '昆明市', '曲靖': '曲靖市', '玉溪': '玉溪市',
    '丽江': '丽江市', '普洱': '普洱市', '临沧': '临沧市',
    '楚雄': '楚雄州', '红河': '红河州', '大理': '大理州',
    '文山': '文山州', '德宏': '德宏州', '版纳': '西双版纳州'
  }

  for (const [key, prefecture] of Object.entries(prefectureMap)) {
    if (q.includes(key) && (q.includes('好高中') || q.includes('高中') || q.includes('学校') || q.includes('哪些'))) {
      return `**${prefecture}优质高中推荐** 🏛️\n\n【重点高中】\n1. **${prefecture}第一中学**\n   - 州/市级重点中学\n   - 录取分数线：约600-650分\n   - 一本率：约70-85%\n\n2. **${prefecture}实验中学**\n   - 优质公办中学\n   - 录取分数线：约580-620分\n\n3. **${prefecture}民族中学**\n   - 特色民族教育\n   - 录取分数线：约560-600分\n\n如需具体学校信息，请告诉我学校名称！`
    }
  }

  if (q.includes('分数线') || q.includes('录取分') || q.includes('多少分')) {
    return `以下是部分云南省优质高中的录取分数线信息（2025年参考）：\n\n| 学校 | 录取分 | 一本率 |\n|------|--------|--------|\n| 云南师范大学附属中学 | 685分 | 98% |\n| 昆明市第一中学 | 678分 | 95% |\n| 云南大学附属中学 | 670分 | 92% |\n| 昆明市第三中学 | 665分 | 88% |\n| 曲靖市第一中学 | 660分 | 90% |\n\n建议结合您的估分情况，选择适合的学校。如需更详细的信息，请说明具体学校名称。`
  }
  if (q.includes('推荐') || q.includes('什么学校') || q.includes('哪些学校') || q.includes('报考')) {
    return `根据云南省中考情况，以下是推荐参考：\n\n**顶尖梯队（680分以上）**：\n- 云南师范大学附属中学\n- 昆明市第一中学\n\n**优秀梯队（660-680分）**：\n- 云南大学附属中学\n- 曲靖市第一中学\n- 昆明市第三中学\n\n**良好梯队（640-660分）**：\n- 玉溪市第一中学\n- 昆明市第十四中学\n- 安宁中学\n\n选校建议：\n1. 根据户籍所在地确认可报考区域\n2. 参考往年录取分数线和排名\n3. 考虑学校的办学特色和优势学科\n4. 关注学校的交通、住宿等条件`
  }
  if (q.includes('对比') || q.includes('哪个好') || q.includes('区别')) {
    return `学校对比分析框架：\n\n**对比维度**：\n1. **录取分数线** - 直接决定能否报考\n2. **一本率/升学率** - 反映教学质量\n3. **师资力量** - 教师团队的实力\n4. **办学特色** - 学科优势、特色课程\n5. **校园环境** - 硬件设施、地理位置\n6. **学费标准** - 公办/民办差异\n7. **毕业生去向** - 往届学生录取情况\n\n请告诉我具体想对比哪两所学校，我会为您提供详细对比分析。`
  }
  if (q.includes('政策') || q.includes('变化') || q.includes('中考')) {
    return `**云南省中考政策要点**：\n\n1. **考试科目**：语文、数学、英语、物理、化学、道德与法治、历史、体育\n2. **总分构成**：各科满分分值不同，总分约700分左右\n3. **录取方式**：实行"分数优先、遵循志愿"的平行志愿投档\n4. **户籍要求**：需在云南省有合法稳定住所和学籍\n5. **加分政策**：少数民族、烈士子女等符合条件的可享受加分\n\n建议关注云南省教育厅官方网站获取最新政策信息。`
  }
  if (q.includes('志愿') || q.includes('填报技巧') || q.includes('怎么填')) {
    return `**中考志愿填报技巧**：\n\n1. **冲稳保策略**\n   - 第一志愿：冲刺理想学校（略高于估分）\n   - 第二志愿：稳妥选择（匹配估分）\n   - 第三志愿：保底选择（低于估分）\n\n2. **注意事项**\n   - 了解学校近3年录取分数线趋势\n   - 考虑学校的地理位置和交通\n   - 关注学校的特色专业和优势学科\n   - 参考往年同分段学生的录取情况\n\n3. **常见误区**\n   - 只填一个志愿，浪费机会\n   - 盲目追求名校，忽略匹配度\n   - 不了解调剂政策\n\n需要具体指导请告诉我您的估分和目标区域。`
  }
  if (q.includes('复习') || q.includes('学习计划') || q.includes('备考')) {
    return `**中考备考学习计划建议**：\n\n**第一阶段（基础巩固）**\n- 全面梳理各科知识点\n- 建立知识框架和错题本\n- 每天保证6-8小时高效学习\n\n**第二阶段（能力提升）**\n- 专项突破薄弱学科\n- 做历年真题，掌握命题规律\n- 限时训练，提升做题速度\n\n**第三阶段（冲刺模拟）**\n- 全真模拟考试环境\n- 查漏补缺，重点复习\n- 调整心态，保证充足睡眠\n\n**每日时间安排参考**：\n- 6:30 起床晨读\n- 8:00-12:00 主科学习\n- 14:00-18:00 理科/文科交替\n- 19:30-22:00 复习+错题整理`
  }
  if (q.includes('学习方法') || q.includes('怎么学') || q.includes('提高')) {
    return `**高效学习方法推荐**：\n\n1. **费曼学习法** - 用自己的话解释概念，发现知识盲点\n2. **艾宾浩斯遗忘曲线** - 按时复习（1天/1周/1月）\n3. **番茄工作法** - 25分钟专注+5分钟休息\n4. **思维导图** - 梳理知识结构，建立知识网络\n\n**学科专项建议**：\n- 语文：多读多写，积累素材\n- 数学：理解原理，多做变式题\n- 英语：坚持背单词，培养语感\n- 物理/化学：重视实验，理解公式推导`
  }
  if (q.includes('宿舍') || q.includes('食宿') || q.includes('环境') || q.includes('校园')) {
    return `**学校环境概况**：\n\n云南省重点高中普遍具备较好的办学条件：\n- **住宿条件**：重点高中一般提供4-6人间宿舍，配有空调、热水器等设施\n- **食堂条件**：多数学校有多样化的食堂，满足不同口味需求\n- **运动设施**：标准操场、篮球场、体育馆等\n- **教学设施**：多媒体教室、实验室、图书馆等\n\n如果您想了解具体某所学校的环境，请告知学校名称，我会提供更详细的信息。`
  }
  if (q.includes('师资') || q.includes('老师')) {
    return `**重点高中师资概况**：\n\n云南省重点高中教师队伍普遍较强：\n- 特级教师、高级教师比例高\n- 多数教师具有研究生及以上学历\n- 省级骨干教师、学科带头人数量多\n- 定期开展教师培训和教学研究\n\n特级教师数量较多的学校：\n- 云南师范大学附属中学\n- 昆明市第一中学\n- 曲靖市第一中学`
  }
  if (q.includes('学费') || q.includes('收费') || q.includes('多少钱')) {
    return `**云南省高中学费参考**：\n\n**公办高中**：\n- 学费：约1000-2000元/学期\n- 住宿费：约400-800元/学期\n- 书本费：按实际收取\n\n**民办高中**：\n- 学费：约8000-30000元/学期\n- 住宿费：约1000-3000元/学期\n- 其他费用视学校而定\n\n各学校具体收费标准可能有所不同，建议咨询目标学校招生办获取准确信息。`
  }
  if (q.includes('交通') || q.includes('怎么去')) {
    return `**学校交通情况**：\n\n昆明主城区学校（师大附中、昆一中、昆三中等）交通便利：\n- 多条公交线路可达\n- 地铁覆盖区域\n- 部分学校有校车接送\n\n地州学校（曲靖一中、玉溪一中等）：\n- 位于各州市中心区域\n- 公共交通可达\n- 高铁/动车便捷\n\n建议实地考察了解具体交通路线。`
  }
  if (q.includes('社团') || q.includes('活动')) {
    return `**高中社团活动概况**：\n\n重点高中普遍重视学生综合素质培养，常见的社团类型：\n- 学术类：数理化竞赛社、英语角、文学社\n- 艺术类：合唱团、舞蹈队、美术社\n- 体育类：篮球社、足球社、羽毛球社\n- 科技类：机器人社、编程社、科技创新社\n- 实践类：志愿者协会、模拟联合国\n\n具体社团设置因学校而异，入学后可了解各校社团招新信息。`
  }
  if (q.includes('联系') || q.includes('电话') || q.includes('招生')) {
    return `**学校联系方式**：\n\n建议通过以下渠道获取联系方式：\n1. 学校官方网站 - 查看招生专栏\n2. 学校官方微信公众号\n3. 各州市教育体育局官网\n4. 云南省教育厅官网\n\n通常每年4-6月是学校招生咨询高峰期，建议提前关注目标学校的招生简章。`
  }
  return `您好！我是小龙虾择校助手。关于"${content.substring(0, 30)}${content.length > 30 ? '...' : ''}"，我可以帮您：\n\n🏫 **学校查询** - 了解各校录取分数、一本率等信息\n🎯 **志愿填报** - 获取志愿填报策略和技巧\n📝 **学习指导** - 备考计划、学习方法推荐\n📊 **政策解读** - 了解中考政策和录取规则\n\n请描述您的具体需求，我会为您提供更精准的帮助！`
}

const handleFuncClick = (item) => {
  inputMessage.value = item.question
  showFuncPanel.value = false
  sendMessage()
}

const createNewChat = () => {
  currentSessionId.value = null
  messages.value = []
  sessionId.value = null
}

const loadSession = async (session) => {
  currentSessionId.value = session.id
  messages.value = []
  scrollToBottom()
}

const saveCurrentSession = async () => {
  if (!isLoggedIn.value || messages.value.length === 0) return
  const userId = userInfo.value.id?.toString() || userInfo.value.phone
  if (!userId || userId === '0') return
}

const loadSessions = async () => {
  if (!isLoggedIn.value) return
  const userId = userInfo.value.id?.toString() || userInfo.value.phone
  if (!userId || userId === '0') return
  sessions.value = []
}

const deleteSession = async (sessionIdToDelete) => {
  sessions.value = sessions.value.filter(s => s.id !== sessionIdToDelete)
  if (currentSessionId.value === sessionIdToDelete) {
    createNewChat()
  }
}

const goLogin = () => {
  router.push('/login')
}

onMounted(() => {
  if (isLoggedIn.value) {
    loadSessions()
  }
  if (route.query.question) {
    inputMessage.value = decodeURIComponent(route.query.question)
    setTimeout(() => sendMessage(), 300)
  }
})

watch(isLoggedIn, (val) => {
  if (val) loadSessions()
})
</script>

<style scoped>
/* ==================== 整体布局 ==================== */
.chat-page {
  display: flex;
  height: 100vh;
  background: var(--wx-bg);
}

/* ==================== 侧边栏 ==================== */
.sidebar {
  width: 280px;
  background: var(--wx-bg-light);
  display: flex;
  flex-direction: column;
  transition: width var(--wx-transition-normal);
  border-right: 1px solid var(--wx-border-light);
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: var(--wx-spacing-md);
  display: flex;
  gap: var(--wx-spacing-sm);
}

.new-chat-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--wx-spacing-sm);
  padding: 10px 16px;
  background: var(--wx-primary);
  border: none;
  border-radius: var(--wx-radius-sm);
  color: var(--wx-text-white);
  cursor: pointer;
  transition: background var(--wx-transition-fast);
  font-weight: 500;
  font-size: var(--wx-font-size-md);
}

.new-chat-btn:hover {
  background: var(--wx-primary-hover);
}

.toggle-btn {
  padding: 10px;
  background: var(--wx-bg-white);
  border: 1px solid var(--wx-border-light);
  color: var(--wx-text-secondary);
  cursor: pointer;
  border-radius: var(--wx-radius-sm);
  transition: all var(--wx-transition-fast);
}

.toggle-btn:hover {
  background: var(--wx-bg-hover);
  color: var(--wx-text-primary);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--wx-spacing-md);
}

.list-header {
  color: var(--wx-text-muted);
  font-size: var(--wx-font-size-xs);
  padding: var(--wx-spacing-sm) var(--wx-spacing-md);
  margin-bottom: var(--wx-spacing-sm);
}

.chat-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-md);
  padding: 10px var(--wx-spacing-md);
  color: var(--wx-text-secondary);
  border-radius: var(--wx-radius-sm);
  cursor: pointer;
  transition: background var(--wx-transition-fast);
}

.chat-item:hover {
  background: var(--wx-bg-hover);
}

.chat-item.active {
  background: var(--wx-primary-light);
  color: var(--wx-primary);
}

.chat-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--wx-font-size-md);
}

.delete-btn {
  opacity: 0;
  background: transparent;
  border: none;
  color: var(--wx-text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--wx-radius-sm);
  transition: all var(--wx-transition-fast);
}

.chat-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: var(--wx-danger);
  background: rgba(250, 81, 81, 0.08);
}

/* ==================== 聊天容器 ==================== */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--wx-bg);
  min-width: 0;
}

/* ==================== 顶部标题栏 ==================== */
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
  gap: var(--wx-spacing-sm);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-md);
}

.func-toggle-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--wx-radius-sm);
  color: var(--wx-text-secondary);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
  font-size: 18px;
}

.func-toggle-btn:hover {
  background: var(--wx-bg-hover);
  color: var(--wx-text-primary);
}

.func-toggle-btn.active {
  background: var(--wx-primary-light);
  color: var(--wx-primary);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
  padding: 4px 12px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-bg);
}

.username {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
}

/* ==================== 聊天主体 ==================== */
.chat-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--wx-spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--wx-spacing-lg);
}

/* ==================== 欢迎区域 ==================== */
.welcome-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  font-size: 72px;
  margin-bottom: var(--wx-spacing-xl);
}

.welcome-area h2 {
  font-size: 24px;
  margin-bottom: var(--wx-spacing-sm);
  color: var(--wx-text-primary);
  font-weight: 600;
}

.welcome-area p {
  color: var(--wx-text-secondary);
  font-size: var(--wx-font-size-md);
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

/* Markdown 内容样式 */
.msg-bubble :deep(h1),
.msg-bubble :deep(h2),
.msg-bubble :deep(h3) {
  margin: 8px 0 4px;
  font-size: 15px;
}

.msg-bubble :deep(p) {
  margin: 4px 0;
}

.msg-bubble :deep(ul),
.msg-bubble :deep(ol) {
  margin: 4px 0;
  padding-left: 18px;
}

.msg-bubble :deep(li) {
  margin: 2px 0;
}

.msg-bubble :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.msg-bubble :deep(th),
.msg-bubble :deep(td) {
  border: 1px solid var(--wx-border-light);
  padding: 6px 10px;
  text-align: left;
  font-size: 13px;
}

.msg-bubble :deep(th) {
  background: var(--wx-bg);
  font-weight: 500;
}

.other .msg-bubble :deep(th) {
  background: var(--wx-bg);
}

.mine .msg-bubble :deep(th),
.mine .msg-bubble :deep(td) {
  border-color: rgba(255, 255, 255, 0.2);
}

.mine .msg-bubble :deep(th) {
  background: rgba(255, 255, 255, 0.1);
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 6px 0 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--wx-text-muted);
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* ==================== 快捷功能面板 ==================== */
.func-panel {
  width: 300px;
  background: var(--wx-bg-white);
  border-left: 1px solid var(--wx-border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
}

.func-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--wx-spacing-lg) var(--wx-spacing-xl);
  border-bottom: 1px solid var(--wx-border-light);
}

.func-title {
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-text-primary);
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--wx-radius-sm);
  color: var(--wx-text-secondary);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
}

.close-btn:hover {
  background: var(--wx-bg-hover);
  color: var(--wx-text-primary);
}

.func-grid {
  flex: 1;
  overflow-y: auto;
  padding: var(--wx-spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--wx-spacing-sm);
}

.func-card {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-md);
  padding: 14px var(--wx-spacing-lg);
  background: var(--wx-bg);
  border: 1px solid var(--wx-border-light);
  border-radius: var(--wx-radius-sm);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
}

.func-card:hover {
  background: var(--wx-primary-light);
  border-color: var(--wx-primary);
}

.func-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.func-info {
  flex: 1;
  min-width: 0;
}

.func-name {
  font-size: var(--wx-font-size-md);
  font-weight: 500;
  color: var(--wx-text-primary);
  margin-bottom: 2px;
}

.func-desc {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.slide-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
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

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .chat-message {
    max-width: 75%;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform var(--wx-transition-normal);
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
    box-shadow: var(--wx-shadow-lg);
  }

  .chat-header {
    padding: 0 var(--wx-spacing-md);
  }

  .chat-messages {
    padding: var(--wx-spacing-md);
  }

  .chat-message {
    max-width: 85%;
  }

  .chat-input-area {
    padding: var(--wx-spacing-sm) var(--wx-spacing-md);
  }

  .func-panel {
    position: fixed;
    right: 0;
    top: 56px;
    bottom: 0;
    z-index: 50;
    width: 280px;
    box-shadow: var(--wx-shadow-lg);
  }
}

@media (max-width: 480px) {
  .chat-message {
    max-width: 90%;
  }

  .logo-icon {
    font-size: 20px;
  }

  .logo-text {
    font-size: var(--wx-font-size-md);
  }

  .username {
    display: none;
  }
}
</style>