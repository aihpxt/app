<template>
  <Teleport to="body">
    <transition name="dialog-fade">
      <div v-if="visible" class="dialog-overlay" @click.self="handleOverlayClick">
        <transition name="dialog-scale">
          <div v-if="visible" :class="['dialog-container', dialogClasses]">
            <div class="dialog-header">
              <div class="header-left">
                <span v-if="icon" class="dialog-icon">{{ icon }}</span>
                <h3 class="dialog-title">{{ title }}</h3>
              </div>
              <button v-if="closable" class="dialog-close" @click="handleClose">
                ✕
              </button>
            </div>
            
            <div class="dialog-body">
              <slot></slot>
            </div>
            
            <div v-if="$slots.footer || showDefaultFooter" class="dialog-footer">
              <slot name="footer">
                <button class="footer-btn cancel-btn" @click="handleCancel">
                  {{ cancelText }}
                </button>
                <button class="footer-btn confirm-btn" @click="handleConfirm" :disabled="confirmLoading">
                  <span v-if="confirmLoading" class="loading-spinner"></span>
                  <span>{{ confirmText }}</span>
                </button>
              </slot>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: String,
  icon: String,
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'info', 'success', 'warning', 'danger'].includes(value)
  },
  width: {
    type: [String, Number],
    default: 500
  },
  closable: {
    type: Boolean,
    default: true
  },
  showDefaultFooter: {
    type: Boolean,
    default: true
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  confirmText: {
    type: String,
    default: '确认'
  },
  confirmLoading: Boolean,
  closeOnOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'confirm', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialogClasses = computed(() => ({
  [`dialog-${props.type}`]: props.type !== 'default'
}))

const handleClose = () => {
  visible.value = false
  emit('close')
}

const handleCancel = () => {
  visible.value = false
  emit('cancel')
}

const handleConfirm = () => {
  emit('confirm')
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    handleClose()
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5000;
  padding: 20px;
}

.dialog-container {
  background: rgba(18, 18, 31, 0.98);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
  max-height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 320px;
}

.dialog-info .dialog-icon {
  color: #667eea;
}

.dialog-success .dialog-icon {
  color: #92fe9d;
}

.dialog-warning .dialog-icon {
  color: #f093fb;
}

.dialog-danger .dialog-icon {
  color: #f5576c;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.dialog-icon {
  font-size: 28px;
  line-height: 1;
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  font-size: 16px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  flex-shrink: 0;
  margin-left: 16px;
}

.dialog-close:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  transform: rotate(90deg);
}

.dialog-body {
  padding: 28px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.02);
}

.footer-btn {
  padding: 12px 28px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  min-width: 100px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.85);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.confirm-btn {
  background: var(--primary-gradient);
  border: none;
  color: #fff;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.45);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-scale-enter-active,
.dialog-scale-leave-active {
  transition: background-color 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dialog-scale-enter-from,
.dialog-scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
