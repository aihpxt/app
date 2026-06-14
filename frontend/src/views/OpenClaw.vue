<template>
  <div class="openclaw-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">OpenClaw 小龙虾智能体</h1>
        <p class="page-desc">智能问答、政策解读、志愿生成，一站式AI助手</p>
      </div>
    </div>

    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="8">
          <div class="chat-section card">
            <div class="section-title">
              <el-icon><ChatLineRound /></el-icon>
              <span>智能问答</span>
            </div>
            <div class="chat-container">
              <div class="chat-messages" ref="chatMessages">
                <div v-for="(message, idx) in chatMessages" :key="message.id || idx" class="message-item" :class="message.type">
                  <div class="message-content">{{ message.content }}</div>
                  <div class="message-time">{{ message.time }}</div>
                </div>
              </div>
              <div class="chat-input">
                <el-input
                  v-model="chatInput"
                  placeholder="请输入您的问题，例如：什么是指标到校政策？"
                  @keyup.enter="sendMessage"
                  clearable
                />
                <el-button type="primary" @click="sendMessage" :loading="chatLoading">
                  <el-icon><Send /></el-icon>
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :lg="16">
          <div class="function-section">
            <div class="function-card card">
              <div class="section-title">
                <el-icon><Grid /></el-icon>
                <span>功能导航</span>
              </div>
              <el-row :gutter="15">
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('analyze')">
                    <el-icon class="function-icon"><DataAnalysis /></el-icon>
                    <h3>智能分析</h3>
                    <p>分析学生数据，生成个性化报告</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('generate-plan')">
                    <el-icon class="function-icon"><Operation /></el-icon>
                    <h3>志愿生成</h3>
                    <p>根据分数和排名生成志愿方案</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('interpret-policy')">
                    <el-icon class="function-icon"><Document /></el-icon>
                    <h3>政策解读</h3>
                    <p>智能解读中考政策，解答疑问</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('user-profile')">
                    <el-icon class="function-icon"><User /></el-icon>
                    <h3>用户画像</h3>
                    <p>创建和分析用户个人画像</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('validate-volunteer')">
                    <el-icon class="function-icon"><Check /></el-icon>
                    <h3>志愿验证</h3>
                    <p>验证志愿表的合理性和风险</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('crawl')">
                    <el-icon class="function-icon"><Refresh /></el-icon>
                    <h3>数据采集</h3>
                    <p>启动爬虫采集最新教育数据</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('school-compare')">
                    <el-icon class="function-icon"><DataAnalysis /></el-icon>
                    <h3>学校比较</h3>
                    <p>多维度对比不同学校</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('admission-calculator')">
                    <el-icon class="function-icon"><Calculator /></el-icon>
                    <h3>录取计算器</h3>
                    <p>预测录取概率</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('career-planning')">
                    <el-icon class="function-icon"><Briefcase /></el-icon>
                    <h3>职业规划</h3>
                    <p>基于兴趣推荐职业</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('school-map')">
                    <el-icon class="function-icon"><Map /></el-icon>
                    <h3>学校地图</h3>
                    <p>可视化学校地理分布</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('scholarship')">
                    <el-icon class="function-icon"><Coin /></el-icon>
                    <h3>奖学金信息</h3>
                    <p>查询各类奖学金</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('learning-resources')">
                    <el-icon class="function-icon"><Book /></el-icon>
                    <h3>学习资源</h3>
                    <p>推荐学习资料</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('campus-activities')">
                    <el-icon class="function-icon"><Calendar /></el-icon>
                    <h3>校园活动</h3>
                    <p>查看重要考试和活动</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('school-environment')">
                    <el-icon class="function-icon"><Location /></el-icon>
                    <h3>周边环境</h3>
                    <p>分析学校周边环境</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-card shadow="hover" class="function-item" @click="navigateTo('personalized-learning')">
                    <el-icon class="function-icon"><MagicStick /></el-icon>
                    <h3>学习计划</h3>
                    <p>生成个性化学习方案</p>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <div v-if="selectedFunction === 'analyze'" class="analyze-card card">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>智能分析</span>
              </div>
              <el-form :model="analyzeForm" :rules="analyzeRules" ref="analyzeFormRef" label-width="100px">
                <el-form-item label="中考分数" prop="score">
                  <el-input-number v-model="analyzeForm.score" :min="0" :max="750" style="width: 100%" />
                </el-form-item>
                <el-form-item label="排名" prop="rank">
                  <el-input-number v-model="analyzeForm.rank" :min="1" style="width: 100%" />
                </el-form-item>
                <el-form-item label="薄弱科目">
                  <el-checkbox-group v-model="analyzeForm.weakSubjects">
                    <el-checkbox label="语文">语文</el-checkbox>
                    <el-checkbox label="数学">数学</el-checkbox>
                    <el-checkbox label="英语">英语</el-checkbox>
                    <el-checkbox label="物理">物理</el-checkbox>
                    <el-checkbox label="化学">化学</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="generateAnalysis" :loading="analyzeLoading" style="width: 100%">
                    <el-icon><MagicStick /></el-icon>
                    生成分析报告
                  </el-button>
                </el-form-item>
              </el-form>
              <div v-if="analysisResult" class="analysis-result">
                <h3>分析报告</h3>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="标题">{{ analysisResult.title }}</el-descriptions-item>
                  <el-descriptions-item label="摘要">{{ analysisResult.summary }}</el-descriptions-item>
                </el-descriptions>
                <div v-if="analysisResult.sections" class="analysis-sections">
                  <h4>详细分析</h4>
                  <el-collapse>
                    <el-collapse-item :title="section.title" v-for="(section, idx) in analysisResult.sections" :key="section.title || idx">
                      {{ section.content }}
                    </el-collapse-item>
                  </el-collapse>
                </div>
                <div v-if="analysisResult.recommendations" class="analysis-recommendations">
                  <h4>建议</h4>
                  <el-list>
                    <el-list-item v-for="(recommendation, idx) in analysisResult.recommendations" :key="recommendation">
                      {{ recommendation }}
                    </el-list-item>
                  </el-list>
                </div>
              </div>
            </div>

            <div v-if="selectedFunction === 'crawl'" class="crawl-card card">
              <div class="section-title">
                <el-icon><Refresh /></el-icon>
                <span>数据采集</span>
              </div>
              <el-form :model="crawlForm" ref="crawlFormRef">
                <el-form-item label="采集类型">
                  <el-radio-group v-model="crawlForm.type">
                    <el-radio value="all">全部</el-radio>
                    <el-radio value="policy">政策数据</el-radio>
                    <el-radio value="school">学校数据</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="startCrawl" :loading="crawlLoading" style="width: 100%">
                    <el-icon><Refresh /></el-icon>
                    开始采集
                  </el-button>
                </el-form-item>
              </el-form>
              <div v-if="crawlResult" class="crawl-result">
                <el-alert
                  :title="crawlResult.success ? '采集成功' : '采集失败'"
                  :type="crawlResult.success ? 'success' : 'error'"
                  show-icon
                />
                <div v-if="crawlResult.data && crawlResult.data.data" class="crawl-data">
                  <h4>采集结果</h4>
                  <el-table :data="crawlResult.data.data" style="width: 100%">
                    <el-table-column prop="title" label="标题" min-width="200" />
                    <el-table-column prop="date" label="日期" width="120" />
                    <el-table-column prop="source" label="来源" width="150" />
                    <el-table-column prop="type" label="类型" width="100" />
                  </el-table>
                </div>
              </div>
            </div>

            <div v-if="selectedFunction === 'interpret-policy'" class="policy-card card">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>政策解读</span>
              </div>
              <el-form :model="policyForm" :rules="policyRules" ref="policyFormRef">
                <el-form-item label="政策问题" prop="question">
                  <el-input
                    v-model="policyForm.question"
                    type="textarea"
                    placeholder="请输入您的政策问题，例如：什么是指标到校政策？"
                    rows="4"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="interpretPolicy" :loading="policyLoading" style="width: 100%">
                    <el-icon><MagicStick /></el-icon>
                    解读政策
                  </el-button>
                </el-form-item>
              </el-form>
              <div v-if="policyResult" class="policy-result">
                <h3>政策解读</h3>
                <el-card>
                  <h4>问题：{{ policyResult.question }}</h4>
                  <p class="policy-answer">{{ policyResult.answer }}</p>
                  <div class="policy-meta">
                    <span>置信度：{{ (policyResult.confidence * 100).toFixed(1) }}%</span>
                    <span>来源：{{ policyResult.source }}</span>
                  </div>
                </el-card>
              </div>
            </div>

            <!-- 学校比较 -->
            <div v-if="selectedFunction === 'school-compare'" class="school-compare-card card">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>学校比较</span>
              </div>
              <el-form :model="schoolCompareForm" ref="schoolCompareFormRef">
                <el-form-item label="学校1">
                  <el-input v-model="schoolCompareForm.school1" placeholder="请输入学校名称" />
                </el-form-item>
                <el-form-item label="学校2">
                  <el-input v-model="schoolCompareForm.school2" placeholder="请输入学校名称" />
                </el-form-item>
                <el-form-item label="学校3">
                  <el-input v-model="schoolCompareForm.school3" placeholder="请输入学校名称（可选）" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="compareSchools" :loading="schoolCompareLoading" style="width: 100%">
                    <el-icon><DataAnalysis /></el-icon>
                    开始比较
                  </el-button>
                </el-form-item>
              </el-form>
              <div v-if="schoolCompareResult" class="school-compare-result">
                <h3>比较结果</h3>
                <el-table :data="schoolCompareResult.schools" style="width: 100%">
                  <el-table-column prop="name" label="学校名称" width="150" />
                  <el-table-column prop="type" label="学校类型" width="120" />
                  <el-table-column prop="district" label="所在区域" width="120" />
                  <el-table-column prop="ranking" label="排名" width="80" />
                  <el-table-column prop="admissionScore" label="录取分数线" width="120" />
                  <el-table-column prop="teacherStudentRatio" label="师生比" width="100" />
                  <el-table-column prop="facilitiesScore" label="设施评分" width="100" />
                </el-table>
              </div>
            </div>

            <!-- 录取计算器 -->
            <div v-if="selectedFunction === 'admission-calculator'" class="admission-calculator-card card">
              <div class="section-title">
                <el-icon><Calculator /></el-icon>
                <span>录取计算器</span>
              </div>
              <el-form :model="admissionCalculatorForm" :rules="admissionCalculatorRules" ref="admissionCalculatorFormRef">
                <el-form-item label="中考分数" prop="score">
                  <el-input-number v-model="admissionCalculatorForm.score" :min="0" :max="750" style="width: 100%" />
                </el-form-item>
                <el-form-item label="排名" prop="rank">
                  <el-input-number v-model="admissionCalculatorForm.rank" :min="1" style="width: 100%" />
                </el-form-item>
                <el-form-item label="目标学校" prop="schoolName">
                  <el-input v-model="admissionCalculatorForm.schoolName" placeholder="请输入目标学校名称" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="calculateAdmission" :loading="admissionCalculatorLoading" style="width: 100%">
                    <el-icon><Calculator /></el-icon>
                    计算录取概率
                  </el-button>
                </el-form-item>
              </el-form>
              <div v-if="admissionCalculatorResult" class="admission-calculator-result">
                <h3>录取概率分析</h3>
                <el-card>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="目标学校">{{ admissionCalculatorResult.schoolName }}</el-descriptions-item>
                    <el-descriptions-item label="录取概率">{{ (admissionCalculatorResult.admissionProbability * 100).toFixed(1) }}%</el-descriptions-item>
                    <el-descriptions-item label="建议">{{ admissionCalculatorResult.suggestion }}</el-descriptions-item>
                  </el-descriptions>
                  <div class="probability-chart" style="margin-top: 20px">
                    <el-progress :percentage="admissionCalculatorResult.admissionProbability * 100" :color="getProgressColor(admissionCalculatorResult.admissionProbability)" />
                  </div>
                </el-card>
              </div>
            </div>

            <!-- 职业规划 -->
            <div v-if="selectedFunction === 'career-planning'" class="career-planning-card card">
              <div class="section-title">
                <el-icon><Briefcase /></el-icon>
                <span>职业规划</span>
              </div>
              <el-form :model="careerPlanningForm" ref="careerPlanningFormRef">
                <el-form-item label="兴趣爱好">
                  <el-checkbox-group v-model="careerPlanningForm.interests">
                    <el-checkbox label="科学">科学</el-checkbox>
                    <el-checkbox label="艺术">艺术</el-checkbox>
                    <el-checkbox label="技术">技术</el-checkbox>
                    <el-checkbox label="商业">商业</el-checkbox>
                    <el-checkbox label="教育">教育</el-checkbox>
                    <el-checkbox label="医疗">医疗</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item label="优势学科">
                  <el-checkbox-group v-model="careerPlanningForm.strongSubjects">
                    <el-checkbox label="语文">语文</el-checkbox>
                    <el-checkbox label="数学">数学</el-checkbox>
                    <el-checkbox label="英语">英语</el-checkbox>
                    <el-checkbox label="物理">物理</el-checkbox>
                    <el-checkbox label="化学">化学</el-checkbox>
                    <el-checkbox label="生物">生物</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="generateCareerPlan" :loading="careerPlanningLoading" style="width: 100%">
                    <el-icon><Briefcase /></el-icon>
                    生成职业规划
                  </el-button>
                </el-form-item>
              </el-form>
              <div v-if="careerPlanningResult" class="career-planning-result">
                <h3>职业规划建议</h3>
                <el-card v-for="career in careerPlanningResult.recommendedCareers" :key="career.career" style="margin-bottom: 15px">
                  <h4>{{ career.career }}</h4>
                  <p>匹配度：{{ (career.matchScore * 100).toFixed(1) }}%</p>
                  <p>推荐理由：{{ career.reason }}</p>
                  <p>相关专业：{{ career.relatedMajors.join('、') }}</p>
                </el-card>
              </div>
            </div>

            <!-- 学校地图 -->
            <div v-if="selectedFunction === 'school-map'" class="school-map-card card">
              <div class="section-title">
                <el-icon><Map /></el-icon>
                <span>学校地图</span>
              </div>
              <el-form :model="schoolMapForm" ref="schoolMapFormRef">
                <el-form-item label="区域">
                  <el-select v-model="schoolMapForm.district" placeholder="选择区域">
                    <el-option label="全部" value="all" />
                    <el-option label="五华区" value="五华区" />
                    <el-option label="盘龙区" value="盘龙区" />
                    <el-option label="官渡区" value="官渡区" />
                    <el-option label="西山区" value="西山区" />
                    <el-option label="呈贡区" value="呈贡区" />
                  </el-select>
                </el-form-item>
                <el-form-item label="学校类型">
                  <el-select v-model="schoolMapForm.type" placeholder="选择学校类型">
                    <el-option label="全部" value="all" />
                    <el-option label="公立高中" value="公立高中" />
                    <el-option label="民办高中" value="民办高中" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="getSchoolMap" :loading="schoolMapLoading" style="width: 100%">
                    <el-icon><Map /></el-icon>
                    获取学校地图
                  </el-button>
                </el-form-item>
              </div>
              <div v-if="schoolMapResult" class="school-map-result">
                <h3>学校分布</h3>
                <div class="map-container" style="height: 400px; background: #f5f7fa; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                  <div class="map-placeholder">
                    <el-icon class="map-icon"><Map /></el-icon>
                    <p>学校地图可视化</p>
                    <p>共 {{ schoolMapResult.schools.length }} 所学校</p>
                  </div>
                </div>
                <el-table :data="schoolMapResult.schools" style="width: 100%; margin-top: 20px">
                  <el-table-column prop="name" label="学校名称" />
                  <el-table-column prop="address" label="地址" />
                  <el-table-column prop="district" label="区域" width="100" />
                </el-table>
              </div>
            </div>

            <!-- 奖学金信息 -->
            <div v-if="selectedFunction === 'scholarship'" class="scholarship-card card">
              <div class="section-title">
                <el-icon><Coin /></el-icon>
                <span>奖学金信息</span>
              </div>
              <el-form :model="scholarshipForm" ref="scholarshipFormRef">
                <el-form-item label="奖学金类型">
                  <el-select v-model="scholarshipForm.type" placeholder="选择奖学金类型">
                    <el-option label="全部" value="all" />
                    <el-option label="国家级" value="国家级" />
                    <el-option label="省级" value="省级" />
                    <el-option label="市级" value="市级" />
                    <el-option label="校级" value="校级" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="getScholarshipInfo" :loading="scholarshipLoading" style="width: 100%">
                    <el-icon><Coin /></el-icon>
                    查询奖学金
                  </el-button>
                </el-form-item>
              </div>
              <div v-if="scholarshipResult" class="scholarship-result">
                <h3>奖学金信息</h3>
                <el-table :data="scholarshipResult.scholarships" style="width: 100%">
                  <el-table-column prop="name" label="奖学金名称" />
                  <el-table-column prop="type" label="类型" width="100" />
                  <el-table-column prop="amount" label="金额" width="100" />
                  <el-table-column prop="eligibility" label="申请条件" />
                </el-table>
              </div>
            </div>

            <!-- 学习资源 -->
            <div v-if="selectedFunction === 'learning-resources'" class="learning-resources-card card">
              <div class="section-title">
                <el-icon><Book /></el-icon>
                <span>学习资源</span>
              </div>
              <el-form :model="learningResourcesForm" ref="learningResourcesFormRef">
                <el-form-item label="学科">
                  <el-select v-model="learningResourcesForm.subject" placeholder="选择学科">
                    <el-option label="全部" value="all" />
                    <el-option label="语文" value="语文" />
                    <el-option label="数学" value="数学" />
                    <el-option label="英语" value="英语" />
                    <el-option label="物理" value="物理" />
                    <el-option label="化学" value="化学" />
                  </el-select>
                </el-form-item>
                <el-form-item label="资源类型">
                  <el-select v-model="learningResourcesForm.type" placeholder="选择资源类型">
                    <el-option label="全部" value="all" />
                    <el-option label="视频课程" value="视频课程" />
                    <el-option label="习题练习" value="习题练习" />
                    <el-option label="学习资料" value="学习资料" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="getLearningResources" :loading="learningResourcesLoading" style="width: 100%">
                    <el-icon><Book /></el-icon>
                    获取学习资源
                  </el-button>
                </el-form-item>
              </div>
              <div v-if="learningResourcesResult" class="learning-resources-result">
                <h3>学习资源推荐</h3>
                <el-table :data="learningResourcesResult.resources" style="width: 100%">
                  <el-table-column prop="title" label="资源标题" />
                  <el-table-column prop="subject" label="学科" width="100" />
                  <el-table-column prop="type" label="类型" width="120" />
                  <el-table-column prop="level" label="难度" width="80" />
                  <el-table-column prop="recommendationScore" label="推荐度" width="100" />
                </el-table>
              </div>
            </div>

            <!-- 校园活动 -->
            <div v-if="selectedFunction === 'campus-activities'" class="campus-activities-card card">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                <span>校园活动</span>
              </div>
              <el-form :model="campusActivitiesForm" ref="campusActivitiesFormRef">
                <el-form-item label="活动类型">
                  <el-select v-model="campusActivitiesForm.type" placeholder="选择活动类型">
                    <el-option label="全部" value="all" />
                    <el-option label="考试" value="考试" />
                    <el-option label="招生" value="招生" />
                    <el-option label="校园活动" value="校园活动" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="getCampusActivities" :loading="campusActivitiesLoading" style="width: 100%">
                    <el-icon><Calendar /></el-icon>
                    获取活动日历
                  </el-button>
                </el-form-item>
              </div>
              <div v-if="campusActivitiesResult" class="campus-activities-result">
                <h3>校园活动日历</h3>
                <el-table :data="campusActivitiesResult.activities" style="width: 100%">
                  <el-table-column prop="title" label="活动名称" />
                  <el-table-column prop="date" label="日期" width="120" />
                  <el-table-column prop="type" label="类型" width="100" />
                  <el-table-column prop="description" label="描述" />
                </el-table>
              </div>
            </div>

            <!-- 学校周边环境 -->
            <div v-if="selectedFunction === 'school-environment'" class="school-environment-card card">
              <div class="section-title">
                <el-icon><Location /></el-icon>
                <span>学校周边环境</span>
              </div>
              <el-form :model="schoolEnvironmentForm" :rules="schoolEnvironmentRules" ref="schoolEnvironmentFormRef">
                <el-form-item label="学校名称" prop="schoolName">
                  <el-input v-model="schoolEnvironmentForm.schoolName" placeholder="请输入学校名称" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="getSchoolEnvironment" :loading="schoolEnvironmentLoading" style="width: 100%">
                    <el-icon><Location /></el-icon>
                    分析周边环境
                  </el-button>
                </el-form-item>
              </div>
              <div v-if="schoolEnvironmentResult" class="school-environment-result">
                <h3>{{ schoolEnvironmentResult.schoolName }} 周边环境分析</h3>
                <el-card>
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="交通便利度">{{ schoolEnvironmentResult.environmentScore.transportation }}分</el-descriptions-item>
                    <el-descriptions-item label="生活便利度">{{ schoolEnvironmentResult.environmentScore.living }}分</el-descriptions-item>
                    <el-descriptions-item label="教育资源">{{ schoolEnvironmentResult.environmentScore.education }}分</el-descriptions-item>
                    <el-descriptions-item label="安全指数">{{ schoolEnvironmentResult.environmentScore.safety }}分</el-descriptions-item>
                  </el-descriptions>
                  <div class="environment-facilities" style="margin-top: 20px">
                    <h4>周边设施</h4>
                    <el-tag v-for="facility in schoolEnvironmentResult.nearbyFacilities" :key="facility" style="margin: 5px">
                      {{ facility }}
                    </el-tag>
                  </div>
                </el-card>
              </div>
            </div>

            <!-- 个性化学习计划 -->
            <div v-if="selectedFunction === 'personalized-learning'" class="personalized-learning-card card">
              <div class="section-title">
                <el-icon><MagicStick /></el-icon>
                <span>个性化学习计划</span>
              </div>
              <el-form :model="personalizedLearningForm" :rules="personalizedLearningRules" ref="personalizedLearningFormRef">
                <el-form-item label="学生ID" prop="studentId">
                  <el-input v-model="personalizedLearningForm.studentId" placeholder="请输入学生ID" />
                </el-form-item>
                <el-form-item label="目标分数" prop="targetScore">
                  <el-input-number v-model="personalizedLearningForm.targetScore" :min="0" :max="750" style="width: 100%" />
                </el-form-item>
                <el-form-item label="优势科目">
                  <el-checkbox-group v-model="personalizedLearningForm.strengths">
                    <el-checkbox label="语文">语文</el-checkbox>
                    <el-checkbox label="数学">数学</el-checkbox>
                    <el-checkbox label="英语">英语</el-checkbox>
                    <el-checkbox label="物理">物理</el-checkbox>
                    <el-checkbox label="化学">化学</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item label="薄弱科目">
                  <el-checkbox-group v-model="personalizedLearningForm.weaknesses">
                    <el-checkbox label="语文">语文</el-checkbox>
                    <el-checkbox label="数学">数学</el-checkbox>
                    <el-checkbox label="英语">英语</el-checkbox>
                    <el-checkbox label="物理">物理</el-checkbox>
                    <el-checkbox label="化学">化学</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="generatePersonalizedLearningPlan" :loading="personalizedLearningLoading" style="width: 100%">
                    <el-icon><MagicStick /></el-icon>
                    生成学习计划
                  </el-button>
                </el-form-item>
              </div>
              <div v-if="personalizedLearningResult" class="personalized-learning-result">
                <h3>个性化学习计划</h3>
                <el-card>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="学生ID">{{ personalizedLearningResult.studentId }}</el-descriptions-item>
                    <el-descriptions-item label="目标分数">{{ personalizedLearningResult.targetScore }}</el-descriptions-item>
                    <el-descriptions-item label="总天数">{{ personalizedLearningResult.totalDays }}天</el-descriptions-item>
                    <el-descriptions-item label="每天学习时间">{{ personalizedLearningResult.dailyHours }}小时</el-descriptions-item>
                  </el-descriptions>
                  <div class="plan-phases" style="margin-top: 20px">
                    <h4>学习阶段</h4>
                    <el-collapse>
                      <el-collapse-item :title="phase.phase" v-for="(phase, idx) in personalizedLearningResult.plan.phases" :key="phase.phase || idx">
                        <p>持续时间：{{ phase.duration }}天</p>
                        <p>重点：{{ phase.focus }}</p>
                        <p>任务：</p>
                        <ul>
                          <li v-for="task in phase.tasks" :key="task">{{ task }}</li>
                        </ul>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </el-card>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, reactive, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatLineRound, Send, Grid, DataAnalysis, Operation, Document,
  User, Check, Refresh, MagicStick, Plus, Briefcase, MapLocation,
  Coin, Book, Calendar
} from '@element-plus/icons-vue'
import { aiServiceApi } from '@/api'

