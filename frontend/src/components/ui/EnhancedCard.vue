<template>
  <div :class="['wx-card', cardClasses]">
    <div v-if="$slots.header || title" class="wx-card-header">
      <slot name="header">
        <h3 v-if="title" class="wx-card-title">{{ title }}</h3>
      </slot>
      <div v-if="$slots.headerExtra" class="wx-card-header-extra">
        <slot name="headerExtra"></slot>
      </div>
    </div>
    
    <div class="wx-card-body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="wx-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  shadow: {
    type: Boolean,
    default: true
  },
  border: {
    type: Boolean,
    default: false
  },
  hoverable: Boolean
})

const cardClasses = computed(() => ({
  'wx-card--shadow': props.shadow,
  'wx-card--border': props.border,
  'wx-card--hoverable': props.hoverable
}))
</script>

<style scoped>
.wx-card {
  background: var(--wx-bg-white);
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.wx-card--shadow {
  box-shadow: var(--wx-shadow-sm);
}

.wx-card--shadow:hover {
  box-shadow: var(--wx-shadow-md);
}

.wx-card--border {
  border: 1px solid var(--wx-border-light);
}

.wx-card--hoverable {
  cursor: pointer;
}

.wx-card--hoverable:hover {
  box-shadow: var(--wx-shadow-md);
}

.wx-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--wx-border-light);
}

.wx-card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--wx-text-primary);
}

.wx-card-header-extra {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wx-card-body {
  padding: 20px;
}

.wx-card-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--wx-border-light);
  background: var(--wx-bg-light);
}
</style>