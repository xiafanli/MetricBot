<template>
  <div class="environment-management">
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
          <el-button type="primary" size="small" @click="showSaveTemplateDialog">
            <el-icon><FolderAdd /></el-icon>
            保存为模板
          </el-button>
          <el-button size="small" @click="showLoadTemplateDialog">
            <el-icon><FolderOpened /></el-icon>
            加载模板
          </el-button>
          <el-button type="warning" size="small" @click="handleRegenerate">
            <el-icon><RefreshRight /></el-icon>
            重新生成
          </el-button>
        </div>
      </div>

      <div v-if="topologyComponents.length === 0" class="no-components">
        <el-empty description="该环境暂无组件" />
      </div>

      <div v-else class="topology-container">
        <div class="topology-toolbar">
          <div class="toolbar-left">
            <div class="legend-item">
              <span class="legend-dot healthy"></span>
              <span>正常</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot fault"></span>
              <span>故障</span>
            </div>
          </div>
          <div class="toolbar-right">
            <el-button-group size="small">
              <el-button @click="zoomIn" title="放大">
                <el-icon><ZoomIn /></el-icon>
              </el-button>
              <el-button @click="zoomOut" title="缩小">
                <el-icon><ZoomOut /></el-icon>
              </el-button>
              <el-button @click="resetView" title="重置视图">
                <el-icon><Refresh /></el-icon>
              </el-button>
              <el-button @click="fitToScreen" title="适应屏幕">
                <el-icon><FullScreen /></el-icon>
              </el-button>
            </el-button-group>
            <span class="zoom-indicator">{{ Math.round(viewState.scale * 100) }}%</span>
          </div>
        </div>

        <div 
          class="topology-canvas-wrapper"
          ref="canvasWrapper"
          @mousedown="startPan"
          @mousemove="onPan"
          @mouseup="endPan"
          @mouseleave="endPan"
          @wheel.prevent="handleWheel"
        >
          <svg 
            class="topology-canvas"
            :viewBox="viewBox"
            :style="{ cursor: viewState.isPanning ? 'grabbing' : 'grab' }"
          >
            <defs>
              <marker id="arrow-healthy" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto">
                <path d="M0,0 L0,8 L10,4 z" fill="#3b82f6" />
              </marker>
              <marker id="arrow-fault" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto">
                <path d="M0,0 L0,8 L10,4 z" fill="#ef4444" />
              </marker>
              <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="rgba(0,0,0,0.3)"/>
              </filter>
              <filter id="glow-blue" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="4" result="blur"/>
                <feFlood flood-color="#3b82f6" flood-opacity="0.5"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge>
                  <feMergeNode/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <filter id="glow-red" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="4" result="blur"/>
                <feFlood flood-color="#ef4444" flood-opacity="0.6"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge>
                  <feMergeNode/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>

            <g class="layer-labels">
              <g v-for="layer in visibleLayers" :key="layer.id" class="layer-label-group">
                <text 
                  class="layer-label"
                  :x="60"
                  :y="layerYPositions[layer.id] + 5"
                >{{ layer.name }}</text>
                <line 
                  class="layer-separator"
                  x1="120"
                  :y1="layerYPositions[layer.id]"
                  :x2="680"
                  :y2="layerYPositions[layer.id]"
                />
              </g>
            </g>

            <g class="connections-layer">
              <g 
                v-for="conn in connections" 
                :key="conn.id"
                class="connection"
              >
                <path 
                  :d="conn.path" 
                  class="connection-line"
                  :class="conn.status"
                  fill="none"
                  :marker-end="`url(#arrow-${conn.status})`"
                />
              </g>
            </g>

            <g class="nodes-layer">
              <g
                v-for="node in nodes"
                :key="node.id"
                class="topology-node"
                :class="node.status"
                :transform="`translate(${node.x}, ${node.y})`"
                @mousedown.stop="startDragNode($event, node)"
                @click="handleNodeClick(node.data)"
              >
                <circle 
                  class="node-circle"
                  :class="node.status"
                  r="32"
                  filter="url(#shadow)"
                />
                <g class="node-icon" :class="node.status">
                  <component :is="node.icon" />
                </g>
                <text class="node-name" y="50">{{ node.data.name }}</text>
                <g v-if="node.faultCount > 0" class="fault-badge">
                  <circle cx="24" cy="-24" r="12" fill="#ef4444" />
                  <text x="24" y="-20" text-anchor="middle" fill="white" font-size="11" font-weight="bold">{{ node.faultCount }}</text>
                </g>
              </g>
            </g>
          </svg>
        </div>

        <div v-if="activeFaults.length > 0" class="active-faults-panel">
          <div class="panel-header">
            <el-icon class="panel-icon"><Warning /></el-icon>
            <span>活跃故障 ({{ activeFaults.length }})</span>
          </div>
          <div class="faults-list">
            <div v-for="fault in activeFaults" :key="fault.id" class="fault-item">
              <div class="fault-info">
                <span class="fault-name">{{ fault.scenario_name || '未知故障' }}</span>
                <span class="fault-component">{{ fault.component_name }}</span>
              </div>
              <div class="fault-time">{{ formatDateTime(fault.start_time) }}</div>
              <el-button type="success" size="small" @click="handleRecoverFault(fault.id)">恢复</el-button>
            </div>
          </div>
        </div>
      </div>

      <ComponentDetail
        v-model="showComponentDetail"
        :component="selectedComponent"
      />

      <el-dialog v-model="saveTemplateDialog" title="保存为模板" width="500px">
        <el-form :model="templateForm" label-width="100px">
          <el-form-item label="模板名称" required>
            <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
          </el-form-item>
          <el-form-item label="模板描述">
            <el-input v-model="templateForm.description" type="textarea" :rows="3" placeholder="请输入模板描述（可选）" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="saveTemplateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveTemplate" :loading="savingTemplate">保存</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="loadTemplateDialog" title="加载模板" width="700px">
        <el-table :data="topologyTemplates" style="width: 100%" v-loading="loadingTemplates">
          <el-table-column prop="name" label="模板名称" min-width="120" />
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleApplyTemplate(row)">应用</el-button>
              <el-button type="danger" link @click="handleDeleteTemplate(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>

      <el-dialog v-model="applyTemplateDialog" title="应用模板" width="500px">
        <el-form :model="applyForm" label-width="100px">
          <el-form-item label="环境名称" required>
            <el-input v-model="applyForm.name" placeholder="请输入新环境名称" />
          </el-form-item>
          <el-form-item label="IP前缀">
            <el-input v-model="applyForm.ip_prefix" placeholder="例如: 192.168.1" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="applyForm.description" type="textarea" :rows="2" placeholder="请输入环境描述（可选）" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="applyTemplateDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmApplyTemplate" :loading="applyingTemplate">应用</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  RefreshRight, FolderAdd, FolderOpened, ZoomIn, ZoomOut, Refresh, FullScreen, Warning
} from '@element-plus/icons-vue'
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
const canvasWrapper = ref<HTMLElement | null>(null)

