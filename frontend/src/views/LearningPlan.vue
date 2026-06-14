<template>
  <div class="learning-plan-page">
    <div class="header-bar">
      <div class="header-left">
        <span class="logo-icon">🦐</span>
        <h1 class="page-title">学习计划生成</h1>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="goBack">返回</el-button>
      </div>
    </div>

    <div class="main-content">
      <div class="plan-form">
        <h2 class="section-title">生成个性化学习计划</h2>
        <el-form :model="form" label-width="120px" class="form-container">
          <el-form-item label="年级">
            <el-select v-model="form.grade" placeholder="请选择年级" class="form-select">
              <el-option label="初一" value="初一" />
              <el-option label="初二" value="初二" />
              <el-option label="初三" value="初三" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="薄弱科目">
            <el-select v-model="form.weakSubjects" multiple placeholder="选择薄弱科目" class="form-select">
              <el-option label="语文" value="语文" />
              <el-option label="数学" value="数学" />
              <el-option label="英语" value="英语" />
              <el-option label="物理" value="物理" />
              <el-option label="化学" value="化学" />
              <el-option label="生物" value="生物" />
              <el-option label="历史" value="历史" />
              <el-option label="地理" value="地理" />
              <el-option label="政治" value="政治" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="目标学校">
            <el-input v-model="form.targetSchool" placeholder="输入目标学校" class="form-input" />
          </el-form-item>
          
          <el-form-item label="可用时间">
            <el-slider v-model="form.availableTime" :min="1" :max="10" :step="0.5" show-input class="form-slider" />
            <span class="time-unit">小时/天</span>
          </el-form-item>
          
          <el-form-item label="学习目标">
            <el-select v-model="form.learningGoal" placeholder="选择学习目标" class="form-select">
              <el-option label="基础巩固" value="基础巩固" />
              <el-option label="成绩提升" value="成绩提升" />
              <el-option label="冲刺高分" value="冲刺高分" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="generatePlan" :loading="loading">生成学习计划</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="plan-result" v-if="showResult">
        <h2 class="section-title">您的个性化学习计划</h2>
        <div class="plan-content" v-html="learningPlan" />
        <div class="plan-actions">
          <el-button type="primary" @click="savePlan">保存计划</el-button>
          <el-button @click="printPlan">打印计划</el-button>
          <el-button @click="sharePlan">分享计划</el-button>
        </div>
      </div>
    </div>

    <footer class="footer-bar">
      <div class="footer-left">
        <span>© 2026 小龙虾择校</span>
        <span class="divider">·</span>
        <span>云南省中考择校智能决策平台</span>
      </div>
      <div class="footer-right">
        <router-link to="/legal/terms">用户协议</router-link>
        <router-link to="/legal/privacy">隐私政策</router-link>
        <router-link to="/legal/copyright">版权声明</router-link>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const showResult = ref(false)
const learningPlan = ref('')

const form = reactive({
  grade: '',
  weakSubjects: [],
  targetSchool: '',
  availableTime: 5,
  learningGoal: ''
})

