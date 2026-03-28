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

<style scoped>
.alert-list {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.stat-card.critical .stat-value {
  color: #f56c6c;
}

.stat-card.warning .stat-value {
  color: #e6a23c;
}

.stat-card.info .stat-value {
  color: #909399;
}

.stat-card.active .stat-value {
  color: #f56c6c;
}

.stat-card.resolved .stat-value {
  color: #67c23a;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-group {
  display: flex;
  gap: 10px;
}
</style>
