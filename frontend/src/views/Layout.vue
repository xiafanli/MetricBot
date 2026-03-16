<template>
  <div class="layout-container">
    <div class="main-layout">
      <aside class="sidebar" :class="{ collapsed: isCollapsed }">
        <div class="sidebar-header">
          <div class="logo-wrapper">
            <div class="logo-icon">
              <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="45" stroke="url(#grad1)" stroke-width="2" fill="none"/>
                <circle cx="50" cy="50" r="35" stroke="url(#grad1)" stroke-width="1.5" fill="none" opacity="0.7"/>
                <circle cx="50" cy="50" r="25" stroke="url(#grad1)" stroke-width="1" fill="none" opacity="0.5"/>
                <path d="M20 50 L40 50 M60 50 L80 50 M50 20 L50 40 M50 60 L50 80" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/>
                <circle cx="50" cy="50" r="8" fill="url(#grad1)"/>
                <defs>
                  <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ffd700"/>
                    <stop offset="50%" style="stop-color:#ff6b35"/>
                    <stop offset="100%" style="stop-color:#f72585"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <span class="logo-text">Metric Bot</span>
          </div>
          <button class="collapse-btn" @click="toggleCollapse">
            <el-icon><Fold /></el-icon>
          </button>
        </div>
        
        <nav class="sidebar-nav">
          <div 
            v-for="item in menuItems" 
            :key="item.path"
            class="nav-item"
            :class="{ 
              active: item.path === activeMenu,
              'has-children': item.children 
            }"
          >
            <div 
              class="nav-title" 
              :class="{ 
                active: item.path === activeMenu || (item.children && isChildActive(item.children)),
                opened: item.children && openedMenus.includes(item.path)
              }"
              @click="handleMenuClick(item)"
            >
              <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
              <span class="nav-text">{{ item.title }}</span>
              <el-icon class="nav-arrow" :class="{ rotated: item.children && openedMenus.includes(item.path) }">
                <ArrowDown v-if="item.children" />
              </el-icon>
            </div>
            
            <div v-if="item.children" class="nav-children" :class="{ expanded: openedMenus.includes(item.path) }">
              <div 
                v-for="child in item.children" 
                :key="child.path"
                class="nav-child"
                :class="{ active: child.path === activeMenu }"
                @click="navigateTo(child.path)"
              >
                <el-icon class="child-icon"><component :is="child.icon" /></el-icon>
                <span class="child-text">{{ child.title }}</span>
              </div>
            </div>
          </div>
        </nav>
        
        <div class="sidebar-footer">
          <div class="user-section">
            <el-avatar :size="40" class="user-avatar">
              {{ userStore.getUsername?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <div class="user-info">
              <div class="user-name">{{ userStore.getUsername }}</div>
              <div class="user-role">
                {{ userStore.getIsSuperuser ? '超级管理员' : '普通用户' }}
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div class="main-content">
        <header class="header">
          <div class="header-left">
            <button v-if="isCollapsed" class="expand-btn" @click="toggleCollapse">
              <el-icon><Expand /></el-icon>
            </button>
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>
          <div class="header-right">
            <el-tooltip content="刷新" placement="bottom">
              <button class="header-btn" @click="refreshPage">
                <el-icon><Refresh /></el-icon>
              </button>
            </el-tooltip>
            
            <el-dropdown @command="handleCommand">
              <div class="user-dropdown">
                <el-avatar :size="36">
                  {{ userStore.getUsername?.charAt(0)?.toUpperCase() }}
                </el-avatar>
                <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人信息
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    系统设置
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </header>

        <main class="content">
          <router-view v-slot="{ Component }">
            <component :is="Component" />
          </router-view>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, markRaw } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor,
  ChatDotRound,
  Bell,
  User,
  SwitchButton,
  ArrowDown,
  Refresh,
  Setting,
  Fold,
  Expand,
  SetUp,
  Coin,
  Document,
  Share
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

interface MenuItem {
  path: string
  title: string
  icon: any
  children?: MenuItem[]
}

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapsed = ref(false)
const openedMenus = ref<string[]>(['/settings'])

const menuItems: MenuItem[] = [
  { path: '/dashboard', title: '监控面板', icon: markRaw(Monitor) },
  { path: '/chat', title: '智能对话', icon: markRaw(ChatDotRound) },
  { path: '/monitor', title: '智能监控', icon: markRaw(Bell) },
  { 
    path: '/settings', 
    title: '配置中心', 
    icon: markRaw(Setting),
    children: [
      { path: '/settings/models', title: '模型管理', icon: markRaw(SetUp) },
      { path: '/settings/datasources', title: '监控数据源', icon: markRaw(Coin) },
      { path: '/settings/logs', title: '日志配置', icon: markRaw(Document) },
      { path: '/settings/hosts', title: '主机模型', icon: markRaw(Monitor) },
      { path: '/settings/relations', title: '关系模型', icon: markRaw(Share) }
    ]
  }
]

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': '监控面板',
    '/chat': '智能对话',
    '/monitor': '智能监控',
    '/settings': '配置中心',
    '/settings/models': '模型管理',
    '/settings/datasources': '监控数据源',
    '/settings/logs': '日志配置',
    '/settings/hosts': '主机模型',
    '/settings/relations': '关系模型'
  }
  return titles[route.path] || 'Metric Bot'
})

