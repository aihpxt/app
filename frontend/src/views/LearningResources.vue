<template>
  <div class="learning-resources-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">学习资源推荐</h1>
        <p class="page-desc">发现适合你的学习资料和课程</p>
      </div>
    </div>

    <div class="container">
      <div class="search-filter-section">
        <div class="card">
          <div class="search-filter-content">
            <div class="search-box">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索学习资源..."
                prefix-icon="Search"
                @keyup.enter="searchResources"
              >
                <template #append>
                  <el-button type="primary" @click="searchResources">
                    <el-icon><Search /></el-icon>
                    搜索
                  </el-button>
                </template>
              </el-input>
            </div>
            <div class="filter-box">
              <el-select v-model="selectedSubject" placeholder="选择科目" class="filter-select">
                <el-option label="全部科目" value="all" />
                <el-option label="语文" value="chinese" />
                <el-option label="数学" value="math" />
                <el-option label="英语" value="english" />
                <el-option label="物理" value="physics" />
                <el-option label="化学" value="chemistry" />
                <el-option label="生物" value="biology" />
                <el-option label="历史" value="history" />
                <el-option label="地理" value="geography" />
                <el-option label="政治" value="politics" />
              </el-select>
              <el-select v-model="selectedType" placeholder="资源类型" class="filter-select">
                <el-option label="全部类型" value="all" />
                <el-option label="视频课程" value="video" />
                <el-option label="练习题" value="exercise" />
                <el-option label="学习资料" value="material" />
                <el-option label="模拟试题" value="mock" />
              </el-select>
              <el-select v-model="selectedLevel" placeholder="难度等级" class="filter-select">
                <el-option label="全部难度" value="all" />
                <el-option label="基础" value="basic" />
                <el-option label="中等" value="medium" />
                <el-option label="高级" value="advanced" />
              </el-select>
            </div>
          </div>
        </div>
      </div>

      <div class="resources-section">
        <div class="section-header">
          <h2 class="section-title">推荐资源</h2>
          <div class="sort-options">
            <span>排序：</span>
            <el-radio-group v-model="sortBy">
              <el-radio value="popular">热门</el-radio>
              <el-radio value="newest">最新</el-radio>
              <el-radio value="rating">评分</el-radio>
            </el-radio-group>
          </div>
        </div>

        <div class="resources-grid">
          <div v-for="resource in filteredResources" :key="resource.id" class="resource-card card">
            <div class="resource-image">
              <img :src="resource.image" :alt="resource.title">
              <div class="resource-type">
                <el-tag :type="getResourceTypeTag(resource.type)">
                  {{ getResourceTypeText(resource.type) }}
                </el-tag>
              </div>
            </div>
            <div class="resource-content">
              <h3 class="resource-title">{{ resource.title }}</h3>
              <div class="resource-meta">
                <span class="resource-subject">{{ resource.subject }}</span>
                <span class="resource-level">{{ getResourceLevelText(resource.level) }}</span>
                <span class="resource-views">{{ resource.views }}次浏览</span>
              </div>
              <p class="resource-desc">{{ resource.description }}</p>
              <div class="resource-actions">
                <el-button type="primary" size="small" @click="viewResource(resource.id)">
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
                <el-button size="small" @click="favoriteResource(resource.id)" :type="resource.favorited ? 'success' : 'default'">
                  <el-icon><Star /></el-icon>
                  {{ resource.favorited ? '已收藏' : '收藏' }}
                </el-button>
              </div>
            </div>
          </div>
          <div v-if="filteredResources.length === 0" class="empty-resources">
            <el-empty description="暂无匹配的学习资源" />
          </div>
        </div>

        <div v-if="filteredResources.length > 0" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 36]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredResources.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <div class="featured-section">
        <div class="card">
          <div class="section-title">
            <el-icon><Star /></el-icon>
            <span>精选资源</span>
          </div>
          <div class="featured-grid">
            <div v-for="resource in featuredResources" :key="resource.id" class="featured-item">
              <div class="featured-image">
                <img :src="resource.image" :alt="resource.title">
              </div>
              <div class="featured-info">
                <h4 class="featured-title">{{ resource.title }}</h4>
                <p class="featured-desc">{{ resource.description }}</p>
                <el-button type="primary" size="small" @click="viewResource(resource.id)">
                  查看详情
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Document, Star } from '@element-plus/icons-vue'

