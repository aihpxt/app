<template>
  <div class="membership-page">
    <div class="page-header">
      <h1>会员中心</h1>
      <p>选择适合您的会员套餐，解锁更多专业功能</p>
    </div>
    
    <div class="current-membership" v-if="currentMembership">
      <div class="membership-card" :class="currentMembership.level_name">
        <div class="card-header">
          <span class="level-badge">{{ currentMembership.level_name }}</span>
          <span class="status" v-if="currentMembership.status === 'active'">有效期至 {{ currentMembership.end_date }}</span>
        </div>
        <div class="card-body">
          <div class="feature-list">
            <div class="feature-item" v-for="(value, key) in currentMembership.features" :key="key">
              <el-icon v-if="getFeatureStatus(value)"><Check /></el-icon>
              <el-icon v-else><Close /></el-icon>
              <span>{{ getFeatureName(key) }}</span>
              <span class="limit" v-if="typeof value === 'object' && value.daily_limit">
                ({{ value.daily_limit === -1 ? '无限' : `每日${value.daily_limit}次` }})
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="pricing-section">
      <h2>选择会员套餐</h2>
      
      <div class="duration-tabs">
        <el-radio-group v-model="selectedDuration" size="large">
          <el-radio-button :value="1">月付</el-radio-button>
          <el-radio-button :value="3">季付</el-radio-button>
          <el-radio-button :value="12">年付</el-radio-button>
        </el-radio-group>
        <span class="discount-hint" v-if="selectedDuration === 12">年付享8折优惠</span>
      </div>
      
      <div class="pricing-cards">
        <div 
          v-for="level in membershipLevels" 
          :key="level.id"
          class="pricing-card"
          :class="{ active: selectedLevel === level.id, free: level.price_monthly === 0 }"
          @click="selectedLevel = level.id"
        >
          <div class="card-header">
            <h3>{{ level.name }}</h3>
            <p class="description">{{ level.description }}</p>
          </div>
          
          <div class="price">
            <span class="currency">¥</span>
            <span class="amount">{{ getPrice(level) }}</span>
            <span class="period">/{{ getDurationText() }}</span>
          </div>
          
          <div class="features">
            <div class="feature" v-for="(value, key) in level.features" :key="key">
              <el-icon v-if="getFeatureStatus(value)"><Check /></el-icon>
              <el-icon v-else><Close /></el-icon>
              <span>{{ getFeatureName(key) }}</span>
            </div>
          </div>
          
          <el-button 
            v-if="level.price_monthly > 0"
            :type="selectedLevel === level.id ? 'primary' : 'default'"
            @click.stop="handlePurchase(level)"
          >
            立即开通
          </el-button>
          <el-button v-else disabled>当前等级</el-button>
        </div>
      </div>
    </div>
    
    <div class="faq-section">
      <h2>常见问题</h2>
      <el-collapse>
        <el-collapse-item title="会员可以退款吗？" name="1">
          <p>会员服务开通后，支持7天内无理由退款。超过7天不支持退款，但可以暂停服务。</p>
        </el-collapse-item>
        <el-collapse-item title="如何升级会员？" name="2">
          <p>您可以直接购买更高等级的会员，系统会自动计算差价并延长有效期。</p>
        </el-collapse-item>
        <el-collapse-item title="会员到期后数据会丢失吗？" name="3">
          <p>会员到期后，您的所有数据都会保留，但部分高级功能将无法使用。</p>
        </el-collapse-item>
        <el-collapse-item title="支持哪些支付方式？" name="4">
          <p>目前支持微信支付、支付宝、银行卡等多种支付方式。</p>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'

const userStore = useUserStore()

const membershipLevels = ref([])
const currentMembership = ref(null)
const selectedLevel = ref(2)
const selectedDuration = ref(1)

const featureNames = {
  'ai_assistant': 'AI智能助手',
  'school_query': '学校查询',
  'policy_view': '政策解读',
  'score_prediction': '分数预测',
  'volunteer_filling': '志愿填报',
  'ai_selection': '智能择校',
  'compare': '学校对比',
  'data_export': '数据导出',
  'history_save': '历史保存',
  'expert_consultation': '专家咨询',
  'priority_support': '优先客服'
}

const getFeatureName = (key) => {
  return featureNames[key] || key
}

const getFeatureStatus = (value) => {
  if (typeof value === 'boolean') return value
  if (typeof value === 'object') return value.daily_limit !== 0
  return !!value
}

