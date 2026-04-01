<template>
  <div class="alert-groups">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>聚合告警</span>
          <div class="header-actions">
            <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px; margin-right: 10px">
              <el-option label="活跃" value="active" />
              <el-option label="已确认" value="acknowledged" />
              <el-option label="已解决" value="resolved" />
            </el-select>
            <el-select v-model="filterStrategy" placeholder="策略筛选" clearable style="width: 140px">
              <el-option label="时间窗口" value="time_window" />
              <el-option label="拓扑关联" value="topology" />
              <el-option label="语义相似" value="semantic" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="groups" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="group_key" label="聚合键" min-width="180" show-overflow-tooltip />
        <el-table-column prop="strategy" label="策略" width="120">
          <template #default="{ row }">
            <el-tag :type="getStrategyTagType(row.strategy)">
              {{ getStrategyLabel(row.strategy) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_count" label="告警数" width="90" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
            <el-button type="success" link @click="analyzeRca(row)" v-if="row.status === 'active'">根因分析</el-button>
            <el-button type="warning" link @click="acknowledgeGroup(row)" v-if="row.status === 'active'">确认</el-button>
            <el-button type="success" link @click="resolveGroup(row)" v-if="row.status !== 'resolved'">解决</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="聚合告警详情" width="80%">
      <el-descriptions :column="2" border v-if="currentGroup">
        <el-descriptions-item label="聚合键">{{ currentGroup.group_key }}</el-descriptions-item>
        <el-descriptions-item label="策略">{{ getStrategyLabel(currentGroup.strategy) }}</el-descriptions-item>
        <el-descriptions-item label="严重级别">{{ currentGroup.severity }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ getStatusLabel(currentGroup.status) }}</el-descriptions-item>
        <el-descriptions-item label="告警数量">{{ currentGroup.alert_count }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentGroup.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="受影响组件" :span="2">
          <el-tag v-for="comp in currentGroup.affected_components" :key="comp" style="margin-right: 5px">
            {{ comp }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>关联告警</el-divider>
      <el-table :data="groupAlerts" v-loading="alertsLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="rcaVisible" title="根因分析报告" width="80%">
      <div v-if="rcaReport">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">{{ rcaReport.status }}</el-descriptions-item>
          <el-descriptions-item label="置信度">{{ (rcaReport.confidence * 100).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(rcaReport.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatTime(rcaReport.completed_at) }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>根因候选</el-divider>
        <el-table :data="rcaCandidates" v-loading="candidatesLoading">
          <el-table-column prop="rank_order" label="排名" width="70" />
          <el-table-column prop="component_name" label="组件" min-width="150" />
          <el-table-column prop="component_type" label="类型" width="120" />
          <el-table-column prop="score" label="得分" width="100">
            <template #default="{ row }">
              {{ (row.score * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="analysis_method" label="分析方法" width="120">
            <template #default="{ row }">
              <el-tag>{{ getMethodLabel(row.analysis_method) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="evidence" label="证据" min-width="200">
            <template #default="{ row }">
              {{ JSON.stringify(row.evidence) }}
            </template>
          </el-table-column>
        </el-table>

        <el-divider>排查建议</el-divider>
        <el-timeline v-if="rcaReport.recommendations">
          <el-timeline-item v-for="(rec, index) in rcaReport.recommendations" :key="index">
            <el-card>
              <h4>{{ rec.component }}</h4>
              <p>{{ rec.action }}</p>
              <el-tag :type="rec.priority === 'high' ? 'danger' : 'warning'">{{ rec.priority }}</el-tag>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

interface AlertGroup {
  id: number
  group_key: string
  strategy: string
  severity: string
  status: string
  alert_count: number
  affected_components: string[]
  created_at: string
}

interface Alert {
  id: number
  title: string
  severity: string
  created_at: string
}

interface RcaReport {
  id: number
  status: string
  confidence: number
  recommendations: any[]
  created_at: string
  completed_at: string
}

interface RcaCandidate {
  id: number
  rank_order: number
  component_name: string
  component_type: string
  score: number
  analysis_method: string
  evidence: any
}

const groups = ref<AlertGroup[]>([])
const loading = ref(false)
const filterStatus = ref('')
const filterStrategy = ref('')
const detailVisible = ref(false)
const currentGroup = ref<AlertGroup | null>(null)
const groupAlerts = ref<Alert[]>([])
const alertsLoading = ref(false)
const rcaVisible = ref(false)
const rcaReport = ref<RcaReport | null>(null)
const rcaCandidates = ref<RcaCandidate[]>([])
const candidatesLoading = ref(false)

const loadGroups = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (filterStrategy.value) params.strategy = filterStrategy.value
    const response = await apiClient.get('/alerts/groups', { params })
    groups.value = response.data
  } catch (error) {
    ElMessage.error('加载聚合告警失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = async (group: AlertGroup) => {
  currentGroup.value = group
  detailVisible.value = true
  alertsLoading.value = true
  try {
    const response = await apiClient.get(`/alerts/groups/${group.id}/alerts`)
    groupAlerts.value = response.data.alerts
  } catch (error) {
    ElMessage.error('加载关联告警失败')
  } finally {
    alertsLoading.value = false
  }
}

const analyzeRca = async (group: AlertGroup) => {
  try {
    ElMessage.info('正在生成根因分析报告...')
    const response = await apiClient.post(`/alerts/groups/${group.id}/rca`)
    rcaReport.value = response.data
    await loadCandidates(response.data.id)
    rcaVisible.value = true
  } catch (error) {
    ElMessage.error('根因分析失败')
  }
}

const loadCandidates = async (reportId: number) => {
  candidatesLoading.value = true
  try {
    const response = await apiClient.get(`/alerts/rca/${reportId}/candidates`)
    rcaCandidates.value = response.data
  } catch (error) {
    ElMessage.error('加载根因候选失败')
  } finally {
    candidatesLoading.value = false
  }
}

const acknowledgeGroup = async (group: AlertGroup) => {
  try {
    await apiClient.put(`/alerts/groups/${group.id}/acknowledge`)
    ElMessage.success('已确认')
    loadGroups()
  } catch (error) {
    ElMessage.error('确认失败')
  }
}

const resolveGroup = async (group: AlertGroup) => {
  try {
    await apiClient.put(`/alerts/groups/${group.id}/resolve`)
    ElMessage.success('已解决')
    loadGroups()
  } catch (error) {
    ElMessage.error('解决失败')
  }
}

const getStrategyTagType = (strategy: string) => {
  const types: Record<string, string> = {
    time_window: 'primary',
    topology: 'success',
    semantic: 'warning',
  }
  return types[strategy] || 'info'
}

const getStrategyLabel = (strategy: string) => {
  const labels: Record<string, string> = {
    time_window: '时间窗口',
    topology: '拓扑关联',
    semantic: '语义相似',
  }
  return labels[strategy] || strategy
}

const getSeverityTagType = (severity: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    info: 'info',
  }
  return types[severity] || 'info'
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    active: 'danger',
    acknowledged: 'warning',
    resolved: 'success',
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    active: '活跃',
    acknowledged: '已确认',
    resolved: '已解决',
  }
  return labels[status] || status
}

const getMethodLabel = (method: string) => {
  const labels: Record<string, string> = {
    random_walk: '随机游走',
    correlation: '时序相关',
    llm: 'LLM推理',
  }
  return labels[method] || method
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

watch([filterStatus, filterStrategy], () => {
  loadGroups()
})

onMounted(() => {
  loadGroups()
})
</script>

<style scoped>
.alert-groups {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>
