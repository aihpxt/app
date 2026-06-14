<template>
  <div class="enhanced-progress">
    <div v-if="showLabel" class="progress-header">
      <span v-if="label" class="progress-label">{{ label }}</span>
      <span class="progress-percentage">{{ percentage }}%</span>
    </div>
    <div class="progress-bar">
      <div 
        class="progress-fill"
        :style="{ width: `${percentage}%` }"
        :class="`progress-${type}`"
      >
        <div class="progress-stripe"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  percentage: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  type: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  label: String,
  showLabel: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.enhanced-progress {
  width: 100%;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.progress-percentage {
  font-size: 14px;
  color: #fff;
  font-weight: 600;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  overflow: hidden;
}

/* 尺寸 */
:deep(.progress-small) {
  height: 4px;
}

:deep(.progress-large) {
  height: 12px;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  position: relative;
  overflow: hidden;
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.progress-primary {
  background: var(--primary-gradient);
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.4);
}

.progress-success {
  background: linear-gradient(135deg, #92fe9d 0%, #00c9ff 100%);
  box-shadow: 0 0 12px rgba(146, 254, 157, 0.4);
}

.progress-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 0 12px rgba(245, 87, 108, 0.4);
}

.progress-danger {
  background: linear-gradient(135deg, #f5576c 0%, #d45079 100%);
  box-shadow: 0 0 12px rgba(245, 87, 108, 0.4);
}

.progress-stripe {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(255, 255, 255, 0.1) 10px,
    rgba(255, 255, 255, 0.1) 20px
  );
  animation: stripeMove 2s linear infinite;
}

@keyframes stripeMove {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 40px 0;
  }
}
</style>
