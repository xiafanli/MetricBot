<template>
  <div class="alert-list">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总告警</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card critical">
          <div class="stat-value">{{ stats.critical }}</div>
          <div class="stat-label">严重</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card warning">
          <div class="stat-value">{{ stats.warning }}</div>
          <div class="stat-label">警告</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card info">
          <div class="stat-value">{{ stats.info }}</div>
          <div class="stat-label">信息</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card active">
          <div class="stat-value">{{ stats.active }}</div>
          <div class="stat-label">进行中</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card resolved">
          <div class="stat-value">{{ stats.resolved }}</div>
          <div class="stat-label">已恢复</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警列表</span>
          <div class="filter-group">
            <el-radio-group v-model="filterStatus" @change="loadAlerts">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="active">进行中</el-radio-button>
              <el-radio-button label="resolved">已恢复</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <el-table :data="alerts" v-loading="loading" stripe>
        <el-table-column prop="rule_name" label="规则名称" min-width="150" />
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="severityMap[row.severity]?.type || 'info'">
              {{ severityMap[row.severity]?.label || row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric_value" label="指标值" width="100">
          <template #default="{ row }">
            {{ row.metric_value?.toFixed(2) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="100">
          <template #default="{ row }">
            {{ row.threshold?.toFixed(2) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="resolved" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.resolved ? 'success' : 'danger'">
              {{ row.resolved ? '已恢复' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="触发时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDiagnosis(row)">AI诊断</el-button>
            <el-button
              v-if="!row.resolved"
              type="success"
              link
              @click="handleResolve(row)"
            >
              恢复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <DiagnosisDialog
      v-model="diagnosisVisible"
      :alert="currentAlert"
      @close="diagnosisVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAlerts,
  getAlertStats,
  resolveAlert,
  type Alert,
  type AlertStats
} from '@/api/alert'
import DiagnosisDialog from './DiagnosisDialog.vue'

const loading = ref(false)
const alerts = ref<Alert[]>([])
const stats = ref<AlertStats>({
  total: 0,
  critical: 0,
  warning: 0,
  info: 0,
  resolved: 0,
  active: 0
})
const filterStatus = ref('')
const diagnosisVisible = ref(false)
const currentAlert = ref<Alert | null>(null)

const severityMap: Record<string, { label: string; type: string }> = {
  critical: { label: '严重', type: 'danger' },
  warning: { label: '警告', type: 'warning' },
  info: { label: '信息', type: 'info' }
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const loadStats = async () => {
  try {
    const data = await getAlertStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadAlerts = async () => {
  loading.value = true
  try {
    const params: any = { limit: 100 }
    if (filterStatus.value === 'active') {
      params.active_only = true
    } else if (filterStatus.value === 'resolved') {
      params.resolved_only = true
    }
    const data = await getAlerts(params)
    alerts.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载告警失败:', error)
    alerts.value = []
  } finally {
    loading.value = false
  }
}

const showDiagnosis = (alert: Alert) => {
  currentAlert.value = alert
  diagnosisVisible.value = true
}

const handleResolve = async (alert: Alert) => {
  try {
    await ElMessageBox.confirm('确定要将此告警标记为已恢复吗？', '提示', {
      type: 'warning'
    })
    await resolveAlert(alert.id)
    ElMessage.success('已标记为恢复')
    loadAlerts()
    loadStats()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

onMounted(() => {
  loadStats()
  loadAlerts()
})
</script>

<style scoped lang="less">
.alert-list {
  padding: 24px;
  background: var(--bg-primary);
  min-height: 100%;
  font-family: var(--font-body);
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-neon);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 245, 255, 0.15);
    border-color: var(--border-medium);

    &::before {
      opacity: 1;
    }
  }

  :deep(.el-card__body) {
    padding: 20px 16px;
  }
}

.stat-value {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--neon-blue);
  line-height: 1.2;
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
}

.stat-card.critical .stat-value {
  color: var(--neon-pink);
  text-shadow: 0 0 10px rgba(255, 0, 153, 0.3);
}

.stat-card.warning .stat-value {
  color: var(--neon-orange);
  text-shadow: 0 0 10px rgba(255, 102, 0, 0.3);
}

.stat-card.info .stat-value {
  color: var(--text-secondary);
  text-shadow: none;
}

.stat-card.active .stat-value {
  color: var(--neon-pink);
  text-shadow: 0 0 10px rgba(255, 0, 153, 0.3);
}

.stat-card.resolved .stat-value {
  color: var(--neon-green);
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 8px;
  font-weight: 500;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  span {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.filter-group {
  display: flex;
  gap: 12px;

  :deep(.el-radio-button__inner) {
    background: var(--bg-tertiary);
    border-color: var(--border-light);
    color: var(--text-secondary);
    font-weight: 500;
    transition: all 0.3s ease;

    &:hover {
      color: var(--neon-blue);
      border-color: var(--neon-blue);
    }
  }

  :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background: var(--gradient-neon);
    border-color: transparent;
    color: white;
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.4);
  }
}

:deep(.el-card) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);

  .el-card__header {
    background: transparent;
    border-bottom: 1px solid var(--border-light);
    padding: 16px 20px;
  }
}

:deep(.el-table) {
  background: transparent;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-tertiary);
  --el-table-row-hover-bg-color: rgba(0, 245, 255, 0.05);
  --el-table-border-color: var(--border-light);

  th.el-table__cell {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  td.el-table__cell {
    color: var(--text-secondary);
  }

  .el-table__row:hover td {
    background: rgba(0, 245, 255, 0.05);
  }
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  border: none;

  &.el-tag--danger {
    background: rgba(255, 0, 153, 0.15);
    color: var(--neon-pink);
  }

  &.el-tag--warning {
    background: rgba(255, 102, 0, 0.15);
    color: var(--neon-orange);
  }

  &.el-tag--success {
    background: rgba(0, 255, 136, 0.15);
    color: var(--neon-green);
  }

  &.el-tag--info {
    background: rgba(0, 245, 255, 0.15);
    color: var(--neon-blue);
  }
}

:deep(.el-button--primary) {
  background: transparent;
  border: none;
  color: var(--neon-blue);
  font-weight: 500;

  &:hover {
    color: var(--neon-purple);
    background: rgba(191, 0, 255, 0.1);
  }
}

:deep(.el-button--success) {
  background: transparent;
  border: none;
  color: var(--neon-green);
  font-weight: 500;

  &:hover {
    background: rgba(0, 255, 136, 0.1);
  }
}
</style>
