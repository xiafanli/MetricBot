<template>
  <div class="monitor-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">智能监控中心</h2>
        <span class="page-desc">告警管理与AI智能诊断</span>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总告警</div>
      </div>
      <div class="stat-item critical">
        <div class="stat-value">{{ stats.critical }}</div>
        <div class="stat-label">严重</div>
      </div>
      <div class="stat-item warning">
        <div class="stat-value">{{ stats.warning }}</div>
        <div class="stat-label">警告</div>
      </div>
      <div class="stat-item active">
        <div class="stat-value">{{ stats.active }}</div>
        <div class="stat-label">进行中</div>
      </div>
      <div class="stat-item resolved">
        <div class="stat-value">{{ stats.resolved }}</div>
        <div class="stat-label">已恢复</div>
      </div>
    </div>

    <div class="modules-row">
      <div class="module-card" @click="goTo('/alerts/rules')">
        <div class="module-icon rules">
          <el-icon size="32"><Setting /></el-icon>
        </div>
        <div class="module-info">
          <h3>告警规则</h3>
          <p>配置和管理告警规则，设置阈值和触发条件</p>
        </div>
        <div class="module-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="module-card" @click="goTo('/alerts/list')">
        <div class="module-icon list">
          <el-icon size="32"><Bell /></el-icon>
        </div>
        <div class="module-info">
          <h3>告警列表</h3>
          <p>查看所有告警记录，进行AI智能诊断分析</p>
        </div>
        <div class="module-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <div class="recent-section">
      <div class="section-header">
        <h3>最近告警</h3>
        <el-button text type="primary" @click="goTo('/alerts/list')">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      
      <div class="recent-list" v-loading="loading">
        <div 
          v-for="alert in recentAlerts" 
          :key="alert.id" 
          class="recent-item"
          :class="alert.severity"
        >
          <div class="item-status">
            <el-icon v-if="alert.resolved" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#f56c6c"><Warning /></el-icon>
          </div>
          <div class="item-content">
            <div class="item-title">{{ alert.rule_name || '未知规则' }}</div>
            <div class="item-message">{{ alert.message }}</div>
          </div>
          <div class="item-meta">
            <el-tag :type="severityMap[alert.severity]?.type || 'info'" size="small">
              {{ severityMap[alert.severity]?.label || alert.severity }}
            </el-tag>
            <span class="item-time">{{ formatTime(alert.created_at) }}</span>
          </div>
        </div>
        
        <el-empty v-if="!loading && recentAlerts.length === 0" description="暂无告警" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Setting, Bell, ArrowRight, Warning, CircleCheck } from '@element-plus/icons-vue'
import { getAlerts, getAlertStats, type Alert, type AlertStats } from '@/api/alert'

const router = useRouter()
const loading = ref(false)
const stats = ref<AlertStats>({
  total: 0,
  critical: 0,
  warning: 0,
  info: 0,
  resolved: 0,
  active: 0
})
const recentAlerts = ref<Alert[]>([])

const severityMap: Record<string, { label: string; type: string }> = {
  critical: { label: '严重', type: 'danger' },
  warning: { label: '警告', type: 'warning' },
  info: { label: '信息', type: 'info' }
}

const formatTime = (time: string) => {
  if (!time) return '-'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleString('zh-CN')
}

const goTo = (path: string) => {
  router.push(path)
}

const loadStats = async () => {
  try {
    const data = await getAlertStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadRecentAlerts = async () => {
  loading.value = true
  try {
    const data = await getAlerts({ limit: 5 })
    recentAlerts.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载告警失败:', error)
    recentAlerts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
  loadRecentAlerts()
})
</script>

<style lang="less" scoped>
.monitor-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.page-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.stat-item {
  padding: 20px;
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  text-align: center;

  &.critical {
    border-color: rgba(245, 108, 108, 0.3);
    .stat-value { color: #f56c6c; }
  }

  &.warning {
    border-color: rgba(230, 162, 60, 0.3);
    .stat-value { color: #e6a23c; }
  }

  &.active {
    border-color: rgba(245, 108, 108, 0.3);
    .stat-value { color: #f56c6c; }
  }

  &.resolved {
    border-color: rgba(103, 194, 58, 0.3);
    .stat-value { color: #67c23a; }
  }
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: white;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.modules-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: rgba(255, 215, 0, 0.3);
    background: rgba(255, 215, 0, 0.05);
    transform: translateY(-2px);
  }
}

.module-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;

  &.rules {
    background: rgba(64, 158, 255, 0.2);
    color: #409eff;
  }

  &.list {
    background: rgba(255, 215, 0, 0.2);
    color: #ffd700;
  }
}

.module-info {
  flex: 1;

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: white;
    margin: 0 0 8px 0;
  }

  p {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
    margin: 0;
  }
}

.module-arrow {
  color: rgba(255, 215, 0, 0.5);
  font-size: 20px;
}

.recent-section {
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: white;
    margin: 0;
  }
}

.recent-list {
  padding: 0;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.05);
  transition: background 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(255, 215, 0, 0.02);
  }
}

.item-status {
  font-size: 20px;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: white;
  margin-bottom: 4px;
}

.item-message {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.item-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
</style>