const getPrice = (level) => {
  if (selectedDuration.value === 1) return level.price_monthly
  if (selectedDuration.value === 3) return level.price_quarterly
  if (selectedDuration.value === 12) return level.price_yearly
  return level.price_monthly
}

const getDurationText = () => {
  if (selectedDuration.value === 1) return '月'
  if (selectedDuration.value === 3) return '季'
  if (selectedDuration.value === 12) return '年'
  return '月'
}

const loadMembershipLevels = async () => {
  try {
    const response = await fetch('/api/membership/levels')
    const result = await response.json()
    if (result.success) {
      membershipLevels.value = result.data
    }
  } catch (error) {
    console.error('加载会员等级失败:', error)
  }
}

const loadCurrentMembership = async () => {
  if (!userStore.isLoggedIn) return
  
  try {
    const userId = userStore.userInfo.id
    const response = await fetch(`/api/membership/user/${userId}`)
    const result = await response.json()
    if (result.success) {
      currentMembership.value = result.data
    }
  } catch (error) {
    console.error('加载会员信息失败:', error)
  }
}

const handlePurchase = async (level) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  
  const price = getPrice(level)
  const durationText = getDurationText()
  
  try {
    await ElMessageBox.confirm(
      `确认购买${level.name}（${durationText}付）？需支付¥${price}`,
      '确认购买',
      { confirmButtonText: '确认支付', cancelButtonText: '取消' }
    )
    
    const response = await fetch('/api/membership/purchase', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userInfo.id,
        level_id: level.id,
        duration_months: selectedDuration.value,
        payment_method: 'wechat'
      })
    })
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success('购买成功！')
      loadCurrentMembership()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('购买失败，请重试')
    }
  }
}

onMounted(() => {
  loadMembershipLevels()
  loadCurrentMembership()
})
</script>

<style scoped>
.membership-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 32px;
  background: #1a1a2e;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-header h1 {
  font-size: 36px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}

.page-header p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 16px;
}

.current-membership {
  margin-bottom: 48px;
}

.membership-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  border-radius: 20px;
  padding: 32px;
  color: #fff;
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
}

.membership-card.免费用户 {
  background: linear-gradient(135deg, #3a3a4a 0%, #2a2a3a 100%);
}

.membership-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.level-badge {
  background: rgba(255,255,255,0.2);
  padding: 10px 20px;
  border-radius: 24px;
  font-weight: 600;
  font-size: 15px;
}

.pricing-section h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #fff;
  font-weight: 600;
}

.duration-tabs {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-bottom: 36px;
}

.duration-tabs :deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.duration-tabs :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.discount-hint {
  color: #f56c6c;
  font-size: 14px;
  font-weight: 500;
}

.pricing-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.pricing-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 32px;
  text-align: center;
  border: 2px solid rgba(255, 255, 255, 0.08);
  transition: color 0.4s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.4s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.pricing-card:hover {
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.2);
}

.pricing-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.25);
}

.pricing-card.free {
  opacity: 0.7;
}

.pricing-card h3 {
  font-size: 22px;
  margin-bottom: 10px;
  color: #fff;
  font-weight: 600;
}

.pricing-card .description {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  margin-bottom: 24px;
}

.pricing-card .price {
  margin-bottom: 24px;
}

.pricing-card .currency {
  font-size: 20px;
  vertical-align: top;
  color: rgba(255, 255, 255, 0.7);
}

.pricing-card .amount {
  font-size: 52px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.pricing-card .period {
  color: rgba(255, 255, 255, 0.4);
}

.pricing-card .features {
  text-align: left;
  margin-bottom: 24px;
}

.pricing-card .feature {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
}

.pricing-card .feature:last-child {
  border-bottom: none;
}

.pricing-card .feature .el-icon {
  color: #67c23a;
  font-size: 18px;
}

.pricing-card :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  padding: 14px 32px;
  font-weight: 500;
}

.pricing-card :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.pricing-card :deep(.el-button--default) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 14px 32px;
}

.pricing-card :deep(.el-button--default:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.faq-section h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #fff;
  font-weight: 600;
}

.faq-section :deep(.el-collapse) {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
}

.faq-section :deep(.el-collapse-item__header) {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 0 24px;
}

.faq-section :deep(.el-collapse-item__header:hover) {
  background: rgba(255, 255, 255, 0.03);
}

.faq-section :deep(.el-collapse-item__wrap) {
  background: transparent;
  border-bottom: none;
}

.faq-section :deep(.el-collapse-item__content) {
  padding: 20px 24px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.7;
}

.faq-section :deep(.el-collapse-item__arrow) {
  color: rgba(255, 255, 255, 0.5);
}
</style>
