<template>
  <div :class="['enhanced-avatar', avatarClasses]">
    <img v-if="src && !error" :src="src" :alt="alt" @error="handleError" class="avatar-image" />
    <div v-else-if="!src || error" class="avatar-text">
      <template v-if="text">{{ text }}</template>
      <template v-else-if="icon">{{ icon }}</template>
      <template v-else>{{ fallbackEmoji }}</template>
    </div>
    <div v-if="badge" :class="['avatar-badge', `badge-${badgeType}`]">
      {{ badge }}
    </div>
    <div v-if="status" :class="['avatar-status', `status-${status}`]"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  src: String,
  text: String,
  icon: String,
  alt: {
    type: String,
    default: 'avatar'
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['mini', 'small', 'medium', 'large', 'xlarge'].includes(value)
  },
  shape: {
    type: String,
    default: 'circle',
    validator: (value) => ['circle', 'square'].includes(value)
  },
  badge: [String, Number],
  badgeType: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger'].includes(value)
  },
  status: String,
  gradient: {
    type: Boolean,
    default: true
  }
})

const error = ref(false)

const fallbackEmoji = computed(() => {
  if (props.text) {
    return props.text.charAt(0).toUpperCase()
  }
  return '👤'
})

const avatarClasses = computed(() => ({
  [`avatar-${props.size}`]: true,
  [`avatar-${props.shape}`]: true,
  'avatar-gradient': props.gradient
}))

const handleError = () => {
  error.value = true
}
</script>

<style scoped>
.enhanced-avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-gradient {
  background: var(--primary-gradient);
}

/* 尺寸 */
.avatar-mini {
  width: 24px;
  height: 24px;
  font-size: 10px;
}

.avatar-small {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.avatar-medium {
  width: 40px;
  height: 40px;
  font-size: 16px;
}

.avatar-large {
  width: 56px;
  height: 56px;
  font-size: 22px;
}

.avatar-xlarge {
  width: 80px;
  height: 80px;
  font-size: 32px;
}

/* 形状 */
.avatar-circle {
  border-radius: 50%;
}

.avatar-square {
  border-radius: 12px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-text {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

/* 徽标 */
.avatar-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: 2px solid rgba(18, 18, 31, 0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.badge-primary {
  background: var(--primary-gradient);
  color: #fff;
}

.badge-success {
  background: linear-gradient(135deg, #92fe9d 0%, #00c9ff 100%);
  color: #0f2027;
}

.badge-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.badge-danger {
  background: linear-gradient(135deg, #f5576c 0%, #d45079 100%);
  color: #fff;
}

/* 状态 */
.avatar-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(18, 18, 31, 0.98);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.status-online {
  background: #92fe9d;
}

.status-offline {
  background: rgba(255, 255, 255, 0.3);
}

.status-busy {
  background: #f5576c;
}

.status-away {
  background: #f093fb;
}
</style>
