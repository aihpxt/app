<template>
  <div :class="['enhanced-loading', loadingClasses]">
    <div class="loading-content">
      <div v-if="type === 'spinner'" class="spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring ring-2"></div>
        <div class="spinner-ring ring-3"></div>
      </div>
      
      <div v-else-if="type === 'dots'" class="dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
      
      <div v-else-if="type === 'pulse'" class="pulse-container">
        <div class="pulse"></div>
      </div>
      
      <div v-else class="bounce">
        <span class="bounce-ball"></span>
        <span class="bounce-ball ball-2"></span>
        <span class="bounce-ball ball-3"></span>
      </div>
      
      <p v-if="text" class="loading-text">{{ text }}</p>
    </div>
    
    <div v-if="overlay" class="loading-overlay"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'spinner',
    validator: (value) => ['spinner', 'dots', 'pulse', 'bounce'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  color: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'white'].includes(value)
  },
  text: String,
  overlay: Boolean,
  fullscreen: Boolean
})

const loadingClasses = computed(() => ({
  'loading-fullscreen': props.fullscreen,
  'loading-overlay': props.overlay,
  [`loading-${props.size}`]: true
}))
</script>

<style scoped>
.enhanced-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.loading-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(8, 8, 16, 0.95);
  backdrop-filter: blur(8px);
  z-index: 9999;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(8, 8, 16, 0.85);
  border-radius: inherit;
  z-index: 10;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 20;
}

/* 尺寸 */
.loading-small .spinner-ring {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.loading-small .dot {
  width: 8px;
  height: 8px;
}

.loading-small .pulse {
  width: 32px;
  height: 32px;
}

.loading-small .bounce-ball {
  width: 10px;
  height: 10px;
}

.loading-medium .spinner-ring {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.loading-medium .dot {
  width: 12px;
  height: 12px;
}

.loading-medium .pulse {
  width: 48px;
  height: 48px;
}

.loading-medium .bounce-ball {
  width: 14px;
  height: 14px;
}

.loading-large .spinner-ring {
  width: 56px;
  height: 56px;
  border-width: 4px;
}

.loading-large .dot {
  width: 16px;
  height: 16px;
}

.loading-large .pulse {
  width: 64px;
  height: 64px;
}

.loading-large .bounce-ball {
  width: 18px;
  height: 18px;
}

/* Spinner */
.spinner {
  position: relative;
  width: 40px;
  height: 40px;
}

.spinner-ring {
  position: absolute;
  border-radius: 50%;
  border-style: solid;
  border-color: transparent;
  border-top-color: #667eea;
  animation: spin 1s ease-in-out infinite;
}

.ring-2 {
  left: 4px;
  top: 4px;
  right: 4px;
  bottom: 4px;
  border-top-color: #764ba2;
  animation-direction: reverse;
  animation-duration: 0.8s;
}

.ring-3 {
  left: 8px;
  top: 8px;
  right: 8px;
  bottom: 8px;
  border-top-color: #f093fb;
  animation-duration: 0.6s;
}

/* Dots */
.dots {
  display: flex;
  gap: 8px;
}

.dot {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: dotPulse 1.4s ease-in-out infinite;
}

.dot:nth-child(1) {
  animation-delay: 0s;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

/* Pulse */
.pulse-container {
  position: relative;
  width: 48px;
  height: 48px;
}

.pulse {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

/* Bounce */
.bounce {
  display: flex;
  gap: 8px;
}

.bounce-ball {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: bounce 0.6s ease-in-out infinite alternate;
}

.ball-2 {
  animation-delay: 0.2s;
}

.ball-3 {
  animation-delay: 0.4s;
}

/* 文字 */
.loading-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
  margin: 0;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes dotPulse {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.8;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes bounce {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-12px);
  }
}
</style>
