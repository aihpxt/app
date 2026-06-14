import type { RouteRecordRaw } from 'vue-router'

const infoRoutes: RouteRecordRaw[] = [
  {
    path: '/policy',
    name: 'Policy',
    component: () => import('../../views/Policy.vue'),
    meta: { title: '政策解读' }
  },
  {
    path: '/policy/:id',
    name: 'PolicyDetail',
    component: () => import('../../views/Policy.vue'),
    meta: { title: '政策详情' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../../views/Dashboard.vue'),
    meta: { title: '数据仪表盘' }
  },
  {
    path: '/unified-dashboard',
    name: 'UnifiedDashboard',
    component: () => import('../../views/UnifiedDashboard.vue'),
    meta: { title: '统一管理平台' }
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import('../../views/Data.vue'),
    meta: { title: '数据中心' }
  },
  {
    path: '/data-visualization',
    name: 'DataVisualization',
    component: () => import('../../views/DataVisualization.vue'),
    meta: { title: '数据分析', requiresAuth: true }
  },
  {
    path: '/campus-events',
    name: 'CampusEvents',
    component: () => import('../../views/CampusEvents.vue'),
    meta: { title: '校园活动日历' }
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('../../views/Help.vue'),
    meta: { title: '帮助中心' }
  },
  {
    path: '/legal/:type',
    name: 'Legal',
    component: () => import('../../views/Legal.vue'),
    meta: { title: '法律文档' }
  }
]

export default infoRoutes