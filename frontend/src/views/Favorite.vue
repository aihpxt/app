<template>
  <div class="favorite-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">我的收藏</h1>
        <p class="page-desc">查看和管理您收藏的学校</p>
      </div>
    </div>

    <div class="container">
      <!-- 统计信息 -->
      <div class="favorite-stats card">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon total">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ favoriteSchools.length }}</div>
                <div class="stat-label">收藏学校</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon public">
                <el-icon><CheckCircle /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ publicCount }}</div>
                <div class="stat-label">公办学校</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon private">
                <el-icon><AlertCircle /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ privateCount }}</div>
                <div class="stat-label">民办学校</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon key">
                <el-icon><Medal /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ keyCount }}</div>
                <div class="stat-label">重点高中</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 操作按钮 -->
      <div class="favorite-actions">
        <el-button @click="refreshFavorites">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
        <el-button type="danger" @click="clearAllFavorites" :disabled="favoriteSchools.length === 0">
          <el-icon><Delete /></el-icon>清空收藏
        </el-button>
        <el-button type="primary" @click="goToCompare" :disabled="selectedForCompare.length < 2">
          <el-icon><ArrowRightBold /></el-icon>对比选中 ({{ selectedForCompare.length }})
        </el-button>
      </div>

      <!-- 收藏列表 -->
      <div class="favorite-list">
        <el-empty v-if="favoriteSchools.length === 0" description="暂无收藏">
          <el-button type="primary" @click="$router.push('/school')">浏览学校</el-button>
        </el-empty>
        
        <div class="school-grid">
          <div 
            class="school-card" 
            v-for="school in favoriteSchools" 
            :key="school.id" 
            @click="viewSchoolDetail(school.id)"
          >
            <!-- 选择框 -->
            <div class="select-box" @click.stop>
              <el-checkbox 
                :checked="selectedForCompare.includes(school.id)" 
                @change="toggleCompareSelect(school.id)" 
              />
            </div>
            
            <!-- 顶部渐变条 -->
            <div class="card-gradient"></div>
            
            <div class="school-header">
              <div class="school-logo-wrapper">
                <img :src="school.logo || generateSchoolLogo(school.name)" class="school-logo" alt="学校logo">
              </div>
              <div class="school-info">
                <h3 class="school-name">{{ school.name }}</h3>
                <div class="school-tags">
                  <el-tag :type="getTypeTag(school)" size="small">
                    {{ getTypeName(school) }}
                  </el-tag>
                  <el-tag type="info" size="small" v-if="school.prefecture || school.city">
                    {{ getPrefectureName(school) }}
                  </el-tag>
                  <el-tag type="danger" size="small" v-if="school.min_score">
                    {{ school.min_score }}分
                  </el-tag>
                </div>
              </div>
              <!-- 取消收藏按钮 -->
              <div class="favorite-btn" @click.stop>
                <el-button
                  type="warning"
                  size="small"
                  circle
                  @click="removeFavorite(school.id)"
                >
                  <template #icon>
                    <StarFilled />
                  </template>
                </el-button>
              </div>
            </div>
            
            <div class="school-details">
              <div class="detail-item">
                <el-icon><MapPin /></el-icon>
                <span>{{ getPrefectureName(school) || '暂无位置信息' }}</span>
              </div>
              <div class="detail-item" v-if="school.address">
                <el-icon><Home /></el-icon>
                <span>{{ school.address }}</span>
              </div>
              <div class="detail-item" v-if="school.phone">
                <el-icon><Phone /></el-icon>
                <span>{{ school.phone }}</span>
              </div>
            </div>
          
            <div class="school-features" v-if="school.features">
              <el-tag
                v-for="feature in getFeatureList(school.features)"
                :key="feature"
                type="warning"
                size="small"
                effect="plain"
                class="feature-tag"
              >
                {{ feature }}
              </el-tag>
            </div>
            
            <div class="school-footer">
              <div class="view-count">
                <el-icon><Eye /></el-icon>
                <span>{{ school.view_count || 0 }} 浏览</span>
              </div>
              <div class="footer-actions">
                <el-button type="primary" size="small" text @click.stop="viewSchoolDetail(school.id)">
                  查看详情<el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Star, StarFilled, Refresh, Delete, Medal,
  MapLocation as MapPin, House as Home, Phone, View as Eye, ArrowRight, ArrowRightBold
} from '@element-plus/icons-vue'
import { useSharedStore } from '../store/shared'
import { schoolApi } from '@/api'

