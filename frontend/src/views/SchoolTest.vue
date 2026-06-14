<template>
  <div class="school-test-page">
    <!-- 顶部标题 -->
    <div class="wx-card page-header">
      <h1 class="header-title">学校列表测试页面</h1>
      <p class="header-desc">如果你能看到这个内容，说明页面能正常加载！</p>
    </div>

    <!-- 测试2: 硬编码的学校数据 -->
    <div class="wx-card test-section">
      <div class="card-title">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        测试2: 硬编码的学校数据
      </div>
      <div class="wx-list">
        <div class="wx-list-item" v-for="school in testSchools" :key="school.id">
          <div class="item-avatar">
            <span class="avatar-text">{{ school.name?.charAt(0) || '校' }}</span>
          </div>
          <div class="item-content">
            <div class="item-title">{{ school.name }}</div>
            <div class="item-subtitle">{{ school.city }}</div>
          </div>
          <div class="item-right">
            <span class="item-arrow">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试3: 从API获取数据 -->
    <div class="wx-card test-section">
      <div class="card-title">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        测试3: 从API获取数据
      </div>
      <div class="wx-card debug-info">
        <div class="debug-grid">
          <div class="debug-item">
            <span class="debug-label">加载状态</span>
            <span class="debug-value">{{ loading ? '是' : '否' }}</span>
          </div>
          <div class="debug-item">
            <span class="debug-label">数据长度</span>
            <span class="debug-value">{{ apiData.length }}</span>
          </div>
          <div class="debug-item">
            <span class="debug-label">错误信息</span>
            <span class="debug-value" :class="{ 'error-text': errorMessage }">{{ errorMessage || '无' }}</span>
          </div>
        </div>
      </div>
      <div class="toolbar-row">
        <button class="wx-btn-primary" @click="fetchData" :disabled="loading">
          {{ loading ? '获取中...' : '获取学校数据' }}
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrap">
        <div class="wx-skeleton" style="height: 60px; margin-bottom: 8px;" v-for="i in 3" :key="i"></div>
      </div>

      <!-- API数据列表 -->
      <div class="wx-list" v-else-if="apiData.length > 0">
        <div class="wx-list-item" v-for="school in apiData" :key="school.id">
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

      <!-- 初始状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">📡</div>
        <div class="empty-title">点击上方按钮获取数据</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const testSchools = [
  { id: 1, name: '昆明第一中学', city: '昆明市' },
  { id: 2, name: '曲靖市第一中学', city: '曲靖市' },
  { id: 3, name: '玉溪市第一中学', city: '玉溪市' },
]

const loading = ref(false)
const apiData = ref<any[]>([])
const errorMessage = ref('')

const fetchData = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch('/api/schools?page=1&size=10')
    const data = await response.json()
    if (data.success && data.data) {
      apiData.value = data.data.items || data.data || []
    } else {
      errorMessage.value = data.message || 'API返回不成功'
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '未知错误'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.school-test-page {
  padding: var(--wx-spacing-lg);
  background: var(--wx-bg);
  min-height: 100%;
}

/* 页面头部 */
.page-header {
  margin-bottom: var(--wx-spacing-lg);
  text-align: center;
}

.header-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--wx-text-primary);
  margin: 0 0 var(--wx-spacing-sm) 0;
}

.header-desc {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
  margin: 0;
}

/* 测试区块 */
.test-section {
  margin-bottom: var(--wx-spacing-lg);
}

.test-section .card-title {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-md);
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-sm);
}

/* 调试信息 */
.debug-info {
  background: var(--wx-primary-light);
  margin-bottom: var(--wx-spacing-md);
  padding: var(--wx-spacing-md) var(--wx-spacing-lg);
}

.debug-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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

.debug-value.error-text {
  color: var(--wx-danger);
}

/* 工具栏行 */
.toolbar-row {
  margin-bottom: var(--wx-spacing-md);
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
  padding: 40px 20px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: var(--wx-spacing-sm);
}

.empty-title {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-muted);
}

@media (max-width: 768px) {
  .debug-grid {
    grid-template-columns: 1fr;
  }

  .school-test-page {
    padding: var(--wx-spacing-md);
  }
}
</style>