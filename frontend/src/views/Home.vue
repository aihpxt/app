<template>
  <div class="home-page">
    <!-- 左侧面板 -->
    <div class="left-panel">
      <!-- 搜索框 -->
      <div class="wx-search">
        <el-icon class="search-icon"><Search /></el-icon>
        <input
          v-model="searchText"
          class="search-input"
          placeholder="搜索功能"
          @input="handleSearch"
        />
      </div>

      <!-- 功能列表 -->
      <div class="wx-list">
        <div
          v-for="item in filteredFeatures"
          :key="item.id"
          class="wx-list-item"
          @click="item.action()"
        >
          <div class="item-avatar">{{ item.icon }}</div>
          <div class="item-content">
            <div class="item-title">{{ item.title }}</div>
            <div class="item-subtitle">{{ item.subtitle }}</div>
          </div>
          <el-icon class="item-arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 底部用户信息 -->
      <div class="left-footer">
        <template v-if="userStore.isLoggedIn && userStore.userInfo && typeof userStore.userInfo === 'object' && !Array.isArray(userStore.userInfo)">
          <el-dropdown @command="handleUserCommand" placement="top-start">
            <div class="sidebar-user">
              <el-avatar :size="32" class="user-avatar-sidebar">
                {{ userStore.userInfo.nickname?.charAt(0) || '用' }}
              </el-avatar>
              <span class="user-name">{{ userStore.userInfo.nickname || '用户' }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="favorites">
                  <el-icon><Star /></el-icon>我的收藏
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><Switch /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <div class="sidebar-user" @click="goLogin">
            <el-avatar :size="32" class="user-avatar-sidebar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="user-name">未登录</span>
          </div>
        </template>
      </div>
    </div>

    <!-- 右侧欢迎面板 -->
    <div class="right-panel">
      <div class="welcome-content">
        <!-- Logo 和标题 -->
        <div class="welcome-header">
          <span class="welcome-logo">🦐</span>
          <h1 class="welcome-title">小龙虾择校</h1>
          <p class="welcome-desc">欢迎使用云南省中考择校智能平台</p>
          <p class="welcome-subtitle">AI赋能，科学择校，让每个孩子都能找到最适合的学校</p>
        </div>

        <!-- 搜索输入框 -->
        <div class="welcome-search" :class="{ 'search-focused': isSearchFocused }">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="2"
            :autosize="{ minRows: 2, maxRows: 4 }"
            placeholder="请输入您的问题，例如：我家孩子估分680分，昆明户籍，推荐哪些学校？"
            class="main-input"
            @keydown.enter.exact.prevent="handleSubmit"
            @focus="isSearchFocused = true"
            @blur="isSearchFocused = false"
          />
          <div class="search-actions">
            <span class="search-tip">按 Enter 发送</span>
            <button
              class="send-btn"
              @click="handleSubmit"
              :disabled="!userInput.trim()"
            >发送</button>
          </div>
        </div>

        <!-- 快捷入口卡片 -->
        <div class="quick-cards">
          <div class="wx-card quick-card" @click="goToAiAssistant">
            <div class="card-icon">🤖</div>
            <div class="card-title">AI智能助手</div>
            <div class="card-desc">AI智能择校咨询</div>
          </div>
          <div class="wx-card quick-card" @click="goToSchool">
            <div class="card-icon">🏫</div>
            <div class="card-title">学校查询</div>
            <div class="card-desc">查询学校详细信息</div>
          </div>
          <div class="wx-card quick-card" @click="goToScorePrediction">
            <div class="card-icon">📊</div>
            <div class="card-title">分数预测</div>
            <div class="card-desc">AI预测录取分数</div>
          </div>
          <div class="wx-card quick-card" @click="goToPolicy">
            <div class="card-icon">📋</div>
            <div class="card-title">政策解读</div>
            <div class="card-desc">了解最新招生政策</div>
          </div>
        </div>

        <!-- 热门问题 -->
        <div class="hot-questions">
          <h3 class="section-title">热门问题</h3>
          <div
            v-for="question in hotQuestions"
            :key="question.id"
            class="hot-question-item"
            @click="goToAiAssistantWithQuestion(question.content)"
          >
            <span class="question-text">{{ question.content }}</span>
            <span class="question-count">{{ question.count }}人关注</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ArrowRight, User, Star, Switch } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const userInput = ref('')
const searchText = ref('')
const isSearchFocused = ref(false)

// 功能列表
const features = [
  {
    id: 1,
    icon: '🤖',
    title: 'AI智能助手',
    subtitle: 'AI智能择校咨询问答',
    action: () => router.push('/ai-assistant')
  },
  {
    id: 2,
    icon: '🏫',
    title: '学校查询',
    subtitle: '查询学校详细信息与分数线',
    action: () => router.push('/school')
  },
  {
    id: 3,
    icon: '📋',
    title: '政策查询',
    subtitle: '了解最新中考招生政策',
    action: () => router.push('/policy')
  },
  {
    id: 4,
    icon: '📊',
    title: '分数预测',
    subtitle: 'AI智能预测录取分数线',
    action: () => goToScorePrediction()
  },
  {
    id: 5,
    icon: '🎯',
    title: '智能择校',
    subtitle: 'AI个性化推荐适合学校',
    action: () => goToAiSelection()
  },
  {
    id: 6,
    icon: '📝',
    title: '志愿填报',
    subtitle: 'AI辅助志愿填报决策',
    action: () => goToVolunteer()
  }
]

