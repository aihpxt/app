<template>
  <div class="spec-page">
    <!-- 顶部搜索栏 -->
    <div class="wx-search search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
      <input
        class="search-input"
        v-model="searchKeyword"
        placeholder="搜索学校名称"
        @keyup.enter="searchSchools"
      />
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tags">
      <span class="filter-chip" :class="{ active: !filterType }" @click="filterType = ''; searchSchools()">全部类型</span>
      <span class="filter-chip" :class="{ active: filterType === '2' }" @click="filterType = '2'; searchSchools()">重点高中</span>
      <span class="filter-chip" :class="{ active: filterType === '1' }" @click="filterType = '1'; searchSchools()">普通高中</span>
      <span class="filter-chip" :class="{ active: filterType === '4' }" @click="filterType = '4'; searchSchools()">民办学校</span>
      <span class="filter-chip" v-if="filterCity || filterType || searchKeyword" @click="resetFilters" style="color: var(--wx-danger); border-color: var(--wx-danger);">清除筛选</span>
    </div>

    <!-- 统计概览 -->
    <div class="stats-row">
      <div class="wx-card stat-card">
        <div class="stat-value">{{ schoolList.length }}</div>
        <div class="stat-label">学校总数</div>
      </div>
      <div class="wx-card stat-card">
        <div class="stat-value green">{{ keySchoolCount }}</div>
        <div class="stat-label">重点高中</div>
      </div>
      <div class="wx-card stat-card">
        <div class="stat-value">{{ avgStudents }}</div>
        <div class="stat-label">平均在校生</div>
      </div>
      <div class="wx-card stat-card">
        <div class="stat-value green">{{ avgRate }}%</div>
        <div class="stat-label">平均一本率</div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <span class="list-count">共 {{ filteredSchools.length }} 所</span>
      <div class="toolbar-right">
        <button class="wx-btn-primary wx-btn-sm" @click="viewCompare" :disabled="selectedSchools.length < 2">
          批量对比
        </button>
      </div>
    </div>

    <!-- 学校规格列表 -->
    <div class="wx-list" v-if="filteredSchools.length > 0">
      <div
        class="wx-list-item spec-item"
        v-for="school in filteredSchools"
        :key="school.id"
        :class="{ selected: selectedSchools.includes(school.id) }"
      >
        <div class="item-check" @click.stop="toggleSelect(school.id)">
          <span class="check-box" :class="{ checked: selectedSchools.includes(school.id) }">
            <svg v-if="selectedSchools.includes(school.id)" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
          </span>
        </div>
        <div class="item-content">
          <div class="item-title">{{ school.name }}</div>
          <div class="item-subtitle">
            <span>{{ school.typeName }}</span>
            <span> · {{ school.nature }}</span>
            <span v-if="school.minScore"> · {{ school.minScore }}分</span>
            <span v-if="school.oneRate"> · 一本率 {{ school.oneRate }}%</span>
          </div>
        </div>
        <div class="item-right">
          <span class="item-arrow" @click.stop="viewDetail(school.id)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">📋</div>
      <div class="empty-title">未找到符合条件的学校</div>
      <button class="wx-btn-secondary" @click="resetFilters">重置筛选</button>
    </div>

    <!-- 详情弹窗 -->
    <div class="wx-dialog-overlay" v-if="showDetail && selectedSchool" @click.self="showDetail = false">
      <div class="wx-dialog" style="max-width: 600px;">
        <div class="wx-dialog-header">{{ selectedSchool.name }} - 详细规格</div>
        <div class="wx-dialog-body">
          <div class="detail-tags">
            <span class="tag-item">{{ selectedSchool.typeName }}</span>
            <span class="tag-item">{{ selectedSchool.nature }}</span>
          </div>

          <div class="detail-section">
            <div class="section-label">基本信息</div>
            <div class="info-row"><span class="info-lbl">学校地址</span><span class="info-val">{{ selectedSchool.address }}</span></div>
            <div class="info-row"><span class="info-lbl">创办时间</span><span class="info-val">{{ selectedSchool.foundedYear || '暂无' }}年</span></div>
            <div class="info-row"><span class="info-lbl">在校学生</span><span class="info-val">{{ selectedSchool.students?.toLocaleString() || '暂无' }}人</span></div>
            <div class="info-row"><span class="info-lbl">教职工</span><span class="info-val">{{ selectedSchool.teachers?.toLocaleString() || '暂无' }}人</span></div>
          </div>

          <div class="detail-section">
            <div class="section-label">招生信息</div>
            <div class="info-row"><span class="info-lbl">录取分数线</span><span class="info-val green">{{ selectedSchool.minScore }}分</span></div>
            <div class="info-row"><span class="info-lbl">学费标准</span><span class="info-val">{{ selectedSchool.tuition === 0 ? '公办免费' : selectedSchool.tuition.toLocaleString() + '元/年' }}</span></div>
            <div class="info-row"><span class="info-lbl">住宿条件</span><span class="info-val">{{ selectedSchool.boarding }}</span></div>
            <div class="info-row"><span class="info-lbl">管理风格</span><span class="info-val">{{ selectedSchool.style }}</span></div>
          </div>

          <div class="detail-section">
            <div class="section-label">升学成绩</div>
            <div class="score-row">
              <div class="score-item">
                <div class="score-bar"><div class="score-fill" :style="{ width: selectedSchool.oneRate + '%', background: 'var(--wx-primary)' }"></div></div>
                <div class="score-label"><span>一本率</span><span>{{ selectedSchool.oneRate }}%</span></div>
              </div>
              <div class="score-item">
                <div class="score-bar"><div class="score-fill" :style="{ width: selectedSchool.twoRate + '%', background: 'var(--wx-info)' }"></div></div>
                <div class="score-label"><span>二本率</span><span>{{ selectedSchool.twoRate }}%</span></div>
              </div>
            </div>
          </div>

          <div class="detail-section" v-if="selectedSchool.features.length > 0">
            <div class="section-label">特色优势</div>
            <div class="features-wrap">
              <span class="feature-chip" v-for="feature in selectedSchool.features" :key="feature">{{ feature }}</span>
            </div>
          </div>
        </div>
        <div class="wx-dialog-footer">
          <button class="wx-btn-secondary" @click="showDetail = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

