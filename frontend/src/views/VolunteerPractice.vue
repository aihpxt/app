<template>
  <div class="volunteer-practice-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">模拟志愿填报演练</h1>
        <p class="page-desc">多次演练，找出最优志愿方案</p>
      </div>
    </div>

    <div class="container">
      <div v-if="!practiceStarted" class="start-section card">
        <div class="start-content">
          <el-icon class="start-icon"><DocumentCopy /></el-icon>
          <h2>开始志愿填报演练</h2>
          <p>通过多次模拟演练，对比不同方案，找到最适合你的志愿组合</p>
          <el-form :model="practiceForm" :rules="practiceRules" ref="practiceFormRef" label-width="100px" class="start-form">
            <el-form-item label="预估分数" prop="score">
              <el-input-number v-model="practiceForm.score" :min="0" :max="750" style="width: 100%" />
            </el-form-item>
            <el-form-item label="演练次数" prop="times">
              <el-radio-group v-model="practiceForm.times">
                <el-radio :value="3">3次</el-radio>
                <el-radio :value="5">5次</el-radio>
                <el-radio :value="10">10次</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" @click="startPractice" :loading="starting" style="width: 100%">
                <el-icon><VideoPlay /></el-icon>
                开始演练
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <div v-else class="practice-section">
        <div class="practice-progress card">
          <div class="progress-header">
            <div class="progress-info">
              <span class="progress-text">演练进度</span>
              <span class="progress-count">{{ currentPractice }}/{{ totalPractices }}</span>
            </div>
            <el-progress :percentage="practicePercentage" :stroke-width="20" />
          </div>
        </div>

        <el-row :gutter="20">
          <el-col :xs="24" :lg="8">
            <div class="input-card card">
              <div class="section-title">
                <el-icon><Edit /></el-icon>
                <span>第 {{ currentPractice }} 次演练</span>
              </div>
              <el-form :model="currentForm" label-width="100px">
                <el-form-item label="策略偏好">
                  <el-radio-group v-model="currentForm.strategy">
                    <el-radio value="conservative">保守型</el-radio>
                    <el-radio value="balanced">均衡型</el-radio>
                    <el-radio value="aggressive">激进型</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="优先考虑">
                  <el-checkbox-group v-model="currentForm.priorities">
                    <el-checkbox label="学校排名">学校排名</el-checkbox>
                    <el-checkbox label="专业选择">专业选择</el-checkbox>
                    <el-checkbox label="地理位置">地理位置</el-checkbox>
                    <el-checkbox label="住宿条件">住宿条件</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="generateCurrentPlan" :loading="generating" style="width: 100%">
                    <el-icon><MagicStick /></el-icon>
                    生成方案
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-col>

          <el-col :xs="24" :lg="16">
            <div v-if="currentPlan" class="result-card card">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>第 {{ currentPractice }} 次演练方案</span>
                <el-tag :type="getStrategyTag(currentForm.strategy)" style="margin-left: auto">
                  {{ getStrategyText(currentForm.strategy) }}
                </el-tag>
              </div>
              
              <div class="plan-overview">
                <el-descriptions :column="3" border>
                  <el-descriptions-item label="冲刺学校">
                    <span class="school-count">{{ currentPlan.sprint.length }}所</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="稳妥学校">
                    <span class="school-count">{{ currentPlan.safe.length }}所</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="保底学校">
                    <span class="school-count">{{ currentPlan.backup.length }}所</span>
                  </el-descriptions-item>
                </el-descriptions>
              </div>

              <el-divider />

              <div class="plan-schools">
                <h4>📈 冲刺志愿</h4>
                <el-row :gutter="10">
                  <el-col :xs="24" :sm="12" v-for="school in currentPlan.sprint" :key="school.name">
                    <div class="school-item sprint">
                      <div class="school-name">{{ school.name }}</div>
                      <div class="school-info">
                        <el-tag size="small" type="danger">冲刺</el-tag>
                        <span class="probability">{{ school.probability }}%</span>
                      </div>
                    </div>
                  </el-col>
                </el-row>

                <h4>📊 稳妥志愿</h4>
                <el-row :gutter="10">
                  <el-col :xs="24" :sm="12" v-for="school in currentPlan.safe" :key="school.name">
                    <div class="school-item safe">
                      <div class="school-name">{{ school.name }}</div>
                      <div class="school-info">
                        <el-tag size="small" type="warning">稳妥</el-tag>
                        <span class="probability">{{ school.probability }}%</span>
                      </div>
                    </div>
                  </el-col>
                </el-row>

                <h4>🛡️ 保底志愿</h4>
                <el-row :gutter="10">
                  <el-col :xs="24" :sm="12" v-for="school in currentPlan.backup" :key="school.name">
                    <div class="school-item backup">
                      <div class="school-name">{{ school.name }}</div>
                      <div class="school-info">
                        <el-tag size="small" type="success">保底</el-tag>
                        <span class="probability">{{ school.probability }}%</span>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <div class="plan-actions">
                <el-button type="success" @click="saveCurrentPlan" :disabled="currentSaved">
                  <el-icon><Collection /></el-icon>
                  {{ currentSaved ? '已保存' : '保存方案' }}
                </el-button>
                <el-button v-if="currentPractice < totalPractices" type="primary" @click="nextPractice">
                  <el-icon><Right /></el-icon>
                  下一次演练
                </el-button>
                <el-button v-else type="primary" @click="finishPractice">
                  <el-icon><Check /></el-icon>
                  完成演练
                </el-button>
              </div>
            </div>

            <div v-else class="empty-result card">
              <el-empty description="点击生成方案按钮，生成第 {{ currentPractice }} 次演练方案" />
            </div>
          </el-col>
        </el-row>

        <div v-if="savedPlans.length > 0" class="saved-plans-card card">
          <div class="section-title">
            <el-icon><Collection /></el-icon>
            <span>已保存的方案 ({{ savedPlans.length }})</span>
            <el-button v-if="savedPlans.length >= 2" type="primary" size="small" @click="comparePlans" style="margin-left: auto">
              <el-icon><Collection /></el-icon>
              对比方案
            </el-button>
          </div>
          <el-row :gutter="15">
            <el-col :xs="24" :sm="12" :lg="8" v-for="(plan, idx) in savedPlans" :key="plan.id || idx">
              <div class="saved-plan-item" :class="{ selected: selectedPlans.includes(idx) }" @click="toggleSelectPlan(idx)">
                <div class="plan-header">
                  <span class="plan-title">方案 {{ idx + 1 }}</span>
                  <el-tag :type="getStrategyTag(plan.strategy)" size="small">
                    {{ getStrategyText(plan.strategy) }}
                  </el-tag>
                </div>
                <div class="plan-stats">
                  <div class="stat">
                    <span class="stat-value">{{ plan.sprintCount }}</span>
                    <span class="stat-label">冲刺</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{{ plan.safeCount }}</span>
                    <span class="stat-label">稳妥</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{{ plan.backupCount }}</span>
                    <span class="stat-label">保底</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{{ plan.avgProbability }}%</span>
                    <span class="stat-label">平均录取率</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div v-if="showComparison" class="comparison-card card">
          <div class="section-title">
            <el-icon><Scale /></el-icon>
            <span>方案对比</span>
            <el-button type="text" @click="showComparison = false" style="margin-left: auto">
              <el-icon><Close /></el-icon>
              关闭
            </el-button>
          </div>
          <el-table :data="comparisonData" style="width: 100%">
            <el-table-column prop="item" label="对比项" width="150" />
            <el-table-column v-for="(plan, idx) in selectedPlanDetails" :key="idx" :label="'方案 ' + (idx + 1)" align="center">
              <template #default="scope">
                <span v-if="scope.row.highlight" class="highlight">{{ scope.row['plan' + (idx + 1)] }}</span>
                <span v-else>{{ scope.row['plan' + (idx + 1)] }}</span>
              </template>
            </el-table-column>
          </el-table>
          <div class="comparison-result">
            <el-alert
              :title="'推荐方案：方案 ' + (bestPlanIndex + 1)"
              type="success"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DocumentCopy, VideoPlay, Edit, MagicStick, Document,
  Collection, Right, Check, Close
} from '@element-plus/icons-vue'

