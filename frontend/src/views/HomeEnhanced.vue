<template>
  <div class="home-page-enhanced">
    <!-- 网格背景 -->
    <div class="grid-bg"></div>

    <!-- 导航栏 -->
    <nav class="nav-bar">
      <div class="nav-content">
        <div class="nav-left" @click="goHome">
          <span class="logo-icon">🦐</span>
          <span class="logo-text">小龙虾择校</span>
        </div>
        <div class="nav-center">
          <router-link to="/" class="nav-link" active-class="active">首页</router-link>
          <router-link to="/school" class="nav-link">学校</router-link>
          <router-link to="/ai-assistant" class="nav-link">AI助手</router-link>
          <router-link to="/data-visualization" class="nav-link">数据</router-link>
        </div>
        <div class="nav-right">
          <template v-if="!userStore.isLoggedIn">
            <button class="nav-btn-secondary" @click="goLogin">登录</button>
            <button class="nav-btn-primary" @click="goLogin">立即体验</button>
          </template>
          <template v-else-if="userStore.userInfo && typeof userStore.userInfo === 'object' && !Array.isArray(userStore.userInfo)">
            <div class="user-menu">
              <div class="user-avatar" @click="toggleUserMenu">
                {{ userStore.userInfo.nickname?.charAt(0) || '用' }}
              </div>
              <div class="user-dropdown" :class="{ visible: isUserMenuOpen }">
                <div class="dropdown-item" @click="goUserCenter">
                  <span class="icon">👤</span>
                  <span>个人中心</span>
                </div>
                <div class="dropdown-item" @click="goFavorites">
                  <span class="icon">⭐</span>
                  <span>我的收藏</span>
                </div>
                <div class="dropdown-divider"></div>
                <div class="dropdown-item" @click="handleLogout">
                  <span class="icon">🚪</span>
                  <span>退出登录</span>
                </div>
              </div>
            </div>
          </template>
          <!-- 移动端菜单按钮 -->
          <button class="mobile-menu-btn" @click="toggleMobileMenu">
            <span class="menu-icon">{{ isMobileMenuOpen ? '✕' : '☰' }}</span>
          </button>
        </div>
      </div>
    </nav>

    <!-- 移动端菜单 -->
    <div class="mobile-menu" :class="{ visible: isMobileMenuOpen }">
      <div class="mobile-menu-overlay" @click="toggleMobileMenu"></div>
      <div class="mobile-menu-content">
        <div class="mobile-menu-header">
          <span class="mobile-logo">🦐 小龙虾择校</span>
          <button class="mobile-menu-close" @click="toggleMobileMenu">✕</button>
        </div>
        <div class="mobile-menu-links">
          <router-link to="/" class="mobile-menu-link" @click="toggleMobileMenu">首页</router-link>
          <router-link to="/school" class="mobile-menu-link" @click="toggleMobileMenu">学校查询</router-link>
          <router-link to="/ai-assistant" class="mobile-menu-link" @click="toggleMobileMenu">AI助手</router-link>
          <router-link to="/data-visualization" class="mobile-menu-link" @click="toggleMobileMenu">数据分析</router-link>
          <router-link to="/volunteer" class="mobile-menu-link" @click="toggleMobileMenu">志愿填报</router-link>
          <router-link to="/help" class="mobile-menu-link" @click="toggleMobileMenu">帮助中心</router-link>
        </div>
        <div class="mobile-menu-footer">
          <button v-if="!userStore.isLoggedIn" class="mobile-login-btn" @click="goLogin">登录/注册</button>
          <button v-else class="mobile-login-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- Hero区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <div class="hero-badge animate-fadeInUp">
            <span class="badge-icon">✨</span>
            <span>AI赋能 · 智慧择校</span>
          </div>
          <h1 class="hero-title animate-fadeInUp animate-delay-1">
            让每个孩子
            <br>
            <span class="highlight">都能找到最适合的学校</span>
          </h1>
          <p class="hero-desc animate-fadeInUp animate-delay-2">
            云南省中考择校智能助手，AI智能分析，精准推荐
            <br>
            让志愿填报更简单、更科学
          </p>
          <div class="hero-actions animate-fadeInUp animate-delay-3">
            <button class="btn-primary btn-enhanced" @click="goAiAssistant">
              <span class="btn-icon">🤖</span>
              <span>开始AI咨询</span>
              <span class="btn-arrow">→</span>
            </button>
            <button class="btn-secondary btn-enhanced" @click="goSchoolList">
              <span class="btn-icon">🏫</span>
              <span>浏览学校</span>
            </button>
          </div>
          <div class="hero-stats animate-fadeInUp animate-delay-4">
            <div class="stat-item">
              <div class="stat-number">500+</div>
              <div class="stat-label">优质学校</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-number">100K+</div>
              <div class="stat-label">用户信赖</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-number">98%</div>
              <div class="stat-label">满意度</div>
            </div>
          </div>
        </div>

        <!-- Hero右侧装饰 -->
        <div class="hero-visual animate-scaleIn">
          <div class="visual-card visual-card-1">
            <div class="visual-icon">📊</div>
            <div class="visual-title">智能分析</div>
            <div class="visual-desc">AI算法精准匹配</div>
          </div>
          <div class="visual-card visual-card-2">
            <div class="visual-icon">🎯</div>
            <div class="visual-title">个性化推荐</div>
            <div class="visual-desc">根据分数智能推荐</div>
          </div>
          <div class="visual-card visual-card-3">
            <div class="visual-icon">💡</div>
            <div class="visual-title">智慧决策</div>
            <div class="visual-desc">科学的志愿填报</div>
          </div>
        </div>
      </section>

      <!-- 输入区域 -->
      <section class="input-section">
        <div class="input-container animate-fadeInUp">
          <div class="input-header">
            <span class="input-icon">💬</span>
            <span class="input-title">AI智能咨询</span>
          </div>
          <div class="input-wrapper">
            <textarea
              v-model="userInput"
              class="main-textarea"
              placeholder="例如：我家孩子估分680分，昆明户籍，想读重点高中，推荐哪些学校？"
              @keydown.enter.prevent="handleSubmit"
              rows="3"
            ></textarea>
            <div class="input-footer">
              <div class="quick-tips">
                <span class="tip-item" @click="useQuickTip('680分推荐学校')">
                  🏫 680分推荐
                </span>
                <span class="tip-item" @click="useQuickTip('昆明重点高中')">
                  📍 昆明重点
                </span>
                <span class="tip-item" @click="useQuickTip('志愿填报技巧')">
                  📝 志愿技巧
                </span>
              </div>
              <button class="send-btn btn-enhanced" @click="handleSubmit" :disabled="!userInput.trim()">
                <span class="send-icon">🚀</span>
                <span>发送</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 特色功能区 -->
      <section class="features-section">
        <div class="section-header">
          <span class="section-tag">功能特性</span>
          <h2 class="section-title">为什么选择小龙虾择校</h2>
          <p class="section-desc">六大核心功能，为您的择校之路保驾护航</p>
        </div>
        <div class="features-grid">
          <div
            v-for="(feature, index) in features"
            :key="feature.id"
            class="feature-card card-enhanced animate-fadeInUp"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="goToFeature(feature.id)"
          >
            <div class="feature-icon-wrapper">
              <span class="feature-icon">{{ feature.icon }}</span>
            </div>
            <h3 class="feature-name">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
            <div class="feature-tag">{{ feature.tag }}</div>
          </div>
        </div>
      </section>

      <!-- 热门问题区 -->
      <section class="hot-questions-section">
        <div class="section-header">
          <span class="section-tag">热门问题</span>
          <h2 class="section-title">大家都在问什么</h2>
        </div>
        <div class="questions-container">
          <div
            v-for="(question, index) in hotQuestions"
            :key="question.id"
            class="question-card animate-fadeInLeft"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="goToAiAssistantWithQuestion(question.content)"
          >
            <div class="question-number">{{ String(index + 1).padStart(2, '0') }}</div>
            <div class="question-content">
              <div class="question-title">{{ question.content }}</div>
              <div class="question-meta">
                <span class="meta-item">🔥 {{ question.count }}人关注</span>
                <span class="meta-item">👀 {{ question.views }}次浏览</span>
              </div>
            </div>
            <div class="question-arrow">→</div>
          </div>
        </div>
      </section>

      <!-- 热门学校区 -->
      <section class="hot-schools-section">
        <div class="section-header">
          <span class="section-tag">热门学校</span>
          <h2 class="section-title">云南省优质高中推荐</h2>
          <p class="section-desc">精选全省顶尖高中，助力学子圆梦</p>
        </div>
        <div class="hot-schools-grid">
          <div
            v-for="(school, index) in hotSchools"
            :key="school.id"
            class="school-card card-enhanced animate-fadeInUp"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="goToSchoolDetail(school.id)"
          >
            <div class="school-card-header">
              <div class="school-rank" :class="school.rank <= 3 ? 'top-three' : ''">
                {{ school.rank }}
              </div>
              <div class="school-logo-wrapper">
                <span class="school-logo-icon">🏛️</span>
              </div>
              <div class="school-favorite" @click.stop="toggleSchoolFavorite(school)">
                <span :class="{ favorited: school.isFavorited }">{{ school.isFavorited ? '❤️' : '🤍' }}</span>
              </div>
            </div>
            <div class="school-card-body">
              <h3 class="school-name">{{ school.name }}</h3>
              <p class="school-location">{{ school.location }}</p>
              <div class="school-tags">
                <el-tag v-if="school.isKey" type="danger" size="small">重点高中</el-tag>
                <el-tag v-if="school.type" type="primary" size="small">{{ school.type }}</el-tag>
              </div>
            </div>
            <div class="school-card-footer">
              <div class="school-score">
                <span class="score-label">录取分</span>
                <span class="score-value">{{ school.minScore }}</span>
              </div>
              <div class="school-rate">
                <span class="rate-label">一本率</span>
                <span class="rate-value">{{ school.rate }}</span>
              </div>
              <button class="school-detail-btn" @click.stop="goToSchoolDetail(school.id)">查看 →</button>
            </div>
          </div>
        </div>
        <div class="section-footer">
          <button class="view-more-btn" @click="goSchoolList">查看更多学校 →</button>
        </div>
      </section>

      <!-- 个性化推荐区 -->
      <section class="recommendations-section" v-if="userStore.isLoggedIn">
        <div class="section-header">
          <span class="section-tag">为你推荐</span>
          <h2 class="section-title">专属你的择校建议</h2>
        </div>
        <div class="recommendations-grid">
          <div
            v-for="(rec, index) in recommendations"
            :key="rec.id"
            class="recommendation-card card-enhanced animate-fadeInUp"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="goToRecommendation(rec)"
          >
            <div class="rec-header">
              <span class="rec-icon">{{ rec.icon }}</span>
              <span class="rec-badge" :class="rec.badgeType">{{ rec.badge }}</span>
            </div>
            <h3 class="rec-title">{{ rec.title }}</h3>
            <p class="rec-desc">{{ rec.description }}</p>
            <div class="rec-footer">
              <span class="rec-stats">👥 {{ rec.stats }}人已使用</span>
              <button class="rec-btn">查看详情 →</button>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA区域 -->
      <section class="cta-section">
        <div class="cta-content">
          <div class="cta-left animate-fadeInLeft">
            <h2 class="cta-title">准备好开始了吗？</h2>
            <p class="cta-desc">
              加入我们，让AI为您的孩子找到最适合的学校
              <br>
              开启智慧择校之旅
            </p>
          </div>
          <div class="cta-right animate-fadeInRight">
            <button class="cta-btn btn-enhanced" @click="goLogin">
              <span class="btn-icon">🚀</span>
              <span>立即开始</span>
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- 返回顶部按钮 -->
    <button 
      class="back-to-top" 
      :class="{ visible: showBackToTop }"
      @click="scrollToTop"
    >
      <span class="back-icon">↑</span>
    </button>

    <!-- 页脚 -->
    <footer class="footer-bar">
      <div class="footer-content">
        <div class="footer-left">
          <div class="footer-logo">
            <span class="logo-icon">🦐</span>
            <span>小龙虾择校</span>
          </div>
          <p class="footer-desc">云南省中考择校智能决策平台</p>
          <p class="footer-copyright">© 2026 小龙虾择校. All rights reserved.</p>
        </div>
        <div class="footer-right">
          <div class="footer-links">
            <div class="link-group">
              <h4 class="link-title">产品</h4>
              <router-link to="/ai-assistant" class="link-item">AI助手</router-link>
              <router-link to="/school" class="link-item">学校库</router-link>
              <router-link to="/data-visualization" class="link-item">数据分析</router-link>
            </div>
            <div class="link-group">
              <h4 class="link-title">帮助</h4>
              <router-link to="/help" class="link-item">使用指南</router-link>
              <router-link to="/help" class="link-item">常见问题</router-link>
              <router-link to="/help" class="link-item">联系我们</router-link>
            </div>
            <div class="link-group">
              <h4 class="link-title">法律</h4>
              <router-link to="/legal/terms" class="link-item">用户协议</router-link>
              <router-link to="/legal/privacy" class="link-item">隐私政策</router-link>
              <router-link to="/legal/copyright" class="link-item">版权声明</router-link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const userInput = ref('')
