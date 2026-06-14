<template>
  <div :class="['enhanced-tag', tagClasses]">
    <span v-if="icon" class="tag-icon">{{ icon }}</span>
    <span class="tag-text">
      <slot>{{ text }}</slot>
    </span>
    <span v-if="closable" class="tag-close" @click="handleClose">✕</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: String,
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'solid',
    validator: (value) => ['solid', 'outline', 'light'].includes(value)
  },
  icon: String,
  closable: Boolean
})

const emit = defineEmits(['close'])

const tagClasses = computed(() => ({
  [`tag-${props.type}`]: true,
  [`tag-${props.size}`]: true,
  [`tag-${props.variant}`]: true
}))

const handleClose = (event) => {
  event.stopPropagation()
  emit('close')
}
</script>

<style scoped>
.enhanced-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  border-radius: 999px;
  transition: background-color 0.2s, color 0.2s;
  user-select: none;
}

/* 尺寸 */
.tag-small {
  padding: 4px 10px;
  font-size: 12px;
}

.tag-medium {
  padding: 6px 14px;
  font-size: 13px;
}

.tag-large {
  padding: 8px 18px;
  font-size: 14px;
}

/* 类型 - Solid */
.tag-solid.tag-primary {
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.tag-solid.tag-success {
  background: linear-gradient(135deg, #92fe9d 0%, #00c9ff 100%);
  color: #0f2027;
  box-shadow: 0 2px 8px rgba(146, 254, 157, 0.3);
}

.tag-solid.tag-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
}

.tag-solid.tag-danger {
  background: linear-gradient(135deg, #f5576c 0%, #d45079 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
}

.tag-solid.tag-info {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.tag-solid.tag-default {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

/* 类型 - Outline */
.tag-outline.tag-primary {
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.4);
  background: transparent;
}

.tag-outline.tag-success {
  color: #92fe9d;
  border: 1px solid rgba(146, 254, 157, 0.4);
  background: transparent;
}

.tag-outline.tag-warning {
  color: #f093fb;
  border: 1px solid rgba(240, 147, 251, 0.4);
  background: transparent;
}

.tag-outline.tag-danger {
  color: #f5576c;
  border: 1px solid rgba(245, 87, 108, 0.4);
  background: transparent;
}

.tag-outline.tag-info {
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.4);
  background: transparent;
}

.tag-outline.tag-default {
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
}

/* 类型 - Light */
.tag-light.tag-primary {
  background: rgba(102, 126, 234, 0.15);
  color: #667eea;
}

.tag-light.tag-success {
  background: rgba(146, 254, 157, 0.15);
  color: #92fe9d;
}

.tag-light.tag-warning {
  background: rgba(240, 147, 251, 0.15);
  color: #f093fb;
}

.tag-light.tag-danger {
  background: rgba(245, 87, 108, 0.15);
  color: #f5576c;
}

.tag-light.tag-info {
  background: rgba(102, 126, 234, 0.15);
  color: #667eea;
}

.tag-light.tag-default {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
}

/* 图标 */
.tag-icon {
  font-size: 14px;
  line-height: 1;
}

/* 关闭按钮 */
.tag-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
  transition: background-color 0.2s, color 0.2s;
  opacity: 0.7;
}

.tag-close:hover {
  background: rgba(255, 255, 255, 0.15);
  opacity: 1;
}
</style>
