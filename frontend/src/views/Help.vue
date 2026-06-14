<template>
  <div class="help-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">帮助中心</h1>
        <p class="page-desc">快速了解平台功能，解决您的疑问</p>
      </div>
    </div>

    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="6">
          <div class="sidebar card">
            <el-menu :default-active="activeSection" @select="handleSectionChange">
              <el-menu-item index="quick-start">
                <el-icon><Service /></el-icon>
                <span>快速入门</span>
              </el-menu-item>
              <el-menu-item index="faq">
                <el-icon><QuestionFilled /></el-icon>
                <span>常见问题</span>
              </el-menu-item>
              <el-menu-item index="guide">
                <el-icon><Reading /></el-icon>
                <span>使用指南</span>
              </el-menu-item>
              <el-menu-item index="video">
                <el-icon><VideoPlay /></el-icon>
                <span>视频教程</span>
              </el-menu-item>
              <el-menu-item index="contact">
                <el-icon><Service /></el-icon>
                <span>联系我们</span>
              </el-menu-item>
            </el-menu>
          </div>
        </el-col>

        <el-col :xs="24" :lg="18">
          <div class="main-content card">
            <div v-if="activeSection === 'quick-start'" class="section">
              <div class="section-title">
              <el-icon><Service /></el-icon>
              <span>快速入门</span>
            </div>
              <div class="quick-start-content">
                <el-steps :active="currentStep" finish-status="success" align-center>
                  <el-step title="注册登录" description="创建您的账号" />
                  <el-step title="完善信息" description="填写考生信息" />
                  <el-step title="AI择校" description="获取智能推荐" />
                  <el-step title="志愿填报" description="完成志愿方案" />
                </el-steps>

                <div class="step-content">
                  <div v-if="currentStep === 0" class="step-detail">
                    <h3>第一步：注册登录</h3>
                    <p>点击页面右上角的"注册"按钮，填写手机号和密码即可完成注册。</p>
                    <div class="step-image-placeholder">
                      <el-icon :size="48"><User /></el-icon>
                      <span>注册登录流程</span>
                    </div>
                    <ul class="step-tips">
                      <li>支持手机号快速注册</li>
                      <li>支持微信扫码登录</li>
                      <li>游客模式可直接体验部分功能</li>
                    </ul>
                  </div>
                  <div v-if="currentStep === 1" class="step-detail">
                    <h3>第二步：完善考生信息</h3>
                    <p>进入个人中心，填写考生的基本信息，包括姓名、学校、成绩等。</p>
                    <div class="step-image-placeholder">
                      <el-icon :size="48"><Edit /></el-icon>
                      <span>完善信息流程</span>
                    </div>
                    <ul class="step-tips">
                      <li>填写模考成绩可提高预测准确度</li>
                      <li>选择正确的州市和区县</li>
                      <li>信息越完整，AI推荐越精准</li>
                    </ul>
                  </div>
                  <div v-if="currentStep === 2" class="step-detail">
                    <h3>第三步：AI智能择校</h3>
                    <p>使用AI智能择校功能，系统将根据您的成绩和偏好推荐合适的学校。</p>
                    <div class="step-image-placeholder">
                      <el-icon :size="48"><MagicStick /></el-icon>
                      <span>AI择校流程</span>
                    </div>
                    <ul class="step-tips">
                      <li>支持多维度筛选条件</li>
                      <li>提供冲刺、稳妥、保底三类推荐</li>
                      <li>可查看学校详细信息和录取概率</li>
                    </ul>
                  </div>
                  <div v-if="currentStep === 3" class="step-detail">
                    <h3>第四步：志愿填报</h3>
                    <p>根据AI推荐结果，完成志愿填报，系统会自动检测风险并给出建议。</p>
                    <div class="step-image-placeholder">
                      <el-icon :size="48"><Document /></el-icon>
                      <span>志愿填报流程</span>
                    </div>
                    <ul class="step-tips">
                      <li>支持模拟志愿填报演练</li>
                      <li>AI自动检测志愿风险</li>
                      <li>可导出志愿表供参考</li>
                    </ul>
                  </div>
                </div>

                <div class="step-actions">
                  <el-button @click="prevStep" :disabled="currentStep === 0">上一步</el-button>
                  <el-button type="primary" @click="nextStep" :disabled="currentStep === 3">下一步</el-button>
                </div>
              </div>
            </div>

            <div v-if="activeSection === 'faq'" class="section">
              <div class="section-title">
                <el-icon><QuestionFilled /></el-icon>
                <span>常见问题</span>
              </div>
              <el-input
                v-model="searchQuestion"
                placeholder="搜索问题..."
                prefix-icon="Search"
                clearable
                style="margin-bottom: 20px;"
              />
              <el-collapse v-model="activeFaq">
                <el-collapse-item
                  v-for="(category, idx) in filteredFaqCategories"
                  :key="category.name"
                  :title="category.name"
                  :name="idx"
                >
                  <div v-for="item in category.questions" :key="item.question" class="faq-item">
                    <div class="faq-question">
                      <el-icon><QuestionFilled /></el-icon>
                      {{ item.question }}
                    </div>
                    <div class="faq-answer">{{ item.answer }}</div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>

            <div v-if="activeSection === 'guide'" class="section">
              <div class="section-title">
                <el-icon><Reading /></el-icon>
                <span>使用指南</span>
              </div>
              <div class="guide-list">
                <div v-for="guide in guides" :key="guide.id" class="guide-card" @click="openGuide(guide)">
                  <div class="guide-icon" :style="{ background: guide.color }">
                    <el-icon :size="32">{{ guide.icon }}</el-icon>
                  </div>
                  <div class="guide-info">
                    <h4>{{ guide.title }}</h4>
                    <p>{{ guide.description }}</p>
                    <div class="guide-meta">
                      <span><el-icon><Clock /></el-icon> {{ guide.duration }}</span>
                      <span><el-icon><View /></el-icon> {{ guide.views }}次阅读</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="activeSection === 'video'" class="section">
              <div class="section-title">
                <el-icon><VideoPlay /></el-icon>
                <span>视频教程</span>
              </div>
              <div class="video-grid">
                <div v-for="video in videos" :key="video.id" class="video-card" @click="playVideo(video)">
                  <div class="video-thumbnail">
                    <div class="thumbnail-placeholder">
                      <el-icon :size="32"><VideoPlay /></el-icon>
                      <span>{{ video.title }}</span>
                    </div>
                    <div class="play-overlay">
                      <el-icon :size="48"><VideoPlay /></el-icon>
                    </div>
                    <span class="video-duration">{{ video.duration }}</span>
                  </div>
                  <div class="video-info">
                    <h4>{{ video.title }}</h4>
                    <p>{{ video.description }}</p>
                    <div class="video-meta">
                      <span><el-icon><View /></el-icon> {{ video.views }}</span>
                      <span><el-icon><Calendar /></el-icon> {{ video.date }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="activeSection === 'contact'" class="section">
              <div class="section-title">
                <el-icon><Service /></el-icon>
                <span>联系我们</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="contact-card">
                    <el-icon :size="40"><Phone /></el-icon>
                    <h4>客服热线</h4>
                    <p>400-888-8888</p>
                    <span>工作时间：9:00-18:00</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="contact-card">
                    <el-icon :size="40"><Message /></el-icon>
                    <h4>在线客服</h4>
                    <p>点击右侧悬浮按钮</p>
                    <span>7x24小时在线</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="contact-card">
                    <el-icon :size="40"><ChatDotRound /></el-icon>
                    <h4>微信公众号</h4>
                    <p>云南省AI择校平台</p>
                    <span>扫码关注获取最新资讯</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="contact-card">
                    <el-icon :size="40"><Location /></el-icon>
                    <h4>公司地址</h4>
                    <p>云南省昆明市五华区</p>
                    <span>科技路88号创新大厦</span>
                  </div>
                </el-col>
              </el-row>

              <el-divider>留言反馈</el-divider>
              <el-form :model="feedbackForm" label-width="80px">
                <el-form-item label="问题类型">
                  <el-select v-model="feedbackForm.type" placeholder="请选择问题类型" style="width: 100%">
                    <el-option label="功能建议" value="suggestion" />
                    <el-option label="问题反馈" value="bug" />
                    <el-option label="合作咨询" value="cooperation" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
                <el-form-item label="联系方式">
                  <el-input v-model="feedbackForm.contact" placeholder="请输入手机号或邮箱" />
                </el-form-item>
                <el-form-item label="问题描述">
                  <el-input
                    v-model="feedbackForm.content"
                    type="textarea"
                    :rows="4"
                    placeholder="请详细描述您的问题或建议..."
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="videoDialogVisible" :title="currentVideo?.title" width="800px">
      <div class="video-content" v-if="currentVideo">
        <div class="video-header">
          <div class="video-info-header">
            <p><el-icon><Clock /></el-icon> 时长：{{ currentVideo.duration }}</p>
            <p><el-icon><View /></el-icon> {{ currentVideo.views }}次观看</p>
            <p><el-icon><Calendar /></el-icon> {{ currentVideo.date }}</p>
          </div>
        </div>
        <el-divider />
        <div class="video-body" v-html="currentVideo.content"></div>
        <el-divider />
        <div class="video-footer">
          <el-button type="primary" @click="videoDialogVisible = false">我知道了</el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="guideDialogVisible" :title="currentGuide?.title" width="800px">
      <div class="guide-content" v-if="currentGuide">
        <div class="guide-header">
          <div class="guide-icon-large" :style="{ background: currentGuide.color }">
            <el-icon :size="48">{{ currentGuide.icon }}</el-icon>
          </div>
          <div class="guide-meta-info">
            <p><el-icon><Clock /></el-icon> 预计阅读时间：{{ currentGuide.duration }}</p>
            <p><el-icon><View /></el-icon> {{ currentGuide.views }}次阅读</p>
          </div>
        </div>
        <el-divider />
        <div class="guide-body" v-html="currentGuide.content"></div>
        <el-divider />
        <div class="guide-footer">
          <el-button type="primary" @click="guideDialogVisible = false">我知道了</el-button>
          <el-button @click="goToFeature(currentGuide.feature)">前往功能</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  QuestionFilled, Reading, VideoPlay, Service,
  Phone, Message, ChatDotRound, Clock, Document, Calendar,
  User, Edit, MagicStick
} from '@element-plus/icons-vue'