// 热门问题
const hotQuestions = [
  { id: 1, content: '2026年昆明中考录取分数线是多少？', count: 1258 },
  { id: 2, content: '如何选择适合自己的高中？', count: 987 },
  { id: 3, content: '中考复习有什么好方法？', count: 876 },
  { id: 4, content: '昆明一级一等高中有哪些？', count: 765 },
  { id: 5, content: '中考志愿填报技巧', count: 654 }
]

// 搜索过滤
const filteredFeatures = computed(() => {
  if (!searchText.value.trim()) return features
  const keyword = searchText.value.trim().toLowerCase()
  return features.filter(
    item =>
      item.title.toLowerCase().includes(keyword) ||
      item.subtitle.toLowerCase().includes(keyword)
  )
})

const handleSearch = () => {
  // 实时过滤由 computed 处理
}

// 路由跳转方法
const handleSubmit = (event) => {
  if (event) event.preventDefault()
  if (!userInput.value.trim()) return
  const question = userInput.value.trim()
  userInput.value = ''
  router.push({
    path: '/ai-assistant',
    query: { question: encodeURIComponent(question) }
  })
}

const goToAiAssistant = () => router.push('/ai-assistant')
const goToSchool = () => router.push('/school')
const goToPolicy = () => router.push('/policy')

const goToScorePrediction = () => {
  if (userStore.isLoggedIn) {
    router.push('/score-prediction')
  } else {
    router.push('/login')
  }
}

const goToAiSelection = () => {
  if (userStore.isLoggedIn) {
    router.push('/ai-selection')
  } else {
    router.push('/login')
  }
}

const goToVolunteer = () => {
  if (userStore.isLoggedIn) {
    router.push('/volunteer')
  } else {
    router.push('/login')
  }
}

const goToAiAssistantWithQuestion = (question) => {
  router.push({
    path: '/ai-assistant',
    query: { question: encodeURIComponent(question) }
  })
}

const goToRecommendation = (item) => {
  if (item.type === 'school') {
    router.push({
      path: '/ai-assistant',
      query: { question: encodeURIComponent(`介绍一下${item.title}`) }
    })
  } else if (item.type === 'plan') {
    router.push({
      path: '/ai-assistant',
      query: { question: encodeURIComponent(item.title) }
    })
  } else if (item.type === 'resource') {
    router.push('/learning-resources')
  }
}

const goLogin = () => router.push('/login')
const goRegister = () => router.push('/login')
const goToUser = () => {
  if (userStore.isLoggedIn) {
    router.push('/user')
  } else {
    router.push('/login')
  }
}
const goToOnlineTest = () => {
  if (userStore.isLoggedIn) {
    router.push('/online-test')
  } else {
    router.push('/login')
  }
}
const goToLearningProgress = () => {
  if (userStore.isLoggedIn) {
    router.push('/learning-progress')
  } else {
    router.push('/login')
  }
}

const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/user')
      break
    case 'favorites':
      router.push('/favorite')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('退出登录成功')
      break
  }
}
</script>

<style scoped>
.home-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--wx-bg);
  font-family: var(--wx-font-family);
}

/* ==================== 左侧面板 ==================== */
.left-panel {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--wx-bg-light);
  border-right: 1px solid var(--wx-border-light);
}

/* 搜索框 */
.wx-search {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px;
}

.wx-search .search-icon {
  position: absolute;
  left: 24px;
  color: var(--wx-text-muted);
  font-size: 16px;
  pointer-events: none;
  z-index: 1;
}

.wx-search .search-input {
  width: 100%;
  height: 36px;
  padding: 0 12px 0 36px;
  border: 1px solid var(--wx-border);
  border-radius: var(--wx-radius-round);
  background: var(--wx-bg);
  color: var(--wx-text-primary);
  font-size: var(--wx-font-size-md);
  font-family: var(--wx-font-family);
  outline: none;
  transition: all var(--wx-transition-fast);
  box-sizing: border-box;
}

.wx-search .search-input:focus {
  background: var(--wx-bg-white);
  border-color: var(--wx-border-focus);
}

.wx-search .search-input::placeholder {
  color: var(--wx-text-placeholder);
}

/* 功能列表 */
.wx-list {
  flex: 1;
  overflow-y: auto;
  background: var(--wx-bg-white);
}

.wx-list-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--wx-border-light);
  cursor: pointer;
  transition: background var(--wx-transition-fast);
  gap: 12px;
}