const viewState = ref({
  scale: 1,
  offsetX: 0,
  offsetY: 0,
  isPanning: false,
  panStartX: 0,
  panStartY: 0,
  panStartOffsetX: 0,
  panStartOffsetY: 0
})

const draggingNode = ref<{ id: number; startX: number; startY: number; nodeStartX: number; nodeStartY: number } | null>(null)
const nodePositions = ref<Map<number, { x: number; y: number }>>(new Map())

const viewBox = computed(() => {
  const width = 800
  const height = 600
  const scaledWidth = width / viewState.value.scale
  const scaledHeight = height / viewState.value.scale
  const x = viewState.value.offsetX - scaledWidth / 2 + width / 2
  const y = viewState.value.offsetY - scaledHeight / 2 + height / 2
  return `${x} ${y} ${scaledWidth} ${scaledHeight}`
})

const layers = [
  { id: 0, name: '客户端层' },
  { id: 1, name: '负载均衡层' },
  { id: 2, name: '应用服务层' },
  { id: 3, name: '缓存层' },
  { id: 4, name: '数据层' }
]

const layerYPositions: Record<number, number> = {
  0: 80,
  1: 180,
  2: 280,
  3: 380,
  4: 480
}

const visibleLayers = computed(() => {
  const usedLayers = new Set(topologyComponents.value.map(c => getComponentLayer(c.component_type)))
  return layers.filter(l => usedLayers.has(l.id))
})

