<template>
  <el-header class="app-header" v-if="showHeader">
    <div class="header-content">
      <div class="logo" @click="goHome">
        <span class="logo-icon">🦐</span>
        <span class="logo-text">小龙虾择校</span>
      </div>
      
      <div class="nav-actions">
        <el-dropdown trigger="click" @command="handleNavCommand" @visible-change="handleNavMenuVisibleChange">
          <el-button text class="nav-btn" :class="{ 'nav-btn-active': isNavMenuVisible }">
            <el-icon class="menu-icon"><Menu /></el-icon>
            <span>功能</span>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu class="nav-dropdown-menu">
              <el-dropdown-item command="/ai-assistant" class="nav-dropdown-item">
                <el-icon><ChatDotRound /></el-icon>AI智能助手
              </el-dropdown-item>
              <el-dropdown-item command="/score-prediction" class="nav-dropdown-item">
                <el-icon><TrendCharts /></el-icon>分数预测
              </el-dropdown-item>
              <el-dropdown-item command="/ai-selection" class="nav-dropdown-item">
                <el-icon><Aim /></el-icon>智能择校
              </el-dropdown-item>
              <el-dropdown-item command="/volunteer" class="nav-dropdown-item">
                <el-icon><Document /></el-icon>志愿填报
              </el-dropdown-item>
              <el-dropdown-item divided command="/school" class="nav-dropdown-item">
                <el-icon><School /></el-icon>学校查询
              </el-dropdown-item>
              <el-dropdown-item command="/policy" class="nav-dropdown-item">
                <el-icon><Reading /></el-icon>政策解读
              </el-dropdown-item>
              <el-dropdown-item command="/data" class="nav-dropdown-item">
                <el-icon><DataAnalysis /></el-icon>数据中心
              </el-dropdown-item>
              <el-dropdown-item command="/help" class="nav-dropdown-item">
                <el-icon><QuestionFilled /></el-icon>帮助中心
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <template v-if="isLoggedIn && userInfo && typeof userInfo === 'object' && !Array.isArray(userInfo)">
            <el-dropdown @command="handleUserCommand" @visible-change="handleUserMenuVisibleChange">
              <span class="user-info" :class="{ 'user-info-active': isUserMenuVisible }">
                <el-avatar :size="28" :src="(userInfo && typeof userInfo === 'object' && !Array.isArray(userInfo)) ? (userInfo.avatar || defaultAvatar) : defaultAvatar" class="user-avatar" />
                <span class="username">{{ (userInfo && typeof userInfo === 'object' && !Array.isArray(userInfo)) ? (userInfo.nickname || '用户') : '用户' }}</span>
                <el-icon class="user-dropdown-icon"><ArrowDown /></el-icon>
              </span>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown-menu">
                <el-dropdown-item command="profile" class="user-dropdown-item">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="favorites" class="user-dropdown-item">
                  <el-icon><Star /></el-icon>我的收藏
                </el-dropdown-item>
                <el-dropdown-item divided command="logout" class="user-dropdown-item">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" size="small" class="login-btn" @click="goLogin">登录</el-button>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script>
import { 
  Menu, ChatDotRound, DataLine, Aim, Document, 
  School, Reading, DataAnalysis, QuestionFilled,
  User, Star, Switch, ArrowDown 
} from '@element-plus/icons-vue'
import { mapState, mapActions } from 'pinia'
import { useUserStore } from '@/store'

export default {
  name: 'AppHeader',
  components: {
    Menu, ChatDotRound, TrendCharts: DataLine, Aim, Document,
    School, Reading, DataAnalysis, QuestionFilled,
    User, Star, SwitchButton: Switch, ArrowDown
  },
  data() {
    return {
      defaultAvatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
      isNavMenuVisible: false,
      isUserMenuVisible: false
    }
  },
  computed: {
    ...mapState(useUserStore, ['isLoggedIn', 'userInfo']),
    showHeader() {
      return this.$route.path !== '/'
    }
  },
  methods: {
    ...mapActions(useUserStore, ['logout']),
    handleNavCommand(index) {
      this.$router.push(index)
      this.isNavMenuVisible = false
    },
    goHome() {
      this.$router.push('/')
    },
    goLogin() {
      this.$router.push('/login')
    },
    handleUserCommand(command) {
      switch (command) {
        case 'profile':
          this.$router.push('/user')
          break
        case 'favorites':
          this.$router.push('/favorite')
          break
        case 'logout':
          this.logout()
          this.$message.success('退出登录成功')
          this.$router.push('/')
          break
      }
      this.isUserMenuVisible = false
    },
    handleNavMenuVisibleChange(visible) {
      this.isNavMenuVisible = visible
      if (!visible) {
        // 菜单关闭时的动画处理
      }
    },
    handleUserMenuVisibleChange(visible) {
      this.isUserMenuVisible = visible
      if (!visible) {
        // 菜单关闭时的动画处理
      }
    }
  }
}
</script>

<style scoped>
.app-header {
  background: rgba(13, 13, 26, 0.85);
  backdrop-filter: blur(20px);
  box-shadow: 
    0 1px 0 rgba(255, 255, 255, 0.05),
    0 4px 24px rgba(0, 0, 0, 0.3);
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
  padding: 8px;
  margin-left: -8px;
  border-radius: 12px;
  gap: 12px;
}

