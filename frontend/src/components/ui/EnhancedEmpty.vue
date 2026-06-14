<template>
  <div class="enhanced-empty">
    <div class="empty-icon">
      <slot name="icon">
        <div class="default-icon">{{ icon }}</div>
      </slot>
    </div>
    <div class="empty-content">
      <h3 class="empty-title">
        <slot name="title">{{ title }}</slot>
      </h3>
      <p v-if="description || $slots.description" class="empty-description">
        <slot name="description">{{ description }}</slot>
      </p>
      <div v-if="$slots.default" class="empty-actions">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  icon: {
    type: String,
    default: '📭'
  },
  title: {
    type: String,
    default: '暂无数据'
  },
  description: String
})
</script>

<style scoped>
.enhanced-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 24px;
}

.default-icon {
  font-size: 72px;
  animation: float 3s ease-in-out infinite;
}

.empty-content {
  max-width: 400px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}
</style>
