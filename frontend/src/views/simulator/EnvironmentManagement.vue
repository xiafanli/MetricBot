<template>
  <div class="environment-management">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">环境管理</h2>
        <span class="page-desc">管理模拟生产环境拓扑</span>
      </div>
      <div class="header-right">
        <el-button v-if="!currentEnvironment" type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建环境
        </el-button>
        <el-button v-else type="warning" @click="handleRegenerate">
          <el-icon><RefreshRight /></el-icon>
          重新生成
        </el-button>
      </div>
    </div>

    <div v-if="!currentEnvironment" class="empty-state">
      <el-empty description="暂无环境，请创建一个模拟环境">
        <el-button type="primary" @click="handleCreate">创建环境</el-button>
      </el-empty>
    </div>

    <div v-else class="topology-view">
      <div class="topology-header">
        <div class="header-info">
          <h3>{{ currentEnvironment.name }}</h3>
          <span class="env-desc">{{ currentEnvironment.description || '暂无描述' }}</span>
        </div>
        <div class="header-actions">
          <el-tag :type="currentEnvironment.is_active ? 'success' : 'info'" size="large">
            {{ currentEnvironment.is_active ? '运行中' : '已停止' }}
          </el-tag>
          <el-button v-if="!currentEnvironment.is_active" type="success" size="small" @click="handleActivate">
            激活
          </el-button>
          <el-button v-else type="danger" size="small" @click="handleDeactivate">
            停止
          </el-button>
          <el-button type="info" size="small" @click="handleSyncToHosts">
            同步到主机
          </el-button>
        </div>
      </div>

      <div v-if="topologyComponents.length === 0" class="no-components">
        <el-empty description="该环境暂无组件" />
      </div>

      <div v-else class="topology-container">
        <div class="topology-controls">
          <el-button-group>
            <el-button size="small" @click="zoomIn">
              <el-icon><ZoomIn /></el-icon>
            </el-button>
            <el-button size="small" @click="zoomOut">
              <el-icon><ZoomOut /></el-icon>
            </el-button>
            <el-button size="small" @click="resetZoom">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </el-button-group>
          <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
        </div>
        <div 
          class="topology-graph-wrapper"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="endDrag"
          @mouseleave="endDrag"
          @wheel.prevent="handleWheel"
        >
          <div 
            class="topology-graph" 
            :style="{ 
              transform: `scale(${zoomLevel}) translate(${panX}px, ${panY}px)`,
              cursor: isDragging ? 'grabbing' : 'grab'
            }"
          >
        <div class="layer client-layer">
          <div class="layer-title">客户端层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(0)"
              :key="node.id"
              class="topology-node client-node"
              :class="{ 'node-unhealthy': node.status && node.status !== 'active', 'node-has-fault': getComponentFaults(node.id).length > 0 }"
              @click="handleNodeClick(node)"
            >
              <div class="node-status" :class="getNodeStatusClass(node.status)"></div>
              <div v-if="getComponentFaults(node.id).length > 0" class="fault-badge">
                {{ getComponentFaults(node.id).length }}
              </div>
              <div class="node-icon">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="node-info">
                <span class="node-name">{{ node.name }}</span>
                <span class="node-ip">{{ node.ip_address }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="layer-arrow">
          <svg width="100%" height="40" class="flow-arrow">
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="rgba(255, 215, 0, 0.5)" />
              </marker>
              <linearGradient id="flowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:rgba(255, 215, 0, 0.8)" />
                <stop offset="50%" style="stop-color:rgba(255, 215, 0, 0.3)" />
                <stop offset="100%" style="stop-color:rgba(255, 215, 0, 0.8)" />
              </linearGradient>
            </defs>
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
            <circle r="4" fill="rgba(255, 215, 0, 0.9)" class="flow-dot">
              <animateMotion dur="1.5s" repeatCount="indefinite" path="M0,0 L0,30" />
            </circle>
          </svg>
        </div>

        <div class="layer lb-layer">
          <div class="layer-title">负载均衡层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(1)"
              :key="node.id"
              class="topology-node nginx-node"
              :class="{ 'node-unhealthy': node.status && node.status !== 'active', 'node-has-fault': getComponentFaults(node.id).length > 0 }"
              @click="handleNodeClick(node)"
            >
              <div class="node-status" :class="getNodeStatusClass(node.status)"></div>
              <div v-if="getComponentFaults(node.id).length > 0" class="fault-badge">
                {{ getComponentFaults(node.id).length }}
              </div>
              <div class="node-icon">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="node-info">
                <span class="node-name">{{ node.name }}</span>
                <span class="node-ip">{{ node.ip_address }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="layer-arrow">
          <svg width="100%" height="40" class="flow-arrow">
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
            <circle r="4" fill="rgba(255, 215, 0, 0.9)" class="flow-dot">
              <animateMotion dur="1.5s" repeatCount="indefinite" path="M0,0 L0,30" begin="0.3s" />
            </circle>
          </svg>
        </div>

        <div class="layer app-layer">
          <div class="layer-title">应用层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(2)"
              :key="node.id"
              class="topology-node app-node"
              :class="{ 'node-unhealthy': node.status && node.status !== 'active', 'node-has-fault': getComponentFaults(node.id).length > 0 }"
              @click="handleNodeClick(node)"
            >
              <div class="node-status" :class="getNodeStatusClass(node.status)"></div>
              <div v-if="getComponentFaults(node.id).length > 0" class="fault-badge">
                {{ getComponentFaults(node.id).length }}
              </div>
              <div class="node-icon">
                <el-icon><DataBoard /></el-icon>
              </div>
              <div class="node-info">
                <span class="node-name">{{ node.name }}</span>
                <span class="node-ip">{{ node.ip_address }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="layer-arrow">
          <svg width="100%" height="40" class="flow-arrow">
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
            <circle r="4" fill="rgba(255, 215, 0, 0.9)" class="flow-dot">
              <animateMotion dur="1.5s" repeatCount="indefinite" path="M0,0 L0,30" begin="0.6s" />
            </circle>
          </svg>
        </div>

        <div class="layer cache-layer">
          <div class="layer-title">缓存层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(3)"
              :key="node.id"
              class="topology-node cache-node"
              :class="{ 'node-unhealthy': node.status && node.status !== 'active', 'node-has-fault': getComponentFaults(node.id).length > 0 }"
              @click="handleNodeClick(node)"
            >
              <div class="node-status" :class="getNodeStatusClass(node.status)"></div>
              <div v-if="getComponentFaults(node.id).length > 0" class="fault-badge">
                {{ getComponentFaults(node.id).length }}
              </div>
              <div class="node-icon">
                <el-icon><Lightning /></el-icon>
              </div>
              <div class="node-info">
                <span class="node-name">{{ node.name }}</span>
                <span class="node-ip">{{ node.ip_address }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="layer-arrow">
          <svg width="100%" height="40" class="flow-arrow">
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
            <circle r="4" fill="rgba(255, 215, 0, 0.9)" class="flow-dot">
              <animateMotion dur="1.5s" repeatCount="indefinite" path="M0,0 L0,30" begin="0.9s" />
            </circle>
          </svg>
        </div>

        <div class="layer db-layer">
          <div class="layer-title">数据库层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(4)"
              :key="node.id"
              class="topology-node db-node"
              :class="{ 'node-unhealthy': node.status && node.status !== 'active', 'node-has-fault': getComponentFaults(node.id).length > 0 }"
              @click="handleNodeClick(node)"
            >
              <div class="node-status" :class="getNodeStatusClass(node.status)"></div>
              <div v-if="getComponentFaults(node.id).length > 0" class="fault-badge">
                {{ getComponentFaults(node.id).length }}
              </div>
              <div class="node-icon">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="node-info">
                <span class="node-name">{{ node.name }}</span>
                <span class="node-ip">{{ node.ip_address }}</span>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <div class="topology-stats">
        <div class="stat-item">
          <span class="stat-label">总组件数</span>
          <span class="stat-value">{{ topologyComponents.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">连接数</span>
          <span class="stat-value">{{ topologyRelations.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Pushgateway</span>
          <span class="stat-value">{{ currentEnvironment.pushgateway_url }}</span>
        </div>
      </div>
    </div>

    <ComponentDetail
      v-model="showComponentDetail"
      :component="selectedComponent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, RefreshRight, Monitor, Connection, DataBoard, Lightning, Coin, ZoomIn, ZoomOut, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import ComponentDetail from '@/components/simulator/ComponentDetail.vue'

interface Environment {
  id: number
  name: string
  description: string
  is_active: boolean
  pushgateway_url: string
  log_path: string
  topology_data: any
  created_at: string
  updated_at: string
}

interface Component {
  id: number
  name: string
  component_type: string
  ip_address: string
  port: number
  layer: number
  status?: string
  properties?: any
}

interface Relation {
  id: number
  source_id: number
  target_id: number
  relation_type: string
}

const router = useRouter()
const currentEnvironment = ref<Environment | null>(null)
const topologyComponents = ref<Component[]>([])
const topologyRelations = ref<Relation[]>([])
const showComponentDetail = ref(false)
const selectedComponent = ref<Component | null>(null)

const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartPanX = ref(0)
const dragStartPanY = ref(0)

const zoomIn = () => {
  if (zoomLevel.value < 2) {
    zoomLevel.value = Math.min(2, zoomLevel.value + 0.1)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value = Math.max(0.5, zoomLevel.value - 0.1)
  }
}

const resetZoom = () => {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
}

const handleWheel = (e: WheelEvent) => {
  const delta = e.deltaY > 0 ? -0.05 : 0.05
  zoomLevel.value = Math.max(0.5, Math.min(2, zoomLevel.value + delta))
}

const startDrag = (e: MouseEvent) => {
  if ((e.target as HTMLElement).closest('.topology-node')) return
  isDragging.value = true
  dragStartX.value = e.clientX
  dragStartY.value = e.clientY
  dragStartPanX.value = panX.value
  dragStartPanY.value = panY.value
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  const dx = e.clientX - dragStartX.value
  const dy = e.clientY - dragStartY.value
  panX.value = dragStartPanX.value + dx / zoomLevel.value
  panY.value = dragStartPanY.value + dy / zoomLevel.value
}

const endDrag = () => {
  isDragging.value = false
}

const loadEnvironment = async () => {
  try {
    const data = await api.getSimulationEnvironments()
    const envs = Array.isArray(data) ? data : []
    if (envs.length > 0) {
      currentEnvironment.value = envs[0]
      await loadTopology(currentEnvironment.value.id)
    } else {
      currentEnvironment.value = null
      topologyComponents.value = []
      topologyRelations.value = []
    }
  } catch (error) {
    console.error('加载环境失败:', error)
    ElMessage.error('加载环境失败')
  }
}

const loadTopology = async (envId: number) => {
  try {
    const [componentsData, relationsData] = await Promise.all([
      api.getComponents(envId),
      api.getSimulatorRelations(envId)
    ])
    topologyComponents.value = Array.isArray(componentsData) ? componentsData : []
    topologyRelations.value = Array.isArray(relationsData) ? relationsData : []
  } catch (error) {
    console.error('加载拓扑数据失败:', error)
    topologyComponents.value = []
    topologyRelations.value = []
  }
}

const getComponentsByLayer = (layer: number) => {
  return topologyComponents.value.filter(c => c.layer === layer)
}

const handleCreate = () => {
  router.push('/simulator/wizard')
}

const handleRegenerate = async () => {
  try {
    await ElMessageBox.confirm('重新生成将删除当前环境及所有组件，确定继续吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    if (currentEnvironment.value) {
      await api.deleteSimulationEnvironment(currentEnvironment.value.id)
      currentEnvironment.value = null
      topologyComponents.value = []
      topologyRelations.value = []
      router.push('/simulator/wizard')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleActivate = async () => {
  if (!currentEnvironment.value) return
  try {
    await api.activateSimulationEnvironment(currentEnvironment.value.id, {})
    ElMessage.success('环境激活成功')
    await loadEnvironment()
  } catch (error) {
    ElMessage.error('环境激活失败')
  }
}

const handleDeactivate = async () => {
  if (!currentEnvironment.value) return
  try {
    await api.deactivateSimulationEnvironment(currentEnvironment.value.id)
    ElMessage.success('环境已停止')
    await loadEnvironment()
  } catch (error) {
    ElMessage.error('停止环境失败')
  }
}

const handleSyncToHosts = async () => {
  if (!currentEnvironment.value) return
  try {
    await ElMessageBox.confirm('确定要将环境同步到主机模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await api.syncEnvironmentToHosts(currentEnvironment.value.id)
    ElMessage.success('同步成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('同步失败')
    }
  }
}

const handleNodeClick = (component: Component) => {
  selectedComponent.value = component
  showComponentDetail.value = true
}

let statusInterval: ReturnType<typeof setInterval> | null = null

const loadEnvironmentStatus = async () => {
  if (!currentEnvironment.value?.id) return

  try {
    const response = await api.getEnvironmentStatus(currentEnvironment.value.id)
    updateComponentStatus(response.components)
    activeFaults.value = response.faults || []
  } catch (error) {
    console.error('Failed to load environment status:', error)
  }
}

const updateComponentStatus = (components: Array<{ id: number; status: string }>) => {
  components.forEach(comp => {
    const node = topologyComponents.value.find(n => n.id === comp.id)
    if (node) {
      node.status = comp.status
    }
  })
}

const activeFaults = ref<Array<{
  id: number
  component_id: number
  component_name: string | null
  scenario_name: string | null
  start_time: string | null
  end_time: string | null
}>>([])

const getComponentFaults = (componentId: number) => {
  return activeFaults.value.filter(f => f.component_id === componentId)
}

const getNodeStatusClass = (status: string | undefined) => {
  if (!status) return 'status-unknown'
  switch (status) {
    case 'active':
      return 'status-healthy'
    case 'inactive':
      return 'status-warning'
    case 'error':
      return 'status-critical'
    default:
      return 'status-unknown'
  }
}

onMounted(() => {
  loadEnvironment()
  statusInterval = setInterval(loadEnvironmentStatus, 10000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>

<style lang="less" scoped>
.environment-management {
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

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 12px;
}

.topology-view {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.topology-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .header-info {
    h3 {
      color: #ffd700;
      margin: 0 0 8px 0;
      font-size: 18px;
    }

    .env-desc {
      color: rgba(255, 255, 255, 0.5);
      font-size: 14px;
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.no-components {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.topology-container {
  position: relative;
}

.topology-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.5);
  padding: 8px 12px;
  border-radius: 8px;
}

.zoom-level {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  min-width: 40px;
}

.topology-graph-wrapper {
  overflow: hidden;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.1);
  min-height: 500px;
  position: relative;
}

.topology-graph {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  transform-origin: center center;
  transition: transform 0.1s ease-out;
  padding: 20px;
}

.layer {
  width: 100%;
  padding: 16px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
}

.layer-title {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin-bottom: 12px;
  font-weight: 500;
}

.layer-nodes {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.layer-arrow {
  width: 100%;
  height: 40px;
  display: flex;
  justify-content: center;
}

.flow-arrow {
  overflow: visible;
}

.flow-dot {
  filter: drop-shadow(0 0 4px rgba(255, 215, 0, 0.8));
}

@keyframes flowPulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.flow-arrow line {
  animation: flowPulse 2s ease-in-out infinite;
}

.topology-node {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  min-width: 180px;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
}

.node-status {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.5);
  animation: pulse 2s infinite;
}

.status-healthy {
  background: #67c23a;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.6);
}

.status-warning {
  background: #e6a23c;
  box-shadow: 0 0 8px rgba(230, 162, 60, 0.6);
}

.status-critical {
  background: #f56c6c;
  box-shadow: 0 0 8px rgba(245, 108, 108, 0.6);
  animation: pulse-critical 1s infinite;
}

.status-unknown {
  background: #909399;
  box-shadow: 0 0 8px rgba(144, 147, 153, 0.6);
}

.node-unhealthy {
  border-color: rgba(245, 108, 108, 0.5) !important;
  animation: shake 0.5s ease-in-out;
}

.node-has-fault {
  box-shadow: 0 0 12px rgba(245, 108, 108, 0.4);
}

.fault-badge {
  position: absolute;
  top: -8px;
  left: -8px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background: linear-gradient(135deg, #f56c6c, #c45656);
  border-radius: 9px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.5);
  animation: badge-pulse 2s infinite;
}

@keyframes badge-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes pulse-critical {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-2px);
  }
  75% {
    transform: translateX(2px);
  }
}

.client-node {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2), rgba(64, 158, 255, 0.1));
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.nginx-node {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2), rgba(103, 194, 58, 0.1));
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.app-node {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.1));
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.cache-node {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(230, 162, 60, 0.1));
  border: 1px solid rgba(230, 162, 60, 0.3);
}

.db-node {
  background: linear-gradient(135deg, rgba(144, 147, 153, 0.2), rgba(144, 147, 153, 0.1));
  border: 1px solid rgba(144, 147, 153, 0.3);
}

.node-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  color: #ffd700;
  font-size: 20px;
}

.node-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.node-name {
  color: white;
  font-weight: 500;
  font-size: 14px;
}

.node-ip {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.topology-stats {
  display: flex;
  gap: 24px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 215, 0, 0.1);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.stat-value {
  color: #ffd700;
  font-size: 16px;
  font-weight: 500;
}
</style>