const componentIcons: Record<string, any> = {
  client: {
    render: () => h('g', { fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: 0, cy: -6, r: 8 }),
      h('path', { d: 'M-12,12 Q0,4 12,12', fill: 'none' }),
      h('line', { x1: 0, y1: 2, x2: 0, y2: 12 }),
    ])
  },
  nginx: {
    render: () => h('g', { fill: 'currentColor' }, [
      h('polygon', { points: '0,-12 12,4 -12,4' }),
      h('rect', { x: -8, y: 4, width: 16, height: 8, rx: 2 }),
    ])
  },
  app: {
    render: () => h('g', { fill: 'currentColor' }, [
      h('rect', { x: -10, y: -10, width: 20, height: 20, rx: 3 }),
      h('rect', { x: -6, y: -6, width: 5, height: 5, rx: 1, fill: '#1e293b' }),
      h('rect', { x: 1, y: -6, width: 5, height: 5, rx: 1, fill: '#1e293b' }),
      h('rect', { x: -6, y: 1, width: 5, height: 5, rx: 1, fill: '#1e293b' }),
      h('rect', { x: 1, y: 1, width: 5, height: 5, rx: 1, fill: '#1e293b' }),
    ])
  },
  redis: {
    render: () => h('g', { fill: 'currentColor' }, [
      h('polygon', { points: '0,-12 12,0 0,12 -12,0' }),
      h('rect', { x: -5, y: -3, width: 10, height: 6, rx: 1, fill: '#1e293b' }),
    ])
  },
  mysql: {
    render: () => h('g', { fill: 'currentColor' }, [
      h('ellipse', { cx: 0, cy: -8, rx: 12, ry: 5 }),
      h('rect', { x: -12, y: -8, width: 24, height: 16 }),
      h('ellipse', { cx: 0, cy: 8, rx: 12, ry: 5 }),
      h('ellipse', { cx: 0, cy: -8, rx: 12, ry: 5, fill: '#1e293b', opacity: 0.3 }),
    ])
  }
}

const getComponentIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    client: 'client',
    nginx: 'nginx',
    app: 'app',
    redis: 'redis',
    mysql: 'mysql'
  }
  return iconMap[type] || 'app'
}

const getComponentLayer = (type: string): number => {
  const layerMap: Record<string, number> = {
    client: 0,
    nginx: 1,
    app: 2,
    redis: 3,
    mysql: 4
  }
  return layerMap[type] ?? 2
}

const nodes = computed(() => {
  const componentsWithLayer = topologyComponents.value.map(comp => ({
    ...comp,
    computedLayer: getComponentLayer(comp.component_type)
  }))
  
  return componentsWithLayer.map((comp) => {
    const layerComponents = componentsWithLayer.filter(c => c.computedLayer === comp.computedLayer)
    const layerIndex = layerComponents.indexOf(comp)
    const layerWidth = layerComponents.length * 140
    const startX = 400 - layerWidth / 2 + 70
    
    let x = startX + layerIndex * 140
    let y = layerYPositions[comp.computedLayer] || 300
    
    if (nodePositions.value.has(comp.id)) {
      const pos = nodePositions.value.get(comp.id)!
      x = pos.x
      y = pos.y
    }
    
    const faults = activeFaults.value.filter(f => f.component_id === comp.id)
    const status = faults.length > 0 ? 'fault' : 'healthy'
    
    return {
      id: comp.id,
      x,
      y,
      data: comp,
      status,
      faultCount: faults.length,
      icon: componentIcons[getComponentIcon(comp.component_type)]
    }
  })
})

