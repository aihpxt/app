import type { RouteRecordRaw } from 'vue-router'

const userRoutes: RouteRecordRaw[] = [
  {
    path: '/user',
    name: 'User',
    component: () => import('../../views/User.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../../views/LoginEnhanced.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../../views/LoginEnhanced.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/favorite',
    name: 'Favorite',
    component: () => import('../../views/Favorite.vue'),
    meta: { title: '我的收藏' }
  },
  {
    path: '/notification',
    name: 'Notification',
    component: () => import('../../views/Notification.vue'),
    meta: { title: '消息通知' }
  }
]

export default userRoutes