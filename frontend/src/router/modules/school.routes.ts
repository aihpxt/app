import type { RouteRecordRaw } from 'vue-router'

const schoolRoutes: RouteRecordRaw[] = [
  {
    path: '/school-test',
    name: 'SchoolTest',
    component: () => import('../../views/SchoolTest.vue'),
    meta: { title: '学校查询测试' }
  },
  {
    path: '/school-simple',
    name: 'SchoolSimple',
    component: () => import('../../views/SchoolSimple.vue'),
    meta: { title: '简化版学校查询' }
  },
  {
    path: '/school',
    name: 'School',
    component: () => import('../../views/School.vue'),
    meta: { title: '学校查询' }
  },
  {
    path: '/school/:id',
    name: 'SchoolDetail',
    component: () => import('../../views/SchoolDetail.vue'),
    meta: { title: '学校详情' }
  },
  {
    path: '/spec',
    name: 'SchoolSpec',
    component: () => import('../../views/SchoolSpec.vue'),
    meta: { title: '学校规格库' }
  },
  {
    path: '/compare',
    name: 'Compare',
    component: () => import('../../views/Compare.vue'),
    meta: { title: 'AI学校对比' }
  },
  {
    path: '/prefecture-policy',
    name: 'PrefecturePolicy',
    component: () => import('../../views/PrefecturePolicy.vue'),
    meta: { title: '各地州招录政策' }
  }
]

export default schoolRoutes