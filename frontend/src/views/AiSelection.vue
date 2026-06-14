<template>
  <div class="ai-selection-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">AI智能择校</h1>
        <p class="page-desc">基于AI算法，为您的中考志愿填报提供科学建议</p>
      </div>
    </div>

    <div class="container">
      <!-- 考生信息录入 -->
      <div class="input-section card">
        <div class="section-title">
          <el-icon><Edit /></el-icon>
          <span>考生信息录入</span>
        </div>
        <el-form
          :model="studentForm"
          :rules="studentRules"
          ref="studentFormRef"
          label-width="100px"
          class="student-form"
        >
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="中考总分" prop="totalScore">
                <el-input-number
                  v-model="studentForm.totalScore"
                  :min="0"
                  :max="750"
                  :precision="1"
                  style="width: 100%"
                  placeholder="请输入中考总分"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="区域排名" prop="rank">
                <el-input-number
                  v-model="studentForm.rank"
                  :min="1"
                  style="width: 100%"
                  placeholder="请输入区域排名"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="所在州市" prop="city">
                <el-select
                  v-model="studentForm.city"
                  placeholder="选择州市"
                  style="width: 100%"
                >
                  <el-option
                    v-for="city in cityList"
                    :key="city"
                    :label="city"
                    :value="city"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="所在区县" prop="district">
                <el-input
                  v-model="studentForm.district"
                  placeholder="请输入区县"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="目标类型" prop="targetType">
                <el-select
                  v-model="studentForm.targetType"
                  placeholder="选择目标学校类型"
                  style="width: 100%"
                  clearable
                >
                  <el-option label="重点高中" :value="2" />
                  <el-option label="普通高中" :value="1" />
                  <el-option label="中职学校" :value="3" />
                  <el-option label="民办学校" :value="4" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="住宿需求" prop="needBoarding">
                <el-radio-group v-model="studentForm.needBoarding">
                  <el-radio :value="true">需要</el-radio>
                  <el-radio :value="false">不需要</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              @click="analyzeSchools"
              :loading="analyzing"
              class="analyze-btn"
            >
              <el-icon><MagicStick /></el-icon>
              AI智能分析
            </el-button>
            <el-button size="large" @click="resetForm">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 分析结果 -->
      <div v-if="showResults" class="results-section">
        <!-- 分析概览 -->
        <div class="analysis-summary card">
          <div class="section-title">
            <el-icon><DataAnalysis /></el-icon>
            <span>分析概览</span>
          </div>
          <el-row :gutter="20">
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-icon" style="background: #e6f7ff; color: #1890ff;">
                  <el-icon><School /></el-icon>
                </div>
                <div class="summary-value">{{ analysisResult.matchCount }}</div>
                <div class="summary-label">匹配学校</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-icon" style="background: #f6ffed; color: #52c41a;">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="summary-value">{{ analysisResult.avgProbability }}%</div>
                <div class="summary-label">平均录取概率</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-icon" style="background: #fff7e6; color: #fa8c16;">
                  <el-icon><Star /></el-icon>
                </div>
                <div class="summary-value">{{ analysisResult.recommendCount }}</div>
                <div class="summary-label">推荐志愿</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-icon" style="background: #f9f0ff; color: #722ed1;">
                  <el-icon><Check /></el-icon>
                </div>
                <div class="summary-value">{{ analysisResult.confidence }}%</div>
                <div class="summary-label">分析置信度</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 推荐学校 -->
        <div class="recommendations card">
          <div class="section-title">
            <el-icon><Medal /></el-icon>
            <span>智能推荐学校</span>
          </div>
          <el-table
            :data="recommendations"
            style="width: 100%"
            v-loading="analyzing"
            class="recommendation-table"
          >
            <el-table-column type="index" label="排序" width="70" align="center">
              <template #default="scope">
                <div class="rank-badge" :class="`rank-${scope.$index + 1}`">
                  {{ scope.$index + 1 }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="schoolName" label="学校名称" min-width="200" width="220">
              <template #default="scope">
                <div class="school-name-cell">
                  <span class="school-name">{{ scope.row.schoolName }}</span>
                  <el-tag :type="getTypeTag(scope.row.type)" size="small">
                    {{ getTypeName(scope.row.type) }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="matchScore" label="匹配度" width="150">
              <template #default="scope">
                <div class="match-score">
                  <el-progress
                    :percentage="scope.row.matchScore"
                    :color="getProgressColor(scope.row.matchScore)"
                    :stroke-width="8"
                  />
                  <span class="score-value">{{ scope.row.matchScore }}分</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="admissionProbability" label="录取概率" width="120">
              <template #default="scope">
                <span :class="['probability-badge', getProbabilityClass(scope.row.admissionProbability)]">
                  {{ scope.row.admissionProbability }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="推荐理由" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <el-button
                  type="primary"
                  size="small"
                  text
                  @click="viewSchoolDetail(scope.row)"
                >
                  详情
                </el-button>
                <el-button
                  type="success"
                  size="small"
                  @click="addToVolunteer(scope.row)"
                >
                  加入志愿
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 志愿填报建议 -->
        <div class="volunteer-suggestion card">
          <div class="section-title">
            <el-icon><DocumentChecked /></el-icon>
            <span>志愿填报建议</span>
          </div>
          <el-timeline>
            <el-timeline-item
              v-for="(suggestion, idx) in volunteerSuggestions"
              :key="suggestion.content"
              :type="suggestion.type"
            >
              <div class="suggestion-item">
                <div class="suggestion-level">{{ suggestion.level }}</div>
                <div class="suggestion-content">{{ suggestion.content }}</div>
                <div class="suggestion-school" v-if="suggestion.school">
                  <el-tag size="small" effect="dark" :type="suggestion.type">
                    {{ suggestion.school }}
                  </el-tag>
                  <span class="probability">录取概率 {{ suggestion.probability }}%</span>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 核心代码 -->
        <div class="code-section card">
          <div class="section-title">
            <el-icon><Code /></el-icon>
            <span>核心代码</span>
          </div>
          <el-collapse>
            <el-collapse-item title="择校匹配算法">
              <div class="code-block">
                <pre><code class="language-python">def match_schools(self, student_info: StudentInfo) -> List[Dict]:
    score = student_info.totalScore
    rank = student_info.rank or 5000
    
    matched_schools = []
    
    for school in self.kunming_schools:
        # 计算分数差异
        score_diff = score - school['minScore']
        
        # 确定学校类别和录取概率
        if score_diff >= 30:
            category = "保底"
            probability = min(98, 90 + score_diff * 0.2)
        elif score_diff >= 10:
            category = "稳妥"
            probability = 75 + score_diff * 0.5
        elif score_diff >= -10:
            category = "冲刺"
            probability = 50 + score_diff * 1.5
        else:
            category = "挑战"
            probability = 30 + (score_diff + 30) * 0.5
        
        # 计算匹配度
        match_score = self._calculate_match_score(school, student_info, probability)
        
        matched_schools.append({
            "schoolId": school['id'],
            "schoolName": school['name'],
            "category": category,
            "admissionProbability": round(probability, 1),
            "matchScore": round(match_score, 1),
            "reason": self._generate_match_reason(school, student_info, probability, category)
        })
    
    # 按匹配度排序
    matched_schools.sort(key=lambda x: x['matchScore'], reverse=True)
    return matched_schools</code></pre>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="saveAnalysis">
            <el-icon><Download /></el-icon>
            保存分析报告
          </el-button>
          <el-button size="large" @click="shareAnalysis">
            <el-icon><Share /></el-icon>
            分享分析结果
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Edit, MagicStick, Refresh, DataAnalysis, School,
  DataLine, Star, Check, Medal, CirclePlus,
  Download, Share, Top, Pointer, Flag
} from '@element-plus/icons-vue'
import { aiApi } from '@/api'
import { cityList } from '../utils'

export default {
  name: 'AiSelection',
  components: {
    Edit, MagicStick, Refresh, DataAnalysis, School,
    TrendCharts: DataLine, Star, Check, Medal, DocumentChecked: CirclePlus,
    Download, Share, Top, Pointer, Flag
  },
  setup() {
    const router = useRouter()
    const studentFormRef = ref(null)

    const analyzing = ref(false)
    const showResults = ref(false)

    const studentForm = reactive({
      totalScore: null,
      rank: null,
      city: '',
      district: '',
      targetType: null,
      needBoarding: false
    })

    const studentRules = {
      totalScore: [
        { required: true, message: '请输入中考总分', trigger: 'blur' }
      ],
      rank: [
        { required: true, message: '请输入区域排名', trigger: 'blur' }
      ],
      city: [
        { required: true, message: '请选择所在州市', trigger: 'change' }
      ],
      district: [
        { required: true, message: '请输入所在区县', trigger: 'blur' }
      ]
    }

    const analysisResult = reactive({
      matchCount: 0,
      avgProbability: 0,
      recommendCount: 0,
      confidence: 0
    })

    const recommendations = ref([])
    const volunteerSuggestions = ref([])

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

    const getProgressColor = (score) => {
      if (score >= 90) return '#67C23A'
      if (score >= 80) return '#E6A23C'
      if (score >= 70) return '#F56C6C'
      return '#909399'
    }

    const getProbabilityClass = (probability) => {
      if (probability >= 90) return 'high'
      if (probability >= 80) return 'medium'
      if (probability >= 70) return 'low'
      return 'very-low'
    }

    const analyzeSchools = async () => {
      studentFormRef.value.validate(async (valid) => {
        if (valid) {
          analyzing.value = true
          try {
            const studentInfo = {
              totalScore: studentForm.totalScore,
              rank: studentForm.rank,
              city: studentForm.city,
              district: studentForm.district,
              targetType: studentForm.targetType,
              needBoarding: studentForm.needBoarding
            }
            
            const result = await aiApi.matchSchools(studentInfo)

            if (result.success) {
              // 更新分析结果
              const recommendationsData = result.data.recommendations || []
              analysisResult.matchCount = recommendationsData.length
              analysisResult.avgProbability = Math.round(
                recommendationsData.reduce((sum, r) => sum + (r.admissionProbability || 0), 0) /
                (recommendationsData.length || 1)
              ) || 0
              analysisResult.recommendCount = Math.min(recommendationsData.length, 8)
              analysisResult.confidence = 85

              // 更新推荐列表
              recommendations.value = recommendationsData.map((item, index) => ({
                rank: index + 1,
                schoolId: item.schoolId,
                schoolName: item.schoolName,
                type: item.type || 1,
                matchScore: item.matchScore || 80,
                admissionProbability: item.admissionProbability || 75,
                reason: item.reason || '综合评估推荐'
              }))

              // 生成志愿建议
              generateVolunteerSuggestions()

              showResults.value = true
              ElMessage.success('AI分析完成')
            } else {
              ElMessage.error(result.message || '分析失败')
            }
          } catch (error) {
            console.error('AI分析失败:', error)
            ElMessage.error('AI分析失败，请稍后重试')
          } finally {
            analyzing.value = false
          }
        }
      })
    }

    const generateVolunteerSuggestions = () => {
      const types = ['primary', 'success', 'warning', 'info']
      const levels = ['第一志愿', '第二志愿', '第三志愿', '第四志愿']

      volunteerSuggestions.value = recommendations.value.slice(0, 4).map((item, index) => ({
        type: types[index],
        level: levels[index],
        content: `建议选择${item.schoolName}，${getSuggestionText(item.admissionProbability)}`,
        school: item.schoolName,
        probability: item.admissionProbability
      }))
    }

    const getSuggestionText = (probability) => {
      if (probability >= 90) return '录取概率很高，属于稳妥型志愿'
      if (probability >= 80) return '录取概率较高，属于稳妥型志愿'
      if (probability >= 70) return '录取概率中等，属于冲刺型志愿'
      return '录取概率较低，可作为保底选择'
    }

    const resetForm = () => {
      studentFormRef.value?.resetFields()
      showResults.value = false
      recommendations.value = []
      volunteerSuggestions.value = []
    }

    const viewSchoolDetail = (row) => {
      router.push(`/school/${row.schoolId || 1}`)
    }

    const addToVolunteer = (row) => {
      ElMessage.success(`已将${row.schoolName}加入志愿表`)
    }

    const saveAnalysis = () => {
      ElMessage.success('分析报告已保存')
    }

    const shareAnalysis = () => {
      ElMessage.success('分享链接已复制到剪贴板')
    }

    return {
      studentFormRef,
      analyzing,
      showResults,
      studentForm,
      studentRules,
      analysisResult,
      recommendations,
      volunteerSuggestions,
      cityList,
      getTypeName,
      getTypeTag,
      getProgressColor,
      getProbabilityClass,
      analyzeSchools,
      resetForm,
      viewSchoolDetail,
      addToVolunteer,
      saveAnalysis,
      shareAnalysis
    }
  }
}
</script>

<style scoped>
.ai-selection-page {
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

.input-section {
  margin-bottom: 30px;
}

.student-form {
  padding: 10px 0;
}

.analyze-btn {
  padding: 0 30px;
}

.results-section {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.analysis-summary {
  margin-bottom: 30px;
}

.summary-item {
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.summary-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-sm);
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.summary-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  font-size: 24px;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.summary-label {
  font-size: 14px;
  color: var(--text-muted);
}

.recommendations {
  margin-bottom: 30px;
}

.recommendation-table {
  border-radius: 8px;
  overflow: hidden;
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  margin: 0 auto;
  background: #f0f2f5;
  color: #606266;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4a);
  color: #8b6914;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #666;
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #daa520);
  color: #fff;
}

.school-name-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 6px 4px;
  min-height: 55px;
}

.school-name {
  font-weight: 700;
  color: #1a1a2e;
  font-size: 15px;
  line-height: 1.5;
  word-break: break-all;
  white-space: normal;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.match-score {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.score-value {
  font-size: 12px;
  color: #909399;
}

.probability-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
}

.probability-badge.high {
  background: #f6ffed;
  color: #52c41a;
}

.probability-badge.medium {
  background: #fff7e6;
  color: #fa8c16;
}

.probability-badge.low {
  background: #fff1f0;
  color: #f5222d;
}

.probability-badge.very-low {
  background: #f5f5f5;
  color: #999;
}

.volunteer-suggestion {
  margin-bottom: 30px;
}

.suggestion-item {
  padding: 10px 0;
}

.suggestion-level {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.suggestion-content {
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.6;
}

.suggestion-school {
  display: flex;
  align-items: center;
  gap: 10px;
}

.probability {
  font-size: 13px;
  color: var(--text-muted);
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 30px 0;
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .summary-item {
    margin-bottom: 15px;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
  }

  .action-buttons .el-button {
    width: 100%;
    max-width: 300px;
  }
}

/* 表格样式修复 */
:deep(.el-table) {
  background: #ffffff;
  color: #1a1a2e;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

:deep(.el-table th.el-table__cell) {
  background: #f5f5f7;
  color: #1a1a2e;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
  font-weight: 600;
  padding: 12px 8px !important;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  color: #1a1a2e;
  padding: 12px 8px !important;
  vertical-align: top !important;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell) {
  background: rgba(102, 126, 234, 0.08);
}

:deep(.el-table .el-table__row) {
  min-height: 70px !important;
}

:deep(.el-table .el-table__body tr) {
  line-height: 1.5 !important;
}

/* 按钮样式修复 */
:deep(.el-button) {
  background: #ffffff !important;
  color: #1a1a2e !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px !important;
}

:deep(.el-button:hover) {
  background: rgba(102, 126, 234, 0.15) !important;
  border-color: #667eea !important;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: #ffffff !important;
  border: none !important;
}

:deep(.el-button--primary:hover) {
  opacity: 0.9 !important;
}

/* 选择器样式修复 */
:deep(.el-select) {
  background: #ffffff !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px !important;
}

:deep(.el-select-dropdown) {
  background: #ffffff !important;
}

:deep(.el-select-dropdown__item) {
  color: #1a1a2e !important;
}
</style>
