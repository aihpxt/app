<template>
  <div class="login-page-enhanced">
    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="bg-gradient bg-gradient-1"></div>
      <div class="bg-gradient bg-gradient-2"></div>
      <div class="bg-gradient bg-gradient-3"></div>
    </div>

    <!-- 返回按钮 -->
    <div class="back-nav">
      <button class="back-btn" @click="goHome">
        <span class="back-icon">←</span>
        <span>返回首页</span>
      </button>
    </div>

    <!-- 主内容 -->
    <div class="login-container">
      <!-- 左侧品牌区域 -->
      <div class="brand-section animate-fadeInLeft">
        <div class="brand-content">
          <div class="brand-logo">
            <span class="logo-icon">🦐</span>
          </div>
          <h1 class="brand-title">小龙虾择校</h1>
          <p class="brand-desc">云南省中考择校智能决策平台</p>
          
          <div class="brand-features">
            <div class="feature-item">
              <span class="feature-icon">🤖</span>
              <span class="feature-text">AI智能推荐</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">📊</span>
              <span class="feature-text">数据分析</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🎯</span>
              <span class="feature-text">精准匹配</span>
            </div>
          </div>

          <div class="brand-stats">
            <div class="stat-card">
              <div class="stat-number">500+</div>
              <div class="stat-label">优质学校</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">100K+</div>
              <div class="stat-label">用户信赖</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区域 -->
      <div class="form-section animate-fadeInRight">
        <div class="form-card">
          <!-- Tab切换 -->
          <div class="form-tabs">
            <div 
              class="tab-item" 
              :class="{ active: activeTab === 'login' }" 
              @click="activeTab = 'login'"
            >
              <span class="tab-icon">🔐</span>
              <span>登录</span>
            </div>
            <div 
              class="tab-item" 
              :class="{ active: activeTab === 'register' }" 
              @click="activeTab = 'register'"
            >
              <span class="tab-icon">📝</span>
              <span>注册</span>
            </div>
          </div>

          <!-- 登录表单 -->
          <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="form-content">
            <div class="form-header">
              <h2 class="form-title">欢迎回来</h2>
              <p class="form-subtitle">登录您的账号，继续使用服务</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">📱</span>
                <span>手机号码</span>
              </label>
              <input 
                v-model="loginForm.phone" 
                type="text" 
                class="form-input" 
                placeholder="请输入手机号码"
                maxlength="11"
              />
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">🔒</span>
                <span>密码</span>
              </label>
              <div class="password-input-wrapper">
                <input 
                  v-model="loginForm.password" 
                  :type="showPassword ? 'text' : 'password'" 
                  class="form-input" 
                  placeholder="请输入密码"
                  autocomplete="current-password"
                />
                <button 
                  type="button" 
                  class="toggle-password" 
                  @click="showPassword = !showPassword"
                >
                  {{ showPassword ? '🙈' : '👁️' }}
                </button>
              </div>
            </div>

            <div class="form-options">
              <label class="checkbox-label">
                <input type="checkbox" v-model="loginForm.remember" />
                <span class="checkmark"></span>
                <span>记住我</span>
              </label>
              <button type="button" class="forgot-link" @click="showForgotPassword">
                忘记密码？
              </button>
            </div>

            <button type="submit" class="submit-btn btn-enhanced" :disabled="loading">
              <template v-if="loading">
                <span class="loading-spinner"></span>
                <span>登录中...</span>
              </template>
              <template v-else>
                <span class="btn-icon">🚀</span>
                <span>登录</span>
              </template>
            </button>
          </form>

          <!-- 注册表单 -->
          <form v-else @submit.prevent="handleRegister" class="form-content">
            <div class="form-header">
              <h2 class="form-title">创建账号</h2>
              <p class="form-subtitle">加入我们，开启智慧择校之旅</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">📱</span>
                <span>手机号码</span>
              </label>
              <input 
                v-model="registerForm.phone" 
                type="text" 
                class="form-input" 
                placeholder="请输入手机号码"
                maxlength="11"
              />
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">📨</span>
                <span>验证码</span>
              </label>
              <div class="code-input-wrapper">
                <input 
                  v-model="registerForm.code" 
                  type="text" 
                  class="form-input" 
                  placeholder="请输入验证码"
                />
                <button 
                  type="button" 
                  class="code-btn" 
                  @click="sendCode" 
                  :disabled="sendingCode || countdown > 0"
                >
                  {{ countdown > 0 ? `${countdown}s` : (sendingCode ? '发送中...' : '获取验证码') }}
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">🔒</span>
                <span>密码</span>
              </label>
              <div class="password-input-wrapper">
                <input 
                  v-model="registerForm.password" 
                  :type="showRegisterPassword ? 'text' : 'password'" 
                  class="form-input" 
                  placeholder="请输入密码（至少6位）"
                  autocomplete="new-password"
                />
                <button 
                  type="button" 
                  class="toggle-password" 
                  @click="showRegisterPassword = !showRegisterPassword"
                >
                  {{ showRegisterPassword ? '🙈' : '👁️' }}
                </button>
              </div>
              <div class="password-strength">
                <div class="strength-bar">
                  <div class="strength-fill" :style="{ width: passwordStrengthPercent }"></div>
                </div>
                <span class="strength-text">{{ passwordStrengthText }}</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">✅</span>
                <span>确认密码</span>
              </label>
              <input 
                v-model="registerForm.confirmPassword" 
                :type="showConfirmPassword ? 'text' : 'password'" 
                class="form-input" 
                placeholder="请再次输入密码"
                autocomplete="new-password"
              />
            </div>

            <div class="form-agreement">
              <label class="checkbox-label">
                <input type="checkbox" v-model="registerForm.agree" />
                <span class="checkmark"></span>
                <span>我已阅读并同意</span>
                <a href="#" class="agreement-link">《用户协议》</a>
                <span>和</span>
                <a href="#" class="agreement-link">《隐私政策》</a>
              </label>
            </div>

            <button type="submit" class="submit-btn btn-enhanced" :disabled="loading">
              <template v-if="loading">
                <span class="loading-spinner"></span>
                <span>注册中...</span>
              </template>
              <template v-else>
                <span class="btn-icon">✨</span>
                <span>立即注册</span>
              </template>
            </button>
          </form>

          <!-- 分隔线 -->
          <div class="form-divider">
            <div class="divider-line"></div>
            <span class="divider-text">或</span>
            <div class="divider-line"></div>
          </div>

          <!-- 访客登录 -->
          <button class="guest-btn btn-enhanced" @click="handleGuestLogin">
            <span class="btn-icon">🎯</span>
            <span>游客体验</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <div v-if="showForgotDialog" class="dialog-overlay" @click.self="showForgotDialog = false">
      <div class="dialog-card animate-scaleIn">
        <div class="dialog-header">
          <h3 class="dialog-title">重置密码</h3>
          <button class="dialog-close" @click="showForgotDialog = false">✕</button>
        </div>
        <form @submit.prevent="handleForgotPassword" class="dialog-body">
          <div class="form-group">
            <label class="form-label">手机号码</label>
            <input 
              v-model="forgotForm.phone" 
              type="text" 
              class="form-input" 
              placeholder="请输入手机号码"
              maxlength="11"
            />
          </div>
          <div class="form-group">
            <label class="form-label">验证码</label>
            <div class="code-input-wrapper">
              <input 
                v-model="forgotForm.code" 
                type="text" 
                class="form-input" 
                placeholder="请输入验证码"
              />
              <button 
                type="button" 
                class="code-btn" 
                @click="sendForgotCode" 
                :disabled="sendingForgotCode || forgotCountdown > 0"
              >
                {{ forgotCountdown > 0 ? `${forgotCountdown}s` : (sendingForgotCode ? '发送中...' : '获取验证码') }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input 
              v-model="forgotForm.newPassword" 
              type="password" 
              class="form-input" 
              placeholder="请输入新密码"
              autocomplete="new-password"
            />
          </div>
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input 
              v-model="forgotForm.confirmPassword" 
              type="password" 
              class="form-input" 
              placeholder="请再次输入新密码"
              autocomplete="new-password"
            />
          </div>
          <div class="dialog-footer">
            <button type="button" class="cancel-btn" @click="showForgotDialog = false">取消</button>
            <button type="submit" class="confirm-btn" :disabled="loading">
              {{ loading ? '重置中...' : '确认重置' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'
import { userApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const sendingCode = ref(false)
const sendingForgotCode = ref(false)
const showPassword = ref(false)
const showRegisterPassword = ref(false)
const showConfirmPassword = ref(false)
const showForgotDialog = ref(false)
const countdown = ref(0)
const forgotCountdown = ref(0)

const loginForm = ref({
  phone: '',
  password: '',
  remember: false
})

const registerForm = ref({
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
  agree: false
})

const forgotForm = ref({
  phone: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordStrengthPercent = computed(() => {
  const pwd = registerForm.value.password
  if (!pwd) return 0
  let score = 0
  if (pwd.length >= 6) score += 25
  if (pwd.length >= 8) score += 25
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score += 25
  if (/\d/.test(pwd)) score += 12.5
  if (/[!@#$%^&*]/.test(pwd)) score += 12.5
  return Math.min(score, 100)
})

const passwordStrengthText = computed(() => {
  const percent = passwordStrengthPercent.value
  if (percent === 0) return ''
  if (percent < 40) return '弱'
  if (percent < 70) return '中等'
  return '强'
})

let countdownTimer = null
let forgotCountdownTimer = null

const startCountdown = () => {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
    }
  }, 1000)
}

const startForgotCountdown = () => {
  forgotCountdown.value = 60
  forgotCountdownTimer = setInterval(() => {
    forgotCountdown.value--
    if (forgotCountdown.value <= 0) {
      clearInterval(forgotCountdownTimer)
    }
  }, 1000)
}

const goHome = () => {
  router.push('/')
}

const handleLogin = async () => {
  if (!loginForm.value.phone || !loginForm.value.password) {
    ElMessage.warning('请输入手机号和密码')
    return
  }

  loading.value = true
  try {
    const response = await userApi.login({
      username: loginForm.value.phone,
      password: loginForm.value.password
    })

    if (response.success && (response.data?.token || response.data?.access_token)) {
      const token = response.data.token || response.data.access_token
      localStorage.setItem('token', token)
      if (response.data.userInfo) {
        localStorage.setItem('userInfo', JSON.stringify(response.data.userInfo))
        userStore.login(response.data.userInfo)
      } else {
        localStorage.setItem('userInfo', JSON.stringify({
          id: 1,
          phone: loginForm.value.phone,
          nickname: '用户',
          role: 1
        }))
        userStore.login({
          id: 1,
          phone: loginForm.value.phone,
          nickname: '用户',
          role: 1
        })
      }
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.phone || !registerForm.value.password) {
    ElMessage.warning('请输入手机号和密码')
    return
  }
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  if (!registerForm.value.agree) {
    ElMessage.warning('请先同意用户协议和隐私政策')
    return
  }

  loading.value = true
  try {
    const response = await userApi.register({
      username: registerForm.value.phone,
      email: registerForm.value.phone + '@example.com',
      phone: registerForm.value.phone,
      password: registerForm.value.password,
      role: 'student'
    })

    if (response.success) {
      ElMessage.success('注册成功，请登录')
      activeTab.value = 'login'
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } catch (error) {
    console.error('Register error:', error)
    if (error.response && error.response.data && error.response.data.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

const sendCode = () => {
  if (!/^1[3-9]\d{9}$/.test(registerForm.value.phone)) {
    ElMessage.error('请输入正确的手机号')
    return
  }

  sendingCode.value = true
  setTimeout(() => {
    ElMessage.success('验证码已发送（演示模式：123456）')
    sendingCode.value = false
    startCountdown()
  }, 1000)
}

const showForgotPassword = () => {
  showForgotDialog.value = true
}

const sendForgotCode = () => {
  if (!/^1[3-9]\d{9}$/.test(forgotForm.value.phone)) {
    ElMessage.error('请输入正确的手机号')
    return
  }

  sendingForgotCode.value = true
  setTimeout(() => {
    ElMessage.success('验证码已发送（演示模式：123456）')
    sendingForgotCode.value = false
    startForgotCountdown()
  }, 1000)
}

const handleForgotPassword = () => {
  if (!forgotForm.value.phone || !forgotForm.value.code || !forgotForm.value.newPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (forgotForm.value.newPassword !== forgotForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    ElMessage.success('密码重置成功，请登录（演示模式）')
    showForgotDialog.value = false
    activeTab.value = 'login'
  } catch (error) {
    ElMessage.error('密码重置失败，请稍后重试')
    console.error('Reset password error:', error)
  } finally {
    loading.value = false
  }
}

const handleGuestLogin = () => {
  const guestUser = {
    id: 0,
    phone: 'guest',
    nickname: '游客用户',
    role: 0
  }

  localStorage.setItem('token', 'guest-token-' + Date.now())
  localStorage.setItem('userInfo', JSON.stringify(guestUser))
  userStore.login(guestUser)

  ElMessage.success('欢迎体验！')
  router.push('/')
}

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
  if (forgotCountdownTimer) clearInterval(forgotCountdownTimer)
})
</script>

<style scoped>
.login-page-enhanced {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #080810 0%, #12121f 100%);
}

/* 背景装饰 */
.login-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: floatSlow 15s ease-in-out infinite;
}

.bg-gradient-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.4) 0%, transparent 70%);
  top: -200px;
  left: -100px;
}

.bg-gradient-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.4) 0%, transparent 70%);
  top: 50%;
  right: -150px;
  animation-delay: 5s;
}

.bg-gradient-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(240, 147, 251, 0.3) 0%, transparent 70%);
  bottom: -100px;
  left: 30%;
  animation-delay: 10s;
}