export default {
  name: 'Help',
  components: {
    QuestionFilled, Reading, VideoPlay, Service,
    Phone, Message, ChatDotRound, Clock, View: Document, Calendar,
    User, Edit, MagicStick
  },
  setup() {
    const activeSection = ref('quick-start')
    const currentStep = ref(0)
    const searchQuestion = ref('')
    const activeFaq = ref([0])
    const videoDialogVisible = ref(false)
    const currentVideo = ref(null)
    const guideDialogVisible = ref(false)
    const currentGuide = ref(null)

    const feedbackForm = ref({
      type: '',
      contact: '',
      content: ''
    })

    const faqCategories = ref([
      {
        name: '账号相关',
        questions: [
          {
            question: '如何注册账号？',
            answer: '点击页面右上角的"注册"按钮，输入手机号和验证码即可完成注册。注册成功后可使用手机号和密码登录。'
          },
          {
            question: '忘记密码怎么办？',
            answer: '在登录页面点击"忘记密码"，通过手机验证码验证身份后即可重置密码。'
          },
          {
            question: '如何修改个人信息？',
            answer: '登录后进入"个人中心"，点击"个人资料"即可修改昵称、头像等基本信息。'
          }
        ]
      },
      {
        name: 'AI择校',
        questions: [
          {
            question: 'AI择校的准确率如何？',
            answer: '我们的AI择校系统基于5年中考数据训练，预测准确率达到95%以上。但请注意，最终录取结果还受当年招生政策等因素影响。'
          },
          {
            question: '如何提高AI推荐准确度？',
            answer: '建议您完善考生信息，包括模考成绩、排名、所在学校等。信息越完整，AI推荐越精准。'
          },
          {
            question: 'AI推荐的学校可以信任吗？',
            answer: 'AI推荐基于大数据分析，仅供参考。建议结合学校实际情况、学生兴趣特长等因素综合考虑。'
          }
        ]
      },
      {
        name: '志愿填报',
        questions: [
          {
            question: '如何进行志愿填报？',
            answer: '进入"AI志愿填报"页面，系统会根据您的成绩自动推荐志愿方案。您也可以手动调整，系统会实时检测风险。'
          },
          {
            question: '什么是"冲稳保"策略？',
            answer: '"冲稳保"是志愿填报的基本策略：冲刺志愿选择略高于自己分数的学校，稳妥志愿选择与自己分数相当的学校，保底志愿选择低于自己分数的学校。'
          },
          {
            question: '志愿填报有风险吗？',
            answer: '我们的系统会自动检测志愿风险，包括滑档风险、批次错误等。但最终录取结果以官方公布为准。'
          }
        ]
      },
      {
        name: '其他问题',
        questions: [
          {
            question: '平台收费吗？',
            answer: '平台基础功能免费使用，包括AI择校、政策解读等。高级功能如一对一咨询、深度分析报告等可能需要付费。'
          },
          {
            question: '如何联系客服？',
            answer: '您可以通过页面右侧的在线客服按钮、拨打客服热线400-888-8888或在帮助中心留言联系我们。'
          }
        ]
      }
    ])

    const filteredFaqCategories = computed(() => {
      if (!searchQuestion.value) return faqCategories.value
      return faqCategories.value.map(category => ({
        ...category,
        questions: category.questions.filter(
          q => q.question.includes(searchQuestion.value) || q.answer.includes(searchQuestion.value)
        )
      })).filter(category => category.questions.length > 0)
    })

    const guides = ref([
      {
        title: 'AI智能择校使用指南',
        description: '详细介绍如何使用AI智能择校功能，获取个性化学校推荐',
        icon: 'MagicStick',
        color: '#e6f7ff',
        duration: '5分钟',
        views: 12580,
        feature: '/ai-selection',
        content: `
          <h3>一、功能入口</h3>
          <p>登录后，点击导航栏的"AI智能择校"进入功能页面。</p>
          
          <h3>二、填写考生信息</h3>
          <p>系统需要您提供以下信息来进行智能匹配：</p>
          <ul>
            <li><strong>中考总分</strong>：请输入您的实际或预估分数（0-700分）</li>
            <li><strong>区域排名</strong>：如果您知道自己在区/县的排名，请填写</li>
            <li><strong>所在州市</strong>：选择您所在的州市，如昆明市</li>
            <li><strong>所在区县</strong>：填写具体区县，如五华区</li>
            <li><strong>目标类型</strong>：选择重点高中、普通高中或民办学校</li>
            <li><strong>住宿需求</strong>：是否需要住宿</li>
          </ul>
          
          <h3>三、查看推荐结果</h3>
          <p>点击"AI智能分析"后，系统将为您推荐匹配的学校，并显示：</p>
          <ul>
            <li>录取概率：预测您被该校录取的可能性</li>
            <li>匹配度：学校与您需求的匹配程度</li>
            <li>推荐理由：为什么推荐这所学校</li>
          </ul>
          
          <h3>四、进一步操作</h3>
          <p>您可以点击学校名称查看详情，或将学校加入志愿表。</p>
        `
      },
      {
        title: '志愿填报完整流程',
        description: '从信息填写到最终提交，手把手教你完成志愿填报',
        icon: 'Document',
        color: '#f6ffed',
        duration: '10分钟',
        views: 8960,
        feature: '/volunteer',
        content: `
          <h3>一、了解批次规则</h3>
          <p>昆明市中考志愿分为多个批次：</p>
          <ul>
            <li><strong>第一批</strong>：一级一等高中（昆一中、昆三中等）</li>
            <li><strong>第二批</strong>：一级二等、三等高中</li>
            <li><strong>第三批</strong>：普通高中、民办高中</li>
          </ul>
          
          <h3>二、"冲稳保"策略</h3>
          <p>合理分配志愿，确保录取成功率：</p>
          <ul>
            <li><strong>冲刺志愿</strong>：选择略高于自己分数的学校（录取概率40-60%）</li>
            <li><strong>稳妥志愿</strong>：选择与自己分数相当的学校（录取概率70-85%）</li>
            <li><strong>保底志愿</strong>：选择低于自己分数的学校（录取概率90%以上）</li>
          </ul>
          
          <h3>三、使用AI生成志愿</h3>
          <p>进入"AI志愿填报"页面，填写分数和排名，系统将自动生成志愿方案。</p>
          
          <h3>四、风险检测</h3>
          <p>系统会自动检测您的志愿是否存在风险，如滑档风险、批次错误等。</p>
          
          <h3>五、导出志愿表</h3>
          <p>确认无误后，可导出志愿表供参考。</p>
        `
      },
      {
        title: '中考政策解读汇总',
        description: '2026年昆明市中考政策全面解读，帮助家长了解最新变化',
        icon: 'Reading',
        color: '#fff7e6',
        duration: '15分钟',
        views: 15230,
        feature: '/policy',
        content: `
          <h3>一、考试科目与分值</h3>
          <p>2026年昆明中考总分750分，各科目分值如下：</p>
          <ul>
            <li>语文：120分</li>
            <li>数学：120分</li>
            <li>英语：120分（含听力30分）</li>
            <li>物理：100分</li>
            <li>化学：100分</li>
            <li>道德与法治：100分</li>
            <li>历史：100分</li>
            <li>体育：50分</li>
            <li>地理、生物：各20分（初二已考）</li>
          </ul>
          
          <h3>二、录取批次</h3>
          <p>昆明市中考录取分为提前批、第一批、第二批、第三批。</p>
          
          <h3>三、加分政策</h3>
          <p>烈士子女、少数民族考生等可享受加分政策，具体以官方公布为准。</p>
          
          <h3>四、志愿填报时间</h3>
          <p>一般在中考成绩公布后一周内完成志愿填报。</p>
        `
      },
      {
        title: '学校对比分析技巧',
        description: '如何使用学校对比功能，科学选择目标学校',
        icon: 'DataAnalysis',
        color: '#f9f0ff',
        duration: '8分钟',
        views: 6780,
        feature: '/compare',
        content: `
          <h3>一、选择对比学校</h3>
          <p>进入"AI学校对比"页面，选择2-5所您感兴趣的学校进行对比。</p>
          
          <h3>二、对比维度</h3>
          <p>系统将从以下维度进行对比分析：</p>
          <ul>
            <li><strong>录取分数线</strong>：历年最低录取分数</li>
            <li><strong>一本率</strong>：高考一本上线率</li>
            <li><strong>学校等级</strong>：一级一等、一级二等等</li>
            <li><strong>办学性质</strong>：公办/民办</li>
            <li><strong>学费标准</strong>：每年学费金额</li>
            <li><strong>住宿条件</strong>：是否提供住宿</li>
            <li><strong>学校特色</strong>：特色课程、优势学科</li>
          </ul>
          
          <h3>三、AI推荐</h3>
          <p>系统会根据您的分数和需求，推荐最适合的学校。</p>
          
          <h3>四、注意事项</h3>
          <p>对比结果仅供参考，请结合实际情况综合考虑。</p>
        `
      },
      {
        title: 'AI分数预测原理',
        description: '了解AI分数预测背后的算法原理，更好地理解预测结果',
        icon: 'TrendCharts',
        color: '#fff0f6',
        duration: '6分钟',
        views: 9450,
        feature: '/score-prediction',
        content: `
          <h3>一、数据来源</h3>
          <p>AI分数预测基于以下数据：</p>
          <ul>
            <li>您提供的多次模考成绩</li>
            <li>历年中考成绩分布数据</li>
            <li>全市排名变化趋势</li>
          </ul>
          
          <h3>二、预测算法</h3>
          <p>系统采用加权平均算法，综合考虑：</p>
          <ul>
            <li><strong>考试类型权重</strong>：市级统考权重最高，校级考试权重较低</li>
            <li><strong>时间权重</strong>：近期考试权重更高</li>
            <li><strong>趋势分析</strong>：成绩上升/下降趋势</li>
          </ul>
          
          <h3>三、预测结果解读</h3>
          <ul>
            <li><strong>预测分数</strong>：中考可能获得的分数</li>
            <li><strong>分数区间</strong>：置信区间，表示分数的波动范围</li>
            <li><strong>预测位次</strong>：全市排名预测</li>
            <li><strong>置信度</strong>：预测结果的可靠程度</li>
          </ul>
          
          <h3>四、提高预测准确性</h3>
          <p>建议提供至少3次模考成绩，并确保成绩真实准确。</p>
        `
      },
      {
        title: '家长常见误区避坑',
        description: '总结中考择校过程中家长容易犯的错误，帮助您避免踩坑',
        icon: 'Warning',
        color: '#fffbe6',
        duration: '12分钟',
        views: 11200,
        feature: '/ai-selection',
        content: `
          <h3>误区一：只看学校名气</h3>
          <p>很多家长只关注名校，忽略了孩子的实际情况。建议根据孩子的分数和特点选择合适的学校。</p>
          
          <h3>误区二：忽视志愿梯度</h3>
          <p>志愿填报没有拉开梯度，导致滑档。建议按照"冲稳保"策略合理分配志愿。</p>
          
          <h3>误区三：盲目追求热门</h3>
          <p>热门学校竞争激烈，录取分数线可能虚高。建议关注一些性价比高的学校。</p>
          
          <h3>误区四：忽略学校特色</h3>
          <p>不同学校有不同的办学特色，建议选择与孩子兴趣特长相匹配的学校。</p>
          
          <h3>误区五：不关注招生计划</h3>
          <p>招生计划的变化会影响录取分数线，建议关注各校当年的招生人数变化。</p>
          
          <h3>误区六：轻信非官方信息</h3>
          <p>以官方发布的政策为准，不要轻信网上的小道消息。</p>
        `
      }
    ])

    const videos = ref([
      {
        title: '平台功能介绍',
        description: '全面了解平台各项功能',
        duration: '05:32',
        views: '2.3万',
        date: '2026-03-01',
        content: `
          <h3>平台功能概览</h3>
          <p>云南省AI择校平台提供以下核心功能：</p>
          <ul>
            <li><strong>AI智能择校</strong>：根据分数和排名智能推荐学校</li>
            <li><strong>AI分数预测</strong>：基于模考成绩预测中考分数</li>
            <li><strong>AI志愿填报</strong>：智能生成冲稳保志愿方案</li>
            <li><strong>学校查询</strong>：查询云南省各高中详细信息</li>
            <li><strong>学校对比</strong>：多维度对比分析学校</li>
            <li><strong>政策解读</strong>：AI解读中考政策</li>
          </ul>
          <h3>使用建议</h3>
          <p>建议先完善个人信息，然后使用AI择校功能获取推荐，最后进行志愿填报。</p>
        `
      },
      {
        title: 'AI择校实操演示',
        description: '手把手教你使用AI择校',
        duration: '08:45',
        views: '1.8万',
        date: '2026-03-05',
        content: `
          <h3>第一步：进入AI择校页面</h3>
          <p>点击导航栏"AI智能择校"进入功能页面。</p>
          
          <h3>第二步：填写考生信息</h3>
          <ul>
            <li>输入中考总分（如：650分）</li>
            <li>输入区域排名（如：500名）</li>
            <li>选择所在州市（如：昆明市）</li>
            <li>填写所在区县（如：五华区）</li>
            <li>选择目标学校类型</li>
          </ul>
          
          <h3>第三步：查看推荐结果</h3>
          <p>系统会显示匹配的学校列表，包括录取概率、匹配度等信息。</p>
          
          <h3>第四步：查看学校详情</h3>
          <p>点击学校名称可查看详细信息，包括历年录取分数线、学校特色等。</p>
        `
      },
      {
        title: '志愿填报技巧',
        description: '专家讲解志愿填报策略',
        duration: '12:20',
        views: '3.1万',
        date: '2026-03-08',
        content: `
          <h3>一、"冲稳保"策略详解</h3>
          <p>志愿填报的核心策略是"冲稳保"：</p>
          <ul>
            <li><strong>冲刺志愿（1-2个）</strong>：选择略高于自己分数的学校，录取概率40-60%</li>
            <li><strong>稳妥志愿（2-3个）</strong>：选择与自己分数相当的学校，录取概率70-85%</li>
            <li><strong>保底志愿（1-2个）</strong>：选择低于自己分数的学校，录取概率90%以上</li>
          </ul>
          
          <h3>二、批次填报技巧</h3>
          <p>昆明市中考分多个批次录取：</p>
          <ul>
            <li>第一批：重点高中，竞争激烈</li>
            <li>第二批：普通高中，选择空间大</li>
            <li>第三批：民办高中，保底选择</li>
          </ul>
          
          <h3>三、常见错误避免</h3>
          <ul>
            <li>不要全部填报热门学校</li>
            <li>不要忽视保底志愿</li>
            <li>注意批次顺序</li>
          </ul>
        `
      },
      {
        title: '政策解读直播回放',
        description: '2026中考政策解读直播',
        duration: '45:00',
        views: '5.6万',
        date: '2026-03-10',
        content: `
          <h3>2026年昆明中考政策要点</h3>
          
          <h4>一、考试科目与分值</h4>
          <ul>
            <li>语文：120分</li>
            <li>数学：120分</li>
            <li>英语：120分（含听力30分）</li>
            <li>物理：100分</li>
            <li>化学：100分</li>
            <li>道德与法治：100分</li>
            <li>历史：100分</li>
            <li>体育：50分</li>
            <li>地理、生物：各20分</li>
          </ul>
          <p>总分：750分</p>
          
          <h4>二、录取批次变化</h4>
          <p>2026年录取批次保持稳定，分为提前批、第一批、第二批、第三批。</p>
          
          <h4>三、加分政策</h4>
          <ul>
            <li>烈士子女：加20分</li>
            <li>少数民族：加5-10分</li>
            <li>军人子女：按政策执行</li>
          </ul>
          
          <h4>四、志愿填报时间</h4>
          <p>预计在成绩公布后一周内完成志愿填报。</p>
        `
      },
      {
        title: '常见问题解答',
        description: '家长最关心的问题解答',
        duration: '10:15',
        views: '1.2万',
        date: '2026-03-12',
        content: `
          <h3>Q1：AI择校的准确率如何？</h3>
          <p>AI择校基于5年历史数据训练，预测准确率达95%以上。但最终录取结果还受当年招生政策影响。</p>
          
          <h3>Q2：如何提高预测准确度？</h3>
          <p>建议完善考生信息，包括模考成绩、排名等。信息越完整，预测越准确。</p>
          
          <h3>Q3：民办学校和公办学校如何选择？</h3>
          <p>公办学校学费低、师资稳定；民办学校管理灵活、特色鲜明。建议根据家庭经济情况和孩子的特点选择。</p>
          
          <h3>Q4：志愿填报后可以修改吗？</h3>
          <p>在规定时间内可以修改，截止后不可更改。建议提前做好规划。</p>
          
          <h3>Q5：如何查询录取结果？</h3>
          <p>录取结果可通过昆明市教育局官网或学校官方渠道查询。</p>
        `
      },
      {
        title: '成功案例分享',
        description: '往届家长经验分享',
        duration: '15:30',
        views: '2.8万',
        date: '2026-03-14',
        content: `
          <h3>案例一：张同学（2025届）</h3>
          <p><strong>分数</strong>：665分</p>
          <p><strong>录取学校</strong>：昆明市第三中学</p>
          <p><strong>经验分享</strong>：使用AI择校后，发现昆三中是最适合的学校，最终成功录取。建议家长要相信数据，不要盲目追求名校。</p>
          
          <h3>案例二：李同学（2025届）</h3>
          <p><strong>分数</strong>：620分</p>
          <p><strong>录取学校</strong>：官渡区第一中学</p>
          <p><strong>经验分享</strong>：分数不高，但通过合理填报志愿，成功进入理想学校。关键是"冲稳保"策略要执行到位。</p>
          
          <h3>案例三：王同学（2025届）</h3>
          <p><strong>分数</strong>：580分</p>
          <p><strong>录取学校</strong>：昆明仁泽中学（民办）</p>
          <p><strong>经验分享</strong>：选择民办学校也是不错的选择，学校管理严格，小班教学效果很好。</p>
          
          <h3>总结</h3>
          <p>成功的关键：了解自己、了解学校、合理填报。</p>
        `
      }
    ])

    const handleSectionChange = (key) => {
      activeSection.value = key
    }

    const prevStep = () => {
      if (currentStep.value > 0) {
        currentStep.value--
      }
    }

    const nextStep = () => {
      if (currentStep.value < 3) {
        currentStep.value++
      }
    }

    const openGuide = (guide) => {
      currentGuide.value = guide
      guideDialogVisible.value = true
    }

    const allowedPaths = ['/', '/school', '/policy', '/ai-assistant', '/volunteer', '/compare', '/user']
    
    const goToFeature = (feature) => {
      if (feature && allowedPaths.includes(feature)) {
        window.location.href = feature
      }
    }

    const playVideo = (video) => {
      currentVideo.value = video
      videoDialogVisible.value = true
    }

    const submitFeedback = () => {
      if (!feedbackForm.value.type || !feedbackForm.value.content) {
        ElMessage.warning('请填写完整信息')
        return
      }
      ElMessage.success('感谢您的反馈，我们会尽快处理')
      feedbackForm.value = {
        type: '',
        contact: '',
        content: ''
      }
    }

    return {
      activeSection,
      currentStep,
      searchQuestion,
      activeFaq,
      filteredFaqCategories,
      guides,
      videos,
      videoDialogVisible,
      currentVideo,
      guideDialogVisible,
      currentGuide,
      feedbackForm,
      handleSectionChange,
      prevStep,
      nextStep,
      openGuide,
      goToFeature,
      playVideo,
      submitFeedback
    }
  }
}
</script>

