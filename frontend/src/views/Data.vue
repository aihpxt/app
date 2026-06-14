<template>
  <div class="data-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">数据中心</h1>
        <p class="page-desc">基于大数据和AI分析，为您提供中考择校数据洞察</p>
      </div>
    </div>

    <div class="container">
      <!-- 数据概览 -->
      <div class="data-overview">
        <div class="section-title">
          <el-icon><DataAnalysis /></el-icon>
          <span>平台数据概览</span>
        </div>
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div class="overview-card">
              <div class="overview-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                <el-icon><School /></el-icon>
              </div>
              <div class="overview-info">
                <div class="overview-value">{{ overviewData.schoolCount }}</div>
                <div class="overview-label">合作学校</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="overview-card">
              <div class="overview-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                <el-icon><User /></el-icon>
              </div>
              <div class="overview-info">
                <div class="overview-value">{{ overviewData.userCount }}</div>
                <div class="overview-label">注册用户</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="overview-card">
              <div class="overview-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-info">
                <div class="overview-value">{{ overviewData.predictionAccuracy }}</div>
                <div class="overview-label">预测准确率</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="overview-card">
              <div class="overview-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                <el-icon><Star /></el-icon>
              </div>
              <div class="overview-info">
                <div class="overview-value">{{ overviewData.satisfactionRate }}</div>
                <div class="overview-label">用户满意度</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 数据筛选 -->
      <div class="data-filter card">
        <div class="section-title">
          <el-icon><Filter /></el-icon>
          <span>数据筛选</span>
        </div>
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="州市">
            <el-select v-model="filterForm.city" placeholder="选择州市" clearable>
              <el-option label="全部" value="" />
              <el-option
                v-for="city in cityList"
                :key="city"
                :label="city"
                :value="city"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="学校类型">
            <el-select v-model="filterForm.type" placeholder="选择学校类型" clearable>
              <el-option label="全部" value="" />
              <el-option label="重点高中" :value="2" />
              <el-option label="普通高中" :value="1" />
              <el-option label="中职学校" :value="3" />
              <el-option label="民办学校" :value="4" />
            </el-select>
          </el-form-item>
          <el-form-item label="年份">
            <el-select v-model="filterForm.year" placeholder="选择年份" clearable>
              <el-option label="2026" :value="2026" />
              <el-option label="2025" :value="2025" />
              <el-option label="2024" :value="2024" />
              <el-option label="2023" :value="2023" />
              <el-option label="2022" :value="2022" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilter">
              <el-icon><Search /></el-icon>应用筛选
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><Refresh /></el-icon>重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据图表 -->
      <div class="charts-section">
        <div class="section-title">
          <el-icon><PieChart /></el-icon>
          <span>数据可视化分析</span>
        </div>
        <el-row :gutter="20">
          <!-- 各州市学校分布 -->
          <el-col :xs="24" :md="12">
            <div class="chart-card">
              <div class="chart-header">
                <h4>各州市学校分布</h4>
              </div>
              <div ref="schoolDistributionChart" class="chart-container"></div>
            </div>
          </el-col>
          <!-- 历年录取分数趋势 -->
          <el-col :xs="24" :md="12">
            <div class="chart-card">
              <div class="chart-header">
                <h4>历年录取分数趋势</h4>
              </div>
              <div ref="scoreTrendChart" class="chart-container"></div>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 20px;">
          <!-- 学校类型分布 -->
          <el-col :xs="24" :md="12">
            <div class="chart-card">
              <div class="chart-header">
                <h4>学校类型分布</h4>
              </div>
              <div ref="schoolTypeChart" class="chart-container"></div>
            </div>
          </el-col>
          <!-- 用户增长趋势 -->
          <el-col :xs="24" :md="12">
            <div class="chart-card">
              <div class="chart-header">
                <h4>用户增长趋势</h4>
              </div>
              <div ref="userGrowthChart" class="chart-container"></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 热门学校排名 -->
      <div class="hot-schools-section card">
        <div class="section-title">
          <el-icon><Medal /></el-icon>
          <span>热门学校排名</span>
        </div>
        <el-table :data="hotSchools" style="width: 100%">
          <el-table-column type="index" label="排名" width="80" />
          <el-table-column prop="name" label="学校名称" min-width="150">
            <template #default="scope">
              <div class="school-name-cell">
                <span class="school-name">{{ scope.row.name }}</span>
                <el-tag :type="getTypeTag(scope.row.type)" size="small">
                  {{ getTypeName(scope.row.type) }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="city" label="所在州市" width="120" />
          <el-table-column prop="avgScore" label="平均分" width="100" />
          <el-table-column prop="rank" label="排名变化" width="100">
            <template #default="scope">
              <span :class="getRankClass(scope.row.rankChange)">
                {{ scope.row.rankChange > 0 ? '↑' : scope.row.rankChange < 0 ? '↓' : '—' }}
                {{ Math.abs(scope.row.rankChange) || 0 }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="viewCount" label="浏览量" width="100" />
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button type="primary" size="small" text @click="viewSchoolDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 数据导出 -->
      <div class="data-export card">
        <div class="section-title">
          <el-icon><Download /></el-icon>
          <span>数据导出</span>
        </div>
        <div class="export-buttons">
          <el-button type="primary" @click="exportData('school')">
            <el-icon><Document /></el-icon>导出学校数据
          </el-button>
          <el-button type="success" @click="exportData('score')">
            <el-icon><Document /></el-icon>导出分数数据
          </el-button>
          <el-button type="info" @click="exportData('policy')">
            <el-icon><Document /></el-icon>导出政策数据
          </el-button>
          <el-button type="warning" @click="exportData('report')">
            <el-icon><Document /></el-icon>导出分析报告
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, Filter, Search, Refresh, PieChart,
  School, User, TrendCharts, Star, Medal, Download, Document
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { cityList } from '../utils'

export default {
  name: 'Data',
  components: {
    DataAnalysis, Filter, Search, Refresh, PieChart,
    School, User, TrendCharts, Star, Medal, Download, Document
  },
  setup() {
    const router = useRouter()
    
    // 图表引用
    const schoolDistributionChart = ref(null)
    const scoreTrendChart = ref(null)
    const schoolTypeChart = ref(null)
    const userGrowthChart = ref(null)

    // 数据
    const overviewData = reactive({
      schoolCount: '1,256',
      userCount: '128,560',
      predictionAccuracy: '95.2%',
      satisfactionRate: '92.8%'
    })

    const filterForm = reactive({
      city: '',
      type: '',
      year: ''
    })

    const hotSchools = ref([
      { id: 1, name: '云南省第一中学', type: 2, city: '昆明市', avgScore: 680, rankChange: 0, viewCount: 12580 },
      { id: 2, name: '昆明市第二中学', type: 2, city: '昆明市', avgScore: 675, rankChange: -1, viewCount: 11250 },
      { id: 3, name: '曲靖市第一中学', type: 2, city: '曲靖市', avgScore: 670, rankChange: 1, viewCount: 9860 },
      { id: 4, name: '玉溪市第一中学', type: 2, city: '玉溪市', avgScore: 665, rankChange: 0, viewCount: 8750 },
      { id: 5, name: '昆明市第三中学', type: 2, city: '昆明市', avgScore: 660, rankChange: 2, viewCount: 7680 }
    ])

    const typeMap = {
      1: '普通高中',
      2: '重点高中',
      3: '中职学校',
      4: '民办学校'
    }

    const tagMap = {
      1: '',
      2: 'success',
      3: 'warning',
      4: 'info'
    }

    const getTypeName = (type) => typeMap[type] || '未知'
    const getTypeTag = (type) => tagMap[type] || ''

    const getRankClass = (change) => {
      if (change > 0) return 'rank-up'
      if (change < 0) return 'rank-down'
      return 'rank-stable'
    }

    const applyFilter = () => {
      ElMessage.success('筛选条件已应用')
      initCharts()
    }

    const resetFilter = () => {
      filterForm.city = ''
      filterForm.type = ''
      filterForm.year = ''
      ElMessage.success('筛选条件已重置')
      initCharts()
    }

    const viewSchoolDetail = (school) => {
      router.push(`/school/${school.id}`)
    }

    const exportData = (type) => {
      const typeMap = {
        school: '学校数据',
        score: '分数数据',
        policy: '政策数据',
        report: '分析报告'
      }
      ElMessage.success(`开始导出${typeMap[type]}`)
    }

    const initCharts = () => {
      nextTick(() => {
        initSchoolDistributionChart()
        initScoreTrendChart()
        initSchoolTypeChart()
        initUserGrowthChart()
      })
    }

    const initSchoolDistributionChart = () => {
      if (!schoolDistributionChart.value) return
      
      const chart = echarts.init(schoolDistributionChart.value)
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['昆明市', '曲靖市', '玉溪市', '保山市', '其他州市']
        },
        series: [
          {
            name: '学校分布',
            type: 'pie',
            radius: '60%',
            center: ['50%', '50%'],
            data: [
              { value: 350, name: '昆明市' },
              { value: 220, name: '曲靖市' },
              { value: 180, name: '玉溪市' },
              { value: 150, name: '保山市' },
              { value: 356, name: '其他州市' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      chart.setOption(option)
    }

    const initScoreTrendChart = () => {
      if (!scoreTrendChart.value) return
      
      const chart = echarts.init(scoreTrendChart.value)
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['重点高中', '普通高中', '中职学校']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: ['2022', '2023', '2024', '2025', '2026']
        },
        yAxis: {
          type: 'value',
          name: '平均分'
        },
        series: [
          {
            name: '重点高中',
            type: 'line',
            data: [650, 655, 660, 670, 675],
            smooth: true
          },
          {
            name: '普通高中',
            type: 'line',
            data: [580, 585, 590, 595, 600],
            smooth: true
          },
          {
            name: '中职学校',
            type: 'line',
            data: [500, 510, 520, 530, 540],
            smooth: true
          }
        ]
      }
      chart.setOption(option)
    }

    const initSchoolTypeChart = () => {
      if (!schoolTypeChart.value) return
      
      const chart = echarts.init(schoolTypeChart.value)
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: ['重点高中', '普通高中', '中职学校', '民办学校']
        },
        series: [
          {
            name: '学校数量',
            type: 'bar',
            data: [156, 680, 320, 100],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#667eea' },
                { offset: 1, color: '#764ba2' }
              ])
            }
          }
        ]
      }
      chart.setOption(option)
    }

    const initUserGrowthChart = () => {
      if (!userGrowthChart.value) return
      
      const chart = echarts.init(userGrowthChart.value)
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        },
        yAxis: {
          type: 'value',
          name: '用户数'
        },
        series: [
          {
            name: '注册用户',
            type: 'line',
            data: [5000, 8000, 12000, 15000, 20000, 35000, 45000, 60000, 80000, 100000, 115000, 128560],
            smooth: true,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                { offset: 1, color: 'rgba(118, 75, 162, 0.1)' }
              ])
            }
          }
        ]
      }
      chart.setOption(option)
    }

    onMounted(() => {
      initCharts()
    })

    return {
      schoolDistributionChart,
      scoreTrendChart,
      schoolTypeChart,
      userGrowthChart,
      overviewData,
      filterForm,
      hotSchools,
      cityList,
      getTypeName,
      getTypeTag,
      getRankClass,
      applyFilter,
      resetFilter,
      viewSchoolDetail,
      exportData
    }
  }
}
</script>

