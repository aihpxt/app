import type { RouteRecordRaw } from 'vue-router'

const aiRoutes: RouteRecordRaw[] = [
  {
    path: '/ai-selection',
    name: 'AiSelection',
    component: () => import('../../views/AiSelection.vue'),
    meta: { title: 'AI智能择校', requiresAuth: true }
  },
  {
    path: '/score-prediction',
    name: 'ScorePrediction',
    component: () => import('../../views/ScorePrediction.vue'),
    meta: { title: 'AI分数预测', requiresAuth: true }
  },
  {
    path: '/volunteer',
    name: 'Volunteer',
    component: () => import('../../views/Volunteer.vue'),
    meta: { title: 'AI志愿填报', requiresAuth: true }
  },
  {
    path: '/transition',
    name: 'Transition',
    component: () => import('../../views/Transition.vue'),
    meta: { title: 'AI高中衔接', requiresAuth: true }
  },
  {
    path: '/volunteer-practice',
    name: 'VolunteerPractice',
    component: () => import('../../views/VolunteerPractice.vue'),
    meta: { title: '模拟志愿填报演练', requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'AiAssistant',
    component: () => import('../../views/AiAssistant.vue'),
    meta: { title: '小龙虾智能助手' }
  },
  {
    path: '/learning-plan',
    name: 'LearningPlan',
    component: () => import('../../views/LearningPlan.vue'),
    meta: { title: '学习计划生成' }
  },
  {
    path: '/learning-resources',
    name: 'LearningResources',
    component: () => import('../../views/LearningResources.vue'),
    meta: { title: '学习资源推荐' }
  }
]

export default aiRoutes