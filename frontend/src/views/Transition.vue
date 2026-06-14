<template>
  <div class="transition-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">AI高中衔接规划</h1>
        <p class="page-desc">智能生成初高衔接学习计划，助您赢在起跑线</p>
      </div>
    </div>

    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="8">
          <div class="input-section card">
            <div class="section-title">
              <el-icon><Edit /></el-icon>
              <span>规划设置</span>
            </div>
            <el-form :model="planForm" :rules="planRules" ref="planFormRef" label-width="100px">
              <el-form-item label="目标学校" prop="targetSchool">
                <el-select v-model="planForm.targetSchool" placeholder="请选择目标学校" style="width: 100%">
                  <el-option
                    v-for="school in schoolList"
                    :key="school"
                    :label="school"
                    :value="school"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="中考分数" prop="studentScore">
                <el-input-number v-model="planForm.studentScore" :min="0" :max="750" style="width: 100%" />
              </el-form-item>
              <el-form-item label="薄弱科目">
                <el-checkbox-group v-model="planForm.weakSubjects">
                  <el-checkbox label="语文">语文</el-checkbox>
                  <el-checkbox label="数学">数学</el-checkbox>
                  <el-checkbox label="英语">英语</el-checkbox>
                  <el-checkbox label="物理">物理</el-checkbox>
                  <el-checkbox label="化学">化学</el-checkbox>
                  <el-checkbox label="生物">生物</el-checkbox>
                  <el-checkbox label="历史">历史</el-checkbox>
                  <el-checkbox label="地理">地理</el-checkbox>
                  <el-checkbox label="政治">政治</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="学习风格">
                <el-radio-group v-model="planForm.learningStyle">
                  <el-radio value="自主型">自主型</el-radio>
                  <el-radio value="指导型">指导型</el-radio>
                  <el-radio value="混合型">混合型</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="generatePlan" :loading="generating" style="width: 100%">
                  <el-icon><MagicStick /></el-icon>
                  生成衔接规划
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :lg="16">
          <div v-if="transitionPlan" class="plan-section">
            <div class="overview-card card">
              <div class="section-title">
                <el-icon><Aim /></el-icon>
                <span>规划概览</span>
              </div>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="目标学校">{{ transitionPlan.targetSchool }}</el-descriptions-item>
                <el-descriptions-item label="中考分数">{{ transitionPlan.studentScore }}分</el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="timeline-card card">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                <span>学习时间线</span>
              </div>
              <el-timeline>
                <el-timeline-item
                  v-for="(item, idx) in transitionPlan.timeline"
                  :key="item.phase"
                  :timestamp="item.phase"
                  placement="top"
                  :type="idx === 0 ? 'primary' : 'info'"
                >
                  <el-card>
                    <h4>{{ item.phase }}</h4>
                    <p>{{ item.content }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>

            <div class="study-plan-card card">
              <div class="section-title">
                <el-icon><Reading /></el-icon>
                <span>学习计划</span>
              </div>
              <el-table :data="transitionPlan.transitionPlan.studyPlan" style="width: 100%">
                <el-table-column prop="subject" label="科目" width="80" align="center" />
                <el-table-column prop="content" label="学习内容" min-width="200" />
                <el-table-column prop="priority" label="优先级" width="80" align="center">
                  <template #default="scope">
                    <el-tag :type="scope.row.priority === '高' ? 'danger' : 'info'" size="small">
                      {{ scope.row.priority }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="hours" label="建议学时" width="100" align="center">
                  <template #default="scope">
                    {{ scope.row.hours }}小时
                  </template>
                </el-table-column>
                <el-table-column prop="resources" label="学习资源" min-width="150">
                  <template #default="scope">
                    <el-tag
                      v-for="res in scope.row.resources"
                      :key="res"
                      size="small"
                      style="margin-right: 5px"
                    >
                      {{ res }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="preview-card card">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>预习内容重点</span>
              </div>
              <el-row :gutter="15">
                <el-col :xs="24" :sm="12" v-for="(item, idx) in transitionPlan.transitionPlan.previewContent" :key="item.subject">
                  <div class="preview-item">
                    <div class="preview-header">
                      <span class="subject">{{ item.subject }}</span>
                      <el-tag :type="getDifficultyTag(item.difficulty)" size="small">
                        {{ item.difficulty }}
                      </el-tag>
                    </div>
                    <div class="preview-content">{{ item.content }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="adaptation-card card">
              <div class="section-title">
                <el-icon><User /></el-icon>
                <span>学校风格适应建议</span>
              </div>
              <el-alert
                v-for="(item, idx) in transitionPlan.transitionPlan.styleAdaptation"
                :key="item"
                :title="item"
                type="info"
                :closable="false"
                show-icon
                style="margin-bottom: 10px"
              />
            </div>

            <div class="suggestions-card card">
              <div class="section-title">
                <el-icon><Star /></el-icon>
                <span>温馨提示</span>
              </div>
              <el-timeline>
                <el-timeline-item
                  v-for="(suggestion, idx) in transitionPlan.suggestions"
                  :key="suggestion"
                  :type="idx % 2 === 0 ? 'primary' : 'success'"
                >
                  {{ suggestion }}
                </el-timeline-item>
              </el-timeline>
            </div>

            <div class="progress-card card">
              <div class="section-title">
                <el-icon><Odometer /></el-icon>
                <span>学习进度追踪</span>
                <el-button type="primary" size="small" @click="resetProgress" style="margin-left: auto">
                  <el-icon><RefreshLeft /></el-icon>
                  重置进度
                </el-button>
              </div>
              <div class="progress-summary">
                <div class="progress-stat">
                  <div class="progress-value">{{ completedTasks }}/{{ totalTasks }}</div>
                  <div class="progress-label">已完成任务</div>
                </div>
                <div class="progress-stat">
                  <div class="progress-value">{{ overallProgress }}%</div>
                  <div class="progress-label">总体进度</div>
                </div>
                <div class="progress-stat">
                  <div class="progress-value">{{ studyDays }}天</div>
                  <div class="progress-label">已学习</div>
                </div>
              </div>
              <el-divider />
              <div class="progress-list">
                <div v-for="(phase, pIndex) in transitionPlan.timeline" :key="pIndex" class="phase-section">
                  <div class="phase-header" @click="togglePhase(pIndex)">
                    <div class="phase-title">
                      <el-icon :class="{ expanded: expandedPhases.includes(pIndex) }"><ArrowRight /></el-icon>
                      <span>{{ phase.phase }}</span>
                    </div>
                    <el-tag :type="getPhaseProgressType(pIndex)" size="small">
                      {{ getPhaseProgress(pIndex) }}%
                    </el-tag>
                  </div>
                  <div v-show="expandedPhases.includes(pIndex)" class="phase-content">
                    <div v-for="(task, tIndex) in getPhaseTasks(phase.phase)" :key="tIndex" class="task-item">
                      <el-checkbox v-model="task.completed" @change="updateProgress">
                        {{ task.content }}
                      </el-checkbox>
                      <div class="task-meta">
                        <el-tag v-if="task.subject" size="small" type="info">{{ task.subject }}</el-tag>
                        <span class="task-hours">{{ task.hours }}小时</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="action-buttons">
              <el-button type="primary" size="large" @click="downloadPlan">
                <el-icon><Download /></el-icon>
                下载规划
              </el-button>
              <el-button size="large" @click="sharePlan">
                <el-icon><Share /></el-icon>
                分享规划
              </el-button>
              <el-button size="large" @click="savePlan">
                <el-icon><Collection /></el-icon>
                保存到我的
              </el-button>
            </div>
          </div>

          <div v-else class="empty-section card">
            <el-empty description="请设置规划参数，生成个性化衔接方案">
              <el-button type="primary" @click="focusInput">开始规划</el-button>
            </el-empty>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit, MagicStick, Aim, Calendar, Reading, Document,
  User, Star, Download, Share, Collection, Odometer,
  RefreshLeft, ArrowRight
} from '@element-plus/icons-vue'
import { aiApi } from '@/api'

export default {
  name: 'Transition',
  components: {
    Edit, MagicStick, Aim, Calendar, Reading, Document,
    User, Star, Download, Share, Collection, Odometer,
    RefreshLeft, ArrowRight
  },
  setup() {
    const planFormRef = ref(null)
    const generating = ref(false)
    const transitionPlan = ref(null)
    const expandedPhases = ref([0])
    const studyTasks = ref([])

    const planForm = reactive({
      targetSchool: '',
      studentScore: null,
      weakSubjects: [],
      learningStyle: '混合型'
    })

    const planRules = {
      targetSchool: [{ required: true, message: '请选择目标学校', trigger: 'change' }],
      studentScore: [{ required: true, message: '请输入中考分数', trigger: 'blur' }]
    }

    const schoolList = ref([
      '云南师范大学附属中学',
      '昆明市第一中学',
      '昆明市第三中学',
      '昆明市第八中学',
      '昆明市第十中学',
      '云南大学附属中学',
      '昆明市第十二中学',
      '昆明市第十四中学',
      '北大附中云南实验学校',
      '云南衡水实验中学'
    ])

    const totalTasks = ref(0)
    const completedTasks = ref(0)
    const overallProgress = ref(0)
    const studyDays = ref(0)

    const generatePlan = async () => {
      planFormRef.value.validate(async (valid) => {
        if (valid) {
          generating.value = true
          try {
            const response = await aiApi.highSchoolTransition(planForm)
            if (response.success) {
              transitionPlan.value = response.data
              initializeStudyTasks()
              updateProgress()
              ElMessage.success('衔接规划生成成功')
            } else {
              ElMessage.error(response.message || '生成失败')
            }
          } catch (error) {
            console.error('生成规划失败:', error)
            ElMessage.error('生成失败，请稍后重试')
          } finally {
            generating.value = false
          }
        }
      })
    }

    const getDifficultyTag = (difficulty) => {
      const tags = { '较难': 'danger', '中等': 'warning', '较易': 'success' }
      return tags[difficulty] || 'info'
    }

    const downloadPlan = () => {
      ElMessage.success('规划已下载')
    }

    const sharePlan = () => {
      ElMessage.success('分享链接已复制')
    }

    const savePlan = () => {
      ElMessage.success('已保存到个人中心')
    }

    const focusInput = () => {
      document.querySelector('.input-section').scrollIntoView({ behavior: 'smooth' })
    }

    const initializeStudyTasks = () => {
      studyTasks.value = [
        { phase: '第1-2周', content: '了解高中学习特点，制定学习计划', completed: false, subject: '综合', hours: 4 },
        { phase: '第1-2周', content: '预习高中数学第一章集合', completed: false, subject: '数学', hours: 6 },
        { phase: '第1-2周', content: '背诵高中英语核心词汇100个', completed: false, subject: '英语', hours: 5 },
        { phase: '第3-4周', content: '重点预习物理运动学基础', completed: false, subject: '物理', hours: 8 },
        { phase: '第3-4周', content: '学习化学物质的量概念', completed: false, subject: '化学', hours: 6 },
        { phase: '第3-4周', content: '复习初中数学重点知识', completed: false, subject: '数学', hours: 4 },
        { phase: '第5-6周', content: '巩固英语词汇，提升阅读能力', completed: false, subject: '英语', hours: 7 },
        { phase: '第5-6周', content: '预习语文文言文阅读', completed: false, subject: '语文', hours: 5 },
        { phase: '第5-6周', content: '了解高中生物课程体系', completed: false, subject: '生物', hours: 3 },
        { phase: '第7-8周', content: '全面复习，查漏补缺', completed: false, subject: '综合', hours: 8 },
        { phase: '第7-8周', content: '调整心态，做好入学准备', completed: false, subject: '综合', hours: 3 },
        { phase: '第7-8周', content: '准备学习用品和参考书', completed: false, subject: '综合', hours: 2 }
      ]
    }

    const togglePhase = (index) => {
      const idx = expandedPhases.value.indexOf(index)
      if (idx > -1) {
        expandedPhases.value.splice(idx, 1)
      } else {
        expandedPhases.value.push(index)
      }
    }

    const getPhaseTasks = (phase) => {
      return studyTasks.value.filter(task => task.phase === phase)
    }

    const updateProgress = () => {
      const completed = studyTasks.value.filter(t => t.completed).length
      totalTasks.value = studyTasks.value.length
      completedTasks.value = completed
      overallProgress.value = Math.round((completed / totalTasks.value) * 100)
      studyDays.value = Math.ceil(completed / 2)
      
      localStorage.setItem('studyTasks', JSON.stringify(studyTasks.value))
    }

    const getPhaseProgress = (phaseIndex) => {
      if (!transitionPlan.value) return 0
      const phase = transitionPlan.value.timeline[phaseIndex]
      const tasks = studyTasks.value.filter(t => t.phase === phase.phase)
      if (tasks.length === 0) return 0
      const completed = tasks.filter(t => t.completed).length
      return Math.round((completed / tasks.length) * 100)
    }

    const getPhaseProgressType = (phaseIndex) => {
      const progress = getPhaseProgress(phaseIndex)
      if (progress >= 80) return 'success'
      if (progress >= 50) return 'warning'
      return 'info'
    }

    const resetProgress = () => {
      studyTasks.value.forEach(task => task.completed = false)
      updateProgress()
      ElMessage.success('进度已重置')
    }

    const loadSavedProgress = () => {
      const saved = localStorage.getItem('studyTasks')
      if (saved) {
        studyTasks.value = JSON.parse(saved)
        updateProgress()
      }
    }

    onMounted(() => {
      loadSavedProgress()
    })

    return {
      planFormRef,
      generating,
      transitionPlan,
      planForm,
      planRules,
      schoolList,
      generatePlan,
      getDifficultyTag,
      downloadPlan,
      sharePlan,
      savePlan,
      focusInput,
      expandedPhases,
      studyTasks,
      togglePhase,
      getPhaseTasks,
      totalTasks,
      completedTasks,
      overallProgress,
      studyDays,
      updateProgress,
      getPhaseProgress,
      getPhaseProgressType,
      resetProgress
    }
  }
}
</script>

<style scoped>
.transition-page {
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
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
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
  color: #409EFF;
}

.input-section {
  position: sticky;
  top: 20px;
}

.preview-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.preview-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.preview-header .subject {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.preview-content {
  color: #606266;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 30px 0;
}

.empty-section {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-summary {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.progress-stat {
  text-align: center;
}

.progress-value {
  font-size: 28px;
  font-weight: 700;
  color: #409EFF;
}

.progress-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.phase-section {
  margin-bottom: 15px;
}

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.phase-header:hover {
  background: #e6f0ff;
}

.phase-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.phase-title .el-icon {
  transition: transform 0.3s;
}

.phase-title .el-icon.expanded {
  transform: rotate(90deg);
}

.phase-content {
  padding: 15px;
  background: #fafafa;
  border-radius: 0 0 8px 8px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.task-item:last-child {
  border-bottom: none;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-hours {
  font-size: 12px;
  color: #909399;
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

  .action-buttons {
    flex-direction: column;
    align-items: center;
  }

  .progress-summary {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