<style scoped>
.data-page {
  min-height: 100%;
  background: var(--bg-secondary);
}

.page-header {
  background: var(--primary-gradient);
  color: var(--text-primary);
  padding: 40px 0;
  margin-bottom: 30px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 10px;
  border: none;
  padding: 0;
  color: var(--text-primary);
}

.page-desc {
  font-size: 16px;
  opacity: 0.9;
  color: var(--text-secondary);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.section-title .el-icon {
  font-size: 20px;
  color: #409EFF;
}

/* 数据概览 */
.data-overview {
  margin-bottom: 30px;
}

.overview-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
  backdrop-filter: blur(10px);
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.3);
}

.overview-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.overview-info {
  flex: 1;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.overview-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 数据筛选 */
.data-filter {
  margin-bottom: 30px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  padding: 20px;
  height: 400px;
  backdrop-filter: blur(10px);
}

.chart-header {
  margin-bottom: 20px;
}

.chart-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.chart-container {
  height: calc(100% - 40px);
}

/* 热门学校排名 */
.hot-schools-section {
  margin-bottom: 30px;
}

.school-name-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.school-name {
  font-weight: 600;
  color: var(--text-primary);
}

.rank-up {
  color: #67C23A;
  font-weight: bold;
}

.rank-down {
  color: #F56C6C;
  font-weight: bold;
}

.rank-stable {
  color: #909399;
}

/* 数据导出 */
.data-export {
  margin-bottom: 30px;
}

.export-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .overview-card {
    flex-direction: column;
    text-align: center;
    padding: 30px;
  }

  .filter-form {
    flex-direction: column;
    align-items: stretch;
  }

  .chart-card {
    height: 300px;
  }

  .export-buttons {
    flex-direction: column;
  }

  .export-buttons .el-button {
    width: 100%;
  }
}
</style>