.wx-list-item:last-child {
  border-bottom: none;
}

.wx-list-item:hover {
  background: var(--wx-bg-hover);
}

.wx-list-item .item-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--wx-radius-sm);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--wx-primary-light);
  font-size: 20px;
}

.wx-list-item .item-content {
  flex: 1;
  min-width: 0;
}

.wx-list-item .item-title {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-primary);
  font-weight: 500;
  line-height: 1.4;
}

.wx-list-item .item-subtitle {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.wx-list-item .item-arrow {
  color: var(--wx-text-muted);
  font-size: 14px;
  flex-shrink: 0;
}

/* 左侧底部 */
.left-footer {
  padding: 8px;
  border-top: 1px solid var(--wx-border-light);
  background: var(--wx-bg-white);
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: var(--wx-radius-md);
  cursor: pointer;
  transition: background var(--wx-transition-fast);
}

.sidebar-user:hover {
  background: var(--wx-bg-hover);
}

.user-avatar-sidebar {
  background: var(--wx-primary);
  color: var(--wx-text-white);
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ==================== 右侧面板 ==================== */
.right-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
  background: var(--wx-bg);
}

.welcome-content {
  width: 100%;
  max-width: 640px;
  padding: 60px 40px;
  text-align: center;
}

.welcome-header {
  margin-bottom: 40px;
}

.welcome-logo {
  font-size: 56px;
  display: block;
  margin-bottom: 16px;
}

.welcome-title {
  font-size: var(--wx-font-size-title);
  font-weight: 700;
  color: var(--wx-text-primary);
  margin: 0 0 12px 0;
}

.welcome-desc {
  font-size: var(--wx-font-size-lg);
  color: var(--wx-text-secondary);
  margin: 0 0 8px 0;
}

.welcome-subtitle {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
  margin: 0;
}

/* 搜索输入框 */
.welcome-search {
  background: var(--wx-bg-white);
  border: 1px solid var(--wx-border);
  border-radius: var(--wx-radius-md);
  padding: 16px;
  margin-bottom: 32px;
  transition: border-color var(--wx-transition-fast), box-shadow var(--wx-transition-fast);
}

.welcome-search.search-focused {
  border-color: #07C160;
  box-shadow: 0 0 0 2px rgba(7, 193, 96, 0.1);
}

.main-input :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  color: var(--wx-text-primary);
  font-size: var(--wx-font-size-md);
  line-height: 1.6;
  resize: none;
  padding: 0;
  font-family: var(--wx-font-family);
  box-shadow: none;
}

.main-input :deep(.el-textarea__inner::placeholder) {
  color: var(--wx-text-placeholder);
}

.main-input :deep(.el-textarea__inner:focus) {
  box-shadow: none;
}

.search-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--wx-border-light);
}

.search-tip {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

.send-btn {
  padding: 6px 20px;
  height: 32px;
  background: var(--wx-primary);
  color: var(--wx-text-white);
  border: none;
  border-radius: var(--wx-radius-sm);
  font-size: var(--wx-font-size-sm);
  font-family: var(--wx-font-family);
  cursor: pointer;
  transition: background var(--wx-transition-fast);
}

.send-btn:hover:not(:disabled) {
  background: var(--wx-primary-hover);
}

.send-btn:active:not(:disabled) {
  background: var(--wx-primary-active);
}

.send-btn:disabled {
  background: var(--wx-bg-active);
  color: var(--wx-text-muted);
  cursor: not-allowed;
}

/* 快捷入口卡片 */
.quick-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 36px;
}

.quick-card {
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  transition: box-shadow var(--wx-transition-normal);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.quick-card:hover {
  box-shadow: var(--wx-shadow-md);
}

.quick-card .card-icon {
  font-size: 32px;
}

.quick-card .card-title {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-primary);
  font-weight: 500;
}

.quick-card .card-desc {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

/* 热门问题 */
.hot-questions {
  background: var(--wx-bg-white);
  border-radius: var(--wx-radius-md);
  box-shadow: var(--wx-shadow-sm);
  padding: 20px;
  text-align: left;
}

.section-title {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin: 0 0 12px 0;
  text-align: left;
}

.hot-question-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--wx-radius-sm);
  cursor: pointer;
  transition: background var(--wx-transition-fast);
  gap: 12px;
}

.hot-question-item:hover {
  background: var(--wx-bg-hover);
}

.hot-question-item .question-text {
  flex: 1;
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hot-question-item .question-count {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  flex-shrink: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .left-panel {
    width: 260px;
  }

  .welcome-content {
    padding: 40px 20px;
  }

  .quick-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .left-panel {
    width: 100%;
    position: absolute;
    z-index: 100;
    height: 100vh;
    box-shadow: var(--wx-shadow-lg);
  }

  .welcome-content {
    padding: 30px 16px;
  }

  .welcome-logo {
    font-size: 44px;
  }

  .welcome-title {
    font-size: var(--wx-font-size-xl);
  }

  .quick-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}
</style>