interface SchoolData {
  id: number
  name: string
  typeName: string
  minScore: number
  type: number
  nature: string
  oneRate: number
  twoRate: number
  tuition: number
  boarding: string
  style: string
  address: string
  foundedYear?: number
  students?: number
  teachers?: number
  features: string[]
}

const router = useRouter()
const searchKeyword = ref('')
const filterCity = ref('')
const filterType = ref('')
const selectedSchools = ref<number[]>([])
const showDetail = ref(false)
const selectedSchool = ref<SchoolData | null>(null)

const schoolList = ref([
  { id: 1, name: '云南师范大学附属中学', typeName: '重点高中', minScore: 690, type: 2, nature: '公办', oneRate: 95, twoRate: 99, tuition: 0, boarding: '提供', style: '严格', address: '昆明市五华区一二一大街298号', foundedYear: 1940, students: 3500, teachers: 280, features: ['百年名校', '师资雄厚', '竞赛强校', '升学率高', '科技创新'] },
  { id: 2, name: '昆明市第一中学', typeName: '重点高中', minScore: 680, type: 2, nature: '公办', oneRate: 92, twoRate: 98, tuition: 0, boarding: '提供', style: '适中', address: '昆明市五华区西昌路233号', foundedYear: 1905, students: 3200, teachers: 260, features: ['历史悠久', '教学严谨', '社团丰富', '艺术教育'] },
  { id: 3, name: '昆明市第三中学', typeName: '重点高中', minScore: 670, type: 2, nature: '公办', oneRate: 88, twoRate: 96, tuition: 0, boarding: '提供', style: '适中', address: '昆明市呈贡区仕林街', foundedYear: 1907, students: 3000, teachers: 240, features: ['环境优美', '设施先进', '素质教育', '国际化'] },
  { id: 4, name: '昆明市第八中学', typeName: '重点高中', minScore: 660, type: 2, nature: '公办', oneRate: 85, twoRate: 95, tuition: 0, boarding: '提供', style: '严格', address: '昆明市五华区龙泉路628号', foundedYear: 1952, students: 2800, teachers: 220, features: ['管理严格', '学风优良', '体育特色'] },
  { id: 5, name: '昆明市第十中学', typeName: '重点高中', minScore: 650, type: 2, nature: '公办', oneRate: 82, twoRate: 93, tuition: 0, boarding: '提供', style: '适中', address: '昆明市盘龙区北京路2192号', foundedYear: 1920, students: 2600, teachers: 200, features: ['艺术特色', '科技创新', '校园文化'] },
  { id: 6, name: '云南大学附属中学', typeName: '重点高中', minScore: 655, type: 2, nature: '民办', oneRate: 86, twoRate: 94, tuition: 18000, boarding: '提供', style: '严格', address: '昆明市五华区一二一大街226号', foundedYear: 1927, students: 4000, teachers: 320, features: ['云大附属', '小班教学', '国际化', '双语教学'] },
  { id: 7, name: '昆明市第十二中学', typeName: '普通高中', minScore: 630, type: 1, nature: '公办', oneRate: 65, twoRate: 85, tuition: 0, boarding: '提供', style: '适中', address: '昆明市官渡区环湖东路', foundedYear: 1940, students: 2000, teachers: 160, features: ['公办普高', '区位优势', '体艺特色'] },
  { id: 8, name: '昆明市第十四中学', typeName: '普通高中', minScore: 620, type: 1, nature: '公办', oneRate: 60, twoRate: 82, tuition: 0, boarding: '不提供', style: '宽松', address: '昆明市五华区科新路', foundedYear: 1954, students: 1800, teachers: 140, features: ['科技教育', '艺术教育', '社团活动'] },
  { id: 9, name: '北大附中云南实验学校', typeName: '民办学校', minScore: 600, type: 4, nature: '民办', oneRate: 70, twoRate: 88, tuition: 25000, boarding: '提供', style: '严格', address: '昆明市官渡区矣六街道', foundedYear: 2003, students: 3500, teachers: 280, features: ['北大资源', '寄宿制', '国际化', '素质教育'] },
  { id: 10, name: '云南衡水实验中学', typeName: '民办学校', minScore: 580, type: 4, nature: '民办', oneRate: 68, twoRate: 86, tuition: 28000, boarding: '提供', style: '严格', address: '昆明市呈贡区吴家营街道', foundedYear: 2014, students: 5000, teachers: 400, features: ['衡水模式', '军事化管理', '提分快', '全封闭'] },
  { id: 11, name: '昆明市实验中学', typeName: '普通高中', minScore: 610, type: 1, nature: '公办', oneRate: 58, twoRate: 80, tuition: 0, boarding: '不提供', style: '适中', address: '昆明市盘龙区人民东路', foundedYear: 1997, students: 1500, teachers: 120, features: ['实验示范', '特色课程', '科技教育'] },
  { id: 12, name: '云南师范大学实验中学', typeName: '民办学校', minScore: 640, type: 4, nature: '民办', oneRate: 80, twoRate: 92, tuition: 20000, boarding: '提供', style: '严格', address: '昆明市五华区东风西路', foundedYear: 2003, students: 2800, teachers: 220, features: ['师大附属', '优质师资', '升学保障', '小班教学'] }
])

