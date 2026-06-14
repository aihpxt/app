<template>
  <div class="test-page">
    <div class="page-header">
      <h1 class="page-title">在线测试</h1>
      <p class="page-subtitle">模拟中考考试，提升应试能力</p>
    </div>

    <div class="test-container">
      <el-card class="test-list-card">
        <template #header>
          <div class="card-header">
            <h3>可用测试</h3>
            <el-tag type="primary" size="small">{{ tests.length }} 个测试</el-tag>
          </div>
        </template>
        <div class="test-list">
          <div
            v-for="test in tests"
            :key="test.id"
            class="test-item"
          >
            <div class="test-info">
              <h4 class="test-title">{{ test.title }}</h4>
              <p class="test-description">{{ test.description }}</p>
              <div class="test-meta">
                <el-tag size="small" :type="getDifficultyType(test.difficulty)">
                  {{ test.difficulty }}
                </el-tag>
                <el-tag size="small" type="info">
                  {{ test.type === 'comprehensive' ? '综合测试' : test.subject + '专项' }}
                </el-tag>
                <span class="test-duration">{{ test.duration }} 分钟</span>
                <span class="test-score">{{ test.totalScore }} 分</span>
                <span class="test-questions">{{ test.questionCount }} 题</span>
              </div>
            </div>
            <div class="test-actions">
              <el-button type="primary" @click="viewTestDetail(test)">
                查看详情
              </el-button>
              <el-button type="success" @click="startTest(test)">
                开始测试
              </el-button>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="test-history-card">
        <template #header>
          <div class="card-header">
            <h3>测试历史</h3>
            <el-tag type="info" size="small">{{ history.length }} 次测试</el-tag>
          </div>
        </template>
        <el-table :data="history" style="width: 100%">
          <el-table-column prop="testTitle" label="测试名称" min-width="200" />
          <el-table-column prop="testDate" label="测试时间" width="180" />
          <el-table-column prop="score" label="得分" width="100">
            <template #default="scope">
              <span :class="getScoreClass(scope.row.score, scope.row.totalScore)">
                {{ scope.row.score }}/{{ scope.row.totalScore }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="accuracy" label="正确率" width="100">
            <template #default="scope">
              <el-progress
                :percentage="scope.row.accuracy"
                :stroke-width="8"
                :format="() => scope.row.accuracy + '%'"
              />
            </template>
          </el-table-column>
          <el-table-column prop="result" label="结果" width="100">
            <template #default="scope">
              <el-tag :type="getResultType(scope.row.result)">
                {{ scope.row.result }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="用时" width="100">
            <template #default="scope">
              {{ scope.row.duration }} 分钟
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button type="primary" size="small" @click="viewTestResult(scope.row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 测试详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="selectedTest?.title || '测试详情'"
      width="800px"
    >
      <div v-if="selectedTest" class="test-detail">
        <div class="detail-section">
          <h4>测试信息</h4>
          <el-descriptions :column="2">
            <el-descriptions-item label="测试类型">
              {{ selectedTest.type === 'comprehensive' ? '综合测试' : selectedTest.subject + '专项' }}
            </el-descriptions-item>
            <el-descriptions-item label="测试时长">
              {{ selectedTest.duration }} 分钟
            </el-descriptions-item>
            <el-descriptions-item label="总分">
              {{ selectedTest.totalScore }} 分
            </el-descriptions-item>
            <el-descriptions-item label="题目数量">
              {{ selectedTest.questionCount }} 题
            </el-descriptions-item>
            <el-descriptions-item label="难度">
              <el-tag :type="getDifficultyType(selectedTest.difficulty)">
                {{ selectedTest.difficulty }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag type="success">可测试</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="detail-section">
          <h4>测试说明</h4>
          <ul class="instructions-list">
            <li v-for="(instruction, idx) in selectedTest.instructions" :key="instruction">
              {{ idx + 1 }}. {{ instruction }}
            </li>
          </ul>
        </div>
        <div class="detail-section" v-if="selectedTest.sections">
          <h4>测试科目</h4>
          <el-table :data="selectedTest.sections" style="width: 100%">
            <el-table-column prop="name" label="科目" />
            <el-table-column prop="score" label="分值" />
            <el-table-column prop="questionCount" label="题目数量" />
            <el-table-column prop="duration" label="建议时长(分钟)" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button type="primary" @click="startTest(selectedTest)">
            开始测试
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 测试答题弹窗 -->
    <el-dialog
      v-model="showTestDialog"
      :title="currentTest?.title || '测试答题'"
      width="1000px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="test-taking">
        <!-- 顶部信息栏 -->
        <div class="test-header">
          <div class="test-info">
            <h3>{{ currentTest?.title }}</h3>
            <p>{{ currentTest?.description }}</p>
          </div>
          <div class="test-stats">
            <div class="timer">
              <el-icon><Clock /></el-icon>
              <span :class="{ 'time-warning': remainingTime < 300, 'time-danger': remainingTime < 60 }">
                {{ formatTime(remainingTime) }}
              </span>
            </div>
            <div class="question-stats">
              <span>已答: {{ answeredCount }}/{{ currentTest?.questionCount || 0 }}</span>
              <span>剩余: {{ (currentTest?.questionCount || 0) - answeredCount }}</span>
            </div>
          </div>
        </div>

        <!-- 题目导航 -->
        <div class="question-nav">
          <div
            v-for="(q, index) in currentTest?.questions"
            :key="q.id"
            class="question-nav-item"
            :class="{
              'answered': answers[index] !== null,
              'current': currentQuestionIndex === index,
              'flagged': flaggedQuestions.includes(index)
            }"
            @click="goToQuestion(index)"
          >
            {{ index + 1 }}
          </div>
        </div>

        <!-- 题目内容 -->
        <div class="question-content" v-if="currentQuestion">
          <div class="question-header">
            <h4>第 {{ currentQuestionIndex + 1 }} 题 ({{ currentQuestion.score }}分)</h4>
            <el-button type="info" size="small" @click="toggleFlag(currentQuestionIndex)">
              {{ flaggedQuestions.includes(currentQuestionIndex) ? '取消标记' : '标记' }}
            </el-button>
          </div>
          <div class="question-text">
            {{ currentQuestion.text }}
          </div>
          <div class="question-options" v-if="currentQuestion.type === 'multiple-choice'">
            <div
              v-for="(option, optIndex) in currentQuestion.options"
              :key="optIndex"
              class="option-item"
              :class="{ 'selected': answers[currentQuestionIndex] === optIndex }"
              @click="selectOption(optIndex)"
            >
              <span class="option-label">{{ String.fromCharCode(65 + optIndex) }}</span>
              <span class="option-text">{{ option }}</span>
            </div>
          </div>
          <div class="question-actions">
            <el-button @click="prevQuestion" :disabled="currentQuestionIndex === 0">
              上一题
            </el-button>
            <el-button @click="nextQuestion" :disabled="currentQuestionIndex === (currentTest?.questions.length || 0) - 1">
              下一题
            </el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="confirmSubmit">
            提交测试
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 测试结果弹窗 -->
    <el-dialog
      v-model="showResultDialog"
      title="测试结果"
      width="800px"
    >
      <div class="test-result" v-if="testResult">
        <div class="result-header">
          <div class="score-section">
            <h2 class="score">{{ testResult.score }}/{{ testResult.totalScore }}</h2>
            <el-tag :type="getResultType(testResult.result)">
              {{ testResult.result }}
            </el-tag>
          </div>
          <div class="stats-section">
            <el-descriptions :column="2">
              <el-descriptions-item label="测试用时">
                {{ testResult.duration }} 分钟
              </el-descriptions-item>
              <el-descriptions-item label="正确率">
                {{ testResult.accuracy }}%
              </el-descriptions-item>
              <el-descriptions-item label="答对题目">
                {{ testResult.correctCount }} 题
              </el-descriptions-item>
              <el-descriptions-item label="答错题目">
                {{ testResult.incorrectCount }} 题
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
        <div class="result-detail">
          <h4>答题情况</h4>
          <el-progress
            :percentage="testResult.accuracy"
            :stroke-width="20"
            :format="() => testResult.accuracy + '%'"
          />
          <div class="question-analysis">
            <h5>题目分析</h5>
            <div class="analysis-item" v-for="(analysis, idx) in testResult.questionAnalysis" :key="analysis.questionText || idx">
              <div class="analysis-header">
                <span>第 {{ idx + 1 }} 题</span>
                <el-tag :type="analysis.correct ? 'success' : 'danger'">
                  {{ analysis.correct ? '正确' : '错误' }}
                </el-tag>
              </div>
              <div class="analysis-content">
                <p>{{ analysis.questionText }}</p>
                <p v-if="analysis.correct">您的答案: {{ analysis.userAnswer }}</p>
                <p v-else>
                  您的答案: {{ analysis.userAnswer }}<br>
                  正确答案: {{ analysis.correctAnswer }}
                </p>
                <p v-if="analysis.explanation" class="explanation">
                  <strong>解析:</strong> {{ analysis.explanation }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showResultDialog = false">关闭</el-button>
          <el-button type="primary" @click="viewTestResultDetail">
            查看详细分析
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Star, Timer } from '@element-plus/icons-vue'
import { aiApi } from '@/api'

export default {
  name: 'OnlineTest',
  components: {
    Clock,
    Star,
    Timer
  },
  setup() {
    const loading = ref(false)
    const tests = ref([])
    const history = ref([])
    const showDetailDialog = ref(false)
    const selectedTest = ref(null)
    const showTestDialog = ref(false)
    const showResultDialog = ref(false)
    const currentTest = ref(null)
    const currentQuestionIndex = ref(0)
    const answers = ref([])
    const flaggedQuestions = ref([])
    const remainingTime = ref(0)
    const testResult = ref(null)
    const timer = ref(null)

    const loadTests = async () => {
      loading.value = true
      try {
        const response = await aiApi.getTestList()
        if (response.success) {
          tests.value = response.data
        }
      } catch (error) {
        ElMessage.error('加载测试列表失败')
      } finally {
        loading.value = false
      }
    }

    const loadHistory = async () => {
      try {
        const response = await aiApi.getTestHistory()
        if (response.success) {
          history.value = response.data
        }
      } catch (error) {
        ElMessage.error('加载测试历史失败')
      }
    }

    const getDifficultyType = (difficulty) => {
      const typeMap = {
        '简单': 'success',
        '中等': 'primary',
        '较难': 'warning',
        '困难': 'danger'
      }
      return typeMap[difficulty] || 'info'
    }

    const getScoreClass = (score, total) => {
      const percentage = (score / total) * 100
      if (percentage >= 90) return 'high-score'
      if (percentage >= 75) return 'medium-score'
      if (percentage >= 60) return 'pass-score'
      return 'low-score'
    }

    const getResultType = (result) => {
      const typeMap = {
        '优秀': 'success',
        '良好': 'primary',
        '及格': 'warning',
        '不及格': 'danger'
      }
      return typeMap[result] || 'info'
    }

    const viewTestDetail = async (test) => {
      try {
        const response = await aiApi.getTestDetail(test.id)
        if (response.success) {
          selectedTest.value = response.data
          showDetailDialog.value = true
        }
      } catch (error) {
        ElMessage.error('加载测试详情失败')
      }
    }

    const startTest = async (test) => {
      try {
        const response = await aiApi.startTest(test.id, {})
        if (response.success) {
          // 获取测试详情
          const detailResponse = await aiApi.getTestDetail(test.id)
          if (detailResponse.success) {
            currentTest.value = detailResponse.data
            currentQuestionIndex.value = 0
            answers.value = Array(currentTest.value.questionCount).fill(null)
            flaggedQuestions.value = []
            remainingTime.value = currentTest.value.duration * 60
            showTestDialog.value = true
            showDetailDialog.value = false
            
            // 开始计时
            startTimer()
          }
        }
      } catch (error) {
        ElMessage.error('开始测试失败')
      }
    }

    const startTimer = () => {
      if (timer.value) {
        clearInterval(timer.value)
      }
      timer.value = setInterval(() => {
        if (remainingTime.value > 0) {
          remainingTime.value--
        } else {
          clearInterval(timer.value)
          submitTest()
        }
      }, 1000)
    }

    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    const currentQuestion = computed(() => {
      if (!currentTest.value || !currentTest.value.questions) return null
      return currentTest.value.questions[currentQuestionIndex.value]
    })

    const answeredCount = computed(() => {
      return answers.value.filter(answer => answer !== null).length
    })

    const goToQuestion = (index) => {
      currentQuestionIndex.value = index
    }

    const selectOption = (optionIndex) => {
      answers.value[currentQuestionIndex.value] = optionIndex
    }

    const prevQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--
      }
    }

    const nextQuestion = () => {
      if (currentQuestionIndex.value < (currentTest.value?.questions.length || 0) - 1) {
        currentQuestionIndex.value++
      }
    }

    const toggleFlag = (index) => {
      const flagIndex = flaggedQuestions.value.indexOf(index)
      if (flagIndex > -1) {
        flaggedQuestions.value.splice(flagIndex, 1)
      } else {
        flaggedQuestions.value.push(index)
      }
    }

    const confirmSubmit = () => {
      ElMessageBox.confirm('确定要提交测试吗？提交后无法修改答案。', '提交测试', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        submitTest()
      }).catch(() => {
        // 取消提交
      })
    }

    const submitTest = async () => {
      if (timer.value) {
        clearInterval(timer.value)
        timer.value = null
      }

      try {
        const response = await aiApi.submitTest(currentTest.value.id, {
          answers: answers.value,
          duration: currentTest.value.duration * 60 - remainingTime.value
        })
        if (response.success) {
          testResult.value = response.data
          showTestDialog.value = false
          showResultDialog.value = true
        }
      } catch (error) {
        ElMessage.error('提交测试失败')
      }
    }

    const viewTestResult = (test) => {
      // 模拟测试结果
      testResult.value = {
        score: test.score,
        totalScore: test.totalScore,
        result: test.result,
        duration: test.duration,
        accuracy: test.accuracy,
        correctCount: Math.floor(test.accuracy / 100 * 10),
        incorrectCount: 10 - Math.floor(test.accuracy / 100 * 10),
        questionAnalysis: [
          {
            correct: true,
            questionText: '下列哪个是二次函数？',
            userAnswer: 'y = x² + 1',
            correctAnswer: 'y = x² + 1',
            explanation: '二次函数的一般形式为y = ax² + bx + c，其中a≠0。'
          },
          {
            correct: false,
            questionText: '下列哪个是无理数？',
            userAnswer: '0.5',
            correctAnswer: '√2',
            explanation: '无理数是不能表示为两个整数之比的实数，√2是无理数，而0.5是有理数。'
          }
        ]
      }
      showResultDialog.value = true
    }

    const viewTestResultDetail = () => {
      ElMessage.info('查看详细分析功能开发中...')
    }

    onMounted(() => {
      loadTests()
      loadHistory()
    })

    onUnmounted(() => {
      if (timer.value) {
        clearInterval(timer.value)
      }
    })

    return {
      loading,
      tests,
      history,
      showDetailDialog,
      selectedTest,
      showTestDialog,
      showResultDialog,
      currentTest,
      currentQuestionIndex,
      answers,
      flaggedQuestions,
      remainingTime,
      testResult,
      getDifficultyType,
      getScoreClass,
      getResultType,
      viewTestDetail,
      startTest,
      formatTime,
      currentQuestion,
      answeredCount,
      goToQuestion,
      selectOption,
      prevQuestion,
      nextQuestion,
      toggleFlag,
      confirmSubmit,
      viewTestResult,
      viewTestResultDetail
    }
  }
}
</script>