const isUserMenuOpen = ref(false)
const isMobileMenuOpen = ref(false)
const showBackToTop = ref(false)

const features = ref([
  {
    id: 1,
    icon: '🤖',
    title: 'AI智能推荐',
    description: '基于深度学习算法，根据分数、地区等多维度精准匹配学校',
    tag: '推荐'
  },
  {
    id: 2,
    icon: '📊',
    title: '数据分析',
    description: '历年录取分数线、招生计划等数据全方位分析对比',
    tag: '分析'
  },
  {
    id: 3,
    icon: '🎯',
    title: '志愿填报',
    description: '科学的志愿填报策略，降低滑档风险',
    tag: '填报'
  },
  {
    id: 4,
    icon: '🏫',
    title: '学校详情',
    description: '完整的学校信息、师资力量、教学特色等介绍',
    tag: '详情'
  },
  {
    id: 5,
    icon: '📈',
    title: '趋势预测',
    description: '预测各学校分数线，为志愿填报提供参考',
    tag: '预测'
  },
  {
    id: 6,
    icon: '👥',
    title: '社区交流',
    description: '与家长、学生交流经验，分享择校心得',
    tag: '社区'
  }
])

const hotQuestions = ref([
  { id: 1, content: '2026年昆明中考录取分数线预测', count: 1258, views: 5680 },
  { id: 2, content: '如何选择适合自己的高中学校', count: 987, views: 4320 },
  { id: 3, content: '中考志愿填报有哪些技巧', count: 876, views: 3980 },
  { id: 4, content: '昆明有哪些一级一等高中', count: 765, views: 3450 },
  { id: 5, content: '师大附中2025年录取分数是多少', count: 654, views: 2890 },
  { id: 6, content: '重点高中和普通高中有什么区别', count: 543, views: 2340 }
])

