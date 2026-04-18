<template>
  <div class="dashboard-container">
    <div class="stats-row">
      <div class="stat-card critical">
        <div class="stat-icon">
          <el-icon :size="28"><WarningFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.critical }}</div>
          <div class="stat-label">严重告警</div>
        </div>
        <div class="stat-trend up">
          <el-icon><Top /></el-icon>
          <span>+12%</span>
        </div>
      </div>
      
      <div class="stat-card warning">
        <div class="stat-icon">
          <el-icon :size="28"><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.warning }}</div>
          <div class="stat-label">警告告警</div>
        </div>
        <div class="stat-trend down">
          <el-icon><Bottom /></el-icon>
          <span>-5%</span>
        </div>
      </div>
      
      <div class="stat-card info">
        <div class="stat-icon">
          <el-icon :size="28"><InfoFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.info }}</div>
          <div class="stat-label">信息告警</div>
        </div>
        <div class="stat-trend up">
          <el-icon><Top /></el-icon>
          <span>+3%</span>
        </div>
      </div>
      
      <div class="stat-card total">
        <div class="stat-icon">
          <el-icon :size="28"><Bell /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ alertStats.total }}</div>
          <div class="stat-label">今日告警</div>
        </div>
        <div class="stat-trend">
          <span class="trend-label">较昨日</span>
          <span class="trend-value">+8</span>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card trend-chart">
        <div class="card-header">
          <h3 class="card-title">告警趋势</h3>
          <div class="card-actions">
            <el-radio-group v-model="trendRange" size="small">
              <el-radio-button label="24h">24小时</el-radio-button>
              <el-radio-button label="7d">7天</el-radio-button>
              <el-radio-button label="30d">30天</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <div class="mock-chart">
              <div class="chart-bars">
                <div v-for="(item, index) in mockTrendData" :key="index" class="bar-item">
                  <div class="bar" :style="{ height: item.value + '%' }"></div>
                  <span class="bar-label">{{ item.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chart-card distribution-chart">
        <div class="card-header">
          <h3 class="card-title">告警分布</h3>
        </div>
        <div class="chart-content">
          <div class="distribution-list">
            <div v-for="(item, index) in distributionData" :key="index" class="distribution-item">
              <div class="dist-label">
                <span class="dist-dot" :style="{ background: item.color }"></span>
                <span class="dist-name">{{ item.name }}</span>
              </div>
              <div class="dist-bar-wrapper">
                <div class="dist-bar" :style="{ width: item.percent + '%', background: item.color }"></div>
              </div>
              <div class="dist-value">{{ item.value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="alerts-section">
      <div class="section-header">
        <h3 class="section-title">实时告警</h3>
        <div class="section-actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索告警..."
            prefix-icon="Search"
            clearable
            class="search-input"
          />
          <el-button type="primary" @click="refreshAlerts">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
      
      <div class="alerts-table">
        <el-table
          :data="filteredAlerts"
          style="width: 100%"
          :header-cell-style="tableHeaderStyle"
          :cell-style="tableCellStyle"
        >
          <el-table-column prop="level" label="级别" width="100">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)" size="small" effect="dark">
                {{ row.level }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="告警名称" min-width="200" />
          <el-table-column prop="source" label="来源" width="150" />
          <el-table-column prop="host" label="主机" width="150" />
          <el-table-column prop="time" label="触发时间" width="180" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === '活跃' ? 'danger' : 'info'" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewAlert(row)">
                查看
              </el-button>
              <el-button type="success" link size="small" @click="handleAlert(row)">
                处理
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  WarningFilled,
  Warning,
  InfoFilled,
  Bell,
  Top,
  Bottom,
  Refresh
} from '@element-plus/icons-vue'

interface Alert {
  id: number
  level: string
  name: string
  source: string
  host: string
  time: string
  status: string
}

const alertStats = ref({
  critical: 0,
  warning: 0,
  info: 0,
  total: 0,
  today: 0,
  week: 0,
  resolution_rate: 0
})

const loadAlertStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/alerts/stats', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      alertStats.value = data
    }
  } catch (error) {
    console.error('加载告警统计失败:', error)
  }
}

onMounted(() => {
  connectWebSocket()
  loadAlertStats()
})

let ws: WebSocket | null = null
let reconnectTimer: number | null = null

