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
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
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
      next('/')
    } else {
      next()
    }
    return
  }
  
  if (!userStore.isLoggedIn) {
    next(toLoginPage(to.fullPath))
    return
  }
  
  if (!userStore.getUid) {
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