const recommendations = ref([
  {
    id: 1,
    icon: '🏫',
    title: '云南师范大学附属中学',
    description: '云南省顶尖高中，师资力量雄厚，一本率高达98%',
    badge: '热门推荐',
    badgeType: 'hot',
    stats: '12.5K'
  },
  {
    id: 2,
    icon: '📅',
    title: '2026中考复习计划',
    description: '根据你的学习情况，制定个性化的复习计划',
    badge: '专属方案',
    badgeType: 'primary',
    stats: '8.3K'
  },
  {
    id: 3,
    icon: '📚',
    title: '中考真题解析',
    description: '2021-2025年中考真题及详细解析资料',
    badge: '资料下载',
    badgeType: 'success',
    stats: '6.7K'
  }
])

const hotSchools = ref([
  { id: 1, name: '云南师范大学附属中学', location: '昆明市呈贡区', minScore: '685', rate: '98%', isKey: true, type: '公办', rank: 1, isFavorited: false },
  { id: 2, name: '昆明市第一中学', location: '昆明市五华区', minScore: '678', rate: '95%', isKey: true, type: '公办', rank: 2, isFavorited: false },
  { id: 3, name: '云南大学附属中学', location: '昆明市盘龙区', minScore: '670', rate: '92%', isKey: true, type: '民办', rank: 3, isFavorited: false },
  { id: 4, name: '昆明市第三中学', location: '昆明市呈贡区', minScore: '665', rate: '88%', isKey: true, type: '公办', rank: 4, isFavorited: false },
  { id: 5, name: '曲靖市第一中学', location: '曲靖市麒麟区', minScore: '660', rate: '90%', isKey: true, type: '公办', rank: 5, isFavorited: false },
  { id: 6, name: '玉溪市第一中学', location: '玉溪市红塔区', minScore: '655', rate: '86%', isKey: true, type: '公办', rank: 6, isFavorited: false },
  { id: 7, name: '昆明市第十四中学', location: '昆明市五华区', minScore: '645', rate: '82%', isKey: true, type: '公办', rank: 7, isFavorited: false },
  { id: 8, name: '安宁中学', location: '昆明市安宁市', minScore: '640', rate: '80%', isKey: true, type: '公办', rank: 8, isFavorited: false }
])

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleClickOutside = (e) => {
  if (!e.target.closest('.user-menu')) {
    isUserMenuOpen.value = false
  }
}

