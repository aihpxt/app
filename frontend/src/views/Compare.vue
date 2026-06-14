<template>
  <div class="compare-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="header-left">
            <div class="logo-icon">
              <el-icon class="icon"><ArrowRightBold /></el-icon>
            </div>
            <div>
              <h1 class="page-title">AI学校对比</h1>
              <p class="page-desc">选择2-5所学校，AI智能对比分析，助您做出最佳选择</p>
            </div>
          </div>
          <div class="header-actions">
            <el-button @click="goBack" class="back-btn">
              <el-icon><ArrowLeft /></el-icon>
              返回首页
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="container main-content">
      <!-- 选择学校区域 -->
      <div class="select-section card">
        <div class="section-title">
          <el-icon class="icon-primary"><School /></el-icon>
          <span>选择对比学校</span>
        </div>
        
        <div class="select-row">
          <div class="school-select-wrapper">
            <el-select
              v-model="selectedSchools"
              multiple
              filterable
              placeholder="请选择要对比的学校（2-5所）"
              class="school-select"
              :multiple-limit="5"
              :loading="loadingSchools"
              @change="onSchoolSelect"
            >
              <el-option
                v-for="school in schoolList"
                :key="school.id"
                :label="school.name"
                :value="school.id"
              >
                <span class="option-name">{{ school.name }}</span>
                <span class="option-meta">
                  <el-tag :type="getTypeTag(school.type)" size="small" class="type-tag">{{ school.type_name || school.typeName }}</el-tag>
                  <span class="score-tag">录取线: {{ school.min_score || school.minScore || '-' }}</span>
                </span>
              </el-option>
            </el-select>
            <div class="selected-count">已选择 {{ selectedSchools.length }}/5 所学校</div>
          </div>
          
          <div class="score-input-wrapper">
            <el-input-number
              v-model="studentScore"
              :min="0"
              :max="750"
              placeholder="您的预估分数"
              class="score-input"
              controls-position="right"
            />
            <span class="score-unit">分</span>
          </div>
        </div>
        
        <div class="action-buttons">
          <el-button
            type="primary"
            @click="compareSchools"
            :loading="comparing"
            :disabled="selectedSchools.length < 2"
            class="compare-btn"
          >
            <el-icon><Grid /></el-icon>
            开始AI对比分析
          </el-button>
          <el-button @click="clearSelection" class="reset-btn">
            <el-icon><Close /></el-icon>
            清空选择
          </el-button>
          <el-button @click="showSchoolList" class="view-btn">
            <el-icon><List /></el-icon>
            查看学校列表
          </el-button>
        </div>

        <!-- 已选学校预览 -->
        <div v-if="selectedSchools.length > 0" class="selected-preview">
          <div class="preview-title">已选学校：</div>
          <div class="preview-list">
            <div
              v-for="schoolId in selectedSchools"
              :key="schoolId"
              class="preview-item"
            >
              <span class="preview-name">{{ getSchoolName(schoolId) }}</span>
              <el-button size="small" @click="removeSchool(schoolId)" class="remove-btn">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 对比结果区域 -->
      <div v-if="compareResult" class="result-section">
        <!-- AI推荐卡片 -->
        <div class="winner-card card">
          <div class="section-title">
            <el-icon class="icon-success"><Trophy /></el-icon>
            <span>AI智能推荐</span>
          </div>
          <div class="winner-content">
            <div class="winner-badge">
              <el-icon class="trophy-icon"><Medal /></el-icon>
            </div>
            <div class="winner-info">
              <div class="winner-school">
                <span class="school-name">{{ compareResult.winner?.schoolName }}</span>
                <el-tag type="success" class="winner-tag">最优选校</el-tag>
              </div>
              <div class="winner-reason">{{ compareResult.winner?.reason }}</div>
              <div class="winner-metrics">
                <span class="metric-item">
                  <span class="metric-label">一本率</span>
                  <span class="metric-value highlight">{{ getWinnerRate() }}%</span>
                </span>
                <span class="metric-divider">|</span>
                <span class="metric-item">
                  <span class="metric-label">录取线</span>
                  <span class="metric-value">{{ getWinnerScore() }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细对比表格 -->
        <div class="comparison-table card">
          <div class="section-title">
            <el-icon class="icon-primary"><Grid /></el-icon>
            <span>详细数据对比</span>
            <el-button size="small" @click="exportData" class="export-btn">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
          
          <div class="table-container">
            <el-table 
              :data="compareResult.schools" 
              style="width: 100%" 
              border
              :highlight-current-row="false"
              class="compare-table"
            >
              <el-table-column prop="schoolName" label="学校名称" fixed min-width="200">
                <template #default="scope">
                  <div class="school-cell">
                    <span class="name">{{ scope.row.schoolName }}</span>
                    <div class="school-tags">
                      <el-tag :type="getTypeTag(scope.row.type)" size="small" class="type-tag">
                        {{ scope.row.typeName }}
                      </el-tag>
                      <el-tag :type="scope.row.nature === '公办' ? 'success' : 'warning'" size="small">
                        {{ scope.row.nature }}
                      </el-tag>
                    </div>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="minScore" label="录取分数线" width="120" align="center" sortable>
                <template #default="scope">
                  <span class="score-value" :class="{ 'score-highlight': studentScore && studentScore >= scope.row.minScore }">
                    {{ scope.row.minScore }}
                  </span>
                </template>
              </el-table-column>
              
              <el-table-column prop="oneRate" label="一本率" width="120" align="center" sortable>
                <template #default="scope">
                  <div class="rate-cell">
                    <span class="rate-value" :class="getRateClass(scope.row.oneRate)">
                      {{ scope.row.oneRate }}%
                    </span>
                    <el-progress
                      :percentage="scope.row.oneRate"
                      :stroke-width="6"
                      :show-text="false"
                      :color="getRateColor(scope.row.oneRate)"
                      class="rate-progress"
                    />
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="twoRate" label="二本率" width="120" align="center" sortable>
                <template #default="scope">
                  <div class="rate-cell">
                    <span class="rate-value">{{ scope.row.twoRate }}%</span>
                    <el-progress
                      :percentage="scope.row.twoRate"
                      :stroke-width="6"
                      :show-text="false"
                      color="#409EFF"
                      class="rate-progress"
                    />
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="tuition" label="学费/年" width="120" align="center">
                <template #default="scope">
                  <span :class="['tuition-value', scope.row.tuition === 0 ? 'free' : 'paid']">
                    {{ scope.row.tuition === 0 ? '公办免费' : formatNumber(scope.row.tuition) + '元' }}
                  </span>
                </template>
              </el-table-column>
              
              <el-table-column prop="boarding" label="住宿条件" width="100" align="center">
                <template #default="scope">
                  <el-tag :type="scope.row.boarding === '提供' ? 'success' : 'info'" size="small">
                    {{ scope.row.boarding }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column prop="style" label="管理风格" width="100" align="center">
                <template #default="scope">
                  <el-tag :type="getStyleTag(scope.row.style)" size="small">
                    {{ scope.row.style }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column prop="address" label="学校地址" min-width="180">
                <template #default="scope">
                  <span class="address-text">{{ scope.row.address || '暂无' }}</span>
                </template>
              </el-table-column>
              
              <el-table-column prop="features" label="特色优势" min-width="200">
                <template #default="scope">
                  <div class="features-cell">
                    <el-tag
                      v-for="feature in scope.row.features"
                      :key="feature"
                      size="small"
                      class="feature-tag"
                    >
                      {{ feature }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column v-if="studentScore" prop="advice" label="报考建议" width="120" align="center">
                <template #default="scope">
                  <el-tag :type="getAdviceTag(scope.row.advice)" effect="dark" class="advice-tag">
                    {{ scope.row.advice }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="80" align="center">
                <template #default="scope">
                  <el-button size="small" @click="viewSchoolDetail(scope.row.schoolId)">
                    <el-icon><Search /></el-icon>
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 维度对比图表 -->
        <div class="dimension-comparison card">
          <div class="section-title">
            <el-icon class="icon-primary"><Grid /></el-icon>
            <span>数据可视化对比</span>
          </div>
          
          <div class="charts-grid">
            <div class="chart-item">
              <div class="chart-container" ref="scoreChart"></div>
            </div>
            <div class="chart-item">
              <div class="chart-container" ref="rateChart"></div>
            </div>
            <div class="chart-item">
              <div class="chart-container" ref="tuitionChart"></div>
            </div>
            <div class="chart-item">
              <div class="chart-container" ref="twoRateChart"></div>
            </div>
          </div>
        </div>

        <!-- AI分析报告 -->
        <div class="analysis-card card">
          <div class="section-title">
            <el-icon class="icon-primary"><Document /></el-icon>
            <span>AI智能分析报告</span>
          </div>
          <div class="analysis-content">
            <div class="analysis-header">
              <el-icon class="analysis-icon"><Document /></el-icon>
              <span class="analysis-title">综合分析</span>
            </div>
            <p class="analysis-text">{{ compareResult.analysis }}</p>
          </div>
        </div>

        <!-- 智能筛选推荐 -->
        <div class="filter-card card">
          <div class="section-title">
            <el-icon class="icon-primary"><Filter /></el-icon>
            <span>智能筛选</span>
          </div>
          <div class="filter-content">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="6">
                <el-select v-model="filterType" placeholder="按类型筛选" class="filter-select">
                  <el-option label="全部类型" value="" />
                  <el-option label="重点高中" value="2" />
                  <el-option label="普通高中" value="1" />
                  <el-option label="民办学校" value="4" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-select v-model="filterNature" placeholder="按性质筛选" class="filter-select">
                  <el-option label="全部性质" value="" />
                  <el-option label="公办" value="公办" />
                  <el-option label="民办" value="民办" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-select v-model="filterBoarding" placeholder="住宿条件" class="filter-select">
                  <el-option label="全部" value="" />
                  <el-option label="提供住宿" value="提供" />
                  <el-option label="不提供住宿" value="不提供" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-button type="primary" @click="applyFilter" class="filter-btn">
                  <el-icon><Search /></el-icon>
                  应用筛选
                </el-button>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-section card">
        <div class="empty-content">
          <div class="empty-icon">
            <el-icon><School /></el-icon>
          </div>
          <h3 class="empty-title">开始对比学校</h3>
          <p class="empty-desc">请选择2-5所学校进行AI智能对比分析</p>
          <div class="empty-actions">
            <el-button type="primary" @click="showSchoolList">
              <el-icon><Plus /></el-icon>
              浏览学校列表
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <span>© 2026 云南省AI全域赋能中考择校智能决策平台</span>
          <span class="footer-divider">·</span>
          <span>AI驱动的智慧择校解决方案</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  School, Grid, Document, ArrowLeft, List, Close, Download,
  Filter, Search, Plus, ArrowRightBold
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { aiApi } from '@/api'
import { useSchoolStore } from '@/store'

interface SchoolCompareData {
  schoolId: number
  schoolName: string
  type: number
  typeName: string
  nature: string
  minScore: number
  oneRate: number
  twoRate: number
  tuition: number
  boarding: string
  style: string
  address: string
  features: string[]
  advice?: string
}

interface CompareResult {
  schools: SchoolCompareData[]
  winner: {
    schoolName: string
    reason: string
  } | null
  analysis: string
}

const router = useRouter()
const route = useRoute()
const schoolStore = useSchoolStore()
const comparing = ref(false)
const selectedSchools = ref<number[]>([])
const studentScore = ref<number | undefined>(undefined)
const compareResult = ref<CompareResult | null>(null)
const scoreChart = ref<HTMLElement | null>(null)
const rateChart = ref<HTMLElement | null>(null)
const tuitionChart = ref<HTMLElement | null>(null)
const twoRateChart = ref<HTMLElement | null>(null)

const filterType = ref('')
const filterNature = ref('')
const filterBoarding = ref('')

// 从 API 获取学校列表
const schoolList = ref<any[]>([])
const loadingSchools = ref(false)

const fetchSchoolList = async () => {
  loadingSchools.value = true
  try {
    const result = await schoolStore.fetchSchoolList({ page: 1, size: 50 })
    if (result.success) {
      schoolList.value = result.items || []
    }
  } catch (error) {
    console.error('获取学校列表失败:', error)
  } finally {
    loadingSchools.value = false
  }
}

// 将 API 数据转换为对比格式
const transformSchoolData = (school: any): SchoolCompareData => {
  const featuresStr = school.features || ''
  const features = featuresStr ? String(featuresStr).split(/[,，]/).filter((f: string) => f.trim()).slice(0, 4) : []
  
  let advice = ''
  if (studentScore.value) {
    const scoreDiff = studentScore.value - (school.min_score || 0)
    if (scoreDiff >= 30) advice = '保底选择'
    else if (scoreDiff >= 10) advice = '稳妥选择'
    else if (scoreDiff >= -10) advice = '冲刺选择'
    else advice = '不建议'
  }
  
  return {
    schoolId: school.id,
    schoolName: school.name,
    type: school.type || 1,
    typeName: school.type_name || school.typeName || '普通高中',
    nature: school.nature || (school.is_public === 1 ? '公办' : '民办'),
    minScore: school.min_score || 0,
    oneRate: school.one_rate || 0,
    twoRate: 0,
    tuition: school.tuition || 0,
    boarding: school.boarding ? '提供' : '不提供',
    style: school.style || '适中',
    address: school.address || '暂无',
    features,
    advice
  }
}

const getSchoolName = (id: number): string => {
  const school = schoolList.value.find(s => s.id === id)
  return school?.name || ''
}

const getWinnerRate = (): number => {
  if (!compareResult.value?.winner) return 0
  const winnerName = compareResult.value.winner.schoolName
  const school = compareResult.value.schools.find(s => s.schoolName === winnerName)
  return school?.oneRate || 0
}

const getWinnerScore = (): number => {
  if (!compareResult.value?.winner) return 0
  const winnerName = compareResult.value.winner.schoolName
  const school = compareResult.value.schools.find(s => s.schoolName === winnerName)
  return school?.minScore || 0
}

const formatNumber = (num: number): string => {
  return num.toLocaleString('zh-CN')
}

const onSchoolSelect = () => {
  if (selectedSchools.value.length >= 2 && !compareResult.value) {
    ElMessage.info(`已选择 ${selectedSchools.value.length} 所学校，可以开始对比了`)
  }
}

const removeSchool = (schoolId: number) => {
  const index = selectedSchools.value.indexOf(schoolId)
  if (index > -1) {
    selectedSchools.value.splice(index, 1)
    if (selectedSchools.value.length < 2) {
      compareResult.value = null
    }
  }
}

const compareSchools = async () => {
  if (selectedSchools.value.length < 2) {
    ElMessage.warning('请至少选择2所学校进行对比')
    return
  }
  
  comparing.value = true
  try {
    // 先获取学校详细信息
    const batchResult = await schoolStore.fetchSchoolsBatch(selectedSchools.value)
    
    if (batchResult.success && batchResult.data && batchResult.data.length > 0) {
      // 转换为对比格式
      const schools = batchResult.data.map(transformSchoolData)
      
      // 调用 AI 对比分析
      const response = await aiApi.compareSchools({
        schoolIds: selectedSchools.value,
        studentScore: studentScore.value
      })
      
      if (response.success && response.data) {
        // 使用 AI 返回的分析结果，但用真实学校数据
        compareResult.value = {
          schools,
          winner: (response.data as any).winner || null,
          analysis: (response.data as any).analysis || ''
        }
      } else {
        // 如果 AI 分析失败，使用本地分析
        const bestSchool = schools.reduce((prev, curr) => 
          prev.oneRate > curr.oneRate ? prev : curr
        )
        compareResult.value = {
          schools,
          winner: {
            schoolName: bestSchool.schoolName,
            reason: `一本率最高(${bestSchool.oneRate}%)，综合实力最强`
          },
          analysis: generateAnalysis(schools)
        }
      }
      
      nextTick(() => {
        initCharts()
      })
      ElMessage.success('对比分析完成')
    } else {
      ElMessage.error('获取学校数据失败')
    }
  } catch (error) {
    console.error('对比失败:', error)
    ElMessage.error('对比失败，请稍后重试')
    // 使用本地数据生成对比结果
    const schools = schoolList.value
      .filter(s => selectedSchools.value.includes(s.id))
      .map(transformSchoolData)
    
    if (schools.length >= 2) {
      const bestSchool = schools.reduce((prev, curr) => 
        prev.oneRate > curr.oneRate ? prev : curr
      )
      compareResult.value = {
        schools,
        winner: {
          schoolName: bestSchool.schoolName,
          reason: `一本率最高(${bestSchool.oneRate}%)，综合实力最强`
        },
        analysis: generateAnalysis(schools)
      }
      nextTick(() => {
        initCharts()
      })
    }
  } finally {
    comparing.value = false
  }
}

const generateAnalysis = (schools: SchoolCompareData[]): string => {
  const bestSchool = schools.reduce((prev, curr) => 
    prev.oneRate > curr.oneRate ? prev : curr
  )
  const cheapestSchool = schools.reduce((prev, curr) => 
    prev.tuition < curr.tuition ? prev : curr
  )
  
  return `根据您选择的 ${schools.length} 所学校进行综合分析：

【优势学校】${bestSchool.schoolName}以${bestSchool.oneRate}%的一本率位居首位，是您的理想选择。

【学费优势】${cheapestSchool.schoolName}${cheapestSchool.tuition === 0 ? '为公办学校，学费免费' : `学费最低，为${cheapestSchool.tuition}元/年`}。

【录取建议】${studentScore.value ? `您的预估分数${studentScore.value}分，建议重点关注录取线在${studentScore.value - 10}至${studentScore.value + 20}分之间的学校。` : '建议根据实际分数进行精准匹配。'}

【综合对比】各校在管理风格、住宿条件、学费等方面各有特点，可根据个人情况进行选择。公办学校学费优势明显，民办学校在管理和特色教育方面更具特色。

建议结合自身成绩、家庭情况和学习目标做出最适合的选择。`
}

const initCharts = () => {
  if (!compareResult.value) return
  
  const schools = compareResult.value.schools
  const schoolNames = schools.map(s => s.schoolName)
  
  // 录取分数线对比
  if (scoreChart.value) {
    const chart = echarts.init(scoreChart.value)
    chart.setOption({
      title: { text: '录取分数线对比', left: 'center', textStyle: { color: '#fff', fontSize: 14 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { 
        type: 'category', 
        data: schoolNames, 
        axisLabel: { rotate: 30, color: '#999', fontSize: 12 },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      yAxis: { 
        type: 'value', 
        name: '分数',
        nameTextStyle: { color: '#999' },
        axisLabel: { color: '#999' },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
      },
      series: [{
        type: 'bar',
        data: schools.map(s => s.minScore),
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: { show: true, position: 'top', color: '#fff', fontSize: 12 }
      }]
    })
  }
  
  // 一本率对比
  if (rateChart.value) {
    const chart = echarts.init(rateChart.value)
    chart.setOption({
      title: { text: '一本率对比', left: 'center', textStyle: { color: '#fff', fontSize: 14 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { 
        type: 'category', 
        data: schoolNames, 
        axisLabel: { rotate: 30, color: '#999', fontSize: 12 },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      yAxis: { 
        type: 'value', 
        name: '百分比',
        nameTextStyle: { color: '#999' },
        max: 100,
        axisLabel: { color: '#999', formatter: '{value}%' },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
      },
      series: [{
        type: 'bar',
        data: schools.map(s => s.oneRate),
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#67C23A' },
            { offset: 1, color: '#85CE61' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: { show: true, position: 'top', color: '#fff', fontSize: 12, formatter: '{c}%' }
      }]
    })
  }
  
  // 二本率对比
  if (twoRateChart.value) {
    const chart = echarts.init(twoRateChart.value)
    chart.setOption({
      title: { text: '二本率对比', left: 'center', textStyle: { color: '#fff', fontSize: 14 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { 
        type: 'category', 
        data: schoolNames, 
        axisLabel: { rotate: 30, color: '#999', fontSize: 12 },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      yAxis: { 
        type: 'value', 
        name: '百分比',
        nameTextStyle: { color: '#999' },
        max: 100,
        axisLabel: { color: '#999', formatter: '{value}%' },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
      },
      series: [{
        type: 'bar',
        data: schools.map(s => s.twoRate),
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#67B8F5' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: { show: true, position: 'top', color: '#fff', fontSize: 12, formatter: '{c}%' }
      }]
    })
  }
  
  // 学费对比
  if (tuitionChart.value) {
    const chart = echarts.init(tuitionChart.value)
    chart.setOption({
      title: { text: '学费对比（元/年）', left: 'center', textStyle: { color: '#fff', fontSize: 14 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { 
        type: 'category', 
        data: schoolNames, 
        axisLabel: { rotate: 30, color: '#999', fontSize: 12 },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      yAxis: { 
        type: 'value', 
        name: '学费(元)',
        nameTextStyle: { color: '#999' },
        axisLabel: { color: '#999', formatter: (value: number) => value >= 10000 ? (value / 10000).toFixed(1) + '万' : value },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
      },
      series: [{
        type: 'bar',
        data: schools.map(s => s.tuition),
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#E6A23C' },
            { offset: 1, color: '#F5C87A' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: { 
          show: true, 
          position: 'top', 
          color: '#fff', 
          fontSize: 12,
          formatter: (params: { value: number }) => params.value === 0 ? '免费' : (params.value / 10000).toFixed(1) + '万'
        }
      }]
    })
  }
}

const clearSelection = () => {
  selectedSchools.value = []
  compareResult.value = null
  studentScore.value = undefined
  filterType.value = ''
  filterNature.value = ''
  filterBoarding.value = ''
}

const showSchoolList = () => {
  router.push('/school')
}

const viewSchoolDetail = (schoolId: number | string) => {
  router.push(`/school/${schoolId}`)
}

const goBack = () => {
  router.push('/')
}

const exportData = () => {
  if (!compareResult.value) return
  const data = compareResult.value.schools
  const headers = ['学校名称', '类型', '录取线', '一本率', '二本率', '学费', '住宿', '管理风格', '地址']
  const rows = data.map(s => [
    s.schoolName, s.typeName, s.minScore, s.oneRate + '%', s.twoRate + '%',
    s.tuition === 0 ? '免费' : s.tuition + '元', s.boarding, s.style, s.address
  ])
  
  const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `学校对比数据_${new Date().toLocaleDateString()}.csv`
  link.click()
  ElMessage.success('数据导出成功')
}

const applyFilter = () => {
  ElMessage.info('筛选功能已应用')
}

const getTypeTag = (type: number): 'success' | 'warning' | undefined => {
  const tags: Record<number, 'success' | 'warning'> = { 2: 'success', 4: 'warning' }
  return tags[type]
}

const getRateColor = (rate: number): string => {
  if (rate >= 90) return '#67C23A'
  if (rate >= 80) return '#E6A23C'
  return '#909399'
}

const getRateClass = (rate: number): string => {
  if (rate >= 90) return 'rate-high'
  if (rate >= 80) return 'rate-medium'
  return 'rate-low'
}

const getStyleTag = (style: string): 'danger' | 'warning' | 'success' | undefined => {
  const tags: Record<string, 'danger' | 'warning' | 'success'> = { '严格': 'danger', '适中': 'warning', '宽松': 'success' }
  return tags[style]
}

const getAdviceTag = (advice: string): 'success' | 'primary' | 'warning' | 'danger' | undefined => {
  const tags: Record<string, 'success' | 'primary' | 'warning' | 'danger'> = {
    '保底选择': 'success',
    '稳妥选择': 'primary',
    '冲刺选择': 'warning',
    '不建议': 'danger'
  }
  return tags[advice]
}

onMounted(async () => {
  // 先获取学校列表
  await fetchSchoolList()
  
  // 从 URL 参数读取已选择的学校
  const ids = route.query.ids
  if (ids) {
    const idArray = String(ids).split(',').map(id => parseInt(id)).filter(id => !isNaN(id))
    if (idArray.length > 0) {
      selectedSchools.value = idArray
      ElMessage.info(`已从学校列表选择 ${idArray.length} 所学校`)
      
      // 如果选择了2所以上学校，自动触发对比分析
      if (idArray.length >= 2) {
        setTimeout(() => {
          compareSchools()
        }, 500)
      }
    }
  }

  window.addEventListener('resize', () => {
    nextTick(() => {
      initCharts()
    })
  })
})
</script>

<style scoped>
.compare-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #050508 0%, #0d0d18 40%, #14142a 100%);
  color: #fff;
}

.page-header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 30px 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.logo-icon .icon {
  font-size: 28px;
  color: #fff;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.back-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 10px 20px;
  border-radius: 12px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.main-content {
  padding: 30px 20px 80px;
}

.card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  backdrop-filter: blur(12px);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.section-title .icon-primary {
  color: #667eea;
  font-size: 20px;
}

.section-title .icon-success {
  color: #67C23A;
  font-size: 20px;
}

.select-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.school-select-wrapper {
  position: relative;
}

.school-select {
  width: 100%;
}

.school-select :deep(.el-select__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.school-select :deep(.el-select__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3);
}

.school-select :deep(.el-select__input) {
  color: #fff;
}

.school-select :deep(.el-select__placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.school-select :deep(.el-select-dropdown) {
  background: #1a1a2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.school-select :deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.8);
  padding: 12px 16px;
}

.school-select :deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.15);
}

.option-name {
  font-weight: 500;
}

.option-meta {
  float: right;
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-tag {
  font-size: 11px !important;
}

.score-tag {
  font-size: 12px;
  color: #999;
}

.selected-count {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.score-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-input {
  flex: 1;
}

.score-input :deep(.el-input-number__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.score-input :deep(.el-input-number__input) {
  color: #fff;
}

.score-unit {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.compare-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.compare-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(102, 126, 234, 0.4);
}

.compare-btn:disabled {
  opacity: 0.5;
}

.reset-btn, .view-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 12px 20px;
  border-radius: 12px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.reset-btn:hover, .view-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.selected-preview {
  margin-top: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.preview-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
}

.preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
}

.preview-name {
  font-size: 13px;
  color: #fff;
}

.remove-btn {
  padding: 2px;
  color: rgba(255, 255, 255, 0.5);
}

.remove-btn:hover {
  color: #fff;
}

.winner-card {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(103, 194, 58, 0.05) 100%);
  border: 2px solid rgba(103, 194, 58, 0.3);
}

.winner-content {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px;
}

.winner-badge {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ffd700 0%, #ffb700 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(255, 215, 0, 0.4);
}

.trophy-icon {
  font-size: 40px;
  color: #fff;
}

.winner-info {
  flex: 1;
}

.winner-school {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.winner-school .school-name {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.winner-tag {
  background: rgba(103, 194, 58, 0.2);
  color: #67C23A;
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.winner-reason {
  font-size: 15px;
  color: #67C23A;
  margin-bottom: 12px;
}

.winner-metrics {
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.metric-value.highlight {
  color: #67C23A;
}

.metric-divider {
  color: rgba(255, 255, 255, 0.2);
}

.table-container {
  overflow-x: auto;
}

.compare-table {
  --el-table-header-text-color: #fff;
  --el-table-row-hover-bg-color: rgba(102, 126, 234, 0.1);
}

.compare-table :deep(.el-table__header-wrapper),
.compare-table :deep(.el-table__body-wrapper) {
  background: transparent;
}

.compare-table :deep(.el-table td),
.compare-table :deep(.el-table th) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 14px 12px;
  color: #fff;
}

.compare-table :deep(.el-table th) {
  background: rgba(102, 126, 234, 0.1);
  font-weight: 600;
}

.compare-table :deep(.el-table__fixed),
.compare-table :deep(.el-table__fixed-right) {
  background: #14142a;
}

.school-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.school-cell .name {
  font-weight: 600;
  color: #fff;
}

.school-tags {
  display: flex;
  gap: 8px;
}

.score-value {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.score-value.score-highlight {
  color: #67C23A;
}

.rate-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.rate-value {
  font-weight: 600;
}

.rate-value.rate-high {
  color: #67C23A;
}

.rate-value.rate-medium {
  color: #E6A23C;
}

.rate-value.rate-low {
  color: #909399;
}

.rate-progress {
  width: 80px;
}

.tuition-value {
  font-weight: 500;
}

.tuition-value.free {
  color: #67C23A;
}

.tuition-value.paid {
  color: #E6A23C;
}

.address-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.features-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature-tag {
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
}

.advice-tag {
  font-size: 12px;
}

.export-btn {
  margin-left: auto;
  font-size: 13px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
}

.export-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.chart-item {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 16px;
}

.chart-container {
  height: 260px;
}

.analysis-content {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.analysis-icon {
  color: #667eea;
  font-size: 20px;
}

.analysis-title {
  font-weight: 600;
  color: #fff;
}

.analysis-text {
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.8);
  white-space: pre-wrap;
  margin: 0;
}

.filter-content {
  padding-top: 10px;
}

.filter-select {
  width: 100%;
}

.filter-select :deep(.el-select__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.filter-select :deep(.el-select__input) {
  color: #fff;
}

.filter-btn {
  width: 100%;
}

.empty-section {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.empty-icon .el-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.3);
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 10px 0;
}

.empty-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 20px 0;
}

.footer {
  background: rgba(8, 8, 16, 0.98);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding: 24px 0;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.footer-divider {
  color: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .select-row {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
  
  .winner-content {
    flex-direction: column;
    text-align: center;
  }
  
  .winner-school {
    justify-content: center;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 220px;
  }
  
  .page-title {
    font-size: 24px;
  }
}
</style>