export default {
  name: 'VolunteerPractice',
  components: {
    DocumentCopy, VideoPlay, Edit, MagicStick, Document,
    Collection, Right, Check, Close
  },
  setup() {
    const practiceFormRef = ref(null)
    const practiceStarted = ref(false)
    const starting = ref(false)
    const generating = ref(false)
    const currentPractice = ref(1)
    const totalPractices = ref(3)
    const currentPlan = ref(null)
    const currentSaved = ref(false)
    const savedPlans = ref([])
    const selectedPlans = ref([])
    const showComparison = ref(false)
    const comparisonData = ref([])
    const selectedPlanDetails = ref([])
    const bestPlanIndex = ref(0)

    const schoolList = [
      '云南师范大学附属中学', '昆明市第一中学', '昆明市第三中学',
      '昆明市第八中学', '昆明市第十中学', '云南大学附属中学',
      '昆明市第十二中学', '昆明市第十四中学', '北大附中云南实验学校',
      '云南衡水实验中学'
    ]

    const practiceForm = reactive({
      score: null,
      times: 3
    })

    const practiceRules = {
      score: [{ required: true, message: '请输入预估分数', trigger: 'blur' }],
      times: [{ required: true, message: '请选择演练次数', trigger: 'change' }]
    }

    const currentForm = reactive({
      strategy: 'balanced',
      priorities: []
    })

    const practicePercentage = computed(() => {
      return Math.round((currentPractice.value / totalPractices.value) * 100)
    })

    const startPractice = () => {
      practiceFormRef.value.validate((valid) => {
        if (valid) {
          starting.value = true
          setTimeout(() => {
            totalPractices.value = practiceForm.times
            practiceStarted.value = true
            starting.value = false
            ElMessage.success('演练开始！')
          }, 1000)
        }
      })
    }

    const generateCurrentPlan = () => {
      generating.value = true
      setTimeout(() => {
        const strategy = currentForm.strategy
        let sprintCount, safeCount, backupCount
        
        if (strategy === 'conservative') {
          sprintCount = 1
          safeCount = 3
          backupCount = 3
        } else if (strategy === 'aggressive') {
          sprintCount = 4
          safeCount = 2
          backupCount = 1
        } else {
          sprintCount = 2
          safeCount = 3
          backupCount = 2
        }

        const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5)
        const shuffledSchools = shuffle(schoolList)

        currentPlan.value = {
          sprint: shuffledSchools.slice(0, sprintCount).map(name => ({
            name,
            probability: Math.floor(Math.random() * 30) + 30
          })),
          safe: shuffledSchools.slice(sprintCount, sprintCount + safeCount).map(name => ({
            name,
            probability: Math.floor(Math.random() * 30) + 55
          })),
          backup: shuffledSchools.slice(sprintCount + safeCount, sprintCount + safeCount + backupCount).map(name => ({
            name,
            probability: Math.floor(Math.random() * 20) + 80
          }))
        }

        currentSaved.value = false
        generating.value = false
        ElMessage.success('方案生成成功！')
      }, 1500)
    }

    const saveCurrentPlan = () => {
      const allSchools = [...currentPlan.value.sprint, ...currentPlan.value.safe, ...currentPlan.value.backup]
      const avgProbability = Math.round(allSchools.reduce((sum, s) => sum + s.probability, 0) / allSchools.length)
      
      savedPlans.value.push({
        strategy: currentForm.strategy,
        priorities: [...currentForm.priorities],
        sprintCount: currentPlan.value.sprint.length,
        safeCount: currentPlan.value.safe.length,
        backupCount: currentPlan.value.backup.length,
        avgProbability,
        plan: { ...currentPlan.value }
      })

      currentSaved.value = true
      ElMessage.success('方案已保存！')
    }

    const nextPractice = () => {
      if (!currentSaved.value) {
        ElMessage.warning('请先保存当前方案')
        return
      }
      currentPractice.value++
      currentPlan.value = null
      currentSaved.value = false
      currentForm.strategy = 'balanced'
      currentForm.priorities = []
    }

    const finishPractice = () => {
      if (!currentSaved.value && currentPlan.value) {
        ElMessage.warning('请先保存当前方案')
        return
      }
      ElMessage.success('演练完成！可以对比已保存的方案')
    }

    const toggleSelectPlan = (idx) => {
      const i = selectedPlans.value.indexOf(idx)
      if (i > -1) {
        selectedPlans.value.splice(i, 1)
      } else {
        if (selectedPlans.value.length < 3) {
          selectedPlans.value.push(idx)
        } else {
          ElMessage.warning('最多选择3个方案进行对比')
        }
      }
    }

    const comparePlans = () => {
      if (selectedPlans.value.length < 2) {
        ElMessage.warning('请至少选择2个方案')
        return
      }

      selectedPlanDetails.value = selectedPlans.value.map(idx => savedPlans.value[idx])
      
      const plans = selectedPlanDetails.value
      comparisonData.value = [
        { item: '策略类型', plan1: getStrategyText(plans[0].strategy), plan2: getStrategyText(plans[1].strategy), plan3: plans[2] ? getStrategyText(plans[2].strategy) : '-' },
        { item: '冲刺学校数', plan1: plans[0].sprintCount, plan2: plans[1].sprintCount, plan3: plans[2] ? plans[2].sprintCount : '-', highlight: true },
        { item: '稳妥学校数', plan1: plans[0].safeCount, plan2: plans[1].safeCount, plan3: plans[2] ? plans[2].safeCount : '-' },
        { item: '保底学校数', plan1: plans[0].backupCount, plan2: plans[1].backupCount, plan3: plans[2] ? plans[2].backupCount : '-' },
        { item: '平均录取率', plan1: plans[0].avgProbability + '%', plan2: plans[1].avgProbability + '%', plan3: plans[2] ? plans[2].avgProbability + '%' : '-', highlight: true }
      ]

      bestPlanIndex.value = plans.reduce((bestIdx, plan, idx, arr) => 
        plan.avgProbability > arr[bestIdx].avgProbability ? idx : bestIdx, 0)

      showComparison.value = true
    }

    const getStrategyTag = (strategy) => {
      const tags = { conservative: 'info', balanced: 'warning', aggressive: 'danger' }
      return tags[strategy] || 'info'
    }

    const getStrategyText = (strategy) => {
      const texts = { conservative: '保守型', balanced: '均衡型', aggressive: '激进型' }
      return texts[strategy] || '均衡型'
    }

    return {
      practiceFormRef,
      practiceStarted,
      starting,
      generating,
      currentPractice,
      totalPractices,
      currentPlan,
      currentSaved,
      savedPlans,
      selectedPlans,
      showComparison,
      comparisonData,
      selectedPlanDetails,
      bestPlanIndex,
      practiceForm,
      practiceRules,
      currentForm,
      practicePercentage,
      startPractice,
      generateCurrentPlan,
      saveCurrentPlan,
      nextPractice,
      finishPractice,
      toggleSelectPlan,
      comparePlans,
      getStrategyTag,
      getStrategyText
    }
  }
}
</script>

