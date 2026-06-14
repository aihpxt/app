<template>
  <div class="transition-courses-page">
    <div class="page-header">
      <h1 class="page-title">高中衔接课程</h1>
      <p class="page-subtitle">提前预习高中课程，顺利过渡到高中学习生活</p>
    </div>

    <div class="courses-container">
      <el-card class="input-card">
        <el-form :model="formData" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="目标学校">
                <el-select v-model="formData.targetSchool" placeholder="请选择目标学校" filterable>
                  <el-option
                    v-for="school in schools"
                    :key="school"
                    :label="school"
                    :value="school"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="中考分数">
                <el-input-number
                  v-model="formData.studentScore"
                  :min="0"
                  :max="750"
                  placeholder="请输入分数"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="学习风格">
                <el-select v-model="formData.learningStyle" placeholder="请选择学习风格">
                  <el-option label="自主学习型" value="self-driven" />
                  <el-option label="结构化学习型" value="structured" />
                  <el-option label="平衡学习型" value="balanced" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="薄弱科目">
                <el-checkbox-group v-model="formData.weakSubjects">
                  <el-checkbox label="语文" />
                  <el-checkbox label="数学" />
                  <el-checkbox label="英语" />
                  <el-checkbox label="物理" />
                  <el-checkbox label="化学" />
                  <el-checkbox label="生物" />
                </el-checkbox-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item>
            <el-button type="primary" @click="loadCourses" :loading="loading">
              生成衔接课程
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <div v-if="coursesData" class="courses-content">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>核心课程</h3>
              <el-tag type="primary">必修</el-tag>
            </div>
          </template>
          <div class="core-courses-grid">
            <div
              v-for="course in coursesData.coreCourses"
              :key="course.courseId"
              class="course-card"
            >
              <div class="course-header">
                <h4 class="course-title">{{ course.title }}</h4>
                <el-tag :type="getDifficultyColor(course.difficulty)" size="small">
                  {{ course.difficulty }}
                </el-tag>
              </div>
              <div class="course-info">
                <div class="info-item">
                  <el-icon><Reading /></el-icon>
                  <span>{{ course.subject }}</span>
                </div>
                <div class="info-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ course.duration }}</span>
                </div>
              </div>
              <div class="course-lessons">
                <h5>课程内容</h5>
                <el-collapse>
                  <el-collapse-item
                    v-for="lesson in course.lessons"
                    :key="lesson.lessonId"
                    :title="`${lesson.lessonId}. ${lesson.title}`"
                  >
                    <div class="lesson-content">
                      <div class="lesson-duration">
                        <el-icon><Timer /></el-icon>
                        <span>{{ lesson.duration }}</span>
                      </div>
                      <p>{{ lesson.content }}</p>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
              <div class="course-requirements">
                <h5>前置要求</h5>
                <el-tag
                  v-for="req in course.prerequisites"
                  :key="req"
                  size="small"
                  type="info"
                >
                  {{ req }}
                </el-tag>
              </div>
              <div class="course-objectives">
                <h5>学习目标</h5>
                <ul>
                  <li v-for="obj in course.learningObjectives" :key="obj">{{ obj }}</li>
                </ul>
              </div>
              <div class="course-resources">
                <h5>学习资源</h5>
                <div class="resources-list">
                  <el-tag
                    v-for="resource in course.resources"
                    :key="resource"
                    size="small"
                    effect="plain"
                  >
                    {{ resource }}
                  </el-tag>
                </div>
              </div>
              <el-button type="primary" class="start-btn" @click="startCourse(course)">
                开始学习
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>选修课程</h3>
              <el-tag type="success">推荐</el-tag>
            </div>
          </template>
          <div class="elective-courses-grid">
            <div
              v-for="course in coursesData.electiveCourses"
              :key="course.courseId"
              class="elective-card"
            >
              <div class="elective-header">
                <h4 class="elective-title">{{ course.title }}</h4>
                <el-tag :type="getDifficultyColor(course.difficulty)" size="small">
                  {{ course.difficulty }}
                </el-tag>
              </div>
              <div class="elective-info">
                <div class="info-item">
                  <el-icon><Reading /></el-icon>
                  <span>{{ course.subject }}</span>
                </div>
                <div class="info-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ course.duration }}</span>
                </div>
              </div>
              <p class="elective-description">{{ course.description }}</p>
              <el-button type="primary" plain class="start-btn" @click="startCourse(course)">
                开始学习
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>学习计划</h3>
              <el-tag type="warning">规划</el-tag>
            </div>
          </template>
          <el-timeline class="study-timeline">
            <el-timeline-item
              v-for="(phase, idx) in coursesData.studyPlan"
              :key="phase.name"
              :timestamp="phase.name"
              placement="top"
            >
              <el-card class="phase-card">
                <h4>{{ phase.name }}</h4>
                <p class="phase-content">{{ phase.content }}</p>
                <div class="phase-courses">
                  <el-tag
                    v-for="courseId in phase.courses"
                    :key="courseId"
                    size="small"
                    type="primary"
                  >
                    {{ getCourseName(courseId) }}
                  </el-tag>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>适应指南</h3>
              <el-tag type="info">建议</el-tag>
            </div>
          </template>
          <div class="adaptation-guide">
            <div
              v-for="(guide, idx) in coursesData.adaptationGuide"
              :key="guide"
              class="guide-item"
            >
              <div class="guide-number">{{ idx + 1 }}</div>
              <div class="guide-content">{{ guide }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Reading, Clock, Timer } from '@element-plus/icons-vue'