const connections = computed(() => {
  return topologyRelations.value.map(rel => {
    const source = nodes.value.find(n => n.id === rel.source_id)
    const target = nodes.value.find(n => n.id === rel.target_id)
    
    if (!source || !target) return null
    
    const path = `M ${source.x} ${source.y + 32} L ${target.x} ${target.y - 32}`
    
    const sourceFault = activeFaults.value.some(f => f.component_id === source.id)
    const targetFault = activeFaults.value.some(f => f.component_id === target.id)
    const status = (sourceFault || targetFault) ? 'fault' : 'healthy'
    
    return {
      id: rel.id,
      path,
      status
    }
  }).filter(Boolean) as { id: number; path: string; status: string }[]
})

const zoomIn = () => {
  viewState.value.scale = Math.min(2, viewState.value.scale + 0.1)
}

const zoomOut = () => {
  viewState.value.scale = Math.max(0.3, viewState.value.scale - 0.1)
}

const resetView = () => {
  viewState.value.scale = 1
  viewState.value.offsetX = 0
  viewState.value.offsetY = 0
  nodePositions.value.clear()
}

const fitToScreen = () => {
  if (nodes.value.length === 0) return
  
  const minX = Math.min(...nodes.value.map(n => n.x)) - 100
  const maxX = Math.max(...nodes.value.map(n => n.x)) + 100
  const minY = Math.min(...nodes.value.map(n => n.y)) - 100
  const maxY = Math.max(...nodes.value.map(n => n.y)) + 100
  
  const width = maxX - minX
  const height = maxY - minY
  
  viewState.value.scale = Math.min(800 / width, 600 / height, 1.5)
  viewState.value.offsetX = (minX + maxX) / 2
  viewState.value.offsetY = (minY + maxY) / 2
}

const handleWheel = (e: WheelEvent) => {
  const delta = e.deltaY > 0 ? -0.05 : 0.05
  viewState.value.scale = Math.max(0.3, Math.min(2, viewState.value.scale + delta))
}

const startPan = (e: MouseEvent) => {
  if ((e.target as HTMLElement).closest('.topology-node')) return
  viewState.value.isPanning = true
  viewState.value.panStartX = e.clientX
  viewState.value.panStartY = e.clientY
  viewState.value.panStartOffsetX = viewState.value.offsetX
  viewState.value.panStartOffsetY = viewState.value.offsetY
}

const onPan = (e: MouseEvent) => {
  if (draggingNode.value) {
    const dx = (e.clientX - draggingNode.value.startX) / viewState.value.scale
    const dy = (e.clientY - draggingNode.value.startY) / viewState.value.scale
    nodePositions.value.set(draggingNode.value.id, {
      x: draggingNode.value.nodeStartX + dx,
      y: draggingNode.value.nodeStartY + dy
    })
    return
  }
  
  if (!viewState.value.isPanning) return
  const dx = (e.clientX - viewState.value.panStartX) / viewState.value.scale
  const dy = (e.clientY - viewState.value.panStartY) / viewState.value.scale
  viewState.value.offsetX = viewState.value.panStartOffsetX - dx
  viewState.value.offsetY = viewState.value.panStartOffsetY - dy
}

const endPan = () => {
  viewState.value.isPanning = false
  draggingNode.value = null
}

const startDragNode = (e: MouseEvent, node: any) => {
  draggingNode.value = {
    id: node.id,
    startX: e.clientX,
    startY: e.clientY,
    nodeStartX: node.x,
    nodeStartY: node.y
  }
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
    nodePositions.value.clear()
  } catch (error) {
    console.error('加载拓扑数据失败:', error)
    topologyComponents.value = []
    topologyRelations.value = []
  }
}

const handleCreate = () => router.push('/simulator/wizard')

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
    if (error !== 'cancel') ElMessage.error('操作失败')
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
    if (error !== 'cancel') ElMessage.error('同步失败')
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
    if (node) node.status = comp.status
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

const handleRecoverFault = async (faultId: number) => {
  try {
    await api.recoverFaultInstance(faultId)
    ElMessage.success('故障已恢复')
    loadEnvironmentStatus()
  } catch (error) {
    console.error('恢复失败:', error)
    ElMessage.error('恢复失败')
  }
}