const goHome = () => {
  router.push('/')
}

const goLogin = () => {
  router.push('/login')
}

const goUserCenter = () => {
  isUserMenuOpen.value = false
  router.push('/user')
}

const goFavorites = () => {
  isUserMenuOpen.value = false
  router.push('/favorite')
}

const goAiAssistant = () => {
  router.push('/ai-assistant')
}

const goSchoolList = () => {
  router.push('/school')
}

const handleLogout = () => {
  isUserMenuOpen.value = false
  userStore.logout()
  ElMessage.success('退出登录成功')
}

const handleSubmit = () => {
  if (!userInput.value.trim()) return
  const question = userInput.value.trim()
  userInput.value = ''
  router.push({
    path: '/ai-assistant',
    query: { question: encodeURIComponent(question) }
  })
}

const useQuickTip = (text) => {
  userInput.value = text
}

const goToAiAssistantWithQuestion = (question) => {
  router.push({
    path: '/ai-assistant',
    query: { question: encodeURIComponent(question) }
  })
}

const goToRecommendation = (rec) => {
  if (rec.id === 1) {
    router.push({
      path: '/ai-assistant',
      query: { question: encodeURIComponent('介绍一下云南师范大学附属中学') }
    })
  } else {
    router.push('/ai-assistant')
  }
}

