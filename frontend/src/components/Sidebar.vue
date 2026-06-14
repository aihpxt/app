<template>
  <aside :class="['app-sidebar', { collapsed: collapsed && !isMobile, 'mobile-open': mobileOpen }]">
    <!-- Logo区域 -->
    <div class="sidebar-header" @click="$emit('navigate', '/')">
      <div class="logo-icon">🦐</div>
      <span class="logo-text">小龙虾择校</span>
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <div
        v-for="item in navItems"
        :key="item.path"
        :class="['sidebar-nav-item', { active: isActive(item.path) }]"
        @click="$emit('navigate', item.path)"
        :title="item.title"
      >
        <span class="nav-icon">
          <el-icon><component :is="item.icon" /></el-icon>
        </span>
        <span class="nav-text">{{ item.title }}</span>
      </div>
    </nav>

    <!-- 底部用户区 -->
    <div class="sidebar-footer">
      <div class="sidebar-user" @click="$emit('navigate', '/user')">
        <el-avatar :size="32" :src="userAvatar" class="user-avatar" />
        <span class="user-name">{{ userName }}</span>
      </div>
    </div>

    <!-- 折叠按钮（桌面端） -->
    <div v-if="!isMobile" class="sidebar-toggle" @click="$emit('toggle')">
      <el-icon><component :is="collapsed ? DArrowRight : DArrowLeft" /></el-icon>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled, ChatDotRound, School, Reading, User, DArrowLeft, DArrowRight
} from '@element-plus/icons-vue'

const props = defineProps({
  collapsed: Boolean,
  mobileOpen: Boolean,
  isMobile: Boolean
})

defineEmits(['toggle', 'navigate', 'closeMobile'])

const route = useRoute()

const navItems = [
  { path: '/', title: '首页', icon: HomeFilled },
  { path: '/ai-assistant', title: 'AI助手', icon: ChatDotRound },
  { path: '/school', title: '学校查询', icon: School },
  { path: '/policy', title: '政策查询', icon: Reading },
  { path: '/user', title: '个人中心', icon: User },
]

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const userName = computed(() => {
  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    return userInfo.nickname || userInfo.username || '未登录'
  } catch {
    return '未登录'
  }
})

const userAvatar = computed(() => {
  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    return userInfo.avatar || ''
  } catch {
    return ''
  }
})
</script>