export default {
  name: 'LearningResources',
  components: {
    Search, View: Document, Star
  },
  setup() {
    const searchKeyword = ref('')
    const selectedSubject = ref('all')
    const selectedType = ref('all')
    const selectedLevel = ref('all')
    const sortBy = ref('popular')
    const currentPage = ref(1)
    const pageSize = ref(12)

    const resources = ref([
      {
        id: 1,
        title: '2026年中考数学必考点精讲',
        description: '全面覆盖中考数学必考知识点，由资深教师讲解，帮助学生快速掌握解题技巧',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '数学',
        type: 'video',
        level: 'medium',
        views: 12580,
        rating: 4.8,
        favorited: false
      },
      {
        id: 2,
        title: '中考英语词汇记忆技巧',
        description: '通过科学的记忆方法，帮助学生快速掌握中考必备英语词汇',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '英语',
        type: 'video',
        level: 'basic',
        views: 9876,
        rating: 4.6,
        favorited: true
      },
      {
        id: 3,
        title: '物理实验操作指南',
        description: '详细讲解中考物理实验操作步骤和注意事项，提高实验题得分率',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '物理',
        type: 'material',
        level: 'medium',
        views: 7654,
        rating: 4.7,
        favorited: false
      },
      {
        id: 4,
        title: '2026年中考模拟试题集',
        description: '包含最新中考模拟试题，帮助学生熟悉考试题型和难度',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '全部科目',
        type: 'mock',
        level: 'advanced',
        views: 15678,
        rating: 4.9,
        favorited: false
      },
      {
        id: 5,
        title: '化学方程式速记手册',
        description: '整理了中考化学必备的化学方程式，帮助学生快速记忆',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '化学',
        type: 'material',
        level: 'basic',
        views: 6543,
        rating: 4.5,
        favorited: true
      },
      {
        id: 6,
        title: '语文阅读理解答题技巧',
        description: '详细讲解中考语文阅读理解的解题方法和技巧，提高阅读题得分率',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '语文',
        type: 'video',
        level: 'medium',
        views: 8765,
        rating: 4.6,
        favorited: false
      },
      {
        id: 7,
        title: '数学几何证明题专项训练',
        description: '针对中考数学几何证明题的专项练习，提高解题能力',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '数学',
        type: 'exercise',
        level: 'advanced',
        views: 5432,
        rating: 4.7,
        favorited: false
      },
      {
        id: 8,
        title: '英语听力提高训练',
        description: '包含中考英语听力模拟题和技巧讲解，帮助学生提高听力水平',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '英语',
        type: 'exercise',
        level: 'medium',
        views: 7890,
        rating: 4.5,
        favorited: false
      },
      {
        id: 9,
        title: '物理力学知识点总结',
        description: '全面总结中考物理力学知识点，帮助学生系统掌握力学内容',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '物理',
        type: 'material',
        level: 'medium',
        views: 6789,
        rating: 4.8,
        favorited: true
      },
      {
        id: 10,
        title: '化学实验视频教程',
        description: '通过视频演示中考化学实验操作过程，帮助学生理解实验原理',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '化学',
        type: 'video',
        level: 'medium',
        views: 8901,
        rating: 4.7,
        favorited: false
      },
      {
        id: 11,
        title: '语文作文写作技巧',
        description: '讲解中考语文作文的写作方法和技巧，帮助学生提高作文水平',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '语文',
        type: 'video',
        level: 'basic',
        views: 10123,
        rating: 4.6,
        favorited: false
      },
      {
        id: 12,
        title: '数学函数专项练习',
        description: '针对中考数学函数部分的专项练习，提高函数题解题能力',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
        subject: '数学',
        type: 'exercise',
        level: 'advanced',
        views: 4321,
        rating: 4.5,
        favorited: false
      }
    ])

    const featuredResources = ref([
      {
        id: 13,
        title: '2026年中考备考指南',
        description: '全面的中考备考策略和方法，帮助学生高效备考',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
      },
      {
        id: 14,
        title: '中考状元学习方法分享',
        description: '历届中考状元的学习方法和经验分享，帮助学生找到适合自己的学习方式',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
      },
      {
        id: 15,
        title: '中考心理调节指南',
        description: '帮助学生调整考试心态，减轻考试压力，发挥最佳水平',
        image: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
      }
    ])

    const filteredResources = computed(() => {
      let result = [...resources.value]

      // 搜索关键词过滤
      if (searchKeyword.value) {
        result = result.filter(resource => 
          resource.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
          resource.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
        )
      }

      // 科目过滤
      if (selectedSubject.value !== 'all') {
        result = result.filter(resource => 
          resource.subject === selectedSubject.value || resource.subject === '全部科目'
        )
      }

      // 类型过滤
      if (selectedType.value !== 'all') {
        result = result.filter(resource => resource.type === selectedType.value)
      }

      // 难度过滤
      if (selectedLevel.value !== 'all') {
        result = result.filter(resource => resource.level === selectedLevel.value)
      }

      // 排序
      if (sortBy.value === 'popular') {
        result.sort((a, b) => b.views - a.views)
      } else if (sortBy.value === 'newest') {
        // 假设资源是按ID降序排列的，ID越大越新
        result.sort((a, b) => b.id - a.id)
      } else if (sortBy.value === 'rating') {
        result.sort((a, b) => b.rating - a.rating)
      }

      return result
    })

    const getResourceTypeTag = (type) => {
      const tags = { video: 'primary', exercise: 'success', material: 'warning', mock: 'danger' }
      return tags[type] || 'info'
    }

    const getResourceTypeText = (type) => {
      const texts = { video: '视频课程', exercise: '练习题', material: '学习资料', mock: '模拟试题' }
      return texts[type] || '其他'
    }

    const getResourceLevelText = (level) => {
      const texts = { basic: '基础', medium: '中等', advanced: '高级' }
      return texts[level] || '未知'
    }

    const searchResources = () => {
      currentPage.value = 1
    }

    const viewResource = (id) => {
      ElMessage.info(`查看资源ID: ${id}`)
    }

    const favoriteResource = (id) => {
      const resource = resources.value.find(r => r.id === id)
      if (resource) {
        resource.favorited = !resource.favorited
        ElMessage.success(resource.favorited ? '已添加到收藏' : '已取消收藏')
      }
    }

    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
    }

    const handleCurrentChange = (current) => {
      currentPage.value = current
    }

    return {
      searchKeyword,
      selectedSubject,
      selectedType,
      selectedLevel,
      sortBy,
      currentPage,
      pageSize,
      resources,
      filteredResources,
      featuredResources,
      getResourceTypeTag,
      getResourceTypeText,
      getResourceLevelText,
      searchResources,
      viewResource,
      favoriteResource,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.learning-resources-page {
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
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(10px);
}

.search-filter-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-box {
  width: 100%;
}

.filter-box {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.filter-select {
  min-width: 150px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-title .el-icon {
  font-size: 24px;
  color: #409eff;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 10px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}

.resource-card {
  display: flex;
  flex-direction: column;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.resource-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.3);
}

.resource-image {
  position: relative;
  height: 180px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 16px;
}

.resource-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.resource-card:hover .resource-image img {
  transform: scale(1.05);
}

.resource-type {
  position: absolute;
  top: 10px;
  left: 10px;
}

.resource-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.resource-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
  line-height: 1.4;
}

.resource-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--text-muted);
}

.resource-desc {
  flex: 1;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 16px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.resource-actions {
  display: flex;
  gap: 10px;
}

.empty-resources {
  grid-column: 1 / -1;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.featured-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.featured-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-sm);
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.featured-image {
  width: 120px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.featured-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.featured-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.featured-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-bottom: 12px;
  flex: 1;
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .filter-box {
    flex-direction: column;
  }

  .filter-select {
    width: 100%;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .resources-grid {
    grid-template-columns: 1fr;
  }

  .featured-grid {
    grid-template-columns: 1fr;
  }

  .featured-item {
    flex-direction: column;
  }

  .featured-image {
    width: 100%;
    height: 150px;
  }
}
</style>