const saveTemplateDialog = ref(false)
const loadTemplateDialog = ref(false)
const applyTemplateDialog = ref(false)
const savingTemplate = ref(false)
const loadingTemplates = ref(false)
const applyingTemplate = ref(false)
const topologyTemplates = ref<Array<{
  id: number
  name: string
  description: string | null
  topology_type: string
  scale: string
  created_at: string
}>>([])
const selectedTemplate = ref<{ id: number; name: string } | null>(null)

const templateForm = ref({ name: '', description: '', topology_type: 'custom', scale: 'medium' })
const applyForm = ref({ name: '', ip_prefix: '', description: '' })

const formatDateTime = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const showSaveTemplateDialog = () => {
  templateForm.value = {
    name: `${currentEnvironment.value?.name || '环境'}模板`,
    description: currentEnvironment.value?.description || '',
    topology_type: 'custom',
    scale: 'medium'
  }
  saveTemplateDialog.value = true
}

const handleSaveTemplate = async () => {
  if (!templateForm.value.name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  savingTemplate.value = true
  try {
    const componentsConfig = topologyComponents.value.map(c => ({
      type: c.component_type,
      name: c.name,
      ip_address: c.ip_address,
      properties: c.properties
    }))
    await api.createTopologyTemplate({
      name: templateForm.value.name,
      description: templateForm.value.description,
      topology_type: templateForm.value.topology_type,
      scale: templateForm.value.scale,
      components_config: { components: componentsConfig }
    })
    ElMessage.success('模板保存成功')
    saveTemplateDialog.value = false
  } catch (error) {
    console.error('Failed to save template:', error)
    ElMessage.error('保存模板失败')
  } finally {
    savingTemplate.value = false
  }
}

const showLoadTemplateDialog = async () => {
  loadTemplateDialog.value = true
  loadingTemplates.value = true
  try {
    const response = await api.getTopologyTemplates() as typeof topologyTemplates.value
    topologyTemplates.value = response
  } catch (error) {
    console.error('Failed to load templates:', error)
    ElMessage.error('加载模板列表失败')
  } finally {
    loadingTemplates.value = false
  }
}

const handleApplyTemplate = (template: typeof topologyTemplates.value[0]) => {
  selectedTemplate.value = { id: template.id, name: template.name }
  applyForm.value = {
    name: `从模板创建-${template.name}`,
    ip_prefix: '',
    description: template.description || ''
  }
  loadTemplateDialog.value = false
  applyTemplateDialog.value = true
}

const confirmApplyTemplate = async () => {
  if (!applyForm.value.name) {
    ElMessage.warning('请输入环境名称')
    return
  }
  if (!selectedTemplate.value) return
  applyingTemplate.value = true
  try {
    const result = await api.applyTopologyTemplate(selectedTemplate.value.id, {
      name: applyForm.value.name,
      ip_prefix: applyForm.value.ip_prefix,
      description: applyForm.value.description
    }) as { environment: Environment }
    ElMessage.success('模板应用成功')
    applyTemplateDialog.value = false
    currentEnvironment.value = result.environment
    await loadTopology(currentEnvironment.value.id)
  } catch (error) {
    console.error('Failed to apply template:', error)
    ElMessage.error('应用模板失败')
  } finally {
    applyingTemplate.value = false
  }
}

const handleDeleteTemplate = async (template: typeof topologyTemplates.value[0]) => {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteTopologyTemplate(template.id)
    ElMessage.success('删除成功')
    topologyTemplates.value = topologyTemplates.value.filter(t => t.id !== template.id)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete template:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadEnvironment()
  statusInterval = setInterval(loadEnvironmentStatus, 10000)
})

onUnmounted(() => {
  if (statusInterval) clearInterval(statusInterval)
})
</script>

<style lang="less" scoped>
.environment-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 12px;
  flex: 1;
}

.topology-view {
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 12px;
  flex: 1;
  min-height: 0;
}

.topology-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.08);
  flex-shrink: 0;

  .header-info {
    h3 {
      color: #ffd700;
      margin: 0 0 4px 0;
      font-size: 16px;
    }
    .env-desc {
      color: rgba(255, 255, 255, 0.5);
      font-size: 13px;
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
  }
}

