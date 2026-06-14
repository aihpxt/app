import type { RouteRecordRaw } from 'vue-router'

const systemRoutes: RouteRecordRaw[] = [
  {
    path: '/high-school-transition',
    name: 'HighSchoolTransitionCourses',
    component: () => import('../../views/HighSchoolTransitionCourses.vue'),
    meta: { title: '高中衔接课程', requiresAuth: true }
  },
  {
    path: '/online-test',
    name: 'OnlineTest',
    component: () => import('../../views/OnlineTest.vue'),
    meta: { title: '在线测试', requiresAuth: true }
  },
  {
    path: '/learning-progress',
    name: 'LearningProgress',
    component: () => import('../../views/LearningProgress.vue'),
    meta: { title: '学习进度', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../../views/Admin.vue'),
    meta: { title: '后台管理', requiresAuth: true, requiresAdmin: true }
  }
]

export default systemRoutes