<template>
  <div class="lazy-image-wrapper">
    <img
      v-if="loaded"
      :src="src"
      :alt="alt"
      :class="['lazy-image', { 'fade-in': loaded }]"
      :style="imageStyle"
      @load="handleLoad"
      @error="handleError"
    />
    <div v-else class="image-placeholder">
      <div class="loading-spinner">
        <div class="spinner"></div>
      </div>
      <span v-if="alt" class="placeholder-text">{{ alt }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  src: string
  alt?: string
  width?: string | number
  height?: string | number
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  width: '100%',
  height: 'auto',
  className: ''
})

const loaded = ref(false)
const observer = ref<IntersectionObserver | null>(null)

const imageStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))

const handleLoad = () => {
  loaded.value = true
}

const handleError = () => {
  loaded.value = true
}

onMounted(() => {
  const img = new Image()
  img.onload = () => {
    loaded.value = true
  }
  img.onerror = () => {
    loaded.value = true
  }
  
  // 使用Intersection Observer实现懒加载
  observer.value = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          img.src = props.src
          observer.value?.disconnect()
        }
      })
    },
    {
      rootMargin: '100px',
      threshold: 0.1
    }
  )
  
  const wrapper = document.querySelector(`[data-lazy-src="${props.src}"]`)
  if (wrapper) {
    observer.value.observe(wrapper)
  }
})

onUnmounted(() => {
  observer.value?.disconnect()
})
</script>

<style scoped>
.lazy-image-wrapper {
  position: relative;
  overflow: hidden;
  background: #f3f4f6;
  border-radius: 8px;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  color: #9ca3af;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  margin-bottom: 8px;
}

.spinner {
  width: 100%;
  height: 100%;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.placeholder-text {
  font-size: 13px;
}

.lazy-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.lazy-image.fade-in {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
