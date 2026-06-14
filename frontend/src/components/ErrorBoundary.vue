<template>
  <div class="error-boundary">
    <template v-if="hasError">
      <div class="error-container">
        <div class="error-icon">❌</div>
        <h3 class="error-title">组件加载失败</h3>
        <p class="error-message">{{ errorMessage }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="handleRetry">
            <el-icon><RefreshLeft /></el-icon>
            重新加载
          </el-button>
          <el-button @click="handleReport">
            <el-icon><QuestionFilled /></el-icon>
            报告问题
          </el-button>
        </div>
      </div>
    </template>
    <template v-else>
      <slot />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { RefreshLeft, QuestionFilled } from '@element-plus/icons-vue'

const hasError = ref(false)
const errorMessage = ref('')
const errorInfo = ref('')

const handleRetry = () => {
  hasError.value = false
  errorMessage.value = ''
  errorInfo.value = ''
}

const handleReport = () => {
  const reportData = {
    message: errorMessage.value,
    stack: errorInfo.value,
    timestamp: new Date().toISOString(),
    url: window.location.href
  }
  console.error('Error Report:', reportData)
  alert('问题已记录，感谢您的反馈！')
}

const errorHandler = (error: Error, _instance: unknown, info: string) => {
  hasError.value = true
  errorMessage.value = error.message || '未知错误'
  errorInfo.value = info
  console.error('Error Boundary:', error, info)
  return false
}

onErrorCaptured(errorHandler)

defineExpose({
  hasError,
  errorMessage,
  retry: handleRetry
})
</script>

<style scoped>
.error-boundary {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-container {
  text-align: center;
  padding: 40px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 16px;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.error-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.error-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.error-message {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 20px 0;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
