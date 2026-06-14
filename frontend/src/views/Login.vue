<template>
  <div class="login-container">
    <div class="login-bg"></div>
    <div class="login-card">
      <div class="login-header">
        <span class="logo-icon">🦐</span>
        <h2 class="login-title">小龙虾择校</h2>
        <p class="login-subtitle">云南省中考择校智能助手</p>
      </div>
      
      <div class="login-tabs">
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'login' }" 
          @click="activeTab = 'login'"
        >登录</div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'register' }" 
          @click="activeTab = 'register'"
        >注册</div>
      </div>
      
      <!-- 登录表单 -->
      <div v-if="activeTab === 'login'" class="form-section">
        <div class="input-group">
          <input 
            v-model="loginForm.phone" 
            type="text" 
            class="input-field" 
            placeholder="请输入手机号"
            maxlength="11"
          />
        </div>
        <div class="input-group">
          <input 
            v-model="loginForm.password" 
            type="password" 
            class="input-field" 
            placeholder="请输入密码"
          />
        </div>
        <div class="form-options">
          <label class="checkbox-label">
            <input type="checkbox" v-model="loginForm.remember" />
            <span>记住我</span>
          </label>
          <a class="forgot-link" @click="showForgotPassword">忘记密码？</a>
        </div>
        <button class="submit-btn" @click="handleLogin" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </div>
      
      <!-- 注册表单 -->
      <div v-else class="form-section">
        <div class="input-group">
          <input 
            v-model="registerForm.phone" 
            type="text" 
            class="input-field" 
            placeholder="请输入手机号"
            maxlength="11"
          />
        </div>
        <div class="input-group code-group">
          <input 
            v-model="registerForm.code" 
            type="text" 
            class="input-field" 
            placeholder="请输入验证码"
          />
          <button class="code-btn" @click="sendCode" :disabled="sendingCode">
            {{ sendingCode ? '发送中...' : '获取验证码' }}
          </button>
        </div>
        <div class="input-group">
          <input 
            v-model="registerForm.password" 
            type="password" 
            class="input-field" 
            placeholder="请输入密码"
          />
        </div>
        <div class="input-group">
          <input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            class="input-field" 
            placeholder="请再次输入密码"
          />
        </div>
        <button class="submit-btn" @click="handleRegister" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </div>
      
      <!-- 访客登录 -->
      <div class="guest-section">
        <div class="divider">
          <span>或</span>
        </div>
        <button class="guest-btn" @click="handleGuestLogin">
          <span>访客体验</span>
        </button>
      </div>
    </div>
    
    <!-- 忘记密码对话框 -->
    <div v-if="showForgotDialog" class="dialog-overlay" @click.self="showForgotDialog = false">
      <div class="dialog-card">
        <div class="dialog-header">
          <h3>重置密码</h3>
          <button class="close-btn" @click="showForgotDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="input-group">
            <input 
              v-model="forgotForm.phone" 
              type="text" 
              class="input-field" 
              placeholder="请输入手机号"
              maxlength="11"
            />
          </div>
          <div class="input-group code-group">
            <input 
              v-model="forgotForm.code" 
              type="text" 
              class="input-field" 
              placeholder="请输入验证码"
            />
            <button class="code-btn" @click="sendForgotCode" :disabled="sendingForgotCode">
              {{ sendingForgotCode ? '发送中...' : '获取验证码' }}
            </button>
          </div>
          <div class="input-group">
            <input 
              v-model="forgotForm.newPassword" 
              type="password" 
              class="input-field" 
              placeholder="请输入新密码"
            />
          </div>
          <div class="input-group">
            <input 
              v-model="forgotForm.confirmPassword" 
              type="password" 
              class="input-field" 
              placeholder="请再次输入新密码"
            />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="cancel-btn" @click="showForgotDialog = false">取消</button>
          <button class="confirm-btn" @click="handleForgotPassword">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const activeTab = ref('login')
    const loading = ref(false)
    const sendingCode = ref(false)
    const sendingForgotCode = ref(false)
    const showForgotDialog = ref(false)
    
    const loginFormRef = ref(null)
    const registerFormRef = ref(null)
    const forgotFormRef = ref(null)
    
    const loginForm = reactive({
      phone: '',
      password: '',
      remember: false
    })
    
    const registerForm = reactive({
      phone: '',
      code: '',
      password: '',
      confirmPassword: ''
    })
    
    const forgotForm = reactive({
      phone: '',
      code: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const validateConfirmPassword = (rule, value, callback) => {
      if (activeTab.value === 'register' && value !== registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else if (activeTab.value === 'forgot' && value !== forgotForm.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const loginRules = {
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ]
    }
    
    const registerRules = {
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
      ],
      code: [
        { required: true, message: '请输入验证码', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
        { max: 72, message: '密码长度不能超过72位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ]
    }
    
    const forgotRules = {
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
      ],
      code: [
        { required: true, message: '请输入验证码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
        { max: 72, message: '密码长度不能超过72位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      if (!loginForm.phone || !loginForm.password) {
        ElMessage.error('请输入手机号和密码')
        return
      }
      
      loading.value = true
      try {
        const response = await userStore.login({
          username: loginForm.phone,
          password: loginForm.password
        })
        
        if (response.success) {
          ElMessage.success('登录成功')
          router.push('/')
        } else {
          ElMessage.error(response.message || '登录失败，请检查用户名和密码')
        }
      } catch (error) {
        console.error('Login error:', error)
        ElMessage.error('登录失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
    
    const handleRegister = async () => {
      if (!registerForm.phone || !registerForm.password) {
        ElMessage.error('请输入手机号和密码')
        return
      }
      if (registerForm.password !== registerForm.confirmPassword) {
        ElMessage.error('两次输入的密码不一致')
        return
      }
      
      loading.value = true
      try {
        const response = await userApi.register({
          username: registerForm.phone,
          email: registerForm.phone + '@example.com',
          password: registerForm.password,
          role: 'user'
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
      if (!/^1[3-9]\d{9}$/.test(registerForm.phone)) {
        ElMessage.error('请输入正确的手机号')
        return
      }
      
      sendingCode.value = true
      setTimeout(() => {
        ElMessage.success('验证码已发送（演示模式：123456）')
        let countdown = 60
        const timer = setInterval(() => {
          countdown--
          if (countdown <= 0) {
            clearInterval(timer)
            sendingCode.value = false
          }
        }, 1000)
      }, 1000)
    }
    
    const showForgotPassword = () => {
      showForgotDialog.value = true
    }
    
    const sendForgotCode = () => {
      if (!/^1[3-9]\d{9}$/.test(forgotForm.phone)) {
        ElMessage.error('请输入正确的手机号')
        return
      }
      
      sendingForgotCode.value = true
      setTimeout(() => {
        ElMessage.success('验证码已发送（演示模式：123456）')
        let countdown = 60
        const timer = setInterval(() => {
          countdown--
          if (countdown <= 0) {
            clearInterval(timer)
            sendingForgotCode.value = false
          }
        }, 1000)
      }, 1000)
    }
    
    const handleForgotPassword = () => {
      forgotFormRef.value.validate(async (valid) => {
        if (valid) {
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
      })
    }
    
    const handleGuestLogin = () => {
      const guestUser = {
        id: 0,
        phone: 'guest',
        nickname: '访客用户',
        role: 0
      }
      
      userStore.setToken('guest-token-' + Date.now())
      userStore.setUserInfo(guestUser)
      
      ElMessage.success('欢迎体验！')
      router.push('/')
    }
    
    return {
      activeTab,
      loading,
      sendingCode,
      sendingForgotCode,
      showForgotDialog,
      loginFormRef,
      registerFormRef,
      forgotFormRef,
      loginForm,
      registerForm,
      forgotForm,
      loginRules,
      registerRules,
      forgotRules,
      handleLogin,
      handleRegister,
      sendCode,
      showForgotPassword,
      sendForgotCode,
      handleForgotPassword,
      handleGuestLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #050508 0%, #0d0d18 40%, #14142a 100%);
  z-index: 0;
}

.login-bg::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 30%, rgba(102, 126, 234, 0.25) 0%, transparent 50%),
              radial-gradient(circle at 70% 70%, rgba(118, 75, 162, 0.25) 0%, transparent 50%);
  animation: rotate 30s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.login-card {
  width: 400px;
  border-radius: 20px;
  box-shadow: 
    var(--shadow-lg),
    0 0 0 1px var(--border-color);
  z-index: 1;
  overflow: hidden;
  background: rgba(12, 12, 22, 0.98);
  backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  padding: 44px 36px;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 36px;
}

.logo-icon {
  font-size: 56px;
  margin-bottom: 18px;
  filter: drop-shadow(0 4px 16px rgba(102, 126, 234, 0.5));
  transform: scaleX(-1);
}

.login-title {
  text-align: center;
  margin: 0 0 10px 0;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 26px;
  font-weight: 700;
  filter: drop-shadow(0 2px 10px rgba(102, 126, 234, 0.3));
}

.login-subtitle {
  text-align: center;
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.login-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  border-bottom: 1px solid var(--border-color);
}

.tab-item {
  padding: 14px 28px;
  color: var(--text-muted);
  font-size: 15px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  position: relative;
}

.tab-item:hover {
  color: var(--text-primary);
}

.tab-item.active {
  color: #667eea;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary-gradient);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.input-group {
  width: 100%;
}

.input-field {
  width: 100%;
  height: 50px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0 18px;
  color: var(--text-primary);
  font-size: 15px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  outline: none;
}

.input-field::placeholder {
  color: var(--text-muted);
}

.input-field:hover {
  border-color: rgba(102, 126, 234, 0.4);
  background: rgba(255, 255, 255, 0.08);
}

.input-field:focus {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
  background: rgba(255, 255, 255, 0.08);
}

.code-group {
  display: flex;
  gap: 12px;
}

.code-group .input-field {
  flex: 1;
}

.code-btn {
  height: 50px;
  padding: 0 18px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  white-space: nowrap;
}

.code-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.4);
}

.code-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #667eea;
}

.forgot-link {
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.3s;
}

.forgot-link:hover {
  color: #667eea;
}

.submit-btn {
  width: 100%;
  height: 50px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 14px;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  margin-top: 10px;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 32px rgba(102, 126, 234, 0.5);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.guest-section {
  margin-top: 28px;
}

.divider {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.divider span {
  padding: 0 18px;
  color: var(--text-muted);
  font-size: 13px;
}

.guest-btn {
  width: 100%;
  height: 50px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  color: var(--text-primary);
  font-size: 15px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.guest-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-card {
  width: 400px;
  background: rgba(18, 18, 31, 0.98);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dialog-header h3 {
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 24px;
  cursor: pointer;
  border-radius: 8px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.dialog-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.cancel-btn {
  height: 40px;
  padding: 0 20px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

.confirm-btn {
  height: 40px;
  padding: 0 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .login-card {
    width: 90%;
    max-width: 400px;
  }
}
</style>