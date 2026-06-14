<template>
  <div class="app-wrapper">
    <Header v-if="showHeaderFooter" />
    <main class="main-content" :class="{ 'no-header': !showHeaderFooter }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Footer v-if="showHeaderFooter" />
    <FeedbackWidget v-if="showHeaderFooter" />
  </div>
</template>

<script>
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import FeedbackWidget from './components/FeedbackWidget.vue'

export default {
  name: 'App',
  components: {
    Header,
    Footer,
    FeedbackWidget
  },
  computed: {
    isHome() {
      return this.$route.path === '/'
    },
    isAiAssistant() {
      return this.$route.path === '/ai-assistant'
    },
    showHeaderFooter() {
      return !this.isHome && !this.isAiAssistant
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(180deg, #080810 0%, #12121f 50%, #1a1a32 100%);
  color: #fff;
}

#app {
  height: 100%;
}

.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background-color: #12121f;
  padding-top: 64px;
}

.main-content.no-header {
  padding-top: 0;
  background: transparent;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  --bg-primary: #080810;
  --bg-secondary: #1a1a32;
  --bg-card: rgba(255, 255, 255, 0.04);
  --border-color: rgba(255, 255, 255, 0.08);
  --text-primary: rgba(255, 255, 255, 1);
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.4);
  --shadow-sm: 0 4px 20px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 8px 40px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 16px 56px rgba(0, 0, 0, 0.4);
}
</style>
