<template>
  <div class="policy-page">
    <!-- 顶部搜索栏 -->
    <div class="wx-search search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
      <input
        class="search-input"
        v-model="searchForm.title"
        placeholder="搜索政策标题关键词"
        @keyup.enter="handleSearch"
      />
    </div>

    <!-- 热门政策快速入口 -->
    <div class="quick-tags">
      <span
        v-for="item in hotPolicies"
        :key="item.key"
        class="quick-chip"
        @click="searchHotPolicy(item.key)"
      >{{ item.label }}</span>
    </div>

    <!-- 筛选区 -->
    <div class="wx-card filter-card">
      <div class="filter-row">
        <select class="filter-select" v-model="searchForm.city" @change="handleSearch">
          <option value="">全部地区</option>
          <option v-for="city in cityList" :key="city" :value="city">{{ city }}</option>
        </select>
        <select class="filter-select" v-model="searchForm.policyType" @change="handleSearch">
          <option value="">全部类型</option>
          <option v-for="type in policyTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
        </select>
        <select class="filter-select" v-model="searchForm.category" @change="handleSearch">
          <option value="">全部分类</option>
          <option v-for="category in policyCategories" :key="category.value" :value="category.value">{{ category.label }}</option>
        </select>
        <button class="wx-btn-text wx-btn-sm" @click="handleReset">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6M23 20v-6h-6"/><path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15"/></svg>
          重置
        </button>
      </div>
    </div>

    <!-- 对比操作栏 -->
    <div class="compare-bar" v-if="selectedPolicies.length > 0">
      <span class="compare-info">已选择 {{ selectedPolicies.length }} 个政策</span>
      <button
        class="wx-btn-primary wx-btn-sm"
        @click="openCompareDialog"
        :disabled="selectedPolicies.length < 2"
      >对比选中政策</button>
      <button class="wx-btn-text wx-btn-sm" @click="clearSelection">清除选择</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrap">
      <div class="wx-skeleton" style="height: 72px; margin-bottom: 8px;" v-for="i in 5" :key="i"></div>
    </div>

    <!-- 政策列表 -->
    <div class="wx-list" v-else-if="policyList.length > 0">
      <div
        class="wx-list-item policy-item"
        v-for="policy in policyList"
        :key="policy.id"
        @click="viewDetail(policy)"
      >
        <div class="item-avatar policy-avatar">
          <span class="avatar-text">策</span>
        </div>
        <div class="item-content">
          <div class="item-title">{{ policy.title }}</div>
          <div class="item-subtitle">
            <span v-if="policy.source">{{ policy.source }}</span>
            <span v-else>全省通用</span>
            <span> · {{ policy.publish_date }}</span>
            <span v-if="policy.category" class="category-tag"> · {{ policy.category }}</span>
            <span v-if="getPolicyTypeLabel(policy)" class="type-tag"> · {{ getPolicyTypeLabel(policy) }}</span>
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
      <div class="empty-icon">📄</div>
      <div class="empty-title">暂无政策数据</div>
      <button class="wx-btn-secondary" @click="handleReset" v-if="searchForm.title || searchForm.city || searchForm.policyType || searchForm.category">清除条件</button>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > 0">
      <button
        class="page-btn"
        :disabled="currentPage <= 1"
        @click="handleCurrentChange(currentPage - 1)"
      >上一页</button>
      <span class="page-info">{{ currentPage }} / {{ Math.ceil(total / pageSize) }}</span>
      <button
        class="page-btn"
        :disabled="currentPage >= Math.ceil(total / pageSize)"
        @click="handleCurrentChange(currentPage + 1)"
      >下一页</button>
    </div>

    <!-- AI政策问答 -->
    <div class="wx-card qa-section">
      <div class="qa-title">AI政策问答</div>
      <div class="qa-chat" ref="qaChat">
        <div class="qa-message" v-for="(msg, idx) in qaMessages" :key="idx">
          <div class="qa-msg-text">{{ msg.content }}</div>
          <div class="qa-msg-time">{{ msg.time }}</div>
        </div>
      </div>
      <div class="qa-input-row">
        <input
          class="wx-input"
          v-model="qaInput"
          placeholder="输入您的问题，如：指标到校政策、加分政策等"
          @keyup.enter="sendQAMessage"
          style="flex: 1;"
        />
        <button class="wx-btn-primary wx-btn-sm" @click="sendQAMessage" :disabled="qaLoading">
          {{ qaLoading ? '发送中...' : '发送' }}
        </button>
      </div>
    </div>

    <!-- AI解读对话框 -->
    <div class="wx-dialog-overlay" v-if="aiDialogVisible" @click.self="aiDialogVisible = false">
      <div class="wx-dialog" style="max-width: 700px;">
        <div class="wx-dialog-header">AI政策解读</div>
        <div class="wx-dialog-body">
          <div class="original-policy" v-if="currentPolicy.title">
            <div class="policy-source-title">{{ currentPolicy.title }}</div>
            <div class="policy-source-meta">
              <span v-if="currentPolicy.city">{{ currentPolicy.city }}</span>
              <span v-else>全省通用</span>
              <span>{{ currentPolicy.publishDate || currentPolicy.publish_date }}</span>
            </div>
            <div class="policy-source-text">{{ currentPolicy.content }}</div>
          </div>
          <div class="ai-analysis" v-if="!aiLoading">
            <div class="analysis-block">
              <div class="analysis-label">政策要点</div>
              <ul>
                <li v-for="point in aiInterpretation.keyPoints" :key="point">{{ point }}</li>
              </ul>
            </div>
            <div class="analysis-block">
              <div class="analysis-label">对考生的影响</div>
              <p>{{ aiInterpretation.impact }}</p>
            </div>
            <div class="analysis-block">
              <div class="analysis-label">应对建议</div>
              <p>{{ aiInterpretation.suggestions }}</p>
            </div>
          </div>
          <div v-else class="loading-wrap">
            <div class="wx-skeleton" style="height: 20px; margin-bottom: 8px;" v-for="i in 8" :key="i"></div>
          </div>
        </div>
        <div class="wx-dialog-footer">
          <button class="wx-btn-secondary" @click="aiDialogVisible = false">关闭</button>
          <button class="wx-btn-primary" @click="saveInterpretation">保存解读</button>
        </div>
      </div>
    </div>

    <!-- 政策详情对话框 -->
    <div class="wx-dialog-overlay" v-if="detailDialogVisible" @click.self="detailDialogVisible = false">
      <div class="wx-dialog" style="max-width: 700px;">
        <div class="wx-dialog-header">政策详情</div>
        <div class="wx-dialog-body">
          <div class="detail-title">{{ currentPolicy.title }}</div>
          <div class="detail-meta">
            <span>{{ currentPolicy.source || '云南省教育厅' }}</span>
            <span> · {{ currentPolicy.publish_date || currentPolicy.publishDate }}</span>
            <span v-if="currentPolicy.category"> · {{ currentPolicy.category }}</span>
          </div>
          <div class="detail-text">{{ currentPolicy.content }}</div>
        </div>
        <div class="wx-dialog-footer">
          <button class="wx-btn-text" @click="downloadPolicy(currentPolicy)">下载文档</button>
          <button class="wx-btn-secondary" @click="detailDialogVisible = false">关闭</button>
          <button class="wx-btn-primary" @click="aiInterpret(currentPolicy)">AI解读</button>
        </div>
      </div>
    </div>

    <!-- 政策对比对话框 -->
    <div class="wx-dialog-overlay" v-if="compareDialogVisible" @click.self="compareDialogVisible = false">
      <div class="wx-dialog" style="max-width: 900px;">
        <div class="wx-dialog-header">政策对比</div>
        <div class="wx-dialog-body">
          <div class="compare-grid">
            <div
              v-for="(policyId, idx) in selectedPolicies"
              :key="policyId"
              class="compare-card"
            >
              <div class="compare-card-title">{{ getPolicyTitle(policyId) }}</div>
              <div class="compare-card-meta">
                <span>{{ getPolicySource(policyId) }}</span>
                <span> · {{ getPolicyDate(policyId) }}</span>
              </div>
              <div class="compare-card-text">{{ getPolicyContent(policyId) }}</div>
            </div>
          </div>
        </div>
        <div class="wx-dialog-footer">
          <button class="wx-btn-secondary" @click="compareDialogVisible = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { policyApi, aiApi } from '../api'