<style scoped>
.volunteer-practice-page {
  min-height: 100%;
  background: #f5f7fa;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
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
  color: #fff;
}

.page-desc {
  font-size: 16px;
  opacity: 0.9;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.section-title .el-icon {
  font-size: 20px;
  color: #409eff;
}

.start-section {
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.start-content {
  text-align: center;
  max-width: 500px;
}

.start-icon {
  font-size: 80px;
  color: #409eff;
  margin-bottom: 20px;
}

.start-content h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.start-content p {
  color: #606266;
  margin-bottom: 30px;
  line-height: 1.6;
}

.start-form {
  text-align: left;
  margin-top: 30px;
}

.practice-progress {
  margin-bottom: 24px;
}

.progress-header {
  margin-bottom: 15px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.progress-count {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.plan-overview {
  margin-bottom: 20px;
}

.school-count {
  font-weight: 600;
  color: #409eff;
}

.plan-schools h4 {
  font-size: 16px;
  color: #303133;
  margin: 20px 0 15px 0;
}

.school-item {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  border: 2px solid transparent;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.school-item.sprint {
  background: #fef0f0;
  border-color: #fbc4c4;
}

.school-item.safe {
  background: #fdf6ec;
  border-color: #f5dab1;
}

.school-item.backup {
  background: #f0f9eb;
  border-color: #c2e7b0;
}

.school-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.school-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.probability {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

.plan-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.empty-result {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.saved-plan-item {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  border: 2px solid transparent;
}

.saved-plan-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.saved-plan-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.plan-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.plan-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.comparison-result {
  margin-top: 20px;
}

.highlight {
  font-weight: 700;
  color: #67c23a;
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .plan-actions {
    flex-direction: column;
  }

  .plan-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
