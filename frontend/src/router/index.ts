import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import schoolRoutes from './modules/school.routes'
import aiRoutes from './modules/ai.routes'
import userRoutes from './modules/user.routes'
import infoRoutes from './modules/info.routes'
import systemRoutes from './modules/system.routes'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeEnhanced.vue'),
    meta: { title: '首页' }
  },
  ...schoolRoutes,
  ...aiRoutes,
  ...userRoutes,
  ...infoRoutes,
  ...systemRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/HomeEnhanced.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(_to: unknown, _from: unknown, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 云南省AI择校平台` : '云南省AI全域赋能中考择校智能决策平台'
  
  const token = localStorage.getItem('token')
  
  let userInfo: Record<string, unknown> = {}
  try {
    const userInfoStr = localStorage.getItem('userInfo')
    if (userInfoStr) {
      userInfo = JSON.parse(userInfoStr)
    }
  } catch (error) {
    console.error('解析userInfo失败:', error)
    userInfo = {}
  }
  
  if (to.meta.requiresAuth && !token) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.meta.requiresAdmin && (!userInfo || userInfo.role !== 3)) {
    next('/user')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/user')
  } else {
    next()
  }
})

export default router