import { cityList, policyCategories } from '../utils'

const loading = ref(false)
const policyList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const aiDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const compareDialogVisible = ref(false)
const aiLoading = ref(false)
const currentPolicy = ref<any>({})
const aiInterpretation = ref({
  keyPoints: [] as string[],
  impact: '',
  suggestions: ''
})

const qaInput = ref('')
const qaLoading = ref(false)
const qaChat = ref<HTMLElement | null>(null)
const qaMessages = ref([
  {
    content: '您好！我是AI政策助手，有什么中考政策问题可以问我，比如指标到校、加分政策、志愿填报等。',
    time: new Date().toLocaleTimeString()
  }
])

const selectedPolicies = ref<any[]>([])

const hotPolicies = [
  { key: '指标到校', label: '指标到校政策' },
  { key: '提前批', label: '提前批政策' },
  { key: '特长生', label: '特长生招生' },
  { key: '民族班', label: '民族班政策' },
  { key: '海军航空班', label: '海军航空班' },
  { key: '志愿填报', label: '志愿填报指导' }
]

const policyTypes = [
  { value: 'zhibiao', label: '指标到校' },
  { value: 'tiqianpi', label: '提前批' },
  { value: 'specialist', label: '特长生' },
  { value: 'minzu', label: '民族班' },
  { value: 'hangkong', label: '海军航空班' },
  { value: 'volunteer', label: '志愿填报' },
  { value: 'score', label: '分数线' },
  { value: 'addscore', label: '加分政策' }
]