interface School {
  id: string | number
  name: string
  city: string
  prefecture: string
  district?: string
  type: number
  typeName?: string
  type_name?: string
  address?: string
  phone?: string
  logo?: string
  features?: string
  view_count?: number
  min_score?: number
  is_public?: number
  nature?: string
  is_key?: number | boolean
  level?: string
  tuition?: number | string
}

const router = useRouter()
const sharedStore = useSharedStore()

const favoriteSchools = ref<School[]>([])
const selectedForCompare = ref<(string | number)[]>([])
const loading = ref(false)

const colorPalette = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
  '#38f9d7', '#fa709a', '#fee140', '#f09819', '#ff9a9e',
  '#a8edea', '#fed6e3', '#6c5ce7', '#fd79a8', '#00b894',
  '#e17055', '#0984e3', '#00cec9', '#6c5ce7', '#fdcb6e'
]

const generateSchoolLogo = (schoolName: string): string => {
  if (!schoolName) {
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjRjNGNEY1Ii8+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAzOHYySDI0di0yaDEyeiIvPjxwYXRoIGQ9Ik0zNiA0MnYySDI0di0yaDEyeiIvPjxwYXRoIGQ9Ik00OCAzMHYySDM2di0yaDEyek00OCAzOHYySDM2di0yaDEyeiIvPjxwYXRoIGQ9Ik00OCA0MnYySDM2di0yaDEyeiIvPjwvc3ZnPg=='
  }
  
  let hash = 0
  for (let i = 0; i < schoolName.length; i++) {
    hash = schoolName.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  const colorIndex = Math.abs(hash) % colorPalette.length
  const bgColor = colorPalette[colorIndex]
  const initial = schoolName.charAt(0)
  
  const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80"><rect width="100%" height="100%" rx="12" fill="${bgColor}"/><text x="40" y="52" font-family="Microsoft YaHei, sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle">${initial}</text></svg>`
  return 'data:image/svg+xml,' + encodeURIComponent(svgStr)
}

const prefectureMap: Record<string, string> = {
  'km': '昆明市', 'qj': '曲靖市', 'yx': '玉溪市', 'bs': '保山市',
  'zt': '昭通市', 'lj': '丽江市', 'pe': '普洱市', 'lc': '临沧市',
  'cx': '楚雄州', 'hh': '红河州', 'ws': '文山州', 'xsbn': '西双版纳州',
  'dl': '大理州', 'dh': '德宏州', 'nj': '怒江州', 'dq': '迪庆州'
}

const getPrefectureName = (school: School): string => {
  if (!school) return ''
  const p = school.prefecture || school.city || school.district || ''
  return prefectureMap[p] || p
}

const typeMap: Record<number | string, string> = {
  1: '普通高中',
  2: '重点高中',
  3: '中职学校',
  4: '民办学校'
}

const tagMap: Record<number | string, string> = {
  1: 'info',
  2: 'success',
  3: 'warning',
  4: 'info'
}

const getTypeName = (school: School): string => {
  if (!school) return '未知'
  if (school.type_name) return school.type_name
  if (school.typeName) return school.typeName
  if (school.type && typeMap[school.type]) return typeMap[school.type]
  if (school.nature) return school.nature
  if (school.is_public === 1) return '公办'
  if (school.is_public === 0) return '民办'
  return '未知'
}

const getTypeTag = (school: School): 'info' | 'success' | 'warning' | 'primary' | 'danger' | undefined => {
  if (!school) return undefined
  if (school.type_name && tagMap[school.type_name]) return tagMap[school.type_name] as any
  if (school.typeName && tagMap[school.typeName]) return tagMap[school.typeName] as any
  if (school.type && tagMap[school.type]) return tagMap[school.type] as any
  if (school.is_public === 1) return 'success'
  if (school.is_public === 0) return 'warning'
  return undefined
}

const getFeatureList = (features: string): string[] => {
  if (!features) return []
  return String(features).split(/[,，]/).filter(f => f.trim()).slice(0, 4)
}

const publicCount = computed(() => 
  favoriteSchools.value.filter(s => s.is_public === 1 || s.nature === '公办' || s.tuition === 0).length
)

const privateCount = computed(() => 
  favoriteSchools.value.filter(s => {
    if (s.is_public === 0) return true
    if (s.nature === '民办') return true
    if (s.tuition && typeof s.tuition === 'number' && s.tuition > 0) return true
    return false
  }).length
)

const keyCount = computed(() => 
  favoriteSchools.value.filter(s => s.is_key === 1 || s.type === 2 || getTypeName(s) === '重点高中').length
)

const fetchFavoriteSchools = async () => {
  loading.value = true
  try {
    const favoriteIds = sharedStore.favorites
    if (favoriteIds.length === 0) {
      favoriteSchools.value = []
      return
    }

    // 批量获取学校信息
    const results: School[] = []
    for (const id of favoriteIds) {
      try {
        const response = await schoolApi.getSchoolDetail(id)
        if (response?.success && response.data) {
          results.push(response.data as unknown as School)
        }
      } catch (error) {
        console.error(`获取学校 ${id} 详情失败:`, error)
      }
    }
    
    favoriteSchools.value = results
  } catch (error) {
    console.error('获取收藏列表失败:', error)
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

const removeFavorite = async (schoolId: string | number) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏这个学校吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    sharedStore.removeFavorite(schoolId)
    favoriteSchools.value = favoriteSchools.value.filter(s => s.id !== schoolId)
    selectedForCompare.value = selectedForCompare.value.filter(id => id !== schoolId)
    ElMessage.success('已取消收藏')
  } catch (error) {
    // 用户取消
  }
}

const clearAllFavorites = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有收藏吗？此操作不可恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    sharedStore.favorites = []
    sharedStore.saveFavorites()
    favoriteSchools.value = []
    selectedForCompare.value = []
    ElMessage.success('清空收藏成功')
  } catch (error) {
    // 用户取消
  }
}