const generatePlan = async () => {
  // 表单验证
  if (!form.grade) {
    ElMessage.warning('请选择年级')
    return
  }
  
  if (!form.weakSubjects || form.weakSubjects.length === 0) {
    ElMessage.warning('请至少选择一个薄弱科目')
    return
  }
  
  if (!form.targetSchool) {
    ElMessage.warning('请输入目标学校')
    return
  }
  
  if (!form.learningGoal) {
    ElMessage.warning('请选择学习目标')
    return
  }
  
  loading.value = true
  
  try {
    // 模拟API调用，生成学习计划
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 生成学习计划内容
    learningPlan.value = generatePlanContent()
    showResult.value = true
    ElMessage.success('学习计划生成成功')
  } catch (error) {
    ElMessage.error('学习计划生成失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const generatePlanContent = () => {
  const grade = form.grade
  const weakSubjects = form.weakSubjects.join('、')
  const targetSchool = form.targetSchool
  const availableTime = form.availableTime
  const learningGoal = form.learningGoal
  
  let plan = `<div class="plan-header">
    <h3>学习计划概览</h3>
    <p><strong>年级：</strong>${grade}</p>
    <p><strong>薄弱科目：</strong>${weakSubjects}</p>
    <p><strong>目标学校：</strong>${targetSchool}</p>
    <p><strong>可用时间：</strong>${availableTime}小时/天</p>
    <p><strong>学习目标：</strong>${learningGoal}</p>
  </div>`
  
  // 生成每日学习计划
  plan += `<div class="plan-section">
    <h3>每日学习计划</h3>
    <div class="daily-plan">
      <h4>周一至周五</h4>
      <ul>
        <li>06:30-07:00：早读（语文/英语）</li>
        <li>18:00-19:00：完成当天作业</li>
        <li>19:00-20:00：${weakSubjects.split('、')[0]}专项练习</li>
        <li>20:00-21:00：${weakSubjects.split('、').length > 1 ? weakSubjects.split('、')[1] : '数学'}专项练习</li>
        <li>21:00-21:30：总结与复习</li>
      </ul>
      <h4>周六</h4>
      <ul>
        <li>09:00-11:00：模拟测试</li>
        <li>14:00-16:00：薄弱科目集中训练</li>
        <li>16:00-18:00：错题整理</li>
      </ul>
      <h4>周日</h4>
      <ul>
        <li>09:00-11:00：下周学习计划制定</li>
        <li>14:00-16:00：兴趣拓展</li>
        <li>16:00-18:00：放松休息</li>
      </ul>
    </div>
  </div>`
  
  // 生成薄弱科目提升计划
  plan += `<div class="plan-section">
    <h3>薄弱科目提升计划</h3>
    <div class="subject-plan">
      ${form.weakSubjects.map(subject => `
        <div class="subject-item">
          <h4>${subject}</h4>
          <ul>
            <li>基础知识梳理：每周1-2次</li>
            <li>专项练习：每天30-60分钟</li>
            <li>错题整理：每周1次</li>
            <li>模拟测试：每两周1次</li>
          </ul>
        </div>
      `).join('')}
    </div>
  </div>`
  
  // 生成学习方法建议
  plan += `<div class="plan-section">
    <h3>学习方法建议</h3>
    <ul>
      <li>制定详细的学习计划，并严格执行</li>
      <li>定期回顾和总结，及时调整学习策略</li>
      <li>建立错题本，定期复习</li>
      <li>多做模拟测试，熟悉考试题型</li>
      <li>保持良好的作息习惯，保证充足的睡眠</li>
      <li>合理安排时间，避免疲劳学习</li>
      <li>积极参加课外活动，保持身心健康</li>
    </ul>
  </div>`
  
  // 生成目标达成计划
  plan += `<div class="plan-section">
    <h3>目标达成计划</h3>
    <div class="goal-plan">
      <h4>短期目标（1个月）</h4>
      <p>掌握薄弱科目的基础知识，建立知识体系</p>
      <h4>中期目标（3个月）</h4>
      <p>提高薄弱科目的成绩，缩小与目标学校录取分数线的差距</p>
      <h4>长期目标（6个月）</h4>
      <p>达到目标学校的录取分数线，顺利通过中考</p>
    </div>
  </div>`
  
  return plan
}

const resetForm = () => {
  form.grade = ''
  form.weakSubjects = []
  form.targetSchool = ''
  form.availableTime = 5
  form.learningGoal = ''
  showResult.value = false
  learningPlan.value = ''
}

const savePlan = () => {
  // 模拟保存学习计划
  ElMessage.success('学习计划保存成功')
}

const printPlan = () => {
  window.print()
}

const sharePlan = () => {
  // 模拟分享学习计划
  ElMessage.success('学习计划分享成功')
}

const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.learning-plan-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #050508 0%, #0d0d18 40%, #14142a 100%);
  display: flex;
  flex-direction: column;
  color: #fff;
  position: relative;
  overflow: hidden;
}

.learning-plan-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse 100% 60% at 50% 0%, rgba(102, 126, 234, 0.25) 0%, transparent 60%),
    radial-gradient(ellipse 70% 50% at 15% 40%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse 70% 50% at 85% 60%, rgba(240, 147, 251, 0.12) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
  animation: bgPulse 8s ease-in-out infinite alternate;
}

@keyframes bgPulse {
  0% { opacity: 1; }
  100% { opacity: 0.75; }
}

