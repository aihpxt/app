<template>
  <div class="campus-events-page">
    <div class="page-header">
      <h1 class="page-title">校园活动日历</h1>
      <p class="page-subtitle">了解昆明市各高中重要活动，提前规划参与</p>
    </div>

    <div class="events-container">
      <div class="filter-section">
        <el-card class="filter-card">
          <div class="filter-controls">
            <div class="filter-item">
              <label>年份</label>
              <el-select v-model="selectedYear" @change="loadEvents">
                <el-option
                  v-for="year in years"
                  :key="year"
                  :label="year"
                  :value="year"
                />
              </el-select>
            </div>
            <div class="filter-item">
              <label>月份</label>
              <el-select v-model="selectedMonth" @change="loadEvents" clearable placeholder="全部月份">
                <el-option
                  v-for="month in months"
                  :key="month.value"
                  :label="month.label"
                  :value="month.value"
                />
              </el-select>
            </div>
            <div class="filter-item">
              <label>活动类型</label>
              <el-select v-model="selectedType" @change="filterEvents" clearable placeholder="全部类型">
                <el-option
                  v-for="type in eventTypes"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
                />
              </el-select>
            </div>
            <div class="filter-item">
              <label>学校</label>
              <el-select v-model="selectedSchool" @change="filterEvents" clearable placeholder="全部学校">
                <el-option
                  v-for="school in schools"
                  :key="school"
                  :label="school"
                  :value="school"
                />
              </el-select>
            </div>
          </div>
        </el-card>
      </div>

      <div class="events-stats" v-if="monthStats">
        <el-card class="stats-card">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number">{{ totalEvents }}</div>
              <div class="stat-label">总活动数</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ monthStats.academic || 0 }}</div>
              <div class="stat-label">学术活动</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ monthStats.sports || 0 }}</div>
              <div class="stat-label">体育活动</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ monthStats.cultural || 0 }}</div>
              <div class="stat-label">文化活动</div>
            </div>
          </div>
        </el-card>
      </div>

      <div class="events-list" v-loading="loading">
        <div v-if="filteredEvents.length === 0" class="empty-state">
          <el-empty description="暂无符合条件的活动" />
        </div>
        <div v-else class="events-grid">
          <template v-for="event in filteredEvents" :key="event.eventId">
            <el-card
              v-if="event && typeof event === 'object' && event.type"
              class="event-card"
              :class="`event-type-${event.type}`"
            >
              <div class="event-date">
                <div class="event-month">{{ event.month }}月</div>
                <div class="event-day">{{ event.day }}</div>
              </div>
              <div class="event-content">
                <div class="event-header">
                  <h3 class="event-title">{{ event.title }}</h3>
                  <el-tag :type="getEventTypeColor(event.type)" size="small">
                    {{ getEventTypeName(event.type) }}
                  </el-tag>
                </div>
                <div class="event-info">
                  <div class="info-item">
                    <el-icon><Clock /></el-icon>
                    <span>{{ event.time }}</span>
                  </div>
                  <div class="info-item">
                    <el-icon><Location /></el-icon>
                    <span>{{ event.location }}</span>
                  </div>
                  <div class="info-item">
                    <el-icon><School /></el-icon>
                    <span>{{ event.schoolName }}</span>
                  </div>
                </div>
                <p class="event-description">{{ event.description }}</p>
                <div class="event-footer">
                  <el-button
                    v-if="event.registrationRequired"
                    type="primary"
                    size="small"
                    @click="handleRegister(event)"
                  >
                    立即报名
                  </el-button>
                  <el-button
                    v-else
                    size="small"
                    @click="handleViewDetails(event)"
                  >
                    查看详情
                  </el-button>
                </div>
              </div>
            </el-card>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Location, School } from '@element-plus/icons-vue'
import { aiApi } from '@/api'

