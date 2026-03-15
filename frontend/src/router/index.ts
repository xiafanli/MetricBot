import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { toLoginPage } from '@/utils/utils'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '监控面板', requiresAuth: true }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/Chat.vue'),
        meta: { title: '智能对话', requiresAuth: true }
      },
      {
        path: 'monitor',
        name: 'Monitor',
        component: () => import('../views/Monitor.vue'),
        meta: { title: '智能监控', requiresAuth: true }
      },
      {
        path: 'settings/models',
        name: 'Models',
        component: () => import('../views/settings/Models.vue'),
        meta: { title: '模型管理', requiresAuth: true }
      },
      {
        path: 'settings/datasources',
        name: 'Datasources',
        component: () => import('../views/settings/Datasources.vue'),
        meta: { title: '监控数据源', requiresAuth: true }
      },
      {
        path: 'settings/logs',
        name: 'Logs',
        component: () => import('../views/settings/Logs.vue'),
        meta: { title: '日志配置', requiresAuth: true }
      },
      {
        path: 'settings/hosts',
        name: 'Hosts',
        component: () => import('../views/settings/Hosts.vue'),
        meta: { title: '主机模型', requiresAuth: true }
      },
      {
        path: 'settings/relations',
        name: 'Relations',
        component: () => import('../views/settings/Relations.vue'),
        meta: { title: '关系模型', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

const whiteList = ['/login']

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (whiteList.includes(to.path)) {
    if (userStore.isLoggedIn) {
      next('/dashboard')
    } else {
      next()
    }
    return
  }
  
  if (!userStore.isLoggedIn) {
    next(toLoginPage(to.fullPath))
    return
  }
  
  if (!userStore.uid) {
    try {
      await userStore.info()
    } catch (error) {
      userStore.clear()
      next(toLoginPage(to.fullPath))
      return
    }
  }
  
  next()
})

export default router
