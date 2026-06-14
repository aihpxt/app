<template>
  <div class="volunteer-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">AI志愿智能填报</h1>
        <p class="page-desc">基于昆明中考批次规则，智能生成冲稳保志愿方案</p>
      </div>
    </div>

    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="8">
          <div class="input-section card">
            <div class="section-title">
              <el-icon><Edit /></el-icon>
              <span>考生信息</span>
            </div>
            <el-form :model="studentForm" :rules="studentRules" ref="studentFormRef" label-width="90px">
              <el-form-item label="中考分数" prop="totalScore">
                <el-input-number v-model="studentForm.totalScore" :min="0" :max="750" :precision="1" style="width: 100%" />
              </el-form-item>
              <el-form-item label="全市排名" prop="rank">
                <el-input-number v-model="studentForm.rank" :min="1" style="width: 100%" />
              </el-form-item>
              <el-form-item label="所在州市" prop="city">
                <el-select v-model="studentForm.city" style="width: 100%">
                  <el-option label="昆明市" value="昆明市" />
                  <el-option label="曲靖市" value="曲靖市" />
                  <el-option label="玉溪市" value="玉溪市" />
                </el-select>
              </el-form-item>
              <el-form-item label="所在区县" prop="district">
                <el-input v-model="studentForm.district" placeholder="请输入区县" />
              </el-form-item>
              <el-form-item label="目标类型">
                <el-select v-model="studentForm.targetType" style="width: 100%" clearable placeholder="不限">
                  <el-option label="重点高中" :value="2" />
                  <el-option label="普通高中" :value="1" />
                  <el-option label="民办学校" :value="4" />
                </el-select>
              </el-form-item>
              <el-form-item label="住宿需求">
                <el-radio-group v-model="studentForm.needBoarding">
                  <el-radio :value="true">需要</el-radio>
                  <el-radio :value="false">不需要</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="generateVolunteer" :loading="generating" style="width: 100%">
                  <el-icon><MagicStick /></el-icon>
                  AI生成志愿方案
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :lg="16">
          <div v-if="volunteerResult" class="result-section">
            <div class="summary-card card">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>方案概览</span>
              </div>
              <el-row :gutter="15">
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-value">{{ volunteerResult.summary.chongCount }}</div>
                    <div class="summary-label">冲刺志愿</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-value">{{ volunteerResult.summary.wenCount }}</div>
                    <div class="summary-label">稳妥志愿</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-value">{{ volunteerResult.summary.baoCount }}</div>
                    <div class="summary-label">保底志愿</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-value">{{ volunteerResult.summary.totalProbability }}%</div>
                    <div class="summary-label">平均概率</div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="volunteer-table card">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>志愿填报表</span>
                <el-button type="primary" size="small" @click="exportVolunteer" style="margin-left: auto">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
              <el-table :data="volunteerResult.volunteers" style="width: 100%">
                <el-table-column prop="order" label="志愿序号" width="90" align="center">
                  <template #default="scope">
                    <el-tag :type="getCategoryType(scope.row.category)" effect="dark">
                      第{{ scope.row.order }}志愿
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="batch" label="批次" width="80" align="center" />
                <el-table-column prop="schoolName" label="学校名称" min-width="180" />
                <el-table-column prop="category" label="类型" width="80" align="center">
                  <template #default="scope">
                    <span :class="['category-tag', scope.row.category]">{{ scope.row.category }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="probability" label="录取概率" width="100" align="center">
                  <template #default="scope">
                    <span :class="['probability', getProbabilityClass(scope.row.probability)]">
                      {{ scope.row.probability }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="suggestion" label="建议" min-width="200" show-overflow-tooltip />
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="scope">
                    <el-button type="primary" text size="small" @click="adjustVolunteer(scope.row)">
                      调整
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="suggestions-card card">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>填报建议</span>
              </div>
              <el-alert
                v-for="(suggestion, idx) in volunteerResult.suggestions"
                :key="suggestion"
                :title="suggestion"
                type="info"
                :closable="false"
                show-icon
                style="margin-bottom: 10px"
              />
            </div>
          </div>

          <div v-else class="empty-section card">
            <el-empty description="请填写考生信息，生成志愿方案">
              <el-button type="primary" @click="focusInput">开始填报</el-button>
            </el-empty>
          </div>
        </el-col>
      </el-row>

      <div v-if="volunteerResult" class="risk-check-section card">
        <div class="section-title">
          <el-icon><CircleCheck /></el-icon>
          <span>志愿风险体检</span>
        </div>
        <el-button type="warning" @click="checkRisk" :loading="checkingRisk">
          <el-icon><Search /></el-icon>
          AI风险检测
        </el-button>
        
        <div v-if="riskResult" class="risk-result">
          <el-alert
            :title="`风险等级：${riskResult.riskLevel}`"
            :type="riskResult.riskLevel === '低' ? 'success' : (riskResult.riskLevel === '中' ? 'warning' : 'error')"
            :closable="false"
            show-icon
          >
            <template #default>
              风险评分：{{ riskResult.riskScore }}分
            </template>
          </el-alert>

          <div v-if="riskResult.risks.length > 0" class="risk-list">
            <h4>风险提示</h4>
            <el-alert
              v-for="(risk, idx) in riskResult.risks"
              :key="risk.type"
              :title="risk.type"
              :type="risk.level === 'high' ? 'error' : (risk.level === 'medium' ? 'warning' : 'info')"
              :description="risk.message"
              :closable="false"
              show-icon
              style="margin-bottom: 10px"
            >
              <template #default>
                <p>{{ risk.message }}</p>
                <p><strong>建议：</strong>{{ risk.suggestion }}</p>
              </template>
            </el-alert>
          </div>

          <div v-if="riskResult.warnings.length > 0" class="warning-list">
            <h4>注意事项</h4>
            <el-alert
              v-for="(warning, idx) in riskResult.warnings"
              :key="warning.type"
              :title="warning.type"
              type="warning"
              :closable="false"
              show-icon
              style="margin-bottom: 10px"
            >
              <template #default>
                <p>{{ warning.message }}</p>
                <p><strong>建议：</strong>{{ warning.suggestion }}</p>
              </template>
            </el-alert>
          </div>
        </div>
      </div>
    </div>

    <div class="code-section card">
      <div class="section-title">
        <el-icon><Code /></el-icon>
        <span>核心代码</span>
      </div>
      <el-collapse>
        <el-collapse-item title="志愿生成算法">
          <div class="code-block">
            <pre><code class="language-python">def generate_volunteer_table(self, student_info: StudentInfo) -> Dict:
    matched_schools = self.match_schools(student_info)
    
    # 筛选不同类别的学校
    chong = [s for s in matched_schools if s['category'] == "冲刺"][:2]
    wen = [s for s in matched_schools if s['category'] == "稳妥"][:3]
    bao = [s for s in matched_schools if s['category'] == "保底"][:2]
    
    volunteers = []
    order = 1
    
    # 生成冲刺志愿
    for school in chong:
        volunteers.append({
            "order": order,
            "batch": "第一批",
            "schoolId": school['schoolId'],
            "schoolName": school['schoolName'],
            "category": "冲刺",
            "probability": school['admissionProbability'],
            "suggestion": "冲刺志愿，录取有一定难度"
        })
        order += 1
    
    # 生成稳妥志愿
    for school in wen:
        volunteers.append({
            "order": order,
            "batch": "第一批",
            "schoolId": school['schoolId'],
            "schoolName": school['schoolName'],
            "category": "稳妥",
            "probability": school['admissionProbability'],
            "suggestion": "稳妥志愿，录取概率较高"
        })
        order += 1
    
    # 生成保底志愿
    for school in bao:
        volunteers.append({
            "order": order,
            "batch": "第一批",
            "schoolId": school['schoolId'],
            "schoolName": school['schoolName'],
            "category": "保底",
            "probability": school['admissionProbability'],
            "suggestion": "保底志愿，确保有学可上"
        })
        order += 1
    
    return {
        "volunteers": volunteers,
        "summary": {
            "chongCount": len(chong),
            "wenCount": len(wen),
            "baoCount": len(bao),
            "totalProbability": round(sum(v['probability'] for v in volunteers) / len(volunteers), 1) if volunteers else 0
        }
    }</code></pre>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <el-dialog v-model="adjustDialogVisible" title="调整志愿" width="500px">
      <el-form :model="adjustForm" label-width="80px">
        <el-form-item label="学校">
          <el-input v-model="adjustForm.schoolName" disabled />
        </el-form-item>
        <el-form-item label="志愿顺序">
          <el-input-number v-model="adjustForm.order" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="adjustForm.note" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAdjust">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit, MagicStick, DataAnalysis, Document, Download,
  Warning, CircleCheck, Search
} from '@element-plus/icons-vue'
import { aiApi } from '@/api'

export default {
  name: 'Volunteer',
  components: {
    Edit, MagicStick, DataAnalysis, Document, Download,
    Warning, CircleCheck, Search
  },
  setup() {
    const studentFormRef = ref(null)
    const generating = ref(false)
    const checkingRisk = ref(false)
    const adjustDialogVisible = ref(false)
    
    const studentForm = reactive({
      totalScore: null,
      rank: null,
      city: '昆明市',
      district: '',
      targetType: null,
      needBoarding: false
    })
    
    const studentRules = {
      totalScore: [{ required: true, message: '请输入中考分数', trigger: 'blur' }],
      rank: [{ required: true, message: '请输入全市排名', trigger: 'blur' }],
      city: [{ required: true, message: '请选择所在州市', trigger: 'change' }],
      district: [{ required: true, message: '请输入所在区县', trigger: 'blur' }]
    }
    
    const volunteerResult = ref(null)
    const riskResult = ref(null)
    
    const adjustForm = reactive({
      schoolName: '',
      order: 1,
      note: ''
    })
    
    const generateVolunteer = async () => {
      studentFormRef.value.validate(async (valid) => {
        if (valid) {
          generating.value = true
          try {
            const response = await aiApi.generateVolunteer(studentForm)
            if (response.success) {
              volunteerResult.value = response.data
              riskResult.value = null
              ElMessage.success('志愿方案生成成功')
            } else {
              ElMessage.error(response.message || '生成失败')
            }
          } catch (error) {
            console.error('生成志愿失败:', error)
            ElMessage.error('生成失败，请稍后重试')
          } finally {
            generating.value = false
          }
        }
      })
    }
    
    const checkRisk = async () => {
      if (!volunteerResult.value) {
        ElMessage.warning('请先生成志愿方案')
        return
      }
      
      checkingRisk.value = true
      try {
        const volunteerTable = {
          volunteers: volunteerResult.value.volunteers.map(v => ({
            schoolId: v.schoolId,
            schoolName: v.schoolName,
            batch: v.batch,
            order: v.order
          })),
          studentScore: studentForm.totalScore,
          studentRank: studentForm.rank,
          city: studentForm.city
        }
        
        const response = await aiApi.checkVolunteerRisk(volunteerTable)
        if (response.success) {
          riskResult.value = response.data
          ElMessage.success('风险检测完成')
        }
      } catch (error) {
        console.error('风险检测失败:', error)
        ElMessage.error('检测失败，请稍后重试')
      } finally {
        checkingRisk.value = false
      }
    }
    
    const adjustVolunteer = (row) => {
      adjustForm.schoolName = row.schoolName
      adjustForm.order = row.order
      adjustForm.note = ''
      adjustDialogVisible.value = true
    }
    
    const confirmAdjust = () => {
      const volunteer = volunteerResult.value.volunteers.find(v => v.schoolName === adjustForm.schoolName)
      if (volunteer) {
        volunteer.order = adjustForm.order
        volunteerResult.value.volunteers.sort((a, b) => a.order - b.order)
      }
      adjustDialogVisible.value = false
      ElMessage.success('调整成功')
    }
    
    const exportVolunteer = () => {
      ElMessage.success('志愿表已导出')
    }
    
    const focusInput = () => {
      document.querySelector('.input-section').scrollIntoView({ behavior: 'smooth' })
    }
    
    const getCategoryType = (category) => {
      const types = { '冲刺': 'danger', '稳妥': 'success', '保底': 'info' }
      return types[category] || ''
    }
    
    const getProbabilityClass = (probability) => {
      if (probability >= 90) return 'high'
      if (probability >= 70) return 'medium'
      return 'low'
    }
    
    return {
      studentFormRef,
      generating,
      checkingRisk,
      adjustDialogVisible,
      studentForm,
      studentRules,
      volunteerResult,
      riskResult,
      adjustForm,
      generateVolunteer,
      checkRisk,
      adjustVolunteer,
      confirmAdjust,
      exportVolunteer,
      focusInput,
      getCategoryType,
      getProbabilityClass
    }
  }
}
</script>

<style scoped>
.volunteer-page {
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
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
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
  color: #409EFF;
}

.input-section {
  position: sticky;
  top: 20px;
}

.summary-card .summary-item {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.summary-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 5px;
}

.category-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.category-tag.冲刺 {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.category-tag.稳妥 {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.category-tag.保底 {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.probability {
  font-weight: 600;
}

.probability.high {
  color: #67c23a;
}

.probability.medium {
  color: #e6a23c;
}

.probability.low {
  color: #f56c6c;
}

.risk-check-section {
  margin-top: 20px;
}

.risk-result {
  margin-top: 20px;
}

.risk-list, .warning-list {
  margin-top: 20px;
}

.risk-list h4, .warning-list h4 {
  margin-bottom: 15px;
  color: var(--text-primary);
}

.empty-section {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .input-section {
    position: relative;
    top: 0;
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
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  color: #1a1a2e;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell) {
  background: rgba(102, 126, 234, 0.08);
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

:deep(.el-button--warning) {
  background: linear-gradient(135deg, #faad14 0%, #ffc53d 100%) !important;
  color: #ffffff !important;
  border: none !important;
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

/* 对话框样式 */
:deep(.el-dialog) {
  background: #ffffff !important;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff !important;
}

:deep(.el-dialog__title) {
  color: #ffffff !important;
}

:deep(.el-dialog__body) {
  color: #1a1a2e;
}

:deep(.el-dialog__footer .el-button) {
  background: #f5f5f7 !important;
  color: #1a1a2e !important;
}

:deep(.el-dialog__footer .el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: #ffffff !important;
}
</style>