.header-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  background: rgba(5, 5, 12, 0.95);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  z-index: 100;
  box-shadow: 
    0 1px 0 rgba(255, 255, 255, 0.04),
    0 8px 40px rgba(0, 0, 0, 0.6);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.logo-icon {
  font-size: 32px;
  filter: drop-shadow(0 3px 12px rgba(102, 126, 234, 0.5));
  display: inline-block;
  transform: scaleX(-1);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-content {
  flex: 1;
  padding: 100px 40px 80px;
  position: relative;
  z-index: 1;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 24px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.plan-form {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 32px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
}

.form-container {
  max-width: 600px;
}

.form-select,
.form-input {
  width: 100%;
  max-width: 400px;
}

.form-select :deep(.el-select__input) {
  color: #fff;
}

.form-select :deep(.el-select__placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.form-select :deep(.el-select-dropdown) {
  background: #16213e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.form-select :deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.8);
}

.form-select :deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.15);
  color: #fff;
}

.form-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
}

.form-input :deep(.el-input__input) {
  color: #fff;
}

.form-input :deep(.el-input__placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.form-slider {
  max-width: 400px;
  margin-bottom: 16px;
}

.form-slider :deep(.el-slider__bar) {
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.form-slider :deep(.el-slider__button) {
  border-color: #667eea;
}

.time-unit {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 12px;
}

.plan-result {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 32px;
  backdrop-filter: blur(10px);
}

.plan-content {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 32px;
}

.plan-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 16px 0;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  padding-bottom: 8px;
}

.plan-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
  margin: 16px 0 12px 0;
}

.plan-content p {
  margin: 0 0 12px 0;
}

.plan-content ul {
  margin: 0 0 16px 0;
  padding-left: 24px;
}

.plan-content li {
  margin-bottom: 8px;
}

.plan-content strong {
  color: #667eea;
}

.plan-header {
  background: rgba(102, 126, 234, 0.1);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.plan-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.plan-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.subject-plan {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.subject-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.plan-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.plan-actions :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 500;
  font-size: 14px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.plan-actions :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
}

.plan-actions :deep(.el-button) {
  border-radius: 12px;
  padding: 10px 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: transparent;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.plan-actions :deep(.el-button:hover) {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.25);
}

.footer-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  background: linear-gradient(180deg, rgba(8, 8, 16, 0.98) 0%, rgba(18, 18, 31, 0.99) 100%);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  z-index: 100;
  box-shadow: 0 -4px 32px rgba(0, 0, 0, 0.35);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-left .divider {
  color: rgba(255, 255, 255, 0.2);
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 28px;
}

.footer-right a {
  color: rgba(255, 255, 255, 0.35);
  text-decoration: none;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  position: relative;
  padding: 6px 0;
}

.footer-right a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s;
}

.footer-right a:hover {
  color: rgba(255, 255, 255, 0.8);
}

.footer-right a:hover::after {
  width: 100%;
}

@media (max-width: 768px) {
  .header-bar {
    padding: 0 20px;
    height: 60px;
  }
  
  .main-content {
    padding: 80px 20px 70px;
  }
  
  .plan-form,
  .plan-result {
    padding: 24px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .form-container {
    max-width: 100%;
  }
  
  .form-select,
  .form-input,
  .form-slider {
    max-width: 100%;
  }
  
  .subject-plan {
    grid-template-columns: 1fr;
  }
  
  .plan-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .footer-bar {
    flex-direction: column;
    height: auto;
    padding: 16px 20px;
    gap: 12px;
  }
  
  .footer-left, .footer-right {
    flex-wrap: wrap;
    justify-content: center;
    gap: 16px;
  }
  
  .footer-right a {
    font-size: 12px;
  }
}

@media print {
  .header-bar,
  .footer-bar {
    display: none;
  }
  
  .main-content {
    padding: 0;
    margin: 0;
  }
  
  .plan-form {
    display: none;
  }
  
  .plan-result {
    background: none;
    border: none;
    padding: 0;
  }
  
  .plan-actions {
    display: none;
  }
  
  .plan-content {
    color: #000;
  }
  
  .plan-content h3,
  .plan-content h4,
  .plan-content strong {
    color: #000;
  }
  
  .plan-header {
    background: #f5f5f5;
    border: 1px solid #ddd;
  }
  
  .subject-item {
    background: #f5f5f5;
    border: 1px solid #ddd;
  }
}
</style>