.logo:hover {
  background: rgba(255, 255, 255, 0.03);
  transform: translateY(-2px);
}

.logo-icon {
  font-size: 36px;
  filter: drop-shadow(0 2px 8px rgba(102, 126, 234, 0.3));
  transition: transform 0.3s, filter 0.3s;
}

.logo:hover .logo-icon {
  transform: scale(1.1) rotate(5deg);
  filter: drop-shadow(0 4px 16px rgba(102, 126, 234, 0.5));
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: color 0.3s;
}

.logo:hover .logo-text {
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.65);
  padding: 10px 18px;
  border-radius: 12px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, transform 0.3s;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.nav-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.4), transparent);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.nav-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
  transform: translateY(-2px);
}

.nav-btn:hover::before {
  transform: scaleX(1);
}

.nav-btn-active {
  color: #667eea !important;
  background: rgba(102, 126, 234, 0.1) !important;
  border: 1px solid rgba(102, 126, 234, 0.2) !important;
}

.nav-btn-active .menu-icon {
  transform: rotate(90deg);
}

.menu-icon {
  transition: transform 0.3s;
  font-size: 18px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 16px 8px 8px;
  border-radius: 28px;
  transition: background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  overflow: hidden;
}

.user-info::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.4), transparent);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.user-info:hover::before {
  transform: scaleX(1);
}

.user-info-active {
  background: rgba(102, 126, 234, 0.1) !important;
  border-color: rgba(102, 126, 234, 0.3) !important;
}

.user-info-active .user-dropdown-icon {
  transform: rotate(180deg);
  color: #667eea;
}

.user-dropdown-icon {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  transition: transform 0.3s, color 0.3s;
}

.login-btn {
  transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
}

.username {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

:deep(.el-dropdown-menu) {
  background: #ffffff !important;
  backdrop-filter: none !important;
  border: 2px solid rgba(102, 126, 234, 0.3) !important;
  border-radius: 16px !important;
  padding: 12px !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
}

:deep(.el-dropdown-menu__item) {
  display: flex !important;
  align-items: center !important;
  gap: 12px;
  padding: 14px 20px !important;
  color: #1a1a2e !important;
  background: transparent !important;
  border-radius: 10px;
  transition: background-color 0.25s, color 0.25s;
  font-weight: 600 !important;
  letter-spacing: 0.5px;
}

:deep(.el-dropdown-menu__item:hover) {
  background: rgba(102, 126, 234, 0.3) !important;
  color: #fff !important;
  text-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.5),
    0 0 12px rgba(102, 126, 234, 0.5);
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 18px;
  color: #667eea !important;
  filter: drop-shadow(0 0 4px rgba(102, 126, 234, 0.6));
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 500;
  font-size: 14px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: box-shadow 0.3s, transform 0.3s;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
}

:deep(.el-avatar) {
  border: 2px solid rgba(102, 126, 234, 0.25);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
@media (max-width: 768px) {
  .header-content {
    padding: 0 20px;
  }
  
  .logo-icon {
    font-size: 28px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .nav-actions {
    gap: 12px;
  }
  
  .nav-btn {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .nav-btn span {
    display: none;
  }
  
  .user-info {
    padding: 6px 12px 6px 6px;
  }
  
  .username {
    display: none;
  }
  
  .user-dropdown-icon {
    display: none;
  }
  
  .app-header {
    height: 56px;
  }
  
  .header-content {
    height: 56px;
  }
  
  :deep(.el-dropdown-menu) {
    min-width: 200px;
  }
  
  :deep(.el-dropdown-menu__item) {
    padding: 10px 16px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 16px;
  }
  
  .logo-text {
    display: none;
  }
  
  .nav-actions {
    gap: 8px;
  }
  
  .nav-btn {
    padding: 6px 8px;
  }
  
  .user-info {
    padding: 4px 8px 4px 4px;
  }
  
  :deep(.el-dropdown-menu) {
    min-width: 180px;
  }
  
  :deep(.el-dropdown-menu__item) {
    padding: 8px 14px;
    font-size: 12px;
  }
}

@media (max-width: 360px) {
  .header-content {
    padding: 0 12px;
  }
  
  .logo-icon {
    font-size: 24px;
  }
  
  .nav-actions {
    gap: 6px;
  }
  
  .nav-btn {
    padding: 4px 6px;
  }
  
  .user-info {
    padding: 2px 6px 2px 2px;
  }
  
  .app-header {
    height: 48px;
  }
  
  .header-content {
    height: 48px;
  }
  
  :deep(.el-avatar) {
    width: 24px !important;
    height: 24px !important;
  }
  
  :deep(.el-dropdown-menu) {
    min-width: 160px;
  }
  
  :deep(.el-dropdown-menu__item) {
    padding: 6px 12px;
    font-size: 11px;
  }
  
  :deep(.el-dropdown-menu__item .el-icon) {
    font-size: 14px;
  }
  
  :deep(.el-button--primary) {
    padding: 8px 16px;
    font-size: 12px;
  }
}
</style>
