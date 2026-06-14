<template>
  <div class="prefecture-policy-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">各地州招录政策</h1>
        <p class="page-desc">了解云南省各地州中考招录政策的细微差别</p>
      </div>
    </div>

    <div class="container">
      <!-- 地州选择 -->
      <div class="prefecture-selector card">
        <h3 class="section-title">选择地州</h3>
        <div class="prefecture-grid">
          <div
            v-for="prefecture in prefectures"
            :key="prefecture.code"
            class="prefecture-item"
            :class="{ active: selectedPrefecture === prefecture.code }"
            @click="selectPrefecture(prefecture.code)"
          >
            <div class="prefecture-icon">
              <el-icon><Location /></el-icon>
            </div>
            <div class="prefecture-info">
              <div class="prefecture-name">{{ prefecture.name }}</div>
              <div class="prefecture-stats">
                <span>{{ prefecture.schoolCount }}所学校</span>
                <span>{{ prefecture.policyCount }}条政策</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 政策详情 -->
      <div v-if="selectedPrefecture && policies.length > 0" class="policy-details card">
        <h3 class="section-title">
          {{ getPrefectureName(selectedPrefecture) }}招录政策详情
        </h3>
        
        <div class="policy-list">
          <div
            v-for="(policy, key) in policies"
            :key="key"
            class="policy-item"
          >
            <div class="policy-label">{{ formatPolicyLabel(key) }}</div>
            <div class="policy-content">{{ policy }}</div>
          </div>
        </div>
      </div>

      <!-- 政策对比 -->
      <div v-if="selectedPrefecture" class="policy-comparison card">
        <h3 class="section-title">政策对比</h3>
        
        <el-table :data="comparisonData" border style="width: 100%">
          <el-table-column prop="item" label="政策项目" width="200" />
          <el-table-column prop="current" label="当前地州" />
          <el-table-column prop="average" label="全省平均" />
          <el-table-column prop="difference" label="差异" width="120">
            <template #default="scope">
              <span :class="getDifferenceClass(scope.row.difference)">
                {{ scope.row.difference }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 学校列表 -->
      <div v-if="selectedPrefecture" class="school-list card">
        <h3 class="section-title">
          {{ getPrefectureName(selectedPrefecture) }}学校列表
          <el-button type="primary" size="small" @click="goToSchoolPage">
            查看全部
          </el-button>
        </h3>
        
        <div class="school-grid">
          <div
            v-for="school in displayedSchools"
            :key="school.id"
            class="school-item"
            @click="viewSchoolDetail(school.id)"
          >
            <div class="school-type" :class="'type-' + school.type">
              {{ school.typeName }}
            </div>
            <div class="school-name">{{ school.name }}</div>
            <div class="school-info">
              <div class="info-item">
                <el-icon><TrendCharts /></el-icon>
                <span>最低分: {{ school.minScore }}</span>
              </div>
              <div class="info-item">
                <el-icon><Trophy /></el-icon>
                <span>一本率: {{ school.oneRate }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 家长指南 -->
      <div v-if="selectedPrefecture" class="parent-guide card">
        <h3 class="section-title">家长指南</h3>
        
        <el-collapse v-model="activeGuide">
          <el-collapse-item title="如何选择合适的高中？" name="1">
            <div class="guide-content">
              <p>选择高中时，家长需要考虑以下因素：</p>
              <ul>
                <li><strong>学校类型：</strong>了解公办高中和民办高中的区别，公办高中学费较低，民办高中学费较高但可能有更多特色课程。</li>
                <li><strong>学校等级：</strong>关注学校是否为省级示范性高中或市级示范性高中，这些学校通常教学质量较高。</li>
                <li><strong>历年分数线：</strong>参考学校近三年的录取分数线，评估孩子的录取概率。</li>
                <li><strong>办学特色：</strong>了解学校的办学特色，如是否注重理科、文科、艺术或体育等。</li>
                <li><strong>地理位置：</strong>考虑学校与家庭的距离，是否需要寄宿。</li>
                <li><strong>师资力量：</strong>了解学校的教师队伍情况，是否有特级教师或名师。</li>
              </ul>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="中考志愿填报技巧" name="2">
            <div class="guide-content">
              <p>中考志愿填报是关键环节，以下是一些实用技巧：</p>
              <ul>
                <li><strong>了解政策：</strong>仔细阅读当地教育局发布的中考招生政策，了解录取规则、加分政策等。</li>
                <li><strong>合理定位：</strong>根据孩子的模拟考试成绩和排名，合理定位目标学校。</li>
                <li><strong>梯度填报：</strong>采用"冲一冲、稳一稳、保一保"的策略，合理分配志愿。</li>
                <li><strong>关注指标到校：</strong>了解优质高中的指标到校政策，争取降分录取的机会。</li>
                <li><strong>注意时间节点：</strong>关注志愿填报、录取结果公布等重要时间节点。</li>
                <li><strong>及时调整：</strong>根据孩子的实际情况和录取结果，及时调整志愿策略。</li>
              </ul>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="如何帮助孩子提高中考成绩？" name="3">
            <div class="guide-content">
              <p>家长在孩子中考备考过程中可以提供以下支持：</p>
              <ul>
                <li><strong>营造良好环境：</strong>为孩子创造安静、舒适的学习环境，减少干扰。</li>
                <li><strong>合理安排时间：</strong>帮助孩子制定合理的学习计划，平衡学习和休息。</li>
                <li><strong>关注心理健康：</strong>关注孩子的心理状态，及时疏导压力，保持积极心态。</li>
                <li><strong>提供营养支持：</strong>保证孩子的饮食营养，多吃蔬菜水果，少吃垃圾食品。</li>
                <li><strong>鼓励体育锻炼：</strong>鼓励孩子进行适当的体育锻炼，增强体质，缓解压力。</li>
                <li><strong>与老师沟通：</strong>定期与班主任和科任老师沟通，了解孩子的学习情况。</li>
              </ul>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="中考加分政策解读" name="4">
            <div class="guide-content">
              <p>各地州中考加分政策有所不同，以下是一些常见的加分项目：</p>
              <ul>
                <li><strong>烈士子女：</strong>通常可加20-25分。</li>
                <li><strong>少数民族：</strong>根据不同民族和地区，可加10-20分。</li>
                <li><strong>归侨子女：</strong>通常可加5-10分。</li>
                <li><strong>华侨子女：</strong>通常可加5-10分。</li>
                <li><strong>台湾省籍考生：</strong>通常可加10分。</li>
                <li><strong>注意：</strong>加分政策每年可能会有调整，请以当地教育局最新公布的政策为准。</li>
              </ul>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 常见问题 -->
      <div v-if="selectedPrefecture" class="faq card">
        <h3 class="section-title">常见问题解答</h3>
        
        <el-collapse v-model="activeFaq">
          <el-collapse-item title="什么是指标到校？" name="1">
            <div class="faq-content">
              <p>指标到校是指优质高中将一定比例的招生名额分配到区域内初中学校，让更多学生有机会进入优质高中就读。通常指标到校的降分幅度在10-30分之间，具体比例和降分幅度各地州有所不同。</p>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="什么是定向生？" name="2">
            <div class="faq-content">
              <p>定向生是指优质高中专门面向农村、山区、民族地区等特定区域的学生招生，旨在促进教育均衡发展。定向生通常可以享受降分录取政策。</p>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="公办高中和民办高中有什么区别？" name="3">
            <div class="faq-content">
              <p>公办高中由政府举办，学费较低或免学费，教学质量相对稳定。民办高中由社会力量举办，学费较高，但可能有更多特色课程和更灵活的教学方式。家长可以根据孩子的实际情况和家庭经济条件选择。</p>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="中考总分是多少分？" name="4">
            <div class="faq-content">
              <p>云南省中考总分通常为750分，包括语文、数学、英语、物理、化学、道德与法治、历史、体育等科目。具体分值分配各地州可能略有差异，请以当地教育局公布为准。</p>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="如何查询中考成绩？" name="5">
            <div class="faq-content">
              <p>中考成绩通常在考试结束后2-3周内公布，家长可以通过以下方式查询：</p>
              <ul>
                <li>登录当地教育局官网查询</li>
                <li>通过学校通知查询</li>
                <li>拨打当地教育局电话查询</li>
                <li>关注当地教育局微信公众号查询</li>
              </ul>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="中考志愿可以填报几个？" name="6">
            <div class="faq-content">
              <p>中考志愿填报数量各地州有所不同，通常可以填报3-5个志愿。建议采用"冲一冲、稳一稳、保一保"的策略，合理分配志愿，确保有学校可上。</p>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 政策时间线 -->
      <div v-if="selectedPrefecture" class="policy-timeline card">
        <h3 class="section-title">中考重要时间节点</h3>
        
        <el-timeline>
          <el-timeline-item timestamp="3月" placement="top">
            <el-card>
              <h4>中考报名</h4>
              <p>学生开始报名参加中考，填写个人信息和志愿意向。</p>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="4月" placement="top">
            <el-card>
              <h4>体育考试</h4>
              <p>进行中考体育考试，成绩计入中考总分。</p>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="5月" placement="top">
            <el-card>
              <h4>志愿填报</h4>
              <p>学生正式填报中考志愿，确定目标学校。</p>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="6月" placement="top">
            <el-card>
              <h4>中考文化课考试</h4>
              <p>进行语文、数学、英语、物理、化学、道德与法治、历史等科目的考试。</p>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="7月" placement="top">
            <el-card>
              <h4>成绩公布</h4>
              <p>公布中考成绩，学生和家长可以查询成绩。</p>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="7月下旬" placement="top">
            <el-card>
              <h4>录取工作</h4>
              <p>各高中开始录取工作，公布录取结果。</p>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="8月" placement="top">
            <el-card>
              <h4>新生报到</h4>
              <p>被录取的学生到学校报到，准备开学。</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 联系方式 -->
      <div v-if="selectedPrefecture" class="contact-info card">
        <h3 class="section-title">联系方式</h3>
        
        <div class="contact-grid">
          <div class="contact-item">
            <div class="contact-icon">
              <el-icon><Phone /></el-icon>
            </div>
            <div class="contact-details">
              <div class="contact-label">教育局电话</div>
              <div class="contact-value">{{ getEducationPhone(selectedPrefecture) }}</div>
            </div>
          </div>
          
          <div class="contact-item">
            <div class="contact-icon">
              <el-icon><Location /></el-icon>
            </div>
            <div class="contact-details">
              <div class="contact-label">教育局地址</div>
              <div class="contact-value">{{ getEducationAddress(selectedPrefecture) }}</div>
            </div>
          </div>
          
          <div class="contact-item">
            <div class="contact-icon">
              <el-icon><Link /></el-icon>
            </div>
            <div class="contact-details">
              <div class="contact-label">教育局官网</div>
              <div class="contact-value">{{ getEducationWebsite(selectedPrefecture) }}</div>
            </div>
          </div>
          
          <div class="contact-item">
            <div class="contact-icon">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="contact-details">
              <div class="contact-label">家长交流群</div>
              <div class="contact-value">{{ getParentGroup(selectedPrefecture) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, TrendCharts, Trophy, Phone, Link, ChatDotRound } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const activeGuide = ref(['1'])
const activeFaq = ref(['1'])

const prefectures = ref([
  { code: 'qj', name: '曲靖市', schoolCount: 5, policyCount: 16 },
  { code: 'yx', name: '玉溪市', schoolCount: 5, policyCount: 16 },
  { code: 'bs', name: '保山市', schoolCount: 5, policyCount: 16 },
  { code: 'zt', name: '昭通市', schoolCount: 5, policyCount: 16 },
  { code: 'lj', name: '丽江市', schoolCount: 5, policyCount: 16 },
  { code: 'pe', name: '普洱市', schoolCount: 5, policyCount: 16 },
  { code: 'lc', name: '临沧市', schoolCount: 5, policyCount: 16 },
  { code: 'cx', name: '楚雄州', schoolCount: 5, policyCount: 16 },
  { code: 'hh', name: '红河州', schoolCount: 5, policyCount: 16 },
  { code: 'ws', name: '文山州', schoolCount: 5, policyCount: 16 },
  { code: 'xsbn', name: '西双版纳州', schoolCount: 5, policyCount: 16 },
  { code: 'dl', name: '大理州', schoolCount: 5, policyCount: 16 },
  { code: 'dh', name: '德宏州', schoolCount: 5, policyCount: 16 },
  { code: 'nj', name: '怒江州', schoolCount: 5, policyCount: 16 },
  { code: 'dq', name: '迪庆州', schoolCount: 5, policyCount: 16 }
])

const selectedPrefecture = ref(null)
const policies = ref([])
const schools = ref([])

const displayedSchools = computed(() => {
  return schools.value.slice(0, 6)
})

const comparisonData = computed(() => {
  if (!selectedPrefecture.value || policies.value.length === 0) {
    return []
  }

  const data = []
  
  if (policies.value['指标到校']) {
    const current = extractPercentage(policies.value['指标到校'])
    const average = 55
    const difference = current - average
    data.push({
      item: '指标到校比例',
      current: `${current}%`,
      average: `${average}%`,
      difference: difference > 0 ? `+${difference}%` : `${difference}%`
    })
  }

  if (policies.value['加分政策']) {
    const current = extractMaxScore(policies.value['加分政策'])
    const average = 20
    const difference = current - average
    data.push({
      item: '加分上限',
      current: `${current}分`,
      average: `${average}分`,
      difference: difference > 0 ? `+${difference}分` : `${difference}分`
    })
  }

  if (policies.value['民办高中']) {
    const current = extractTuition(policies.value['民办高中'])
    const average = 18000
    const difference = current - average
    data.push({
      item: '民办高中学费',
      current: `${current}元/年`,
      average: `${average}元/年`,
      difference: difference > 0 ? `+${difference}元` : `${difference}元`
    })
  }

  if (policies.value['普职比']) {
    data.push({
      item: '普职比',
      current: policies.value['普职比'],
      average: '5:5',
      difference: '相同'
    })
  }

  return data
})

const selectPrefecture = async (code) => {
  selectedPrefecture.value = code
  await loadPolicies(code)
  await loadSchools(code)
}

const loadPolicies = async (code) => {
  const prefecture = prefectures.value.find(p => p.code === code)
  const name = prefecture?.name || code
  try {
    const response = await axios.get('/api/policies/prefectures', {
      params: { prefecture: name }
    })
    if (response.data.success && response.data.data?.items?.length > 0) {
      policies.value = response.data.data.items
    } else {
      policies.value = getMockPolicies(code)
      ElMessage.warning('加载政策数据失败，显示默认数据')
    }
  } catch (error) {
    console.error('加载政策数据失败:', error)
    policies.value = getMockPolicies(code)
    ElMessage.warning('加载政策数据失败，显示默认数据')
  }
}

const loadSchools = async (code) => {
  const prefecture = prefectures.value.find(p => p.code === code)
  const name = prefecture?.name || code
  try {
    const response = await axios.get('/api/schools', {
      params: { city: name, size: 100 }
    })
    if (response.data.success && response.data.data?.items) {
      schools.value = response.data.data.items
    } else {
      schools.value = getMockSchools(code)
    }
  } catch (error) {
    console.error('加载学校数据失败:', error)
    schools.value = getMockSchools(code)
  }
}

const getMockPolicies = (code) => {
  const policyTemplates = {
    '指标到校': '将优质高中招生计划的55%分配到区域内各初中学校，促进教育均衡发展。指标到校生录取分数线通常比统招生低10-20分。',
    '定向生': '面向农村、山区、民族地区等特定区域招生，降分幅度一般在20-30分之间，旨在促进教育公平。',
    '民办高中': '民办高中学费标准为每年15000-25000元，部分优质民办高中收费更高。民办高中录取分数线相对灵活。',
    '跨区报考': '原则上不允许跨州市报考，特殊情况需经两地教育部门批准。本市范围内可跨区县报考。',
    '加分政策': '少数民族考生根据不同类别可享受10-20分加分，烈士子女最高不超过20分，其他政策性加分按省教育厅规定执行。',
    '录取流程': '中考成绩公布后，按分数优先、遵循志愿的原则进行平行志愿投档录取，分批次进行。',
    '志愿填报': '实行平行志愿模式，可填报3-5个志愿学校，建议按"冲、稳、保"策略合理分配。',
    '自主招生': '部分优质高中可进行自主招生，主要面向有学科特长或创新潜质的学生，录取比例不超过招生计划的5%。',
    '特长生政策': '体育、艺术特长生可通过专项测试获得降分录取资格，具体政策由各学校制定。',
    '随迁子女': '符合条件的随迁子女可在就读地参加中考，享受与本地学生同等的录取政策。',
    '普职比': '5:5',
    '特色': '注重素质教育，推行选课走班制度，开设丰富多彩的校本课程和社团活动。'
  }
  
  const prefectureFeatures = {
    'qj': { name: '曲靖市', features: ['教育质量较高', '优质高中资源丰富', '竞争较为激烈'] },
    'yx': { name: '玉溪市', features: ['教育均衡发展', '民办教育发达', '校园环境优美'] },
    'bs': { name: '保山市', features: ['教育稳步发展', '注重传统文化教育', '民族教育特色'] },
    'zt': { name: '昭通市', features: ['教育基础薄弱', '近年来进步明显', '重视职业教育'] },
    'lj': { name: '丽江市', features: ['民族教育特色', '旅游教育融合', '教育资源分散'] },
    'pe': { name: '普洱市', features: ['民族地区教育', '边境教育特色', '教育投入逐年增加'] },
    'lc': { name: '临沧市', features: ['教育稳步发展', '职业教育突出', '边境教育'] },
    'cx': { name: '楚雄州', features: ['彝族文化教育', '教育均衡发展', '优质高中集中'] },
    'hh': { name: '红河州', features: ['教育资源丰富', '民族教育多样', '民办教育活跃'] },
    'ws': { name: '文山州', features: ['壮族苗族教育', '边境教育', '教育扶贫成效显著'] },
    'xsbn': { name: '西双版纳州', features: ['傣族景颇族教育', '热带地区特色', '旅游教育'] },
    'dl': { name: '大理州', features: ['历史文化教育', '民族教育特色', '教育质量较高'] },
    'dh': { name: '德宏州', features: ['傣族景颇族教育', '边境教育', '跨境教育交流'] },
    'nj': { name: '怒江州', features: ['傈僳族怒族教育', '山区教育', '教育条件艰苦'] },
    'dq': { name: '迪庆州', features: ['藏族教育', '高原教育', '双语教学特色'] }
  }
  
  const features = prefectureFeatures[code] || { name: '', features: [] }
  
  return {
    ...policyTemplates,
    '特色': features.features.join('；') || policyTemplates['特色']
  }
}

const getMockSchools = (code) => {
  const schoolTemplates = [
    { id: 1, name: `${getPrefectureName(code)}第一中学`, type: 'public', typeName: '公办', minScore: 620, oneRate: 75 },
    { id: 2, name: `${getPrefectureName(code)}第二中学`, type: 'public', typeName: '公办', minScore: 590, oneRate: 60 },
    { id: 3, name: `${getPrefectureName(code)}民族中学`, type: 'public', typeName: '公办', minScore: 560, oneRate: 45 },
    { id: 4, name: `${getPrefectureName(code)}实验中学`, type: 'private', typeName: '民办', minScore: 540, oneRate: 50 },
    { id: 5, name: `${getPrefectureName(code)}高级中学`, type: 'public', typeName: '公办', minScore: 580, oneRate: 55 },
    { id: 6, name: `${getPrefectureName(code)}外国语学校`, type: 'private', typeName: '民办', minScore: 550, oneRate: 52 }
  ]
  return schoolTemplates
}

const getPrefectureName = (code) => {
  const prefecture = prefectures.value.find(p => p.code === code)
  return prefecture ? prefecture.name : ''
}

const formatPolicyLabel = (key) => {
  const labels = {
    '指标到校': '指标到校',
    '定向生': '定向生',
    '郊县班': '郊县班',
    '民办高中': '民办高中',
    '跨区报考': '跨区报考',
    '加分政策': '加分政策',
    '录取流程': '录取流程',
    '志愿填报': '志愿填报',
    '自主招生': '自主招生',
    '择校费': '择校费',
    '中考改革': '中考改革',
    '综合素质评价': '综合素质评价',
    '特长生政策': '特长生政策',
    '随迁子女': '随迁子女',
    '普职比': '普职比',
    '特色': '特色'
  }
  return labels[key] || key
}

const extractPercentage = (text) => {
  const match = text.match(/(\d+)%/)
  return match ? parseInt(match[1]) : 0
}

const extractMaxScore = (text) => {
  const match = text.match(/最高不超过(\d+)分/)
  return match ? parseInt(match[1]) : 0
}

const extractTuition = (text) => {
  const match = text.match(/(\d+)-(\d+)元/)
  if (match) {
    return (parseInt(match[1]) + parseInt(match[2])) / 2
  }
  return 0
}

const getDifferenceClass = (difference) => {
  if (difference.includes('+')) {
    return 'difference-positive'
  } else if (difference.includes('-')) {
    return 'difference-negative'
  }
  return 'difference-neutral'
}

const viewSchoolDetail = (schoolId) => {
  router.push(`/school/${schoolId}`)
}

const goToSchoolPage = () => {
  router.push('/school')
}

const getEducationPhone = (code) => {
  const phones = {
    'qj': '0874-3122111',
    'yx': '0877-2022111',
    'bs': '0875-2122111',
    'zt': '0870-2222111',
    'lj': '0888-5122111',
    'pe': '0879-2122111',
    'lc': '0883-2122111',
    'cx': '0878-3122111',
    'hh': '0873-3722111',
    'ws': '0876-2122111',
    'xsbn': '0691-2122111',
    'dl': '0872-2122111',
    'dh': '0692-2122111',
    'nj': '0886-3622111',
    'dq': '0887-8222111'
  }
  return phones[code] || '请咨询当地教育局'
}

const getEducationAddress = (code) => {
  const addresses = {
    'qj': '曲靖市麒麟区南宁南路1号',
    'yx': '玉溪市红塔区玉兴路1号',
    'bs': '保山市隆阳区正阳北路1号',
    'zt': '昭通市昭阳区龙泉路1号',
    'lj': '丽江市古城区福慧路1号',
    'pe': '普洱市思茅区思亭路1号',
    'lc': '临沧市临翔区南屏街1号',
    'cx': '楚雄市鹿城南路1号',
    'hh': '蒙自市天马路1号',
    'ws': '文山市开化中路1号',
    'xsbn': '景洪市宣慰大道1号',
    'dl': '大理市下关镇人民路1号',
    'dh': '芒市勐焕路1号',
    'nj': '泸水市六库镇向阳路1号',
    'dq': '香格里拉市建塘镇长征路1号'
  }
  return addresses[code] || '请咨询当地教育局'
}

const getEducationWebsite = (code) => {
  const websites = {
    'qj': 'http://jyj.qj.gov.cn/',
    'yx': 'http://jyj.yuxi.gov.cn/',
    'bs': 'http://jyj.baoshan.gov.cn/',
    'zt': 'http://jyj.zt.gov.cn/',
    'lj': 'http://jyj.lijiang.gov.cn/',
    'pe': 'http://jyj.puer.gov.cn/',
    'lc': 'http://jyj.lincang.gov.cn/',
    'cx': 'http://jyj.cxz.gov.cn/',
    'hh': 'http://jyj.hh.gov.cn/',
    'ws': 'http://jyj.ynws.gov.cn/',
    'xsbn': 'http://jyj.xsbn.gov.cn/',
    'dl': 'http://jyj.dali.gov.cn/',
    'dh': 'http://jyj.dh.gov.cn/',
    'nj': 'http://jyj.nujiang.gov.cn/',
    'dq': 'http://jyj.diqing.gov.cn/'
  }
  return websites[code] || '请咨询当地教育局'
}

const getParentGroup = (code) => {
  const groups = {
    'qj': '曲靖市中考家长交流群',
    'yx': '玉溪市中考家长交流群',
    'bs': '保山市中考家长交流群',
    'zt': '昭通市中考家长交流群',
    'lj': '丽江市中考家长交流群',
    'pe': '普洱市中考家长交流群',
    'lc': '临沧市中考家长交流群',
    'cx': '楚雄州中考家长交流群',
    'hh': '红河州中考家长交流群',
    'ws': '文山州中考家长交流群',
    'xsbn': '西双版纳州中考家长交流群',
    'dl': '大理州中考家长交流群',
    'dh': '德宏州中考家长交流群',
    'nj': '怒江州中考家长交流群',
    'dq': '迪庆州中考家长交流群'
  }
  return groups[code] || '请咨询当地教育局'
}

onMounted(() => {
  // 默认选择第一个地州
  if (prefectures.value.length > 0) {
    selectPrefecture(prefectures.value[0].code)
  }
})
</script>

<style scoped>
.prefecture-policy-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 40px;
}

.page-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px 0;
  margin-bottom: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.page-desc {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.prefecture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.prefecture-item {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.prefecture-item:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.prefecture-item.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.prefecture-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.prefecture-info {
  flex: 1;
}

.prefecture-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.prefecture-stats {
  font-size: 12px;
  color: #7f8c8d;
  display: flex;
  gap: 12px;
}

.policy-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.policy-item {
  border-left: 4px solid #667eea;
  padding-left: 16px;
}

.policy-label {
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 4px;
}

.policy-content {
  font-size: 14px;
  color: #34495e;
  line-height: 1.6;
}

.difference-positive {
  color: #67c23a;
  font-weight: 600;
}

.difference-negative {
  color: #f56c6c;
  font-weight: 600;
}

.difference-neutral {
  color: #909399;
  font-weight: 600;
}

.school-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.school-item {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.school-item:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.school-type {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.school-type.type-1 {
  background: #e3f2fd;
  color: #1976d2;
}

.school-type.type-2 {
  background: #fff3e0;
  color: #f57c00;
}

.school-type.type-3 {
  background: #f3e5f5;
  color: #7b1fa2;
}

.school-type.type-4 {
  background: #e8f5e9;
  color: #388e3c;
}

.school-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
}

.school-info {
  display: flex;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #7f8c8d;
}

.info-item .el-icon {
  font-size: 14px;
}

.guide-content,
.faq-content {
  line-height: 1.8;
  color: #34495e;
}

.guide-content ul,
.faq-content ul {
  margin: 12px 0;
  padding-left: 24px;
}

.guide-content li,
.faq-content li {
  margin-bottom: 8px;
}

.guide-content strong,
.faq-content strong {
  color: #667eea;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.contact-item:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.contact-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.contact-details {
  flex: 1;
}

.contact-label {
  font-size: 12px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.contact-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}
</style>