/* 返回导航 */
.back-nav {
  position: fixed;
  top: 24px;
  left: 40px;
  z-index: 1000;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.3);
  color: #fff;
  transform: translateX(-5px);
}

.back-icon {
  font-size: 18px;
}

/* 主容器 */
.login-container {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1600px;
  margin: 0 auto;
}

/* 品牌区域 */
.brand-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.brand-content {
  max-width: 500px;
}

.brand-logo {
  width: 96px;
  height: 96px;
  background: var(--primary-gradient);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.35);
  animation: pulseGlow 3s ease-in-out infinite;
}

.logo-icon {
  font-size: 56px;
  transform: scaleX(-1);
}

.brand-title {
  font-size: 48px;
  font-weight: 800;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 12px 0;
}

.brand-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 40px 0;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.feature-item:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
  transform: translateX(10px);
}

.feature-icon {
  font-size: 28px;
}

.feature-text {
  font-size: 16px;
  font-weight: 500;
  color: #fff;
}

.brand-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stat-card {
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

/* 表单区域 */
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.form-card {
  width: 100%;
  max-width: 500px;
  background: rgba(18, 18, 31, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.4);
}

.form-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px;
  border-radius: 14px;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.tab-item:hover {
  color: rgba(255, 255, 255, 0.9);
}

.tab-item.active {
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.tab-icon {
  font-size: 18px;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-header {
  text-align: center;
  margin-bottom: 12px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.label-icon {
  font-size: 16px;
}

.form-input {
  width: 100%;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  color: #fff;
  font-size: 15px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  outline: none;
}

.form-input:focus {
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
  background: rgba(255, 255, 255, 0.08);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.password-input-wrapper,
.code-input-wrapper {
  position: relative;
}

.toggle-password,
.code-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.toggle-password:hover,
.code-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.3);
}

.code-btn {
  font-size: 13px;
  color: #fff;
  padding: 10px 16px;
}

.code-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.password-input-wrapper .form-input {
  padding-right: 60px;
}

.code-input-wrapper .form-input {
  padding-right: 120px;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.strength-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 3px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.strength-fill[style*="0%"] {
  background: transparent;
}

.strength-fill[style*="25%"],
.strength-fill[style*="37.5%"] {
  background: linear-gradient(90deg, #f5576c, #f093fb);
}

.strength-fill[style*="50%"],
.strength-fill[style*="62.5%"] {
  background: linear-gradient(90deg, #f093fb, #667eea);
}

.strength-fill[style*="75%"],
.strength-fill[style*="100%"] {
  background: linear-gradient(90deg, #667eea, #92fe9d);
}

.strength-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  min-width: 30px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  accent-color: #667eea;
}

.forgot-link {
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.forgot-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.form-agreement {
  margin-top: -8px;
}

.agreement-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.agreement-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 32px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 14px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.35);
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.45);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.form-divider {
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 32px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.divider-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.guest-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.guest-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.dialog-card {
  width: 100%;
  max-width: 480px;
  background: rgba(18, 18, 31, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.dialog-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.dialog-close:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.dialog-body {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  padding-top: 8px;
}

.cancel-btn,
.confirm-btn {
  flex: 1;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.confirm-btn {
  background: var(--primary-gradient);
  border: none;
  color: #fff;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 32px rgba(102, 126, 234, 0.45);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .login-container {
    grid-template-columns: 1fr;
  }

  .brand-section {
    display: none;
  }

  .form-section {
    padding: 100px 40px 60px;
  }
}

@media (max-width: 768px) {
  .back-nav {
    left: 20px;
  }

  .form-section {
    padding: 100px 20px 40px;
  }

  .form-card {
    padding: 32px 24px;
  }

  .form-title {
    font-size: 24px;
  }

  .brand-stats {
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .back-nav {
    left: 16px;
    top: 16px;
  }

  .back-btn {
    padding: 8px 16px;
  }

  .form-section {
    padding: 90px 16px 30px;
  }

  .form-card {
    padding: 28px 20px;
  }
}
</style>
