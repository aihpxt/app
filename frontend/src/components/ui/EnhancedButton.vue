<template>
  <button 
    :class="[
      'wx-btn',
      `wx-btn-${type}`,
      `wx-btn-${size}`,
      { 
        'wx-btn-block': block, 
        'wx-btn-loading': loading,
        'wx-btn-disabled': disabled
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="wx-btn-spinner"></span>
    <slot v-if="!loading"></slot>
  </button>
</template>

<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'text'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  block: Boolean,
  loading: Boolean,
  disabled: Boolean
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.wx-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 500;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, opacity 0.15s ease;
  outline: none;
  font-family: var(--wx-font-family);
  user-select: none;
  white-space: nowrap;
}

/* 尺寸 */
.wx-btn-small {
  padding: 4px 12px;
  font-size: 12px;
  height: 28px;
}

.wx-btn-medium {
  padding: 8px 20px;
  font-size: 14px;
  height: 36px;
}

.wx-btn-large {
  padding: 10px 24px;
  font-size: 16px;
  height: 44px;
}

/* 主按钮 */
.wx-btn-primary {
  background: var(--wx-primary);
  color: var(--wx-text-white);
}

.wx-btn-primary:hover:not(.wx-btn-disabled):not(.wx-btn-loading) {
  background: var(--wx-primary-hover);
}

.wx-btn-primary:active:not(.wx-btn-disabled):not(.wx-btn-loading) {
  background: var(--wx-primary-active);
}

/* 次按钮 */
.wx-btn-secondary {
  background: var(--wx-bg-white);
  color: var(--wx-primary);
  border: 1px solid var(--wx-primary);
}

.wx-btn-secondary:hover:not(.wx-btn-disabled):not(.wx-btn-loading) {
  background: var(--wx-primary-light);
}

.wx-btn-secondary:active:not(.wx-btn-disabled):not(.wx-btn-loading) {
  background: var(--wx-primary-light-hover);
}

/* 危险按钮 */
.wx-btn-danger {
  background: var(--wx-danger);
  color: var(--wx-text-white);
}

.wx-btn-danger:hover:not(.wx-btn-disabled):not(.wx-btn-loading) {
  background: var(--wx-danger-hover);
}

/* 文字按钮 */
.wx-btn-text {
  background: transparent;
  color: var(--wx-text-secondary);
  padding-inline: 12px;
}

.wx-btn-text:hover:not(.wx-btn-disabled):not(.wx-btn-loading) {
  background: var(--wx-bg-hover);
  color: var(--wx-text-primary);
}

/* 块级 */
.wx-btn-block {
  width: 100%;
}

/* 加载中 */
.wx-btn-loading {
  cursor: not-allowed;
  opacity: 0.7;
}

.wx-btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: wx-spin 0.8s linear infinite;
}

/* 禁用 */
.wx-btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes wx-spin {
  to { transform: rotate(360deg); }
}
</style>