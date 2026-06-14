<template>
  <div class="school-simple-page">
    <!-- 顶部搜索栏 -->
    <div class="wx-search search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
      <input
        class="search-input"
        v-model="searchKeyword"
        placeholder="搜索学校名称"
        @keyup.enter="fetchData"
      />
    </div>

    <!-- 调试信息面板 -->
    <div class="wx-card debug-panel">
      <div class="card-title">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        调试信息
      </div>
      <div class="debug-grid">
        <div class="debug-item">
          <span class="debug-label">加载中</span>
          <span class="debug-value">{{ loading ? '是' : '否' }}</span>
        </div>
        <div class="debug-item">
          <span class="debug-label">学校数</span>
          <span class="debug-value">{{ schoolList.length }}</span>
        </div>
        <div class="debug-item">
          <span class="debug-label">总数</span>
          <span class="debug-value">{{ total }}</span>
        </div>
        <div class="debug-item">
          <span class="debug-label">错误</span>
          <span class="debug-value">{{ error || '无' }}</span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrap">
      <div class="wx-skeleton" style="height: 60px; margin-bottom: 8px;" v-for="i in 5" :key="i"></div>
    </div>

    <!-- 学校列表 -->
    <div class="wx-list" v-else-if="schoolList.length > 0">
      <div
        class="wx-list-item"
        v-for="school in filteredSchools"
        :key="school.id"
      >
        <div class="item-avatar">
          <span class="avatar-text">{{ school.name?.charAt(0) || '校' }}</span>
        </div>
        <div class="item-content">
          <div class="item-title">{{ school.name }}</div>
          <div class="item-subtitle">
            <span>{{ school.prefecture || school.city || '未知地区' }}</span>
            <span v-if="school.min_score"> · {{ school.min_score }}分</span>
            <span> · {{ school.type_name || '未知类型' }}</span>
          </div>
        </div>
        <div class="item-right">
          <span class="item-arrow">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">📭</div>
      <div class="empty-title">没有学校数据</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const loading = ref(true)
const schoolList = ref<any[]>([])
const total = ref(0)
const error = ref('')
const searchKeyword = ref('')

const filteredSchools = computed(() => {
  if (!searchKeyword.value.trim()) return schoolList.value
  const kw = searchKeyword.value.trim().toLowerCase()
  return schoolList.value.filter((s: any) =>
    (s.name || '').toLowerCase().includes(kw)
  )
})

const fetchData = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, string> = { page: '1', size: '20' }
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    const queryString = new URLSearchParams(params).toString()
    const response = await fetch(`/api/schools?${queryString}`)
    const data = await response.json()

    if (data.success) {
      schoolList.value = data.data.items || data.data || []
      total.value = data.data.total || schoolList.value.length
    } else {
      error.value = data.message || '获取失败'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '未知错误'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.school-simple-page {
  padding: var(--wx-spacing-lg);
  background: var(--wx-bg);
  min-height: 100%;
}

/* 搜索栏 */
.search-bar {
  margin-bottom: var(--wx-spacing-md);
  max-width: 600px;
}

/* 调试面板 */
.debug-panel {
  margin-bottom: var(--wx-spacing-lg);
}

.debug-panel .card-title {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-md);
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
}

.debug-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--wx-spacing-md);
}

.debug-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.debug-label {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

.debug-value {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-text-primary);
}

/* 加载 */
.loading-wrap {
  padding: var(--wx-spacing-md) 0;
}

/* 列表项右侧 */
.item-right {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
  flex-shrink: 0;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--wx-spacing-md);
}

.empty-title {
  font-size: var(--wx-font-size-lg);
  color: var(--wx-text-primary);
}

@media (max-width: 768px) {
  .debug-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .school-simple-page {
    padding: var(--wx-spacing-md);
  }
}
</style>