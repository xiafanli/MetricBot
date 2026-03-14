<template>
  <div class="home-container">
    <el-container class="main-layout">
      <el-aside class="sidebar" width="240">
        <div class="logo-area">
          <span class="logo-text">PrometheusBot</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><Monitor /></el-icon>
            <span>监控面板</span>
          </el-menu-item>
          <el-menu-item index="/chat">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能问答</span>
          </el-menu-item>
          <el-menu-item index="/alerts">
            <el-icon><Bell /></el-icon>
            <span>告警管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container class="main-content">
        <el-header class="header">
          <div class="header-left">
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="36">{{ userStore.getUsername?.charAt(0)?.toUpperCase() }}</el-avatar>
                <span class="username">{{ userStore.getUsername }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人信息
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
            <el-card class="welcome-card">
              <div class="welcome-content">
                <div class="welcome-icon">
                  <el-icon :size="80"><DataLine /></el-icon>
                </div>
                <h1 class="welcome-title">欢迎使用 PrometheusBot</h1>
                <p class="welcome-description">
                  基于大语言模型的 Prometheus 监控查询助手，让监控数据查询更简单、更智能
                </p>
              </div>
            </el-card>
          </div>

          <div class="features-section">
            <el-row :gutter="24">
              <el-col :span="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon">
                    <el-icon :size="40"><ChatDotRound /></el-icon>
                  </div>
                  <h3 class="feature-title">自然语言查询</h3>
                  <p class="feature-desc">用自然语言描述你的查询需求，AI自动生成PromQL</p>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon">
                    <el-icon :size="40"><DataLine /></el-icon>
                  </div>
                  <h3 class="feature-title">数据可视化</h3>
                  <p class="feature-desc">自动生成图表，直观展示监控数据趋势</p>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon">
                    <el-icon :size="40"><Bell /></el-icon>
                  </div>
                  <h3 class="feature-title">智能告警分析</h3>
                  <p class="feature-desc">分析告警信息，提供问题排查建议</p>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div class="actions-section">
            <el-button type="primary" size="large" @click="checkHealth">
              <el-icon><Connection /></el-icon>
              检查后端连接
            </el-button>
            <div v-if="healthStatus" class="status">
              <el-alert
                :title="healthStatus.message"
                type="success"
                :closable="false"
                show-icon
              />
            </div>
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
  DataLine,
  Connection
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

const checkHealth = async () => {
  try {
    const response = await api.healthCheck()
    healthStatus.value = response
  } catch (error) {
    console.error('Health check failed:', error)
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
  }
}
</script>

<style scoped>
.home-container {
  height: 100vh;
  background-color: #f5f7fa;
}

.main-layout {
  height: 100%;
}

.sidebar {
  background-color: #001529;
  display: flex;
  flex-direction: column;
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background-color: #001529;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.sidebar-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.65);
}

.sidebar-menu .el-menu-item:hover {
  color: white;
  background-color: #1890ff;
}

.sidebar-menu .el-menu-item.is-active {
  color: white;
  background-color: #1890ff;
}

.main-content {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
}

.header-left .page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.welcome-section {
  margin-bottom: 32px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.welcome-content {
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  color: white;
  margin-bottom: 24px;
}

.welcome-title {
  color: white;
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.welcome-description {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  margin: 0;
  line-height: 1.6;
}

.features-section {
  margin-bottom: 32px;
}

.feature-card {
  text-align: center;
  padding: 32px 24px;
  cursor: pointer;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #262626;
}

.feature-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6;
}

.actions-section {
  text-align: center;
}

.status {
  margin-top: 20px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}
</style>