<style scoped>
.test-page {
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
  border-radius: 16px;
  margin: 0 0 30px 0;
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

.test-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-list-card,
.test-history-card {
  border-radius: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.test-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.test-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
}

.test-item:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.test-info {
  flex: 1;
}

.test-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.test-description {
  margin: 0 0 15px 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.test-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.test-duration,
.test-score,
.test-questions {
  color: var(--text-muted);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.test-actions {
  display: flex;
  gap: 10px;
}

.test-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.instructions-list {
  margin: 0;
  padding-left: 20px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.instructions-list li {
  margin-bottom: 8px;
}

.high-score {
  color: #67C23A;
  font-weight: 600;
}

.medium-score {
  color: #409EFF;
  font-weight: 600;
}

.pass-score {
  color: #E6A23C;
  font-weight: 600;
}

.low-score {
  color: #F56C6C;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 测试答题相关样式 */
.test-taking {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.test-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.test-info p {
  margin: 0;
  color: var(--text-secondary);
}

.test-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.timer {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.time-warning {
  color: #E6A23C;
}

.time-danger {
  color: #F56C6C;
}

.question-stats {
  display: flex;
  gap: 15px;
  color: var(--text-secondary);
  font-size: 14px;
}

.question-nav {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.question-nav-item {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  color: var(--text-secondary);
}

.question-nav-item:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.question-nav-item.answered {
  background: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.3);
  color: #67C23A;
}

.question-nav-item.current {
  background: var(--primary-gradient);
  color: #fff;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.question-nav-item.flagged {
  background: rgba(230, 162, 60, 0.1);
  border-color: rgba(230, 162, 60, 0.3);
  color: #E6A23C;
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-secondary);
}

.option-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(102, 126, 234, 0.2);
}

.option-item.selected {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
  color: var(--text-primary);
}

.option-label {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-secondary);
}

.option-item.selected .option-label {
  background: var(--primary-gradient);
  color: #fff;
}

.question-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

/* 测试结果样式 */
.test-result {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.score-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.score {
  font-size: 48px;
  font-weight: 600;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.stats-section {
  flex: 1;
  margin-left: 30px;
}

.result-detail {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-analysis {
  margin-top: 10px;
}

.analysis-item {
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 10px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.analysis-content {
  line-height: 1.6;
  color: var(--text-secondary);
}

.explanation {
  margin-top: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .test-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .test-actions {
    align-self: flex-end;
  }

  .test-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .test-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .test-stats {
    align-items: flex-start;
  }

  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }

  .stats-section {
    margin-left: 0;
    width: 100%;
  }

  .question-nav {
    justify-content: center;
  }
}

:deep(.el-card) {
  background: transparent;
  border: none;
}

:deep(.el-button--primary) {
  background: var(--primary-gradient);
  border: none;
  border-radius: 12px;
  padding: 0 20px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.el-button) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-primary);
  border-radius: 12px;
  padding: 0 20px;
  height: 44px;
  font-size: 15px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

:deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.4);
}

:deep(.el-table) {
  background: transparent;
  color: var(--text-secondary);
}

:deep(.el-table th.el-table__cell) {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell) {
  background: rgba(102, 126, 234, 0.1);
}

:deep(.el-descriptions__label) {
  color: var(--text-muted);
}

:deep(.el-descriptions__content) {
  color: var(--text-secondary);
}

:deep(.el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  backdrop-filter: blur(20px);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-dialog__title) {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  color: var(--text-secondary);
}

:deep(.el-dialog__footer) {
  border-top: 1px solid var(--border-color);
}

:deep(.el-progress__text) {
  color: var(--text-secondary);
}
</style>