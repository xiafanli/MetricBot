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
        redirect: '/alerts/list'
      },
      {
        path: 'alerts/rules',
        name: 'AlertRules',
        component: () => import('../views/alert/AlertRules.vue'),
        meta: { title: '告警规则', requiresAuth: true }
      },
      {
        path: 'alerts/list',
        name: 'AlertList',
        component: () => import('../views/alert/AlertList.vue'),
        meta: { title: '告警列表', requiresAuth: true }
      },
      {
        path: 'alerts/groups',
        name: 'AlertGroups',
        component: () => import('../views/alert/AlertGroups.vue'),
        meta: { title: '聚合告警', requiresAuth: true }
      },
      {
        path: 'alerts/policies',
        name: 'PolicyConfig',
        component: () => import('../views/alert/PolicyConfig.vue'),
        meta: { title: '聚合策略配置', requiresAuth: true }
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
      },
      {
        path: 'simulator',
        name: 'SimulatorLayout',
        component: () => import('../views/simulator/Layout.vue'),
        redirect: '/simulator/environment',
        meta: { title: '生产环境模拟器', requiresAuth: true },
        children: [
          {
            path: 'environment',
            name: 'SimulatorEnvironment',
            component: () => import('../views/simulator/EnvironmentManagement.vue'),
            meta: { title: '环境管理', requiresAuth: true }
          },
          {
            path: 'templates',
            name: 'SimulatorTemplates',
            component: () => import('../views/simulator/TemplateManagement.vue'),
            meta: { title: '模板管理', requiresAuth: true }
          },
          {
            path: 'faults',
            name: 'SimulatorFaults',
            component: () => import('../views/simulator/FaultManagement.vue'),
            meta: { title: '故障场景', requiresAuth: true }
          }
        ]
      },
      {
        path: 'simulator/wizard',
        name: 'SimulatorWizard',
        component: () => import('../views/simulator/TopologyWizard.vue'),
        meta: { title: '拓扑生成向导', requiresAuth: true }
      },
      {
        path: 'simulator/replay',
        name: 'ScenarioReplay',
        component: () => import('../views/simulator/ScenarioReplay.vue'),
        meta: { title: '历史场景回放', requiresAuth: true }
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
