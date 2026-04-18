<template>
  <div class="scenario-replay">
    <div class="page-header">
      <h2 class="page-title">历史场景回放</h2>
    </div>

    <div class="config-card">
      <el-table :data="scenarioHistory" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="场景名称" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template #default="{ row }">
            {{ row.end_time ? formatDateTime(row.end_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'">
              {{ row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="replayScenario(row)">
              <el-icon><VideoPlay /></el-icon>
              回放
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="replayDialogVisible" title="场景回放" width="80%" top="5vh">
      <div class="replay-container" v-if="currentSnapshot">
        <div class="replay-controls">
          <el-button-group>
            <el-button @click="startReplay" :disabled="isReplaying" type="primary">
              <el-icon><VideoPlay /></el-icon>
              开始
            </el-button>
            <el-button @click="pauseReplay" :disabled="!isReplaying">
              <el-icon><VideoPause /></el-icon>
              暂停
            </el-button>
            <el-button @click="resetReplay">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-button-group>
          <div class="progress-wrapper">
            <el-slider
              v-model="replayProgress"
              :max="100"
              :format-tooltip="formatProgress"
              style="width: 300px;"
            />
            <span class="replay-time">{{ formatTime(currentTime) }} / {{ formatTime(totalTime) }}</span>
          </div>
          <div class="speed-control">
            <span>速度:</span>
            <el-select v-model="replaySpeed" style="width: 100px;">
              <el-option label="0.5x" :value="0.5" />
              <el-option label="1x" :value="1" />
              <el-option label="2x" :value="2" />
              <el-option label="4x" :value="4" />
            </el-select>
          </div>
        </div>
        
        <div class="replay-view">
          <div class="snapshot-info">
            <h3>场景快照信息</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="环境ID">{{ currentSnapshot.env_id }}</el-descriptions-item>
              <el-descriptions-item label="场景名称">{{ currentSnapshot.name }}</el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ formatDateTime(currentSnapshot.start_time) }}</el-descriptions-item>
              <el-descriptions-item label="结束时间">{{ currentSnapshot.end_time ? formatDateTime(currentSnapshot.end_time) : '-' }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="snapshot-events" v-if="currentSnapshot.snapshot_data?.events?.length">
            <h3>事件时间线</h3>
            <el-timeline>
              <el-timeline-item
                v-for="(event, index) in currentSnapshot.snapshot_data.events"
                :key="index"
                :timestamp="formatDateTime(event.time)"
                :type="getEventType(event.type)"
                placement="top"
              >
                <el-card>
                  <h4>{{ event.title }}</h4>
                  <p>{{ event.description }}</p>
                  <div v-if="event.component" class="event-component">
                    <el-tag size="small">{{ event.component }}</el-tag>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>

          <div class="snapshot-metrics" v-if="currentSnapshot.snapshot_data?.metrics">
            <h3>指标快照</h3>
            <div class="metrics-grid">
              <div v-for="(value, key) in currentSnapshot.snapshot_data.metrics" :key="key" class="metric-item">
                <span class="metric-label">{{ key }}</span>
                <span class="metric-value">{{ typeof value === 'number' ? value.toFixed(2) : value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="replayDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { VideoPlay, VideoPause, Refresh, Delete } from '@element-plus/icons-vue'
import { api } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface ScenarioHistoryItem {
  id: number
  env_id: number
  name: string
  description: string | null
  start_time: string
  end_time: string | null
  status: string
  snapshot_data: {
    events?: Array<{
      time: string
      type: string
      title: string
      description: string
      component?: string
    }>
    metrics?: Record<string, number | string>
    components?: Array<{
      id: number
      name: string
      type: string
      status: string
    }>
  } | null
  created_at: string
}

const loading = ref(false)
const scenarioHistory = ref<ScenarioHistoryItem[]>([])
const replayDialogVisible = ref(false)
const currentSnapshot = ref<ScenarioHistoryItem | null>(null)
const isReplaying = ref(false)
const replayProgress = ref(0)
const replaySpeed = ref(1)
const currentTime = ref(0)
const totalTime = ref(0)

let replayInterval: ReturnType<typeof setInterval> | null = null

const loadScenarioHistory = async () => {
  loading.value = true
  try {
    const response = await api.getScenarioHistory()
    scenarioHistory.value = response.data as ScenarioHistoryItem[]
  } catch (error) {
    console.error('Failed to load scenario history:', error)
    ElMessage.error('加载历史场景失败')
  } finally {
    loading.value = false
  }
}

const formatDateTime = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatProgress = (val: number) => {
  return `${val}%`
}

const getEventType = (type: string) => {
  switch (type) {
    case 'fault':
      return 'danger'
    case 'recovery':
      return 'success'
    case 'warning':
      return 'warning'
    default:
      return 'info'
  }
}

const replayScenario = async (row: ScenarioHistoryItem) => {
  try {
    const response = await api.replayScenarioHistory(row.id)
    const data = response.data as { snapshot_data: ScenarioHistoryItem['snapshot_data'] }
    currentSnapshot.value = {
      ...row,
      snapshot_data: data.snapshot_data || row.snapshot_data
    }
    
    if (currentSnapshot.value.snapshot_data?.events) {
      const events = currentSnapshot.value.snapshot_data.events
      if (events.length > 0) {
        const startTime = new Date(events[0].time).getTime()
        const endTime = new Date(events[events.length - 1].time).getTime()
        totalTime.value = (endTime - startTime) / 1000
      }
    }
    
    replayProgress.value = 0
    currentTime.value = 0
    replayDialogVisible.value = true
  } catch (error) {
    console.error('Failed to replay scenario:', error)
    ElMessage.error('回放场景失败')
  }
}

const startReplay = () => {
  if (isReplaying.value) return
  isReplaying.value = true
  
  const stepDuration = 100 / (totalTime.value * 10 / replaySpeed.value)
  
  replayInterval = setInterval(() => {
    if (replayProgress.value >= 100) {
      pauseReplay()
      ElMessage.success('回放完成')
      return
    }
    replayProgress.value = Math.min(100, replayProgress.value + stepDuration)
    currentTime.value = (replayProgress.value / 100) * totalTime.value
  }, 100)
}

const pauseReplay = () => {
  isReplaying.value = false
  if (replayInterval) {
    clearInterval(replayInterval)
    replayInterval = null
  }
}

const resetReplay = () => {
  pauseReplay()
  replayProgress.value = 0
  currentTime.value = 0
}

const handleDelete = async (row: ScenarioHistoryItem) => {
  try {
    await ElMessageBox.confirm('确定要删除该历史场景吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.deleteScenarioHistory(row.id)
    ElMessage.success('删除成功')
    loadScenarioHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete scenario:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadScenarioHistory()
})

onUnmounted(() => {
  if (replayInterval) {
    clearInterval(replayInterval)
  }
})
</script>

<style scoped lang="less">
.scenario-replay {
  padding: 20px;
  background: var(--bg-primary);
  min-height: 100%;
  font-family: var(--font-body);
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.config-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-light);
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-tertiary);
  --el-table-row-hover-bg-color: rgba(0, 245, 255, 0.05);
  --el-table-border-color: var(--border-light);
  --el-table-text-color: var(--text-secondary);
  --el-table-header-text-color: var(--text-primary);

  background: transparent !important;

  .el-table__inner-wrapper::before {
    display: none;
  }

  th.el-table__cell {
    background: var(--el-table-header-bg-color) !important;
    border-bottom: 1px solid var(--el-table-border-color) !important;
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  td.el-table__cell {
    border-bottom: 1px solid var(--el-table-border-color);
  }

  tr {
    background: transparent !important;
  }

  .el-table__body tr:hover > td.el-table__cell {
    background: var(--el-table-row-hover-bg-color) !important;
  }
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  border: none;

  &.el-tag--success {
    background: rgba(0, 255, 136, 0.15);
    color: var(--neon-green);
  }

  &.el-tag--info {
    background: rgba(0, 245, 255, 0.15);
    color: var(--neon-blue);
  }
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;

  &.is-link {
    color: var(--neon-blue);
    background: transparent;
    border: none;

    &:hover {
      color: var(--neon-purple);
    }
  }
}

:deep(.el-dialog) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);

  .el-dialog__header {
    background: transparent;
    border-bottom: 1px solid var(--border-light);
    padding: 20px 24px;

    .el-dialog__title {
      font-family: var(--font-display);
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }

  .el-dialog__body {
    padding: 24px;
    color: var(--text-secondary);
  }

  .el-dialog__footer {
    background: transparent;
    border-top: 1px solid var(--border-light);
    padding: 16px 24px;
  }
}

.replay-container {
  min-height: 400px;
}

.replay-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid var(--border-light);

  :deep(.el-button-group) {
    .el-button {
      background: var(--bg-secondary);
      border: 1px solid var(--border-light);
      color: var(--text-secondary);

      &:hover {
        border-color: var(--neon-blue);
        color: var(--neon-blue);
      }

      &.el-button--primary {
        background: var(--gradient-neon);
        border: none;
        color: white;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
        }
      }
    }
  }
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;

  :deep(.el-slider) {
    .el-slider__runway {
      background: var(--bg-secondary);
    }

    .el-slider__bar {
      background: var(--gradient-neon);
    }

    .el-slider__button {
      border-color: var(--neon-blue);
    }
  }
}

.replay-time {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--text-tertiary);
  min-width: 80px;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);

  :deep(.el-select) {
    .el-input__wrapper {
      background: var(--bg-secondary);
      border: 1px solid var(--border-light);
    }
  }
}

.replay-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.snapshot-info,
.snapshot-events,
.snapshot-metrics {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 16px;
}

.snapshot-info h3,
.snapshot-events h3,
.snapshot-metrics h3 {
  margin: 0 0 16px 0;
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

:deep(.el-descriptions) {
  .el-descriptions__label {
    background: var(--bg-secondary);
    color: var(--neon-blue);
    font-weight: 600;
  }

  .el-descriptions__content {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  .el-descriptions__cell {
    border-color: var(--border-light);
  }
}

:deep(.el-timeline) {
  .el-timeline-item__timestamp {
    color: var(--text-tertiary);
  }

  .el-timeline-item__node--danger {
    background-color: var(--neon-pink);
  }

  .el-timeline-item__node--success {
    background-color: var(--neon-green);
  }

  .el-timeline-item__node--warning {
    background-color: var(--neon-orange);
  }

  .el-timeline-item__node--info {
    background-color: var(--neon-blue);
  }

  .el-timeline-item__tail {
    border-left-color: var(--border-light);
  }

  .el-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    color: var(--text-primary);

    h4 {
      color: var(--text-primary);
      margin: 0 0 8px 0;
    }

    p {
      color: var(--text-secondary);
      margin: 0;
    }
  }
}

.event-component {
  margin-top: 8px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-light);
}

.metric-label {
  font-size: 14px;
  color: var(--text-tertiary);
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--neon-blue);
}
</style>