const filteredSchools = computed(() => {
  return schoolList.value.filter(school => {
    if (searchKeyword.value && !school.name.includes(searchKeyword.value)) return false
    if (filterCity.value && school.address && !school.address.includes(filterCity.value)) return false
    if (filterType.value && school.type !== Number(filterType.value)) return false
    return true
  })
})

const keySchoolCount = computed(() => schoolList.value.filter(s => s.type === 2).length)
const avgStudents = computed(() => {
  const total = schoolList.value.reduce((sum, s) => sum + (s.students || 0), 0)
  return Math.round(total / schoolList.value.length).toLocaleString()
})
const avgRate = computed(() => {
  const total = schoolList.value.reduce((sum, s) => sum + s.oneRate, 0)
  return (total / schoolList.value.length).toFixed(1)
})

const toggleSelect = (schoolId: number) => {
  const index = selectedSchools.value.indexOf(schoolId)
  if (index > -1) {
    selectedSchools.value.splice(index, 1)
  } else if (selectedSchools.value.length < 5) {
    selectedSchools.value.push(schoolId)
  } else {
    ElMessage.warning('最多只能选择5所学校进行对比')
  }
}

const searchSchools = () => {
  ElMessage.info('筛选完成，共找到 ' + filteredSchools.value.length + ' 所学校')
}