const goToSchoolDetail = (schoolId) => {
  router.push(`/school/${schoolId}`)
}

const toggleSchoolFavorite = (school) => {
  school.isFavorited = !school.isFavorited
  if (school.isFavorited) {
    ElMessage.success('已收藏该学校')
  } else {
    ElMessage.info('已取消收藏')
  }
}

const goToFeature = (featureId) => {
  const featureRoutes = {
    1: '/ai-selection',      // AI智能推荐
    2: '/data-visualization', // 数据分析
    3: '/volunteer',         // 志愿填报
    4: '/school',            // 学校详情
    5: '/score-prediction',  // 趋势预测
    6: '/ai-assistant'       // 社区交流 -> AI助手
  }
  const route = featureRoutes[featureId] || '/ai-assistant'
  router.push(route)
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

const handleScroll = () => {
  showBackToTop.value = window.scrollY > 500
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.home-page-enhanced {
  min-height: 100%;
  position: relative;
  overflow-x: hidden;
  background: linear-gradient(135deg, #080810 0%, #12121f 30%, #1a1a32 60%, #0d0d1a 100%);
}

/* 网格背景 */
.grid-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

/* 导航栏 */
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 72px;
  z-index: 1000;
  background: rgba(8, 8, 16, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.nav-left:hover {
  transform: translateX(5px);
}

.logo-icon {
  font-size: 36px;
  filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.4));
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-center {
  display: flex;
  gap: 40px;
}

.nav-link {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: color 0.3s;
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 8px 0;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--primary-gradient);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.nav-link:hover,
.nav-link.active {
  color: #fff;
}

.nav-link:hover::after,
.nav-link.active::after {
  transform: scaleX(1);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-btn-secondary,
.nav-btn-primary {
  padding: 10px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.nav-btn-secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.nav-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-btn-primary {
  background: var(--primary-gradient);
  border: none;
  color: #fff;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.nav-btn-primary:hover {
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
}

/* 用户菜单 */
.user-menu {
  position: relative;
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.user-avatar:hover {
  transform: scale(1.1);
}

.user-dropdown {
  position: absolute;
  top: 54px;
  right: 0;
  min-width: 180px;
  background: #ffffff;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 8px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.user-dropdown.visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
  color: #1a1a2e;
}

.dropdown-item:hover {
  background: rgba(102, 126, 234, 0.15);
  color: #1a1a2e;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 4px 0;
}

/* 主内容 */
.main-content {
  position: relative;
  z-index: 1;
  padding-top: 72px;
}

/* Hero区域 */
.hero-section {
  padding: 100px 40px 60px;
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 50px;
  color: #667eea;
  font-size: 14px;
  font-weight: 500;
  width: fit-content;
}

.badge-icon {
  font-size: 16px;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.2;
  margin: 0;
  color: #fff;
}

.highlight {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.8;
  margin: 0;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-top: 12px;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.btn-primary {
  background: var(--primary-gradient);
  border: none;
  color: #fff;
  box-shadow: var(--shadow-primary);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-primary-hover);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
}

.btn-icon {
  font-size: 20px;
}

.btn-arrow {
  transition: transform 0.3s;
}

.btn-primary:hover .btn-arrow {
  transform: translateX(5px);
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-top: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

/* Hero视觉 */
.hero-visual {
  position: relative;
  height: 500px;
}

.visual-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 24px;
  transition: box-shadow 0.4s, transform 0.4s, background-color 0.4s;
}

.visual-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(102, 126, 234, 0.3);
}

.visual-card-1 {
  top: 20%;
  left: 10%;
  animation: float 4s ease-in-out;
}

.visual-card-2 {
  top: 45%;
  right: 5%;
  animation: floatSlow 5s ease-in-out;
}

.visual-card-3 {
  bottom: 15%;
  left: 20%;
  animation: float 6s ease-in-out;
}

.visual-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.visual-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6px;
}

.visual-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

/* 输入区域 */
.input-section {
  padding: 40px;
  max-width: 900px;
  margin: 0 auto;
}

.input-container {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 32px;
  box-shadow: var(--shadow-md);
}

.input-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.input-icon {
  font-size: 24px;
}

.input-title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.main-textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 18px 20px;
  color: #fff;
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  outline: none;
  transition: box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}

.main-textarea:focus {
  border-color: rgba(102, 126, 234, 0.7);
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2),
              0 0 30px rgba(102, 126, 234, 0.1);
  background: rgba(0, 0, 0, 0.25);
  transform: translateY(-2px);
}

.main-textarea:hover:not(:focus) {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.25);
}

.main-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-tips {
  display: flex;
  gap: 12px;
}

.tip-item {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.tip-item:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
  color: #667eea;
}

.send-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-primary);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-icon {
  font-size: 18px;
}