import { aiApi } from '@/api'

export default {
  name: 'HighSchoolTransitionCourses',
  components: {
    Reading,
    Clock,
    Timer
  },
  setup() {
    const loading = ref(false)
    const coursesData = ref(null)
    const formData = ref({
      targetSchool: '',
      studentScore: 600,
      learningStyle: 'balanced',
      weakSubjects: []
    })

    const schools = [
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
    ]

    const loadCourses = async () => {
      loading.value = true
      try {
        const response = await aiApi.getHighSchoolTransitionCourses({
          targetSchool: formData.value.targetSchool,
          studentScore: formData.value.studentScore,
          learningStyle: formData.value.learningStyle,
          weakSubjects: formData.value.weakSubjects
        })
        coursesData.value = response.data
        ElMessage.success('衔接课程生成成功！')
      } catch (error) {
        ElMessage.error('生成衔接课程失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }

    const resetForm = () => {
      formData.value = {
        targetSchool: '',
        studentScore: 600,
        learningStyle: 'balanced',
        weakSubjects: []
      }
      coursesData.value = null
    }

    const getDifficultyColor = (difficulty) => {
      const colorMap = {
        '简单': 'success',
        '中等': 'primary',
        '较难': 'warning',
        '困难': 'danger'
      }
      return colorMap[difficulty] || 'info'
    }

    const getCourseName = (courseId) => {
      if (!coursesData.value) return courseId
      const allCourses = [
        ...coursesData.value.coreCourses,
        ...coursesData.value.electiveCourses
      ]
      const course = allCourses.find(c => c.courseId === courseId)
      return course ? course.title : courseId
    }

    const startCourse = (course) => {
      ElMessage.success(`开始学习${course.title}，祝您学习顺利！`)
    }

    onMounted(() => {
      loadCourses()
    })

    return {
      loading,
      coursesData,
      formData,
      schools,
      loadCourses,
      resetForm,
      getDifficultyColor,
      getCourseName,
      startCourse
    }
  }
}
</script>

<style scoped>
.transition-courses-page {
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 16px;
  color: #606266;
}

.courses-container {
  max-width: 1400px;
  margin: 0 auto;
}

.input-card {
  margin-bottom: 30px;
  border-radius: 8px;
}

.courses-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.section-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.core-courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.course-card {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.course-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-5px);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.course-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.course-info {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
  font-size: 14px;
}

.course-lessons,
.course-requirements,
.course-objectives,
.course-resources {
  margin-bottom: 15px;
}

.course-lessons h5,
.course-requirements h5,
.course-objectives h5,
.course-resources h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.lesson-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lesson-duration {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 13px;
}

.lesson-content p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.course-requirements .el-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.course-objectives ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  line-height: 1.8;
}

.course-objectives li {
  margin-bottom: 5px;
}

.resources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.start-btn {
  width: 100%;
  margin-top: 10px;
}

.elective-courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.elective-card {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.elective-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-5px);
}

.elective-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.elective-title {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.elective-info {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.elective-description {
  margin: 0 0 15px 0;
  color: #606266;
  line-height: 1.6;
  min-height: 60px;
}

.study-timeline {
  padding-left: 20px;
}

.phase-card {
  border-radius: 8px;
}

.phase-card h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.phase-content {
  margin: 0 0 15px 0;
  color: #606266;
  line-height: 1.6;
}

.phase-courses {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.adaptation-guide {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.guide-item {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.guide-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.guide-content {
  flex: 1;
  color: #606266;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .core-courses-grid,
  .elective-courses-grid,
  .adaptation-guide {
    grid-template-columns: 1fr;
  }

  .courses-content .el-row {
    flex-direction: column;
  }

  .courses-content .el-col {
    width: 100%;
  }
}
</style>