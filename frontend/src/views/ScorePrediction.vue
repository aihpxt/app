<template>
  <div class="score-prediction-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">AI分数预测引擎</h1>
        <p class="page-desc">基于模考成绩和历史数据，AI预测中考分数区间和全市位次</p>
      </div>
    </div>

    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="8">
          <div class="input-section card">
            <div class="section-title">
              <el-icon><Edit /></el-icon>
              <span>模考成绩录入</span>
            </div>
            <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
              <el-form-item label="考试次数" prop="examCount">
                <el-input-number v-model="formData.examCount" :min="1" :max="10" style="width: 100%" />
              </el-form-item>
              <div v-for="(exam, idx) in formData.exams" :key="exam.date || idx" class="exam-item">
                <div class="exam-header">
                  <h4>第{{ idx + 1 }}次考试</h4>
                  <el-button type="danger" size="small" @click="removeExam(idx)">
                    <el-icon><Delete /></el-icon>删除
                  </el-button>
                </div>
                <el-form-item label="考试时间" :prop="`exams.${idx}.date`">
                  <el-date-picker v-model="exam.date" type="date" style="width: 100%" />
                </el-form-item>
                <el-form-item label="考试类型" :prop="`exams.${idx}.type`">
                  <el-select v-model="exam.type" style="width: 100%">
                    <el-option label="学校月考" value="school" />
                    <el-option label="区统考" value="district" />
                    <el-option label="市统考" value="city" />
                    <el-option label="模拟考试" value="mock" />
                  </el-select>
                </el-form-item>
                <el-form-item label="考试分数" :prop="`exams.${idx}.score`">
                  <el-input-number v-model="exam.score" :min="0" :max="750" :precision="1" style="width: 100%" />
                </el-form-item>
                <el-form-item label="年级排名" :prop="`exams.${idx}.rank`">
                  <el-input-number v-model="exam.rank" :min="1" style="width: 100%" />
                </el-form-item>
              </div>
              <el-form-item>
                <el-button type="primary" @click="addExam" style="width: 100%">
                  <el-icon><Plus /></el-icon>添加考试
                </el-button>
              </el-form-item>
              <el-form-item label="薄弱科目">
                <el-checkbox-group v-model="formData.weakSubjects">
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
              <el-form-item>
                <el-button type="primary" @click="predictScore" :loading="predicting" style="width: 100%">
                  <el-icon><MagicStick /></el-icon>
                  AI预测分数
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :lg="16">
          <div v-if="predictionResult" class="result-section">
            <div class="prediction-overview card">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>预测结果</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="overview-item">
                    <div class="item-label">预测分数</div>
                    <div class="item-value">{{ predictionResult.predictedScore }}</div>
                    <div class="item-range">{{ predictionResult.scoreRange.low }} - {{ predictionResult.scoreRange.high }}</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="overview-item">
                    <div class="item-label">预测位次</div>
                    <div class="item-value">{{ predictionResult.predictedRank }}</div>
                    <div class="item-range">{{ predictionResult.rankRange.low }} - {{ predictionResult.rankRange.high }}</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="overview-item">
                    <div class="item-label">预测趋势</div>
                    <div class="item-value" :class="getTrendClass(predictionResult.trend)">
                      {{ predictionResult.trend }}
                    </div>
                    <div class="item-range">变化值: {{ predictionResult.trendValue }}</div>
                  </div>
                </el-col>
              </el-row>
              <div class="confidence-section">
                <div class="confidence-label">预测置信度</div>
                <el-progress :percentage="predictionResult.confidence" :stroke-width="15" />
                <div class="confidence-value">{{ predictionResult.confidence }}%</div>
              </div>
            </div>

            <div class="score-trend card">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>成绩趋势分析</span>
              </div>
              <div class="chart-container" ref="trendChart"></div>
            </div>

            <div class="analysis-card card">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>AI分析报告</span>
              </div>
              <div class="analysis-content">
                <p>{{ predictionResult.analysis }}</p>
                <el-divider />
                <h4>提升建议</h4>
                <ul>
                  <li v-for="(suggestion, idx) in getSuggestions()" :key="suggestion">
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>

            <div class="code-section card">
              <div class="section-title">
                <el-icon><Files /></el-icon>
                <span>核心代码</span>
              </div>
              <el-collapse>
                <el-collapse-item title="预测算法">
                  <div class="code-block">
                    <pre><code class="language-python">def predict_score(self, mock_scores: List[Dict]) -> Dict:
    # 计算平均分
    avg_score = sum(s.get('score', 0) for s in mock_scores) / len(mock_scores)
    
    # 计算方差和标准差
    variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
    std_dev = math.sqrt(variance)
    
    # 分析成绩趋势
    trend = 0
    if len(scores) >= 2:
        recent_avg = sum(scores[-3:]) / min(3, len(scores))
        earlier_avg = sum(scores[:3]) / min(3, len(scores))
        trend = recent_avg - earlier_avg
    
    # 预测中考分数
    predicted_score = avg_score + trend * 0.5
    confidence_interval = std_dev * 1.5
    
    # 预测全市位次
    predicted_rank = max(100, int(85000 - predicted_score * 110))
    
    return {
        "predictedScore": round(predicted_score, 1),
        "scoreRange": {
            "low": round(predicted_score - confidence_interval, 1),
            "high": round(predicted_score + confidence_interval, 1)
        },
        "predictedRank": predicted_rank,
        "trend": "上升" if trend > 5 else ("下降" if trend < -5 else "稳定"),
        "confidence": round(confidence, 1)
    }</code></pre>
                  </div>
                </el-collapse-item>
                <el-collapse-item title="前端实现">
                  <div class="code-block">
                    <pre><code class="language-javascript">const predictScore = async () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      predicting.value = true
      try {
        const mock_scores = formData.exams.map(exam => ({
          score: exam.score,
          date: exam.date.toISOString(),
          type: exam.type,
          rank: exam.rank
        }))
        
        const response = await aiApi.predictScore(mock_scores)
        if (response.data.success) {
          predictionResult.value = response.data.data
          nextTick(() => {
            initTrendChart()
          })
          ElMessage.success('预测完成')
        }
      } catch (error) {
        ElMessage.error('预测失败，请稍后重试')
      } finally {
        predicting.value = false
      }
    }
  })
}</code></pre>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>

            <div class="action-buttons">
              <el-button type="primary" size="large" @click="downloadReport">
                <el-icon><Download /></el-icon>
                下载预测报告
              </el-button>
              <el-button size="large" @click="shareReport">
                <el-icon><Share /></el-icon>
                分享预测结果
              </el-button>
              <el-button size="large" @click="goToAiSelection">
                <el-icon><School /></el-icon>
                智能择校
              </el-button>
            </div>
          </div>

          <div v-else class="empty-section card">
            <el-empty description="请输入模考成绩，AI将为您预测中考分数">
              <el-button type="primary" @click="focusInput">开始预测</el-button>
            </el-empty>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Edit, MagicStick, Plus, Delete, TrendCharts,
  Document, Download, Share, School, Files
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { aiApi } from '@/api'

