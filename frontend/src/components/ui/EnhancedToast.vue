<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast-list">
        <div 
          v-for="toast in toasts" 
          :key="toast.id" 
          :class="['toast-item', `toast-${toast.type}`]"
        >
          <span class="toast-icon">{{ getTypeIcon(toast.type) }}</span>
          <div class="toast-content">
            <div class="toast-message">{{ toast.message }}</div>
            <div v-if="toast.description" class="toast-description">{{ toast.description }}</div>
          </div>
          <button class="toast-close" @click="removeToast(toast.id)">✕</button>
          <div class="toast-progress" :style="{ animationDuration: `${toast.duration}ms` }"></div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

const getTypeIcon = (type) => {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  }
  return icons[type] || icons.info
}

const showToast = (options) => {
  const id = ++toastId
  const defaults = {
    type: 'info',
    duration: 4000
  }
  const toast = typeof options === 'string' 
    ? { ...defaults, id, message: options }
    : { ...defaults, id, ...options }
  
  toasts.value.push(toast)
  
  if (toast.duration > 0) {
    setTimeout(() => removeToast(id), toast.duration)
  }
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

// 暴露方法给外部使用
defineExpose({
  show: showToast,
  success: (msg, desc) => showToast({ type: 'success', message: msg, description: desc }),
  error: (msg, desc) => showToast({ type: 'error', message: msg, description: desc }),
  warning: (msg, desc) => showToast({ type: 'warning', message: msg, description: desc }),
  info: (msg, desc) => showToast({ type: 'info', message: msg, description: desc })
})

// 也可以直接通过组件实例调用
const toast = {
  show: showToast,
  success: (msg, desc) => showToast({ type: 'success', message: msg, description: desc }),
  error: (msg, desc) => showToast({ type: 'error', message: msg, description: desc }),
  warning: (msg, desc) => showToast({ type: 'warning', message: msg, description: desc }),
  info: (msg, desc) => showToast({ type: 'info', message: msg, description: desc })
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 6000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 420px;
  pointer-events: none;
}

.toast-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(18, 18, 31, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
  pointer-events: auto;
  overflow: hidden;
}

.toast-success {
  border-color: rgba(146, 254, 157, 0.4);
}

.toast-success .toast-icon {
  color: #92fe9d;
}

.toast-error {
  border-color: rgba(245, 87, 108, 0.4);
}

.toast-error .toast-icon {
  color: #f5576c;
}

.toast-warning {
  border-color: rgba(240, 147, 251, 0.4);
}

.toast-warning .toast-icon {
  color: #f093fb;
}

.toast-info {
  border-color: rgba(102, 126, 234, 0.4);
}

.toast-info .toast-icon {
  color: #667eea;
}

.toast-icon {
  font-size: 22px;
  line-height: 1;
  margin-top: 2px;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-message {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 4px;
}

.toast-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.5;
}

.toast-close {
  padding: 4px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 16px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  flex-shrink: 0;
  margin-left: 8px;
  line-height: 1;
}

.toast-close:hover {
  color: #fff;
}

.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.6), rgba(240, 147, 251, 0.6));
  animation: progress linear forwards;
}

@keyframes progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

/* 动画 */
.toast-list-enter-active,
.toast-list-leave-active {
  transition: background-color 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-list-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-list-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