export default {
  name: 'OpenClaw',
  components: {
    ChatLineRound, Send, Grid, DataAnalysis, Operation, Document,
    User, Check, Refresh, MagicStick, Calculator: Plus, Briefcase, Map: MapLocation,
    Coin, Book, Calendar
  },
  setup() {
    const chatMessages = ref([
      {
        type: 'system',
        content: '你好！我是 OpenClaw 小龙虾智能体，有什么可以帮助你的吗？',
        time: new Date().toLocaleTimeString()
      }
    ])
    const chatInput = ref('')
    const chatLoading = ref(false)
    const chatMessagesRef = ref(null)
    
    const selectedFunction = ref('')
    
    const analyzeForm = reactive({
      score: null,
      rank: null,
      weakSubjects: []
    })
    const analyzeRules = {
      score: [{ required: true, message: '请输入中考分数', trigger: 'blur' }],
      rank: [{ required: true, message: '请输入排名', trigger: 'blur' }]
    }
    const analyzeFormRef = ref(null)
    const analyzeLoading = ref(false)
    const analysisResult = ref(null)
    
    const crawlForm = reactive({
      type: 'all'
    })
    const crawlFormRef = ref(null)
    const crawlLoading = ref(false)
    const crawlResult = ref(null)
    
    const policyForm = reactive({
      question: ''
    })
    const policyRules = {
      question: [{ required: true, message: '请输入政策问题', trigger: 'blur' }]
    }
    const policyFormRef = ref(null)
    const policyLoading = ref(false)
    const policyResult = ref(null)
    
    // 学校比较
    const schoolCompareForm = reactive({
      school1: '',
      school2: '',
      school3: ''
    })
    const schoolCompareFormRef = ref(null)
    const schoolCompareLoading = ref(false)
    const schoolCompareResult = ref(null)
    
    // 录取计算器
    const admissionCalculatorForm = reactive({
      score: null,
      rank: null,
      schoolName: ''
    })
    const admissionCalculatorRules = {
      score: [{ required: true, message: '请输入中考分数', trigger: 'blur' }],
      rank: [{ required: true, message: '请输入排名', trigger: 'blur' }],
      schoolName: [{ required: true, message: '请输入目标学校名称', trigger: 'blur' }]
    }
    const admissionCalculatorFormRef = ref(null)
    const admissionCalculatorLoading = ref(false)
    const admissionCalculatorResult = ref(null)
    
    // 职业规划
    const careerPlanningForm = reactive({
      interests: [],
      strongSubjects: []
    })
    const careerPlanningFormRef = ref(null)
    const careerPlanningLoading = ref(false)
    const careerPlanningResult = ref(null)
    
    // 学校地图
    const schoolMapForm = reactive({
      district: 'all',
      type: 'all'
    })
    const schoolMapFormRef = ref(null)
    const schoolMapLoading = ref(false)
    const schoolMapResult = ref(null)
    
    // 奖学金信息
    const scholarshipForm = reactive({
      type: 'all'
    })
    const scholarshipFormRef = ref(null)
    const scholarshipLoading = ref(false)
    const scholarshipResult = ref(null)
    
    // 学习资源
    const learningResourcesForm = reactive({
      subject: 'all',
      type: 'all'
    })
    const learningResourcesFormRef = ref(null)
    const learningResourcesLoading = ref(false)
    const learningResourcesResult = ref(null)
    
    // 校园活动
    const campusActivitiesForm = reactive({
      type: 'all'
    })
    const campusActivitiesFormRef = ref(null)
    const campusActivitiesLoading = ref(false)
    const campusActivitiesResult = ref(null)
    
    // 学校周边环境
    const schoolEnvironmentForm = reactive({
      schoolName: ''
    })
    const schoolEnvironmentRules = {
      schoolName: [{ required: true, message: '请输入学校名称', trigger: 'blur' }]
    }
    const schoolEnvironmentFormRef = ref(null)
    const schoolEnvironmentLoading = ref(false)
    const schoolEnvironmentResult = ref(null)
    
    // 个性化学习计划
    const personalizedLearningForm = reactive({
      studentId: '',
      targetScore: null,
      strengths: [],
      weaknesses: []
    })
    const personalizedLearningRules = {
      studentId: [{ required: true, message: '请输入学生ID', trigger: 'blur' }],
      targetScore: [{ required: true, message: '请输入目标分数', trigger: 'blur' }]
    }
    const personalizedLearningFormRef = ref(null)
    const personalizedLearningLoading = ref(false)
    const personalizedLearningResult = ref(null)
    
    const sendMessage = async () => {
      if (!chatInput.value.trim()) {
        ElMessage.warning('请输入您的问题')
        return
      }
      
      // 添加用户消息
      chatMessages.value.push({
        type: 'user',
        content: chatInput.value,
        time: new Date().toLocaleTimeString()
      })
      
      const question = chatInput.value
      chatInput.value = ''
      chatLoading.value = true
      
      try {
        const response = await aiServiceApi.openclawChat({ 
          question, 
          session_id: 'openclaw_session' 
        })
        if (response.success) {
          // 添加系统回复
          chatMessages.value.push({
            type: 'system',
            content: response.data.answer,
            time: new Date().toLocaleTimeString()
          })
          // 成功提示
          ElMessage.success('回答生成成功')
        } else {
          chatMessages.value.push({
            type: 'system',
            content: '抱歉，我暂时无法回答您的问题，请稍后再试。',
            time: new Date().toLocaleTimeString()
          })
          ElMessage.error('智能问答失败')
        }
      } catch (error) {
        console.error('智能问答失败:', error)
        chatMessages.value.push({
          type: 'system',
          content: '抱歉，系统出现错误，请稍后再试。',
          time: new Date().toLocaleTimeString()
        })
        ElMessage.error('网络错误，请检查网络连接')
      } finally {
        chatLoading.value = false
        // 滚动到底部
        nextTick(() => {
          if (chatMessagesRef.value) {
            chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
          }
        })
      }
    }
    
    const navigateTo = (functionName) => {
      selectedFunction.value = functionName
    }
    
    const generateAnalysis = async () => {
      analyzeFormRef.value.validate(async (valid) => {
        if (valid) {
          analyzeLoading.value = true
          try {
            const response = await aiServiceApi.openclawAnalyze({ studentData: analyzeForm })
            if (response.success) {
              analysisResult.value = response.data
              ElMessage.success('分析报告生成成功')
            } else {
              ElMessage.error('生成失败')
            }
          } catch (error) {
            console.error('生成分析报告失败:', error)
            ElMessage.error('生成失败，请稍后重试')
          } finally {
            analyzeLoading.value = false
          }
        }
      })
    }
    
    const startCrawl = async () => {
      crawlLoading.value = true
      try {
        const response = await aiServiceApi.openclawCrawl({ type: crawlForm.type })
        crawlResult.value = response
        if (response.success) {
          ElMessage.success('数据采集成功')
        } else {
          ElMessage.error('数据采集失败')
        }
      } catch (error) {
        console.error('数据采集失败:', error)
        ElMessage.error('数据采集失败，请稍后重试')
      } finally {
        crawlLoading.value = false
      }
    }
    
    const interpretPolicy = async () => {
      policyFormRef.value.validate(async (valid) => {
        if (valid) {
          policyLoading.value = true
          try {
            const response = await aiServiceApi.openclawInterpretPolicy({ question: policyForm.question })
            if (response.success) {
              policyResult.value = response.data
              ElMessage.success('政策解读成功')
            } else {
              ElMessage.error('解读失败')
            }
          } catch (error) {
            console.error('政策解读失败:', error)
            ElMessage.error('解读失败，请稍后重试')
          } finally {
            policyLoading.value = false
          }
        }
      })
    }
    
    // 学校比较方法
    const compareSchools = async () => {
      schoolCompareLoading.value = true
      try {
        const response = await aiApi.enhancedCrawlSchoolCompare({ schools: [schoolCompareForm.school1, schoolCompareForm.school2, schoolCompareForm.school3].filter(Boolean) })
        if (response.success) {
          schoolCompareResult.value = response.data.schoolComparison
          ElMessage.success('学校比较成功')
        } else {
          ElMessage.error('比较失败')
        }
      } catch (error) {
        console.error('学校比较失败:', error)
        ElMessage.error('比较失败，请稍后重试')
      } finally {
        schoolCompareLoading.value = false
      }
    }
    
    // 录取计算器方法
    const calculateAdmission = async () => {
      admissionCalculatorFormRef.value.validate(async (valid) => {
        if (valid) {
          admissionCalculatorLoading.value = true
          try {
            const response = await aiApi.enhancedCrawlAdmissionCalculator({
              score: admissionCalculatorForm.score,
              rank: admissionCalculatorForm.rank,
              schoolName: admissionCalculatorForm.schoolName
            })
            if (response.success) {
              admissionCalculatorResult.value = response.data.admissionCalculator
              ElMessage.success('录取概率计算成功')
            } else {
              ElMessage.error('计算失败')
            }
          } catch (error) {
            console.error('录取概率计算失败:', error)
            ElMessage.error('计算失败，请稍后重试')
          } finally {
            admissionCalculatorLoading.value = false
          }
        }
      })
    }
    
    // 职业规划方法
    const generateCareerPlan = async () => {
      careerPlanningLoading.value = true
      try {
        const response = await aiApi.enhancedCrawlCareerPlanning({
          interests: careerPlanningForm.interests,
          strongSubjects: careerPlanningForm.strongSubjects
        })
        if (response.success) {
          careerPlanningResult.value = response.data.careerPlanning
          ElMessage.success('职业规划生成成功')
        } else {
          ElMessage.error('生成失败')
        }
      } catch (error) {
        console.error('职业规划生成失败:', error)
        ElMessage.error('生成失败，请稍后重试')
      } finally {
        careerPlanningLoading.value = false
      }
    }
    
    // 学校地图方法
    const getSchoolMap = async () => {
      schoolMapLoading.value = true
      try {
        const response = await aiApi.enhancedCrawlSchoolMap({
          district: schoolMapForm.district,
          type: schoolMapForm.type
        })
        if (response.success) {
          schoolMapResult.value = response.data.schoolMap
          ElMessage.success('学校地图获取成功')
        } else {
          ElMessage.error('获取失败')
        }
      } catch (error) {
        console.error('学校地图获取失败:', error)
        ElMessage.error('获取失败，请稍后重试')
      } finally {
        schoolMapLoading.value = false
      }
    }
    
    // 奖学金信息方法
    const getScholarshipInfo = async () => {
      scholarshipLoading.value = true
      try {
        const response = await aiApi.enhancedCrawlScholarship({ type: scholarshipForm.type })
        if (response.success) {
          scholarshipResult.value = response.data.scholarship
          ElMessage.success('奖学金信息获取成功')
        } else {
          ElMessage.error('获取失败')
        }
      } catch (error) {
        console.error('奖学金信息获取失败:', error)
        ElMessage.error('获取失败，请稍后重试')
      } finally {
        scholarshipLoading.value = false
      }
    }
    
    // 学习资源方法
    const getLearningResources = async () => {
      learningResourcesLoading.value = true
      try {
        const response = await aiApi.enhancedCrawlLearningResources({
          subject: learningResourcesForm.subject,
          type: learningResourcesForm.type
        })
        if (response.success) {
          learningResourcesResult.value = response.data.learningResources
          ElMessage.success('学习资源获取成功')
        } else {
          ElMessage.error('获取失败')
        }
      } catch (error) {
        console.error('学习资源获取失败:', error)
        ElMessage.error('获取失败，请稍后重试')
      } finally {
        learningResourcesLoading.value = false
      }
    }
    
    // 校园活动方法
    const getCampusActivities = async () => {
      campusActivitiesLoading.value = true
      try {
        const response = await aiApi.enhancedCrawlCampusActivities({ type: campusActivitiesForm.type })
        if (response.success) {
          campusActivitiesResult.value = response.data.campusActivities
          ElMessage.success('校园活动获取成功')
        } else {
          ElMessage.error('获取失败')
        }
      } catch (error) {
        console.error('校园活动获取失败:', error)
        ElMessage.error('获取失败，请稍后重试')
      } finally {
        campusActivitiesLoading.value = false
      }
    }
    
    // 学校周边环境方法
    const getSchoolEnvironment = async () => {
      schoolEnvironmentFormRef.value.validate(async (valid) => {
        if (valid) {
          schoolEnvironmentLoading.value = true
          try {
            const response = await aiApi.enhancedCrawlSchoolEnvironment({ schoolName: schoolEnvironmentForm.schoolName })
            if (response.success) {
              schoolEnvironmentResult.value = response.data.schoolEnvironment
              ElMessage.success('周边环境分析成功')
            } else {
              ElMessage.error('分析失败')
            }
          } catch (error) {
            console.error('周边环境分析失败:', error)
            ElMessage.error('分析失败，请稍后重试')
          } finally {
            schoolEnvironmentLoading.value = false
          }
        }
      })
    }
    
    // 个性化学习计划方法
    const generatePersonalizedLearningPlan = async () => {
      personalizedLearningFormRef.value.validate(async (valid) => {
        if (valid) {
          personalizedLearningLoading.value = true
          try {
            const response = await aiApi.enhancedCrawlPersonalizedLearningPlan({
              student_id: personalizedLearningForm.studentId,
              strengths: personalizedLearningForm.strengths,
              weaknesses: personalizedLearningForm.weaknesses,
              target_score: personalizedLearningForm.targetScore
            })
            if (response.success) {
              personalizedLearningResult.value = response.data.personalizedLearningPlan
              ElMessage.success('学习计划生成成功')
            } else {
              ElMessage.error('生成失败')
            }
          } catch (error) {
            console.error('学习计划生成失败:', error)
            ElMessage.error('生成失败，请稍后重试')
          } finally {
            personalizedLearningLoading.value = false
          }
        }
      })
    }
    
    // 辅助方法：获取进度条颜色
    const getProgressColor = (probability) => {
      if (probability >= 0.8) return '#67C23A'
      if (probability >= 0.6) return '#E6A23C'
      return '#F56C6C'
    }
    
    return {
      chatMessages,
      chatInput,
      chatLoading,
      chatMessagesRef,
      selectedFunction,
      analyzeForm,
      analyzeRules,
      analyzeFormRef,
      analyzeLoading,
      analysisResult,
      crawlForm,
      crawlFormRef,
      crawlLoading,
      crawlResult,
      policyForm,
      policyRules,
      policyFormRef,
      policyLoading,
      policyResult,
      schoolCompareForm,
      schoolCompareFormRef,
      schoolCompareLoading,
      schoolCompareResult,
      admissionCalculatorForm,
      admissionCalculatorRules,
      admissionCalculatorFormRef,
      admissionCalculatorLoading,
      admissionCalculatorResult,
      careerPlanningForm,
      careerPlanningFormRef,
      careerPlanningLoading,
      careerPlanningResult,
      schoolMapForm,
      schoolMapFormRef,
      schoolMapLoading,
      schoolMapResult,
      scholarshipForm,
      scholarshipFormRef,
      scholarshipLoading,
      scholarshipResult,
      learningResourcesForm,
      learningResourcesFormRef,
      learningResourcesLoading,
      learningResourcesResult,
      campusActivitiesForm,
      campusActivitiesFormRef,
      campusActivitiesLoading,
      campusActivitiesResult,
      schoolEnvironmentForm,
      schoolEnvironmentRules,
      schoolEnvironmentFormRef,
      schoolEnvironmentLoading,
      schoolEnvironmentResult,
      personalizedLearningForm,
      personalizedLearningRules,
      personalizedLearningFormRef,
      personalizedLearningLoading,
      personalizedLearningResult,
      sendMessage,
      navigateTo,
      generateAnalysis,
      startCrawl,
      interpretPolicy,
      compareSchools,
      calculateAdmission,
      generateCareerPlan,
      getSchoolMap,
      getScholarshipInfo,
      getLearningResources,
      getCampusActivities,
      getSchoolEnvironment,
      generatePersonalizedLearningPlan,
      getProgressColor
    }
  }
}
</script>

<style scoped>
.openclaw-page {
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

/* 聊天区域 */
.chat-section {
  position: sticky;
  top: 20px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 15px;
  padding: 1