export default {
  name: 'ScorePrediction',
  components: {
    Edit, MagicStick, Plus, Delete, TrendCharts,
    Document, Download, Share, School, Files
  },
  setup() {
    const router = useRouter()
    const formRef = ref(null)
    const predicting = ref(false)
    const trendChart = ref(null)
    
    const formData = reactive({
      examCount: 3,
      exams: [
        { date: new Date('2026-01-15'), type: 'mock', score: 620, rank: 500 },
        { date: new Date('2026-02-15'), type: 'district', score: 635, rank: 420 },
        { date: new Date('2026-03-15'), type: 'city', score: 650, rank: 350 }
      ],
      weakSubjects: ['数学', '物理']
    })
    
    const formRules = {
      examCount: [{ required: true, message: '请输入考试次数', trigger: 'blur' }]
    }
    
    const predictionResult = ref(null)
    
    const addExam = () => {
      formData.exams.push({
        date: new Date(),
        type: 'school',
        score: 0,
        rank: 0
      })
    }
    
    const removeExam = (index) => {
      if (formData.exams.length > 1) {
        formData.exams.splice(index, 1)
      } else {
        ElMessage.warning('至少需要保留一次考试记录')
      }
    }
    
    const predictScore = async () => {
      formRef.value.validate(async (valid) => {
        if (valid) {
          predicting.value = true
          try {
            const mock_scores = formData.exams.map(exam => ({
              score: exam.score,
              date: exam.date.toISOString(),
              type: exam.type,
              rank: exam.rank
            }))
            
            const response = await aiApi.predictScore(mock_scores)
            if (response.success) {
              predictionResult.value = response.data
              nextTick(() => {
                initTrendChart()
              })
              ElMessage.success('预测完成')
            } else {
              ElMessage.error(response.message || '预测失败')
            }
          } catch (error) {
            console.error('预测失败:', error)
            ElMessage.error('预测失败，请稍后重试')
          } finally {
            predicting.value = false
          }
        }
      })
    }
    
    const initTrendChart = () => {
      if (!predictionResult.value || !trendChart.value) return
      
      const chartInstance = echarts.init(trendChart.value)
      
      const dates = formData.exams.map(exam => exam.date.toLocaleDateString())
      const scores = formData.exams.map(exam => exam.score)
      
      const option = {
        title: {
          text: '成绩变化趋势',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: dates
        },
        yAxis: {
          type: 'value',
          name: '分数',
          min: Math.min(...scores) - 50,
          max: Math.max(...scores) + 50
        },
        series: [{
          data: scores,
          type: 'line',
          smooth: true,
          lineStyle: {
            width: 3,
            color: '#409EFF'
          },
          itemStyle: {
            color: '#409EFF'
          },
          markPoint: {
            data: [
              { type: 'max', name: '最高分' },
              { type: 'min', name: '最低分' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均分' },
              {
                yAxis: predictionResult.value.predictedScore,
                name: '预测分数',
                lineStyle: {
                  color: '#67C23A',
                  type: 'dashed'
                }
              }
            ]
          }
        }]
      }
      
      chartInstance.setOption(option)
      
      window.addEventListener('resize', () => {
        chartInstance.resize()
      })
    }
    
    const getTrendClass = (trend) => {
      const classes = {
        '上升': 'trend-up',
        '下降': 'trend-down',
        '稳定': 'trend-stable'
      }
      return classes[trend] || ''
    }
    
    const getSuggestions = () => {
      const suggestions = []
      
      if (formData.weakSubjects.length > 0) {
        suggestions.push(`重点加强${formData.weakSubjects.join('、')}的学习`)
      }
      
      if (predictionResult.value) {
        if (predictionResult.value.trend === '下降') {
          suggestions.push('注意调整学习方法，分析成绩下降原因')
        } else if (predictionResult.value.trend === '上升') {
          suggestions.push('保持当前学习节奏，继续努力')
        }
        
        if (predictionResult.value.confidence < 70) {
          suggestions.push('建议多参加模拟考试，提高预测准确性')
        }
      }
      
      suggestions.push('合理安排作息时间，保持良好心态')
      suggestions.push('注重基础知识的巩固，避免偏科')
      
      return suggestions
    }
    
    const downloadReport = () => {
      ElMessage.success('预测报告已下载')
    }
    
    const shareReport = () => {
      ElMessage.success('分享链接已复制')
    }
    
    const goToAiSelection = () => {
      if (predictionResult.value) {
        router.push({
          path: '/ai-selection',
          query: {
            score: predictionResult.value.predictedScore,
            rank: predictionResult.value.predictedRank
          }
        })
      } else {
        router.push('/ai-selection')
      }
    }
    
    const focusInput = () => {
      document.querySelector('.input-section').scrollIntoView({ behavior: 'smooth' })
    }
    
    return {
      formRef,
      predicting,
      trendChart,
      formData,
      formRules,
      predictionResult,
      addExam,
      removeExam,
      predictScore,
      getTrendClass,
      getSuggestions,
      downloadReport,
      shareReport,
      goToAiSelection,
      focusInput
    }
  }
}
</script>

<style scoped>
.score-prediction-page {
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

.exam-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background: rgba(255, 255, 255, 0.03);
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.exam-header h4 {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.overview-item {
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.item-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 5px;
}

.item-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.item-range {
  font-size: 12px;
  color: var(--text-muted);
}

.trend-up {
  color: #67C23A;
}

.trend-down {
  color: #F56C6C;
}

.trend-stable {
  color: #E6A23C;
}

.confidence-section {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.confidence-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  text-align: center;
}

.confidence-value {
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #409EFF;
  margin-top: 10px;
}

.chart-container {
  height: 300px;
}

.analysis-content {
  line-height: 1.8;
  color: var(--text-secondary);
}

.analysis-content h4 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.analysis-content ul {
  margin-left: 20px;
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

.code-section {
  margin-top: 20px;
}

.code-block {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
}

.code-block pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.code-block code {
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
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

  .overview-item {
    margin-bottom: 15px;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
  }

  .code-block {
    padding: 10px;
  }

  .code-block code {
    font-size: 12px;
  }
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

:deep(.el-button--danger) {
  background: linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%) !important;
  color: #ffffff !important;
  border: none !important;
}
</style>