const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/ws/alerts`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket连接已建立')
    ElMessage.success('实时告警连接已建立')
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    } catch (error) {
      console.error('解析WebSocket消息失败:', error)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket错误:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket连接已关闭')
    if (!reconnectTimer) {
      reconnectTimer = window.setTimeout(() => {
        console.log('尝试重新连接WebSocket...')
        connectWebSocket()
        reconnectTimer = null
      }, 5000)
    }
  }
}

const handleWebSocketMessage = (data: any) => {
  if (data.type === 'alert') {
    const alert = data.data
    ElMessage({
      type: alert.severity === 'critical' ? 'error' : alert.severity === 'warning' ? 'warning' : 'info',
      message: `新告警: ${alert.message}`,
      duration: 5000
    })
    
    alertStats.value.total++
    if (alert.severity === 'critical') {
      alertStats.value.critical++
    } else if (alert.severity === 'warning') {
      alertStats.value.warning++
    } else {
      alertStats.value.info++
    }
  } else if (data.type === 'alert_update') {
    if (data.status === 'resolved') {
      ElMessage.success('告警已恢复')
    }
  } else if (data.type === 'stats_update') {
    alertStats.value = data.data
  }
}

const disconnectWebSocket = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (ws) {
    ws.close()
    ws = null
  }
}

onUnmounted(() => {
  disconnectWebSocket()
})

const trendRange = ref('24h')

const mockTrendData = ref([
  { label: '00:00', value: 30 },
  { label: '04:00', value: 20 },
  { label: '08:00', value: 45 },
  { label: '12:00', value: 60 },
  { label: '16:00', value: 75 },
  { label: '20:00', value: 55 },
  { label: '现在', value: 40 }
])

const distributionData = ref([
  { name: 'CPU使用率', value: 28, percent: 37, color: '#ffd700' },
  { name: '内存使用', value: 22, percent: 29, color: '#ff6b35' },
  { name: '磁盘空间', value: 15, percent: 20, color: '#f72585' },
  { name: '网络延迟', value: 8, percent: 11, color: '#7209b7' },
  { name: '服务状态', value: 2, percent: 3, color: '#3a0ca3' }
])

const searchKeyword = ref('')

const alerts = ref<Alert[]>([
  { id: 1, level: '严重', name: 'CPU使用率超过95%', source: 'Prometheus', host: 'server-01', time: '2026-03-15 10:23:45', status: '活跃' },
  { id: 2, level: '严重', name: '内存使用率超过90%', source: 'Prometheus', host: 'server-02', time: '2026-03-15 10:20:12', status: '活跃' },
  { id: 3, level: '警告', name: '磁盘空间不足20%', source: 'Zabbix', host: 'server-03', time: '2026-03-15 10:15:33', status: '活跃' },
  { id: 4, level: '警告', name: '网络延迟超过100ms', source: 'Prometheus', host: 'server-04', time: '2026-03-15 10:10:00', status: '活跃' },
  { id: 5, level: '信息', name: '服务重启完成', source: 'Zabbix', host: 'server-05', time: '2026-03-15 10:05:21', status: '已处理' },
  { id: 6, level: '信息', name: '备份任务完成', source: 'Prometheus', host: 'server-06', time: '2026-03-15 09:55:00', status: '已处理' }
])

const filteredAlerts = computed(() => {
  if (!searchKeyword.value) return alerts.value
  const keyword = searchKeyword.value.toLowerCase()
  return alerts.value.filter(alert => 
    alert.name.toLowerCase().includes(keyword) ||
    alert.host.toLowerCase().includes(keyword) ||
    alert.source.toLowerCase().includes(keyword)
  )
})

const tableHeaderStyle = {
  background: 'rgba(255, 215, 0, 0.05)',
  color: 'rgba(255, 255, 255, 0.9)',
  borderBottom: '1px solid rgba(255, 215, 0, 0.1)'
}

const tableCellStyle = {
  background: 'transparent',
  color: 'rgba(255, 255, 255, 0.8)',
  borderBottom: '1px solid rgba(255, 215, 0, 0.05)'
}

const getLevelType = (level: string) => {
  const types: Record<string, string> = {
    '严重': 'danger',
    '警告': 'warning',
    '信息': 'info'
  }
  return types[level] || 'info'
}

const refreshAlerts = () => {
  ElMessage.success('告警数据已刷新')
}

const viewAlert = (row: Alert) => {
  ElMessage.info(`查看告警: ${row.name}`)
}

const handleAlert = (row: Alert) => {
  ElMessage.success(`已处理告警: ${row.name}`)
}
</script>

<style lang="less" scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  }

  &.critical .stat-icon {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
  }

  &.warning .stat-icon {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
  }

  &.info .stat-icon {
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
  }

  &.total .stat-icon {
    background: rgba(255, 215, 0, 0.15);
    color: #ffd700;
  }
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 6px;

  &.up {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }

  &.down {
    color: #22c55e;
    background: rgba(34, 197, 94, 0.1);
  }

  .trend-label {
    color: rgba(255, 255, 255, 0.5);
  }

  .trend-value {
    color: #ffd700;
    font-weight: 600;
  }
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-card {
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0;
}

.card-actions {
  :deep(.el-radio-button__inner) {
    background: rgba(255, 215, 0, 0.05);
    border-color: rgba(255, 215, 0, 0.2);
    color: rgba(255, 255, 255, 0.7);
  }

  :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background: linear-gradient(135deg, #ffd700 0%, #ff6b35 100%);
    border-color: #ffd700;
    color: #0a0a0a;
  }
}

.chart-content {
  padding: 20px;
  min-height: 280px;
}

.chart-placeholder {
  height: 100%;
}

.mock-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: 0 10px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.bar {
  width: 32px;
  background: linear-gradient(180deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
}

.bar-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.distribution-item {
  display: grid;
  grid-template-columns: 100px 1fr 40px;
  align-items: center;
  gap: 12px;
}

.dist-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dist-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dist-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.dist-bar-wrapper {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.dist-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.dist-value {
  font-size: 14px;
  font-weight: 600;
  color: white;
  text-align: right;
}

.alerts-section {
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
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;

  :deep(.el-input__wrapper) {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 215, 0, 0.2);
    box-shadow: none;

    .el-input__inner {
      color: white;

      &::placeholder {
        color: rgba(255, 255, 255, 0.3);
      }
    }
  }
}

.alerts-table {
  :deep(.el-table) {
    background: transparent;

    tr {
      background: transparent;

      &:hover > td {
        background: rgba(255, 215, 0, 0.03) !important;
      }
    }

    .el-table__inner-wrapper::before {
      display: none;
    }
  }
}
</style>