const toggleCompareSelect = (schoolId: string | number) => {
  const index = selectedForCompare.value.indexOf(schoolId)
  if (index > -1) {
    selectedForCompare.value.splice(index, 1)
  } else {
    if (selectedForCompare.value.length >= 4) {
      ElMessage.warning('最多只能选择4所学校进行对比')
      return
    }
    selectedForCompare.value.push(schoolId)
  }
}

const goToCompare = () => {
  if (selectedForCompare.value.length < 2) {
    ElMessage.warning('请至少选择2所学校进行对比')
    return
  }
  router.push(`/compare?ids=${selectedForCompare.value.join(',')}`)
}

const viewSchoolDetail = (schoolId: string | number) => {
  router.push(`/school/${schoolId}`)
}

const refreshFavorites = () => {
  fetchFavoriteSchools()
}

onMounted(() => {
  fetchFavoriteSchools()
})
</script>

<style scoped>
.favorite-page {
  min-height: 100vh;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.page-header {
  background: var(--primary-gradient);
  color: var(--text-primary);
  padding: 40px 0;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.page-desc {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px;
}

.favorite-stats {
  margin-bottom: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 28px;
  backdrop-filter: blur(10px);
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 15px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.public {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-icon.private {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
}

.stat-icon.key {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.favorite-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.favorite-list {
  margin-bottom: 40px;
}

.school-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

.school-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.school-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.select-box {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
}

.card-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.school-header {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  position: relative;
}

.school-logo-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-tertiary);
}

.school-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.school-info {
  flex: 1;
  min-width: 0;
}

.school-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.school-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.favorite-btn {
  flex-shrink: 0;
}

.school-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.detail-item .el-icon {
  flex-shrink: 0;
}

.school-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.feature-tag {
  font-size: 12px;
}

.school-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.footer-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
  
  .school-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-item {
    padding: 15px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .favorite-actions {
    flex-direction: column;
  }
  
  .favorite-actions .el-button {
    width: 100%;
  }
  
  .page-header {
    padding: 30px 0;
  }
  
  .page-title {
    font-size: 24px;
  }
}
</style>