/* Section通用样式 */
.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-tag {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 50px;
  color: #667eea;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 16px;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px 0;
}

.section-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* 特色功能区 */
.features-section {
  padding: 80px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 32px;
  cursor: pointer;
  transition: box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.4s, border-color 0.4s;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.feature-card:hover::before {
  left: 100%;
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.02);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 25px 50px rgba(102, 126, 234, 0.25);
}

.feature-icon-wrapper {
  width: 72px;
  height: 72px;
  background: var(--primary-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover .feature-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.45);
}

.feature-icon {
  font-size: 36px;
}

.feature-name {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 12px 0;
}

.feature-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 16px 0;
  line-height: 1.7;
}

.feature-tag {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  color: #667eea;
  font-size: 12px;
}

/* 热门问题区 */
.hot-questions-section {
  padding: 80px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.questions-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px 28px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.question-card:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateX(8px);
}

.question-number {
  font-size: 24px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  min-width: 50px;
}

.question-content {
  flex: 1;
}

.question-title {
  font-size: 16px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 8px;
}

.question-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.question-arrow {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.4);
  transition: transform 0.3s;
}

.question-card:hover .question-arrow {
  color: #667eea;
  transform: translateX(5px);
}

/* 热门学校区 */
.hot-schools-section {
  padding: 80px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.hot-schools-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.school-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 28px;
  cursor: pointer;
  transition: box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.school-card:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
}

.school-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.school-rank {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.6);
}

.school-rank.top-three {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.school-logo-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.school-logo-icon {
  font-size: 48px;
}

.school-favorite {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.school-favorite:hover {
  transform: scale(1.3);
}

.school-card-body {
  text-align: center;
  margin-bottom: 20px;
}

.school-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px 0;
}

.school-location {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 12px 0;
}

.school-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.school-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.school-score,
.school-rate {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-label,
.rate-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 4px;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
}

.rate-value {
  font-size: 20px;
  font-weight: 700;
  color: #92fe9d;
}

.school-detail-btn {
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  color: #667eea;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}

.school-detail-btn:hover {
  background: rgba(102, 126, 234, 0.3);
  color: #fff;
}

.section-footer {
  text-align: center;
  margin-top: 48px;
}

.view-more-btn {
  background: transparent;
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 12px;
  color: #667eea;
  padding: 14px 36px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s, transform 0.3s;
}

.view-more-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  color: #fff;
  transform: translateY(-2px);
}

/* 推荐区域 */
.recommendations-section {
  padding: 80px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.recommendation-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 28px;
  cursor: pointer;
  transition: box-shadow 0.3s, transform 0.3s, background-color 0.3s, border-color 0.3s;
}

.recommendation-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.rec-icon {
  font-size: 40px;
}

.rec-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.rec-badge.hot {
  background: rgba(245, 87, 108, 0.2);
  color: #f5576c;
  border: 1px solid rgba(245, 87, 108, 0.3);
}

.rec-badge.primary {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.rec-badge.success {
  background: rgba(146, 254, 157, 0.2);
  color: #92fe9d;
  border: 1px solid rgba(146, 254, 157, 0.3);
}

.rec-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 10px 0;
}

.rec-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 20px 0;
  line-height: 1.7;
}

