<template>
  <div class="home-container">
    <el-container class="main-layout">
      <el-aside class="sidebar" width="240">
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
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon class="menu-icon"><Monitor /></el-icon>
            <span>监控面板</span>
          </el-menu-item>
          <el-menu-item index="/chat">
            <el-icon class="menu-icon"><ChatDotRound /></el-icon>
            <span>智能问答</span>
          </el-menu-item>
          <el-menu-item index="/alerts">
            <el-icon class="menu-icon"><Bell /></el-icon>
            <span>告警管理</span>
          </el-menu-item>
        </el-menu>
        
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
      </el-aside>

      <el-container class="main-content">
        <el-header class="header">
          <div class="header-left">
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>
          <div class="header-right">
            <el-tooltip content="刷新" placement="bottom">
              <el-button circle class="header-btn" @click="refreshPage">
                <el-icon><Refresh /></el-icon>
              </el-button>
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
        </el-header>

        <el-main class="content">
          <div class="welcome-section">
            <div class="welcome-card">
              <div class="welcome-content">
                <div class="welcome-icon">
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
                <h1 class="welcome-title">欢迎使用 Metric Bot</h1>
                <p class="welcome-description">
                  智能运维监控平台，让运维分析更简单、更智能
                </p>
                <el-button type="primary" size="large" class="start-btn" @click="checkHealth">
                  <el-icon><Connection /></el-icon>
                  开始使用
                </el-button>
              </div>
            </div>
          </div>

          <div class="features-section">
            <div class="section-header">
              <h3 class="section-title">核心功能</h3>
              <p class="section-desc">强大的功能，简单的操作</p>
            </div>
            
            <el-row :gutter="24">
              <el-col :span="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon-wrapper" style="background: linear-gradient(135deg, #ffd700 0%, #ff6b35 100%);">
                    <el-icon :size="36"><ChatDotRound /></el-icon>
                  </div>
                  <h3 class="feature-title">自然语言查询</h3>
                  <p class="feature-desc">用自然语言描述你的查询需求，AI自动生成PromQL语句</p>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon-wrapper" style="background: linear-gradient(135deg, #ff6b35 0%, #f72585 100%);">
                    <el-icon :size="36"><DataLine /></el-icon>
                  </div>
                  <h3 class="feature-title">数据可视化</h3>
                  <p class="feature-desc">自动生成图表，直观展示监控数据趋势和变化</p>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon-wrapper" style="background: linear-gradient(135deg, #f72585 0%, #7209b7 100%);">
                    <el-icon :size="36"><Bell /></el-icon>
                  </div>
                  <h3 class="feature-title">智能告警分析</h3>
                  <p class="feature-desc">分析告警信息，提供问题排查建议和解决方案</p>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div class="stats-section">
            <div class="section-header">
              <h3 class="section-title">系统状态</h3>
            </div>
            
            <el-row :gutter="24">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-icon" style="background: rgba(255, 215, 0, 0.1);">
                    <el-icon :size="28" style="color: #ffd700;"><TrendCharts /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">3</div>
                    <div class="stat-label">数据源</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-icon" style="background: rgba(255, 107, 53, 0.1);">
                    <el-icon :size="28" style="color: #ff6b35;"><ChatDotRound /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">0</div>
                    <div class="stat-label">对话数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-icon" style="background: rgba(247, 37, 133, 0.1);">
                    <el-icon :size="28" style="color: #f72585;"><Bell /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">0</div>
                    <div class="stat-label">告警数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-icon" style="background: rgba(114, 9, 183, 0.1);">
                    <el-icon :size="28" style="color: #7209b7;"><User /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">1</div>
                    <div class="stat-label">用户数</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div v-if="healthStatus" class="health-section">
            <el-alert
              :title="healthStatus.message"
              type="success"
              :closable="false"
              show-icon
              class="health-alert"
            />
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor,
  ChatDotRound,
  Bell,
  User,
  SwitchButton,
  ArrowDown,
  TrendCharts,
  Connection,
  Refresh,
  Setting
} from '@element-plus/icons-vue'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const healthStatus = ref<any>(null)
const activeMenu = ref('/')

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/': '监控面板',
    '/chat': '智能问答',
    '/alerts': '告警管理'
  }
  return titles[route.path] || '监控面板'
})

const refreshPage = () => {
  window.location.reload()
}

const checkHealth = async () => {
  try {
    const response = await api.healthCheck()
    healthStatus.value = response
    ElMessage.success('后端连接正常！')
  } catch (error) {
    console.error('Health check failed:', error)
    ElMessage.error('后端连接失败，请检查服务状态')
  }
}

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  if (index === '/chat') {
    ElMessage.info('智能问答功能开发中...')
  } else if (index === '/alerts') {
    ElMessage.info('告警管理功能开发中...')
  }
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
    ElMessage.info('系统设置功能开发中...')
  }
}
</script>

<style lang="less" scoped>
.home-container {
  height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.main-layout {
  height: 100%;
}

.sidebar {
  background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 215, 0, 0.1);
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
}

.logo-wrapper {
  text-align: center;
}

.logo-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 12px;
}

.logo-text {
  display: block;
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 16px 0;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.sidebar-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.6);
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
  transition: all 0.2s;

  &:hover {
    color: white;
    background: rgba(255, 215, 0, 0.1);
  }

  &.is-active {
    color: white;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(247, 37, 133, 0.15) 100%);
    border-left: 2px solid #ffd700;
  }
}

.menu-icon {
  font-size: 18px;
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
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background: linear-gradient(180deg, rgba(26, 26, 46, 0.95) 0%, rgba(22, 33, 62, 0.95) 100%);
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 28px;
  height: 64px;
}

.header-left .page-title {
  margin: 0;
  font-size: 20px;
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
  padding: 28px;
}

.welcome-section {
  margin-bottom: 28px;
}

.welcome-card {
  border-radius: 16px;
  border: none;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.05) 0%, rgba(247, 37, 133, 0.05) 100%);
  border: 1px solid rgba(255, 215, 0, 0.1);
}

.welcome-content {
  text-align: center;
  padding: 48px 32px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-description {
  font-size: 14px;
  margin: 0 0 28px 0;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.7;
  max-width: 550px;
  margin-left: auto;
  margin-right: auto;
}

.start-btn {
  height: 46px;
  padding: 0 28px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  border: none;
  color: #0a0a0a;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
    color: #0a0a0a;
  }

  &:active {
    transform: translateY(0);
  }
}

.features-section {
  margin-bottom: 28px;
}

.section-header {
  text-align: center;
  margin-bottom: 28px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin: 0 0 6px 0;
}

.section-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.feature-card {
  text-align: center;
  padding: 28px 24px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
    border-color: rgba(255, 215, 0, 0.25);
  }
}

.feature-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  color: white;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
}

.feature-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 10px 0;
  color: white;
}

.feature-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.6;
}

.stats-section {
  margin-bottom: 28px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 18px;
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 215, 0, 0.2);
  }
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.health-section {
  margin-top: 20px;
}

.health-alert {
  border-radius: 10px;
}
</style>