<style scoped>
.help-page {
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
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.sidebar {
  position: sticky;
  top: 20px;
}

.main-content {
  min-height: 600px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #409EFF;
}

.section-title .el-icon {
  color: #409EFF;
}

.quick-start-content {
  padding: 20px 0;
}

.step-content {
  margin: 40px 0;
}

.step-detail {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
}

.step-detail h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 15px;
}

.step-detail p {
  color: #606266;
  margin-bottom: 20px;
}

.step-image {
  width: 100%;
  max-width: 600px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.step-tips {
  padding-left: 20px;
  color: #606266;
}

.step-tips li {
  margin-bottom: 8px;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.faq-item {
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.faq-question .el-icon {
  color: #409EFF;
}

.faq-answer {
  color: #606266;
  line-height: 1.8;
  padding-left: 26px;
}

.guide-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.guide-card {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  cursor: pointer;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.guide-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.guide-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
  flex-shrink: 0;
}

.guide-info h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.guide-info p {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
  line-height: 1.5;
}

.guide-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #c0c4cc;
}

.guide-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.video-card {
  background: #f5f7fa;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.video-thumbnail {
  position: relative;
  height: 160px;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s;
}

.video-card:hover .play-overlay {
  opacity: 1;
}

.video-duration {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.video-info {
  padding: 15px;
}

.video-info h4 {
  font-size: 15px;
  color: #303133;
  margin-bottom: 8px;
}

.video-info p {
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
}

.video-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #c0c4cc;
}

.video-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.contact-card {
  text-align: center;
  padding: 30px 20px;
  background: #f5f7fa;
  border-radius: 12px;
  margin-bottom: 20px;
}

.contact-card .el-icon {
  color: #409EFF;
  margin-bottom: 15px;
}

.contact-card h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 10px;
}

.contact-card p {
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8px;
}

.contact-card span {
  font-size: 13px;
  color: #909399;
}

.video-player {
  background: #000;
  border-radius: 8px;
  height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-placeholder {
  text-align: center;
  color: #fff;
}

.guide-content {
  padding: 10px;
}

.guide-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.guide-icon-large {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
}

.guide-meta-info {
  color: #909399;
  font-size: 14px;
}

.guide-meta-info p {
  margin: 5px 0;
  display: flex;
  align-items: center;
  gap: 5px;
}

.guide-body {
  line-height: 1.8;
  color: #303133;
}

.guide-body h3 {
  color: #303133;
  margin: 20px 0 10px;
  font-size: 16px;
  border-left: 3px solid #409EFF;
  padding-left: 10px;
}

.guide-body h3:first-child {
  margin-top: 0;
}

.guide-body p {
  margin: 10px 0;
  color: #606266;
}

.guide-body ul {
  padding-left: 20px;
  margin: 10px 0;
}

.guide-body li {
  margin: 8px 0;
  color: #606266;
}

.guide-body strong {
  color: #303133;
}

.guide-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.video-content {
  padding: 10px;
}

.video-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.video-info-header {
  color: #909399;
  font-size: 14px;
}

.video-info-header p {
  margin: 5px 0;
  display: flex;
  align-items: center;
  gap: 5px;
}

.video-body {
  line-height: 1.8;
  color: #303133;
}

.video-body h3 {
  color: #303133;
  margin: 20px 0 10px;
  font-size: 16px;
  border-left: 3px solid #67C23A;
  padding-left: 10px;
}

.video-body h3:first-child {
  margin-top: 0;
}

.video-body h4 {
  color: #303133;
  margin: 15px 0 10px;
  font-size: 15px;
}

.video-body p {
  margin: 10px 0;
  color: #606266;
}

.video-body ul {
  padding-left: 20px;
  margin: 10px 0;
}

.video-body li {
  margin: 8px 0;
  color: #606266;
}

.video-body strong {
  color: #303133;
}

.video-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.player-placeholder .el-icon {
  margin-bottom: 20px;
}

.video-url {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.step-image-placeholder {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin: 20px 0;
}

.step-image-placeholder .el-icon {
  margin-bottom: 10px;
  opacity: 0.9;
}

.step-image-placeholder span {
  font-size: 16px;
  font-weight: 500;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.thumbnail-placeholder .el-icon {
  margin-bottom: 8px;
}

.thumbnail-placeholder span {
  font-size: 12px;
  text-align: center;
  padding: 0 10px;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }

  .guide-list,
  .video-grid {
    grid-template-columns: 1fr;
  }

  .step-actions {
    flex-direction: column;
  }
}
</style>
