<template>
  <div class="enhanced-input-wrapper">
    <label v-if="label" class="input-label">
      <span v-if="labelIcon" class="label-icon">{{ labelIcon }}</span>
      <span>{{ label }}</span>
      <span v-if="required" class="required-mark">*</span>
    </label>
    
    <div class="input-container" :class="{ 'input-error': error, 'input-focus': isFocused }">
      <span v-if="prefixIcon" class="input-prefix">{{ prefixIcon }}</span>
      <input 
        v-model="inputValue"
        :type="inputType"
        :placeholder="placeholder"
        :disabled="disabled"
        :maxlength="maxlength"
        class="enhanced-input"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @input="handleInput"
      />
      <div v-if="clearable && inputValue && !disabled" class="input-clear" @click="clearInput">
        ✕
      </div>
      <button 
        v-if="showPasswordToggle && (type === 'password')"
        type="button" 
        class="input-suffix" 
        @click="togglePassword"
      >
        {{ showPassword ? '🙈' : '👁️' }}
      </button>
      <span v-else-if="suffixIcon" class="input-suffix">{{ suffixIcon }}</span>
    </div>
    
    <div class="input-hint">
      <span v-if="error" class="hint-error">{{ error }}</span>
      <span v-else-if="hint" class="hint-text">{{ hint }}</span>
      <span v-if="showCount && maxlength" class="hint-count">{{ inputValue.length }} / {{ maxlength }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'password', 'email', 'number', 'tel', 'url'].includes(value)
  },
  label: String,
  labelIcon: String,
  placeholder: String,
  prefixIcon: String,
  suffixIcon: String,
  hint: String,
  error: String,
  disabled: Boolean,
  required: Boolean,
  clearable: {
    type: Boolean,
    default: true
  },
  showPasswordToggle: {
    type: Boolean,
    default: true
  },
  showCount: Boolean,
  maxlength: Number
})

const emit = defineEmits(['update:modelValue', 'input', 'change', 'clear'])

const inputValue = ref(props.modelValue ?? '')
const isFocused = ref(false)
const showPassword = ref(false)

const inputType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type
})

watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue ?? ''
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  emit('input', event.target.value)
}

const clearInput = () => {
  inputValue.value = ''
  emit('update:modelValue', '')
  emit('clear')
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}
</script>

<style scoped>
.enhanced-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

.label-icon {
  font-size: 16px;
}

.required-mark {
  color: #f5576c;
  margin-left: 4px;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  transition: border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.input-focus {
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
  background: rgba(255, 255, 255, 0.08);
}

.input-error {
  border-color: rgba(245, 87, 108, 0.6);
  box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.15);
}

.input-prefix,
.input-suffix {
  padding: 0 16px;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.5);
  user-select: none;
}

.input-suffix {
  cursor: pointer;
  transition: border-color 0.3s, background-color 0.3s, box-shadow 0.3s;
}

.input-suffix:hover {
  color: rgba(255, 255, 255, 0.8);
}

.enhanced-input {
  flex: 1;
  width: 100%;
  padding: 14px 0;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 15px;
  outline: none;
}

.enhanced-input:disabled {
  cursor: not-allowed;
  color: rgba(255, 255, 255, 0.4);
}

.enhanced-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-clear {
  padding: 0 12px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: border-color 0.3s, background-color 0.3s, box-shadow 0.3s;
  line-height: 1;
}

.input-clear:hover {
  color: #fff;
}

.input-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 18px;
}

.hint-text,
.hint-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.hint-error {
  font-size: 12px;
  color: #f5576c;
}
</style>