export default {
  name: 'CampusEvents',
  components: {
    Clock,
    Location,
    School
  },
  setup() {
    const loading = ref(false)
    const events = ref([])
    const selectedYear = ref(2026)
    const selectedMonth = ref(null)
    const selectedType = ref(null)
    const selectedSchool = ref(null)
    const showDetailDialog = ref(false)
    const selectedEvent = ref(null)

    const years = [2025, 2026, 2027]
    const months = [
      { label: '1月', value: 1 },
      { label: '2月', value: 2 },
      { label: '3月', value: 3 },
      { label: '4月', value: 4 },
      { label: '5月', value: 5 },
      { label: '6月', value: 6 },
      { label: '7月', value: 7 },
      { label: '8月', value: 8 },
      { label: '9月', value: 9 },
      { label: '10月', value: 10 },
      { label: '11月', value: 11 },
      { label: '12月', value: 12 }
    ]

    const eventTypes = [
      { label: '学术活动', value: 'academic' },
      { label: '体育活动', value: 'sports' },
      { label: '文化活动', value: 'cultural' },
      { label: '其他活动', value: 'other' }
    ]

    const monthStats = computed(() => {
      if (!selectedMonth.value) return null
      const monthKey = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}`
      return statsData.value[monthKey] || null
    })

    const totalEvents = computed(() => {
      return monthStats.value ? monthStats.value.total : 0
    })

    const statsData = ref({})

    const filteredEvents = computed(() => {
      // 确保events.value是数组
      const eventsArray = Array.isArray(events.value) ? events.value : []
      
      // 过滤掉无效的event对象，并确保每个event对象都有type属性
      let result = eventsArray.filter(event => {
        return event && typeof event === 'object' && event.type
      })

      if (selectedType.value) {
        result = result.filter(event => event.type === selectedType.value)
      }

      if (selectedSchool.value) {
        result = result.filter(event => event.schoolName === selectedSchool.value)
      }

      return result
    })

    const schools = computed(() => {
      const schoolSet = new Set((events.value || []).map(event => event?.schoolName).filter(Boolean))
      return Array.from(schoolSet).sort()
    })

    const loadEvents = async () => {
      loading.value = true
      try {
        const params = {
          year: selectedYear.value
        }
        if (selectedMonth.value) {
          params.month = selectedMonth.value
        }

        const response = await aiApi.getCampusEventsCalendar(params)
        // 确保events.value始终是一个数组
        if (response && response.data && Array.isArray(response.data.events)) {
          events.value = response.data.events
        } else {
          events.value = []
        }
        statsData.value = response?.data?.monthStats || {}
      } catch (error) {
        ElMessage.error('加载活动数据失败')
        // 发生错误时，确保events.value是一个空数组
        events.value = []
        statsData.value = {}
      } finally {
        loading.value = false
      }
    }

    const filterEvents = () => {
      // 筛选逻辑通过computed属性自动处理
    }

    const getEventTypeColor = (type) => {
      const colorMap = {
        'academic': 'primary',
        'sports': 'success',
        'cultural': 'warning',
        'other': 'info'
      }
      return colorMap[type] || 'info'
    }

    const getEventTypeName = (type) => {
      const nameMap = {
        'academic': '学术活动',
        'sports': '体育活动',
        'cultural': '文化活动',
        'other': '其他活动'
      }
      return nameMap[type] || '其他活动'
    }

    const handleViewDetails = (event) => {
      selectedEvent.value = event
      showDetailDialog.value = true
    }

    const handleRegister = (event) => {
      ElMessage.success(`报名成功！我们将尽快联系您确认${event.title}的参与信息。`)
      showDetailDialog.value = false
    }

    onMounted(() => {
      loadEvents()
    })

    return {
      loading,
      events,
      selectedYear,
      selectedMonth,
      selectedType,
      selectedSchool,
      showDetailDialog,
      selectedEvent,
      years,
      months,
      eventTypes,
      monthStats,
      totalEvents,
      filteredEvents,
      schools,
      loadEvents,
      filterEvents,
      getEventTypeColor,
      getEventTypeName,
      handleViewDetails,
      handleRegister
    }
  }
}
</script>

<style scoped>
.campus-events-page {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-secondary);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  background: var(--primary-gradient);
  color: var(--text-primary);
  padding: 40px 0;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
}

.events-container {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-card {
  border-radius: 8px;
}

.filter-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 14px;
}

.events-stats {
  margin-bottom: 20px;
}

.stats-card {
  border-radius: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.events-list {
  min-height: 400px;
}

.empty-state {
  padding: 60px 0;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.event-card {
  border-radius: 8px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  cursor: pointer;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(10px);
}

.event-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.3);
}

.event-type-academic {
  border-left: 4px solid #409EFF;
}

.event-type-sports {
  border-left: 4px solid #67C23A;
}

.event-type-cultural {
  border-left: 4px solid #E6A23C;
}

.event-type-other {
  border-left: 4px solid #909399;
}

.event-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.event-month {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 5px;
}

.event-day {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.event-content {
  flex: 1;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.event-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
  margin-right: 10px;
}

.event-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: var(--text-secondary);
}

.event-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 15px;
  min-height: 60px;
}

.event-footer {
  display: flex;
  justify-content: flex-end;
}

.event-detail .detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.event-detail .detail-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--text-primary);
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  display: flex;
  gap: 10px;
}

.detail-item strong {
  min-width: 80px;
  color: var(--text-primary);
}

.detail-item span,
.detail-item p {
  flex: 1;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .events-grid {
    grid-template-columns: 1fr;
  }

  .filter-controls {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>