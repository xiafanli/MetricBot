<template>
  <div class="simulator-layout">
    <div class="sub-tabs-header">
      <div class="tabs-nav">
        <router-link 
          v-for="tab in tabs" 
          :key="tab.path"
          :to="tab.path"
          class="tab-item"
          :class="{ active: isActive(tab.path) }"
        >
          <el-icon v-if="tab.icon"><component :is="tab.icon" /></el-icon>
          <span>{{ tab.title }}</span>
        </router-link>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="small" @click="goToWizard">
          <el-icon><Plus /></el-icon>
          向导生成
        </el-button>
      </div>
    </div>
    <div class="sub-tabs-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Monitor, Document, Warning } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const tabs = [
  { path: '/simulator/environment', title: '环境管理', icon: Monitor },
  { path: '/simulator/templates', title: '模板管理', icon: Document },
  { path: '/simulator/faults', title: '故障场景', icon: Warning }
]

const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const goToWizard = () => {
  router.push('/simulator/wizard')
}
</script>

<style lang="less" scoped>
.simulator-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
  font-family: var(--font-body);
}

.sub-tabs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}

.tabs-nav {
  display: flex;
  gap: 0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 20px;
  color: var(--text-tertiary);
  font-size: 14px;
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;

  &:hover {
    color: var(--text-primary);
    background: rgba(0, 245, 255, 0.05);
  }

  &.active {
    color: var(--neon-blue);
    border-bottom-color: var(--neon-blue);
    background: rgba(0, 245, 255, 0.08);
  }

  .el-icon {
    font-size: 16px;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;

  .el-button--primary {
    background: var(--gradient-neon);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
  }
}

.sub-tabs-content {
  flex: 1;
  min-height: 0;
  overflow: auto;
  background: var(--bg-primary);
}
</style>