const isChildActive = (children: MenuItem[]) => {
  return children.some(child => child.path === route.path)
}

const handleMenuClick = (item: MenuItem) => {
  if (item.children) {
    const index = openedMenus.value.indexOf(item.path)
    if (index > -1) {
      openedMenus.value.splice(index, 1)
    } else {
      openedMenus.value.push(item.path)
    }
  } else {
    navigateTo(item.path)
  }
}

const navigateTo = (path: string) => {
  router.push(path)
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const refreshPage = () => {
  window.location.reload()
}

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await userStore.logout()
      ElMessage.success('退出登录成功！')
      router.push('/login')
    } catch (error) {
      console.log('取消退出登录')
    }
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能开发中...')
  } else if (command === 'settings') {
    router.push('/settings/models')
  }
}
</script>

<style lang="less" scoped>
.layout-container {
  height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.main-layout {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 215, 0, 0.1);
  flex-shrink: 0;
  transform: translateZ(0);
  backface-visibility: hidden;

  &.collapsed {
    width: 64px;
  }
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  box-sizing: border-box;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.collapse-btn, .expand-btn {
  background: transparent;
  border: none;
  color: rgba(255, 215, 0, 0.6);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: #ffd700;
    background: rgba(255, 215, 0, 0.1);
  }
}

.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
  transform: translateZ(0);
}

.nav-item {
  margin: 4px 12px;
}

.nav-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 44px;
  height: 44px;
  border-radius: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  transform: translateZ(0);

  &:hover {
    color: white;
    background: rgba(255, 215, 0, 0.1);
  }

  &.active {
    color: white;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(247, 37, 133, 0.15) 100%);
    border-left: 2px solid #ffd700;
  }

  &.opened {
    color: white;
    background: rgba(255, 215, 0, 0.08);
  }
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.nav-text {
  flex: 1;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  opacity: 1;
}

.nav-arrow {
  font-size: 12px;
  flex-shrink: 0;
  opacity: 1;
  width: 12px;
  visibility: hidden;

  &.rotated {
    transform: rotate(180deg);
  }

  .el-icon {
    visibility: visible;
  }
}

.nav-children {
  max-height: 0;
  overflow: hidden;
  opacity: 0;

  &.expanded {
    max-height: 300px;
    opacity: 1;
  }
}

.sidebar.collapsed {
  .nav-text,
  .nav-arrow,
  .nav-children,
  .sidebar-footer,
  .logo-text,
  .collapse-btn {
    opacity: 0;
    pointer-events: none;
  }
}

.nav-child {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px 0 44px;
  height: 40px;
  margin: 2px 0;
  border-radius: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.5);
  transform: translateZ(0);

  &:hover {
    color: white;
    background: rgba(255, 215, 0, 0.1);
  }

  &.active {
    color: white;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(247, 37, 133, 0.2) 100%);
    border-left: 2px solid #ffd700;
  }
}

.child-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.child-text {
  font-size: 13px;
  white-space: nowrap;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 215, 0, 0.1);
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  background: rgba(255, 215, 0, 0.03);
}

.user-avatar {
  background: linear-gradient(135deg, #ffd700 0%, #f72585 100%);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  color: white;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.user-role {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.header {
  background: linear-gradient(180deg, rgba(26, 26, 46, 0.95) 0%, rgba(22, 33, 62, 0.95) 100%);
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left .page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-btn {
  background: rgba(255, 215, 0, 0.05);
  border: 1px solid rgba(255, 215, 0, 0.2);
  color: #ffd700;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 215, 0, 0.1);
    border-color: rgba(255, 215, 0, 0.4);
    color: #ffd700;
  }
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 10px;
  background: rgba(255, 215, 0, 0.03);
  border: 1px solid rgba(255, 215, 0, 0.1);
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 215, 0, 0.08);
    border-color: rgba(255, 215, 0, 0.3);
  }
}

.dropdown-arrow {
  color: rgba(255, 215, 0, 0.5);
  font-size: 14px;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
