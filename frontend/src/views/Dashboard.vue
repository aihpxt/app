<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">数据仪表盘</h1>
        <p class="page-desc">全面掌握你的升学数据和学习进度</p>
      </div>
    </div>

    <div class="container">
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8">
            <div class="stat-card card">
              <div class="stat-icon score">
                <el-icon><BellFilled /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ userScore }}</div>
                <div class="stat-label">预估分数</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="stat-card card">
              <div class="stat-icon school">
                <el-icon><School /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ matchedSchools }}</div>
                <div class="stat-label">匹配学校数</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="stat-card card">
              <div class="stat-icon practice">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ practiceCount }}</div>
                <div class="stat-label">演练次数</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <div class="charts-section">
        <el-row :gutter="20">
          <el-col :xs="24" :lg="12">
            <div class="chart-card card">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>成绩趋势</span>
              </div>
              <div id="scoreChart" class="chart-container"></div>
            </div>
          </el-col>
          <el-col :xs="24" :lg="12">
            <div class="chart-card card">
              <div class="section-title">
                <el-icon><PieChart /></el-icon>
                <span>学校类型分布</span>
              </div>
              <div id="schoolTypeChart" class="chart-container"></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <div class="recommendations-section">
        <div class="card">
          <div class="section-title">
            <el-icon><Star /></el-icon>
            <span>推荐学校</span>
          </div>
          <div class="recommendation-list">
            <div v-for="school in recommendedSchools" :key="school.id" class="recommendation-item">
              <div class="school-info">
                <div class="school-name">{{ school.name }}</div>
                <div class="school-tag">
                  <el-tag size="small" :type="getMatchType(school.matchType)">
                    {{ getMatchTypeText(school.matchType) }}
                  </el-tag>
                </div>
              </div>
              <div class="match-info">
                <div class="match-score">
                  <span class="score-text">{{ school.matchScore }}%</span>
                  <span class="score-label">匹配度</span>
                </div>
                <el-button type="primary" size="small" @click="goToSchoolDetail(school.id)">
                  查看详情
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="activity-section">
        <div class="card">
          <div class="section-title">
            <el-icon><Timer /></el-icon>
            <span>最近活动</span>
          </div>
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :type="activity.type"
              :timestamp="activity.time"
            >
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-desc">{{ activity.description }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  BellFilled, School, DataAnalysis, TrendCharts, 
  PieChart, Star, Timer 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useRouter } from 'vue-router'

export default {
  name: 'Dashboard',
  components: {
    BellFilled, School, DataAnalysis, TrendCharts,
    PieChart, Star, Timer
  },
  setup() {
    const router = useRouter()
    const userScore = ref(650)
    const matchedSchools = ref(12)
    const practiceCount = ref(5)
    const scoreChart = ref(null)
    const schoolTypeChart = ref(null)

    const recommendedSchools = ref([
      { id: 1, name: '云南师范大学附属中学', matchType: 'excellent', matchScore: 95 },
      { id: 2, name: '昆明市第一中学', matchType: 'good', matchScore: 88 },
      { id: 3, name: '昆明市第三中学', matchType: 'good', matchScore: 85 },
      { id: 4, name: '云南大学附属中学', matchType: 'good', matchScore: 82 },
      { id: 5, name: '昆明市第八中学', matchType: 'average', matchScore: 78 }
    ])

    const recentActivities = ref([
      {
        title: '完成了AI智能择校分析',
        description: '分析了你的成绩和排名，为你推荐了10所匹配学校',
        type: 'success',
        time: '2026-01-15 14:30'
      },
      {
        title: '进行了志愿填报演练',
        description: '完成了3次模拟演练，生成了3套志愿方案',
        type: 'info',
        time: '2026-01-14 10:20'
      },
      {
        title: '查看了学校详情',
        description: '浏览了昆明市第一中学的详细信息和录取数据',
        type: 'primary',
        time: '2026-01-13 16:45'
      },
      {
        title: '使用了分数预测功能',
        description: '基于模考成绩，预测了你的中考分数范围',
        type: 'warning',
        time: '2026-01-12 09:15'
      }
    ])

    const scoreData = [
      { name: '1月', value: 620 },
      { name: '2月', value: 635 },
      { name: '3月', value: 642 },
      { name: '4月', value: 650 },
      { name: '5月', value: 655 },
      { name: '6月', value: 660 }
    ]

    const schoolTypeData = [
      { name: '省级示范', value: 5 },
      { name: '市级示范', value: 8 },
      { name: '普通中学', value: 12 }
    ]

    const getMatchType = (type) => {
      const types = { excellent: 'success', good: 'warning', average: 'info' }
      return types[type] || 'info'
    }

    const getMatchTypeText = (type) => {
      const texts = { excellent: '非常匹配', good: '比较匹配', average: '一般匹配' }
      return texts[type] || '一般匹配'
    }

    const goToSchoolDetail = (id) => {
      router.push(`/school/detail/${id}`)
    }

    const initScoreChart = () => {
      const chartDom = document.getElementById('scoreChart')
      if (chartDom) {
        scoreChart.value = echarts.init(chartDom)
        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              label: {
                backgroundColor: '#6a7985'
              }
            }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: [
            {
              type: 'category',
              boundaryGap: false,
              data: scoreData.map(item => item.name)
            }
          ],
          yAxis: [
            {
              type: 'value',
              min: 0,
              max: 700
            }
          ],
          series: [
            {
              name: '分数',
              type: 'line',
              stack: 'Total',
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
                  { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
                ])
              },
              emphasis: {
                focus: 'series'
              },
              data: scoreData.map(item => item.value)
            }
          ]
        }
        scoreChart.value.setOption(option)
      }
    }

    const initSchoolTypeChart = () => {
      const chartDom = document.getElementById('schoolTypeChart')
      if (chartDom) {
        schoolTypeChart.value = echarts.init(chartDom)
        const option = {
          tooltip: {
            trigger: 'item'
          },
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          series: [
            {
              name: '学校类型',
              type: 'pie',
              radius: '50%',
              data: schoolTypeData,
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
        schoolTypeChart.value.setOption(option)
      }
    }

    const handleResize = () => {
      scoreChart.value?.resize()
      schoolTypeChart.value?.resize()
    }

    onMounted(() => {
      initScoreChart()
      initSchoolTypeChart()
      window.addEventListener('resize', handleResize)
    })

    return {
      userScore,
      matchedSchools,
      practiceCount,
      recommendedSchools,
      recentActivities,
      getMatchType,
      getMatchTypeText,
      goToSchoolDetail
    }
  }
}
</script>

<style scoped>
.dashboard-page {
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
  color: var(--text-primary);
}

.page-desc {
  font-size: 16px;
  opacity: 0.9;
  color: var(--text-secondary);
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(10px);
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
  color: #409eff;
}

.stats-section {
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.3);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-icon.score {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.school {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.practice {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 5px;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.recommendation-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-sm);
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.school-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.match-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.match-score {
  text-align: center;
}

.score-text {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.activity-content {
  min-width: 300px;
}

.activity-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.activity-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
    padding: 30px 20px;
  }

  .recommendation-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .match-info {
    width: 100%;
    justify-content: space-between;
  }

  .chart-container {
    height: 250px;
  }
}
</style>