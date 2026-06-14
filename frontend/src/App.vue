<template>
  <div class="app-layout">
    <!-- 移动端遮罩 -->
    <div v-if="isMobile && sidebarOpen" class="mobile-overlay" @click="sidebarOpen = false"></div>

    <!-- 左侧导航栏 -->
    <Sidebar
      :collapsed="sidebarCollapsed"
      :mobile-open="sidebarOpen"
      :is-mobile="isMobile"
      @toggle="toggleSidebar"
      @navigate="handleNavigate"
      @close-mobile="sidebarOpen = false"
    />

    <!-- 右侧主内容区 -->
    <div class="app-main">
      <!-- 移动端顶部栏 -->
      <div v-if="isMobile" class="mobile-header">
        <button class="menu-btn" @click="sidebarOpen = true">
          <el-icon><Menu /></el-icon>
        </button>
        <span class="header-title">{{ currentPageTitle }}</span>
      </div>

      <!-- 主内容 -->
      <div class="app-main-content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <keep-alive :include="cachedComponents">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </div>

      <!-- 底部状态栏 -->
      <div class="status-bar">© 2026 爱鹏航 保留所有权利</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu } from '@element-plus/icons-vue'
import Sidebar from './components/Sidebar.vue'
import { trackAsyncOperation, trackEvent } from './utils/performance'

const router = useRouter()
const route = useRoute()
const sidebarCollapsed = ref(false)
const sidebarOpen = ref(false)
const isMobile = ref(false)

const cachedComponents = ['Home', 'School', 'Policy', 'User']

const currentPageTitle = computed(() => {
  return String(route.meta.title) || '小龙虾择校'
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleNavigate = (path) => {
    router.push(path)
    if (isMobile.value) {
      sidebarOpen.value = false
    }
  }

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    sidebarOpen.value = false
  }
}

const initApp = async () => {
  await trackAsyncOperation('router-ready', async () => {
    await router.isReady()
  })
  
  await trackAsyncOperation('preload-data', async () => {
    try {
      await Promise.all([
        fetch('/api/schools?size=10').catch(() => {}),
        fetch('/api/policies?size=5').catch(() => {}),
      ])
      trackEvent('app-ready', 'system')
    } catch {
      // 预加载失败不影响正常使用
    }
  })
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  initApp()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
</style>