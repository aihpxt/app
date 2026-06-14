<template>
  <button 
    :class="['enhanced-switch', { 'switch-checked': modelValue, 'switch-disabled': disabled }]"
    :disabled="disabled"
    @click="handleClick"
    role="switch"
    :aria-checked="modelValue"
  >
    <div class="switch-track">
      <div class="switch-thumb">
        <span class="thumb-icon">{{ modelValue ? (checkedIcon || '✓') : (uncheckedIcon || '') }}</span>
      </div>
    </div>
    <div v-if="$slots.default || label" class="switch-label">
      <slot>{{ label }}</slot>
    </div>
  </button>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: String,
  checkedIcon: String,
  uncheckedIcon: String,
  disabled: Boolean
})

const emit = defineEmits(['update:modelValue', 'change'])

const handleClick = () => {
  if (!props.disabled) {
    emit('update:modelValue', !props.modelValue)
    emit('change', !props.modelValue)
  }
}
</script>

<style scoped>
.enhanced-switch {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  outline: none;
}

.switch-disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.switch-track {
  position: relative;
  width: 48px;
  height: 26px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  transition: background-color 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.switch-checked .switch-track {
  background: var(--primary-gradient);
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
}

.switch-thumb {
  position: absolute;
  top: 50%;
  left: 3px;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.switch-checked .switch-thumb {
  left: calc(100% - 23px);
}

.thumb-icon {
  font-size: 12px;
  font-weight: 700;
  color: #667eea;
  line-height: 1;
}

.switch-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  user-select: none;
}

.switch-checked .switch-label {
  color: #fff;
}
</style>