.no-components {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.topology-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.topology-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(255, 215, 0, 0.08);
  flex-shrink: 0;

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7);
  }

  .legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    
    &.healthy {
      background: #3b82f6;
      box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
    }
    
    &.fault {
      background: #ef4444;
      box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
    }
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .zoom-indicator {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.6);
    min-width: 45px;
    text-align: center;
    font-family: 'SF Mono', 'Monaco', monospace;
  }
}

.topology-canvas-wrapper {
  flex: 1;
  min-height: 400px;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
  overflow: hidden;
  position: relative;
}

.topology-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.layer-labels {
  .layer-label-group {
    .layer-label {
      font-size: 12px;
      fill: rgba(255, 255, 255, 0.4);
      font-weight: 500;
      text-anchor: end;
    }
    
    .layer-separator {
      stroke: rgba(255, 255, 255, 0.05);
      stroke-width: 1;
      stroke-dasharray: 4 4;
    }
  }
}

.connections-layer {
  .connection {
    .connection-line {
      stroke-width: 2;
      stroke-linecap: round;
      transition: stroke 0.3s ease;
      
      &.healthy {
        stroke: #3b82f6;
      }
      
      &.fault {
        stroke: #ef4444;
        stroke-dasharray: 6 3;
        animation: dash-flow 0.5s linear infinite;
      }
    }
  }
}

@keyframes dash-flow {
  to {
    stroke-dashoffset: -9;
  }
}

.nodes-layer {
  .topology-node {
    cursor: pointer;

    &:hover {
      .node-circle {
        stroke-width: 3;
      }
    }

    .node-circle {
      transition: all 0.3s ease;
      stroke-width: 2;
      
      &.healthy {
        fill: rgba(59, 130, 246, 0.15);
        stroke: #3b82f6;
      }
      
      &.fault {
        fill: rgba(239, 68, 68, 0.15);
        stroke: #ef4444;
        animation: pulse-circle 1.5s ease-in-out infinite;
      }
    }

    .node-icon {
      font-size: 20px;
      transition: all 0.3s ease;
      
      &.healthy {
        color: #3b82f6;
      }
      
      &.fault {
        color: #ef4444;
      }
    }

    .node-name {
      font-size: 11px;
      font-weight: 500;
      fill: rgba(255, 255, 255, 0.9);
      text-anchor: middle;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
  }
}

@keyframes pulse-circle {
  0%, 100% {
    stroke-opacity: 1;
    fill-opacity: 0.15;
  }
  50% {
    stroke-opacity: 0.6;
    fill-opacity: 0.25;
  }
}

.active-faults-panel {
  background: rgba(239, 68, 68, 0.08);
  border-top: 1px solid rgba(239, 68, 68, 0.2);
  padding: 12px 20px;
  flex-shrink: 0;
  max-height: 150px;
  overflow-y: auto;

  .panel-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    color: #f87171;
    font-size: 13px;
    font-weight: 600;
  }

  .panel-icon {
    font-size: 16px;
  }

  .faults-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .fault-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 6px;
    border: 1px solid rgba(239, 68, 68, 0.15);
  }

  .fault-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .fault-name {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.9);
  }

  .fault-component {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
  }

  .fault-time {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    font-family: 'SF Mono', 'Monaco', monospace;
  }
}

:deep(.el-dialog) {
  background: rgba(20, 20, 30, 0.95);
  border: 1px solid rgba(255, 215, 0, 0.2);

  .el-dialog__header {
    border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  }

  .el-dialog__title {
    color: #ffd700;
  }

  .el-form-item__label {
    color: rgba(255, 255, 255, 0.8);
  }
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(255, 215, 0, 0.08);
  --el-table-row-hover-bg-color: rgba(255, 215, 0, 0.05);
  --el-table-border-color: rgba(255, 215, 0, 0.1);
  --el-table-text-color: rgba(255, 255, 255, 0.85);
  --el-table-header-text-color: rgba(255, 255, 255, 0.95);

  background: transparent !important;

  .el-table__inner-wrapper::before {
    display: none;
  }

  th.el-table__cell {
    background: var(--el-table-header-bg-color) !important;
    border-bottom: 1px solid var(--el-table-border-color) !important;
    font-weight: 600;
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
</style>