const searchForm = reactive({
  title: '',
  city: '',
  policyType: '',
  category: '',
  dateRange: [] as any[]
})

const fetchPolicyList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      pageSize: pageSize.value,
      title: searchForm.title,
      city: searchForm.city,
      policyType: searchForm.policyType,
      category: searchForm.category
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.startDate = searchForm.dateRange[0]
      params.endDate = searchForm.dateRange[1]
    }
    const response = await policyApi.getPolicyList(params)
    if (response.success) {
      policyList.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      ElMessage.error(response.message || '获取政策列表失败')
    }
  } catch (error) {
    console.error('获取政策列表失败:', error)
    ElMessage.error('获取政策列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchPolicyList()
}

const handleReset = () => {
  searchForm.title = ''
  searchForm.city = ''
  searchForm.policyType = ''
  searchForm.category = ''
  searchForm.dateRange = []
  currentPage.value = 1
  fetchPolicyList()
}

const searchHotPolicy = (key: string) => {
  searchForm.title = key
  currentPage.value = 1
  fetchPolicyList()
}

const viewDetail = (policy: any) => {
  currentPolicy.value = policy
  detailDialogVisible.value = true
}

const aiInterpret = async (policy: any) => {
  currentPolicy.value = policy
  aiDialogVisible.value = true
  aiLoading.value = true
  try {
    const response = await aiApi.interpretPolicy({
      policyId: policy.id,
      policyContent: policy.content
    })
    if (response.success) {
      aiInterpretation.value = response.data || { keyPoints: [], impact: '', suggestions: '' }
    } else {
      ElMessage.error(response.message || '获取AI解读失败')
    }
  } catch (error) {
    console.error('获取AI解读失败:', error)
    ElMessage.error('获取AI解读失败')
  } finally {
    aiLoading.value = false
  }
}

const downloadPolicy = (policy: any) => {
  const content = `【${policy.title}】\n\n来源：${policy.source || '云南省教育厅'}\n发布日期：${policy.publish_date || policy.publishDate}\n分类：${policy.category || '招生政策'}\n\n${policy.content}`
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${policy.title}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success(`已下载《${policy.title}》`)
}

const saveInterpretation = () => {
  ElMessage.success('解读已保存')
  aiDialogVisible.value = false
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchPolicyList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchPolicyList()
}

const sendQAMessage = async () => {
  if (!qaInput.value.trim()) return
  const question = qaInput.value.trim()
  qaInput.value = ''
  qaMessages.value.push({ content: question, time: new Date().toLocaleTimeString() })
  qaLoading.value = true
  try {
    const response = await aiApi.openclawChat({ message: question, type: 'policy' })
    if (response.success) {
      qaMessages.value.push({
        content: response.data.answer || '感谢您的问题，我正在学习更多政策知识，稍后为您解答。',
        time: new Date().toLocaleTimeString()
      })
    } else {
      ElMessage.error(response.message || '获取AI回答失败')
    }
  } catch (error) {
    console.error('获取AI回答失败:', error)
    ElMessage.error('获取AI回答失败')
  } finally {
    qaLoading.value = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (qaChat.value) {
      qaChat.value.scrollTop = qaChat.value.scrollHeight
    }
  })
}