.rec-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rec-stats {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.rec-btn {
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  color: #667eea;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.rec-btn:hover {
  background: rgba(102, 126, 234, 0.25);
}

/* CTA区域 */
.cta-section {
  padding: 80px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.cta-content {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cta-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px 0;
}

.cta-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.8;
}

.cta-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 14px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.35);
}

.cta-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.45);
}

/* 页脚 */
.footer-bar {
  background: rgba(8, 8, 16, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 60px 40px 30px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 60px;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.footer-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.footer-copyright {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

.footer-right {
  display: flex;
  justify-content: flex-end;
}

.footer-links {
  display: flex;
  gap: 80px;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.link-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.link-item {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: color 0.3s;
}

.link-item:hover {
  color: #667eea;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-visual {
    height: 350px;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-stats {
    justify-content: center;
  }

  .hero-badge {
    margin: 0 auto;
  }
}

@media (max-width: 992px) {
  .features-grid,
  .recommendations-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .nav-center {
    display: none;
  }

  .cta-content {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .nav-content {
    padding: 0 20px;
  }

  .hero-section {
    padding: 80px 20px 40px;
  }

  .hero-title {
    font-size: 36px;
  }

  .hero-desc {
    font-size: 16px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .features-grid,
  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .input-section {
    padding: 40px 20px;
  }

  .quick-tips {
    flex-wrap: wrap;
  }

  .footer-content {
    grid-template-columns: 1fr;
  }

  .footer-links {
    gap: 40px;
  }
}

@media (max-width: 480px) {
  .nav-content {
    padding: 0 16px;
  }

  .hero-title {
    font-size: 28px;
  }

  .section-title {
    font-size: 28px;
  }

  .features-section,
  .hot-questions-section,
  .recommendations-section,
  .cta-section {
    padding: 60px 20px;
  }

  .cta-content {
    padding: 40px 24px;
  }
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.mobile-menu-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 移动端菜单 */
.mobile-menu {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  visibility: hidden;
  opacity: 0;
  transition: visibility 0.3s, opacity 0.3s;
}

.mobile-menu.visible {
  visibility: visible;
  opacity: 1;
}

.mobile-menu-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
}

.mobile-menu-content {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 80%;
  max-width: 280px;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.mobile-menu.visible .mobile-menu-content {
  transform: translateX(0);
}

.mobile-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.mobile-logo {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.mobile-menu-close {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

.mobile-menu-links {
  padding: 20px 0;
}

.mobile-menu-link {
  display: block;
  padding: 16px 24px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 16px;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
  border-left: 3px solid transparent;
}

.mobile-menu-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
  border-left-color: #6366f1;
}

.mobile-menu-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.mobile-login-btn {
  width: 100%;
  padding: 12px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
}

/* 返回顶部按钮 */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background: rgba(99, 102, 241, 0.9);
  border: none;
  border-radius: 50%;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s, background 0.3s;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.back-to-top:hover {
  background: rgba(99, 102, 241, 1);
}

.back-to-top.visible {
  opacity: 1;
  visibility: visible;
}

.back-icon {
  font-weight: bold;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .nav-center {
    display: none;
  }

  .nav-right {
    gap: 12px;
  }

  .nav-btn-secondary,
  .nav-btn-primary {
    display: none;
  }

  .user-menu {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-menu {
    display: block;
  }

  .hot-schools-section,
  .features-section,
  .recommendations-section {
    padding: 60px 20px;
  }

  .hot-schools-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .school-card {
    padding: 20px;
  }

  .school-name {
    font-size: 15px;
  }

  .score-value,
  .rate-value {
    font-size: 16px;
  }
}
</style>