const resetFilters = () => {
  searchKeyword.value = ''
  filterCity.value = ''
  filterType.value = ''
}

const viewDetail = (schoolId: number) => {
  const school = schoolList.value.find(s => s.id === schoolId)
  if (school) {
    selectedSchool.value = school
    showDetail.value = true
  }
}

const viewCompare = () => {
  if (selectedSchools.value.length < 2) {
    ElMessage.warning('请至少选择2所学校进行对比')
    return
  }
  router.push({ path: '/compare', query: { schools: selectedSchools.value.join(',') } })
}
</script>

<style scoped>
.spec-page {
  padding: var(--wx-spacing-lg);
  background: var(--wx-bg);
  min-height: 100%;
}

/* 搜索栏 */
.search-bar {
  margin-bottom: var(--wx-spacing-md);
  max-width: 600px;
}

/* 筛选标签 */
.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
  margin-bottom: var(--wx-spacing-lg);
}

.filter-chip {
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

.filter-chip:hover {
  background: var(--wx-bg-hover);
  color: var(--wx-text-primary);
}

.filter-chip.active {
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  border-color: var(--wx-primary);
}

/* 统计 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--wx-spacing-md);
  margin-bottom: var(--wx-spacing-lg);
}

.stat-card {
  text-align: center;
  padding: var(--wx-spacing-lg);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--wx-text-primary);
  margin-bottom: 4px;
}

.stat-value.green {
  color: var(--wx-primary);
}

.stat-label {
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--wx-spacing-md);
  padding: var(--wx-spacing-sm) 0;
}

.list-count {
  font-size: var(--wx-font-size-sm);
  color: var(--wx-text-muted);
}

.toolbar-right {
  display: flex;
  gap: var(--wx-spacing-sm);
}

/* 列表项 */
.spec-item {
  padding: var(--wx-spacing-md) var(--wx-spacing-lg);
}

.spec-item.selected {
  background: var(--wx-primary-light);
}

.item-check {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.check-box {
  width: 20px;
  height: 20px;
  border: 2px solid var(--wx-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--wx-transition-fast);
}

.check-box.checked {
  background: var(--wx-primary);
  border-color: var(--wx-primary);
  color: var(--wx-text-white);
}

.item-right {
  display: flex;
  align-items: center;
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
  margin-bottom: var(--wx-spacing-md);
}

/* 详情弹窗 */
.detail-tags {
  display: flex;
  gap: var(--wx-spacing-sm);
  margin-bottom: var(--wx-spacing-lg);
}

.tag-item {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  font-size: var(--wx-font-size-xs);
}

.detail-section {
  margin-bottom: var(--wx-spacing-xl);
}

.section-label {
  font-size: var(--wx-font-size-md);
  font-weight: 600;
  color: var(--wx-primary);
  margin-bottom: var(--wx-spacing-sm);
  padding-bottom: var(--wx-spacing-sm);
  border-bottom: 1px solid var(--wx-border-light);
}

.info-row {
  display: flex;
  padding: 6px 0;
  font-size: var(--wx-font-size-sm);
}

.info-lbl {
  color: var(--wx-text-muted);
  min-width: 80px;
  flex-shrink: 0;
}

.info-val {
  color: var(--wx-text-primary);
}

.info-val.green {
  color: var(--wx-primary);
  font-weight: 600;
}

.score-row {
  display: flex;
  flex-direction: column;
  gap: var(--wx-spacing-md);
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.score-bar {
  height: 10px;
  background: var(--wx-bg);
  border-radius: 5px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.score-label {
  display: flex;
  justify-content: space-between;
  font-size: var(--wx-font-size-xs);
  color: var(--wx-text-muted);
}

.features-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wx-spacing-sm);
}

.feature-chip {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--wx-radius-round);
  background: var(--wx-primary-light);
  color: var(--wx-primary);
  font-size: var(--wx-font-size-xs);
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>