const clearSelection = () => {
  selectedPolicies.value = []
}

const openCompareDialog = () => {
  if (selectedPolicies.value.length >= 2) {
    compareDialogVisible.value = true
  } else {
    ElMessage.warning('请至少选择2个政策进行对比')
  }
}

const getPolicyTitle = (policyId: any) => {
  const policy = policyList.value.find(p => p.id === policyId)
  return policy ? policy.title : '未知政策'
}

const getPolicySource = (policyId: any) => {
  const policy = policyList.value.find(p => p.id === policyId)
  return policy ? (policy.source || '云南省教育厅') : ''
}

const getPolicyDate = (policyId: any) => {
  const policy = policyList.value.find(p => p.id === policyId)
  return policy ? (policy.publish_date || policy.publishDate || '') : ''
}

const getPolicyContent = (policyId: any) => {
  const policy = policyList.value.find(p => p.id === policyId)
  return policy ? policy.content : ''
}

const getPolicyTypeLabel = (policy: any) => {
  const title = policy.title || ''
  if (title.includes('指标到校')) return '指标到校'
  if (title.includes('提前批')) return '提前批'
  if (title.includes('特长生')) return '特长生'
  if (title.includes('民族班')) return '民族班'
  if (title.includes('航空班')) return '航空班'
  return ''
}

onMounted(() => {
  fetchPolicyList()
})
</script>

<style scoped>
.policy-page {
  padding: var(--wx-spacing-lg);
  background: var(--wx-bg);
  min-height: 100%;
}

/* 搜索栏 */
.search-bar {
  margin-bottom: var(--wx-spacing-md);
  max-width: 600px;
}

/* 热门政策标签 */
.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
  margin-bottom: var(--wx-spacing-lg);
}

.quick-chip {
  display: inline-block;
  padding: 4px 14px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-bg-white);
  border: 1px solid var(--wx-border-light);
  color: var(--wx-text-secondary);
  font-size: var(--wx-font-size-sm);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
  user-select: none;
}

.quick-chip:hover {
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  border-color: var(--wx-primary);
}

/* 筛选卡片 */
.filter-card {
  margin-bottom: var(--wx-spacing-lg);
  padding: var(--wx-spacing-md);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
  align-items: center;
}

.filter-select {
  padding: 6px 10px;
  border: 1px solid var(--wx-border-light);
  border-radius: var(--wx-radius-sm);
  background: var(--wx-bg-white);
  color: var(--wx-text-primary);
  font-size: var(--wx-font-size-sm);
  font-family: var(--wx-font-family);
  outline: none;
  cursor: pointer;
  min-width: 120px;
}

/* 对比操作栏 */
.compare-bar {
  display: flex;
  align-items: center;
  gap: var(--wx-spacing-md);
  padding: var(--wx-spacing-md);
  background: var(--wx-bg-white);
  border: 1px solid var(--wx-border-light);
  border-radius: var(--wx-radius-md);
  margin-bottom: var(--wx-spacing-md);
}

.compare-info {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
}

/* 加载状态 */
.loading-wrap {
  padding: var(--wx-spacing-md) 0;
}

/* 政策列表项 */
.policy-item {
  padding: var(--wx-spacing-lg) var(--wx-spacing-lg);
}

.policy-avatar {
  background: var(--wx-primary-light) !important;
  color: var(--wx-primary) !important;
}

.policy-avatar .avatar-text {
  font-size: 16px;
  font-weight: 600;
}

.item-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.category-tag {
  color: var(--wx-info);
}

.type-tag {
  color: var(--wx-primary);
  font-weight: 500;
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
  margin-bottom: var(--wx-spacing-md);
}

