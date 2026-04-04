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

      <div v-else class="topology-graph">
        <div class="layer client-layer">
          <div class="layer-title">客户端层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(0)"
              :key="node.id"
              class="topology-node client-node"
              @click="handleNodeClick(node)"
            >
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
          <svg width="100%" height="40">
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="rgba(255, 215, 0, 0.5)" />
              </marker>
            </defs>
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
          </svg>
        </div>

        <div class="layer lb-layer">
          <div class="layer-title">负载均衡层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(1)"
              :key="node.id"
              class="topology-node nginx-node"
              @click="handleNodeClick(node)"
            >
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
          <svg width="100%" height="40">
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
          </svg>
        </div>

        <div class="layer app-layer">
          <div class="layer-title">应用层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(2)"
              :key="node.id"
              class="topology-node app-node"
              @click="handleNodeClick(node)"
            >
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
          <svg width="100%" height="40">
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
          </svg>
        </div>

        <div class="layer cache-layer">
          <div class="layer-title">缓存层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(3)"
              :key="node.id"
              class="topology-node cache-node"
              @click="handleNodeClick(node)"
            >
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
          <svg width="100%" height="40">
            <line x1="50%" y1="0" x2="50%" y2="30" stroke="rgba(255, 215, 0, 0.3)" stroke-width="2" marker-end="url(#arrowhead)" />
          </svg>
        </div>

        <div class="layer db-layer">
          <div class="layer-title">数据库层</div>
          <div class="layer-nodes">
            <div
              v-for="node in getComponentsByLayer(4)"
              :key="node.id"
              class="topology-node db-node"
              @click="handleNodeClick(node)"
            >
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
import { Plus, RefreshRight, Monitor, Connection, DataBoard, Lightning, Coin } from '@element-plus/icons-vue'
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

.topology-graph {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
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

.topology-node {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  min-width: 180px;
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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