/* 分页 */
.pagination-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--wx-spacing-lg);
  padding: var(--wx-spacing-xl) 0;
}

.page-btn {
  padding: 6px 16px;
  border: 1px solid var(--wx-border);
  border-radius: var(--wx-radius-sm);
  background: var(--wx-bg-white);
  color: var(--wx-text-primary);
  font-size: var(--wx-font-size-sm);
  font-family: var(--wx-font-family);
  cursor: pointer;
  transition: all var(--wx-transition-fast);
}

.page-btn:hover:not(:disabled) {
  background: var(--wx-bg-hover);
  border-color: var(--wx-primary);
  color: var(--wx-primary);
}

.page-btn:disabled {
  color: var(--wx-text-muted);
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
}

/* AI问答 */
.qa-section {
  margin-top: var(--wx-spacing-xl);
}

.qa-title {
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-md);
  padding-bottom: var(--wx-spacing-md);
  border-bottom: 1px solid var(--wx-border-light);
}

.qa-chat {
  max-height: 300px;
  overflow-y: auto;
  padding: var(--wx-spacing-md);
  background: var(--wx-bg);
  border-radius: var(--wx-radius-sm);
  margin-bottom: var(--wx-spacing-md);
}

.qa-message {
  margin-bottom: var(--wx-spacing-md);
}

.qa-message:last-child {
  margin-bottom: 0;
}

.qa-msg-text {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-primary);
  line-height: var(--wx-line-height-lg);
  padding: var(--wx-spacing-sm) var(--wx-spacing-md);
  background: var(--wx-bg-white);
  border-radius: var(--wx-radius-sm);
  box-shadow: var(--wx-shadow-sm);
}

.qa-msg-time {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  margin-top: 4px;
  text-align: right;
}

.qa-input-row {
  display: flex;
  gap: var(--wx-spacing-sm);
  align-items: center;
}

/* 对话框内容样式 */
.original-policy {
  margin-bottom: var(--wx-spacing-xl);
  padding-bottom: var(--wx-spacing-lg);
  border-bottom: 1px solid var(--wx-border-light);
}

.policy-source-title {
  font-size: var(--wx-font-size-lg);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-sm);
}

.policy-source-meta {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
  margin-bottom: var(--wx-spacing-md);
  display: flex;
  gap: var(--wx-spacing-sm);
}

.policy-source-text {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-secondary);
  line-height: var(--wx-line-height-lg);
}

.ai-analysis {
  color: var(--wx-text-primary);
}

.analysis-block {
  margin-bottom: var(--wx-spacing-lg);
}

.analysis-block:last-child {
  margin-bottom: 0;
}

.analysis-label {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-primary);
  margin-bottom: var(--wx-spacing-sm);
}

.analysis-block ul {
  padding-left: 20px;
  margin: 0;
}

.analysis-block li {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-primary);
  line-height: var(--wx-line-height-lg);
  margin-bottom: 4px;
}

.analysis-block p {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-primary);
  line-height: var(--wx-line-height-lg);
  margin: 0;
}

/* 详情对话框 */
.detail-title {
  font-size: var(--wx-font-size-xl);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-sm);
}

.detail-meta {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
  margin-bottom: var(--wx-spacing-lg);
  padding-bottom: var(--wx-spacing-md);
  border-bottom: 1px solid var(--wx-border-light);
}

.detail-text {
  font-size: var(--wx-font-size-md);
  color: var(--wx-text-secondary);
  line-height: var(--wx-line-height-lg);
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
}

/* 对比 */
.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--wx-spacing-md);
}

.compare-card {
  padding: var(--wx-spacing-md);
  background: var(--wx-bg);
  border-radius: var(--wx-radius-md);
  border: 1px solid var(--wx-border-light);
}

.compare-card-title {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-text-primary);
  margin-bottom: var(--wx-spacing-sm);
}

.compare-card-meta {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
  margin-bottom: var(--wx-spacing-md);
  padding-bottom: var(--wx-spacing-sm);
  border-bottom: 1px solid var(--wx-border-light);
}

.compare-card-text {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-secondary);
  line-height: var(--wx-line-height);
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  .compare-grid {
    grid-template-columns: 1fr;
  }
}
</style>