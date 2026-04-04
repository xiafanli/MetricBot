# 模拟器完善实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成模拟器的所有待办功能，包括故障场景适配、前端交互优化、可视化增强和高级功能，并确保样式一致性。

**Architecture:** 
- 后端：扩展现有的故障引擎和API，支持新增组件类型的故障场景
- 前端：优化拓扑图交互，添加可视化增强功能，实现高级功能
- 样式：统一修复对话框按钮等组件的深色主题样式

**Tech Stack:** 
- 后端：Python FastAPI, SQLAlchemy
- 前端：Vue 3, TypeScript, Element Plus
- 可视化：ECharts, AntV X6（可选）

---

## 文件结构

### 后端文件
- `backend/apps/simulator/router.py` - API路由（修改）
- `backend/apps/simulator/engine/fault_engine.py` - 故障引擎（修改）
- `backend/apps/simulator/models.py` - 数据模型（修改）
- `backend/apps/simulator/schemas.py` - 数据模式（修改）

### 前端文件
- `frontend/src/style.less` - 全局样式（修改）
- `frontend/src/views/simulator/EnvironmentManagement.vue` - 环境管理页面（修改）
- `frontend/src/views/simulator/FaultManagement.vue` - 故障管理页面（修改）
- `frontend/src/views/simulator/TopologyWizard.vue` - 拓扑向导页面（修改）
- `frontend/src/api/simulator.ts` - API接口（修改）

### 新增文件
- `frontend/src/components/simulator/TopologyGraph.vue` - 拓扑图组件（新增）
- `frontend/src/components/simulator/ComponentDetail.vue` - 组件详情组件（新增）
- `backend/apps/simulator/migrations/add_fault_scenarios.py` - 故障场景迁移脚本（新增）

---

## Task 1: 修复对话框样式问题

**Files:**
- Modify: `frontend/src/style.less`

**问题分析：**
当前对话框的取消按钮可能还是白色背景，需要统一修复为深色主题样式。

- [ ] **Step 1: 添加对话框按钮样式**

在 `frontend/src/style.less` 文件末尾添加：

```less
/* Element Plus Dialog Button 深色主题适配 */
.el-dialog {
  .el-button--default {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 215, 0, 0.2);
    color: rgba(255, 255, 255, 0.8);

    &:hover {
      background: rgba(255, 255, 255, 0.15);
      border-color: rgba(255, 215, 0, 0.3);
      color: white;
    }

    &:active {
      background: rgba(255, 255, 255, 0.2);
    }
  }

  .el-button--primary {
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.9) 0%, rgba(247, 37, 133, 0.9) 100%);
    border: none;
    color: #0a0a0a;
    font-weight: 600;

    &:hover {
      opacity: 0.9;
      box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
    }
  }
}

/* Element Plus Message Box 深色主题适配 */
.el-message-box {
  background: rgba(26, 26, 46, 0.98) !important;
  border: 1px solid rgba(255, 215, 0, 0.2) !important;
  border-radius: 12px !important;

  .el-message-box__header {
    background: rgba(0, 0, 0, 0.3);
    border-bottom: 1px solid rgba(255, 215, 0, 0.15);
    border-radius: 12px 12px 0 0;
    padding: 16px 20px;
  }

  .el-message-box__title {
    color: white !important;
    font-weight: 600;
  }

  .el-message-box__content {
    color: rgba(255, 255, 255, 0.85);
    padding: 20px;
  }

  .el-message-box__btns {
    padding: 16px 20px;
    border-top: 1px solid rgba(255, 215, 0, 0.15);

    .el-button--default {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 215, 0, 0.2);
      color: rgba(255, 255, 255, 0.8);

      &:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 215, 0, 0.3);
        color: white;
      }
    }

    .el-button--primary {
      background: linear-gradient(135deg, rgba(255, 215, 0, 0.9) 0%, rgba(247, 37, 133, 0.9) 100%);
      border: none;
      color: #0a0a0a;
      font-weight: 600;

      &:hover {
        opacity: 0.9;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
      }
    }
  }
}
```

- [ ] **Step 2: 提交样式修复**

```bash
git add frontend/src/style.less
git commit -m "style: fix dialog and message box button styles for dark theme"
```

---

## Task 2: 故障场景适配

**Files:**
- Modify: `backend/apps/simulator/models.py`
- Modify: `backend/apps/simulator/engine/fault_engine.py`
- Create: `backend/apps/simulator/migrations/add_fault_scenarios.py`

**目标：** 支持新增组件类型的故障场景

- [ ] **Step 1: 扩展故障类型定义**

在 `backend/apps/simulator/models.py` 中添加故障类型常量：

```python
class FaultType:
    HOST_CPU_OVERLOAD = "host_cpu_overload"
    HOST_MEMORY_EXHAUST = "host_memory_exhaust"
    HOST_DISK_FULL = "host_disk_full"
    HOST_NETWORK_LATENCY = "host_network_latency"
    
    NGINX_CONNECTION_OVERFLOW = "nginx_connection_overflow"
    NGINX_UPSTREAM_TIMEOUT = "nginx_upstream_timeout"
    NGINX_CACHE_MISS = "nginx_cache_miss"
    
    APP_MEMORY_LEAK = "app_memory_leak"
    APP_GC_OVERHEAD = "app_gc_overhead"
    APP_THREAD_BLOCK = "app_thread_block"
    APP_API_TIMEOUT = "app_api_timeout"
    
    API_GATEWAY_CIRCUIT_BREAK = "api_gateway_circuit_break"
    API_GATEWAY_RATE_LIMIT = "api_gateway_rate_limit"
    
    REDIS_CONNECTION_EXHAUST = "redis_connection_exhaust"
    REDIS_MEMORY_OVERFLOW = "redis_memory_overflow"
    REDIS_CACHE_PENETRATION = "redis_cache_penetration"
    
    MYSQL_CONNECTION_EXHAUST = "mysql_connection_exhaust"
    MYSQL_SLOW_QUERY = "mysql_slow_query"
    MYSQL_DEADLOCK = "mysql_deadlock"
    MYSQL_REPLICATION_LAG = "mysql_replication_lag"
    
    FIREWALL_RULE_BLOCK = "firewall_rule_block"
    FIREWALL_CONNECTION_OVERFLOW = "firewall_connection_overflow"
    
    KAFKA_PARTITION_UNBALANCE = "kafka_partition_unbalance"
    KAFKA_CONSUMER_LAG = "kafka_consumer_lag"
    
    CONFIG_CENTER_SYNC_FAIL = "config_center_sync_fail"
```

- [ ] **Step 2: 创建故障场景迁移脚本**

创建 `backend/apps/simulator/migrations/add_fault_scenarios.py`：

```python
from sqlalchemy.orm import Session
from apps.simulator.models import FaultScenario
from apps.simulator.engine.fault_engine import FaultType

FAULT_SCENARIOS = [
    {
        "name": "Nginx连接数溢出",
        "description": "Nginx连接数超过最大限制",
        "fault_type": FaultType.NGINX_CONNECTION_OVERFLOW,
        "target_component_type": "nginx",
        "config": {"duration_minutes": 10, "connection_multiplier": 2.0},
        "probability": 0.008,
        "is_enabled": True,
    },
    {
        "name": "Nginx上游超时",
        "description": "Nginx上游服务器响应超时",
        "fault_type": FaultType.NGINX_UPSTREAM_TIMEOUT,
        "target_component_type": "nginx",
        "config": {"duration_minutes": 8, "timeout_rate": 0.3},
        "probability": 0.006,
        "is_enabled": True,
    },
    {
        "name": "Redis连接池耗尽",
        "description": "Redis连接池连接数耗尽",
        "fault_type": FaultType.REDIS_CONNECTION_EXHAUST,
        "target_component_type": "redis",
        "config": {"duration_minutes": 12, "connection_usage": 0.95},
        "probability": 0.007,
        "is_enabled": True,
    },
    {
        "name": "Redis内存溢出",
        "description": "Redis内存使用率达到极限",
        "fault_type": FaultType.REDIS_MEMORY_OVERFLOW,
        "target_component_type": "redis",
        "config": {"duration_minutes": 15, "memory_usage": 0.98},
        "probability": 0.005,
        "is_enabled": True,
    },
    {
        "name": "MySQL连接池耗尽",
        "description": "MySQL连接池连接数耗尽",
        "fault_type": FaultType.MYSQL_CONNECTION_EXHAUST,
        "target_component_type": "mysql",
        "config": {"duration_minutes": 10, "connection_usage": 0.95},
        "probability": 0.008,
        "is_enabled": True,
    },
    {
        "name": "MySQL慢查询",
        "description": "MySQL查询响应时间异常增长",
        "fault_type": FaultType.MYSQL_SLOW_QUERY,
        "target_component_type": "mysql",
        "config": {"duration_minutes": 20, "query_time_multiplier": 10.0},
        "probability": 0.01,
        "is_enabled": True,
    },
    {
        "name": "MySQL死锁",
        "description": "MySQL发生死锁",
        "fault_type": FaultType.MYSQL_DEADLOCK,
        "target_component_type": "mysql",
        "config": {"duration_minutes": 5, "lock_wait_multiplier": 5.0},
        "probability": 0.006,
        "is_enabled": True,
    },
    {
        "name": "API网关熔断",
        "description": "API网关触发熔断器",
        "fault_type": FaultType.API_GATEWAY_CIRCUIT_BREAK,
        "target_component_type": "api_gateway",
        "config": {"duration_minutes": 8, "error_rate": 0.5},
        "probability": 0.007,
        "is_enabled": True,
    },
    {
        "name": "API网关限流",
        "description": "API网关触发限流",
        "fault_type": FaultType.API_GATEWAY_RATE_LIMIT,
        "target_component_type": "api_gateway",
        "config": {"duration_minutes": 10, "reject_rate": 0.3},
        "probability": 0.009,
        "is_enabled": True,
    },
    {
        "name": "防火墙规则阻断",
        "description": "防火墙规则异常阻断正常流量",
        "fault_type": FaultType.FIREWALL_RULE_BLOCK,
        "target_component_type": "firewall",
        "config": {"duration_minutes": 15, "block_rate": 0.2},
        "probability": 0.005,
        "is_enabled": True,
    },
]

def run_migration(db: Session):
    for scenario_data in FAULT_SCENARIOS:
        existing = db.query(FaultScenario).filter(
            FaultScenario.fault_type == scenario_data["fault_type"]
        ).first()
        
        if not existing:
            scenario = FaultScenario(**scenario_data)
            db.add(scenario)
    
    db.commit()
    print(f"Added {len(FAULT_SCENARIOS)} fault scenarios")
```

- [ ] **Step 3: 更新故障引擎**

在 `backend/apps/simulator/engine/fault_engine.py` 中添加故障影响计算：

```python
def get_fault_impact(self, fault_type: str, component_type: str) -> Dict[str, Any]:
    impact_map = {
        FaultType.NGINX_CONNECTION_OVERFLOW: {
            "nginx_connection_count": 2.0,
            "nginx_request_rate": 0.5,
        },
        FaultType.NGINX_UPSTREAM_TIMEOUT: {
            "nginx_upstream_response_time": 3.0,
            "nginx_error_rate": 5.0,
        },
        FaultType.REDIS_CONNECTION_EXHAUST: {
            "redis_connected_clients": 1.5,
            "redis_blocked_clients": 10.0,
        },
        FaultType.REDIS_MEMORY_OVERFLOW: {
            "redis_used_memory": 1.2,
            "redis_evicted_keys": 100.0,
        },
        FaultType.MYSQL_CONNECTION_EXHAUST: {
            "mysql_threads_connected": 1.5,
            "mysql_connection_errors": 10.0,
        },
        FaultType.MYSQL_SLOW_QUERY: {
            "mysql_slow_queries": 10.0,
            "mysql_query_time": 10.0,
        },
        FaultType.MYSQL_DEADLOCK: {
            "mysql_table_locks_waited": 5.0,
            "mysql_innodb_row_lock_waits": 10.0,
        },
        FaultType.API_GATEWAY_CIRCUIT_BREAK: {
            "api_gateway_circuit_breaker_open": 1.0,
            "api_gateway_error_rate": 5.0,
        },
        FaultType.API_GATEWAY_RATE_LIMIT: {
            "api_gateway_rate_limit_rejected": 10.0,
            "api_gateway_request_success_rate": 0.7,
        },
        FaultType.FIREWALL_RULE_BLOCK: {
            "firewall_blocked_connections": 5.0,
            "firewall_rule_hits": 2.0,
        },
    }
    
    return impact_map.get(fault_type, {})
```

- [ ] **Step 4: 提交故障场景适配**

```bash
git add backend/apps/simulator/models.py backend/apps/simulator/engine/fault_engine.py backend/apps/simulator/migrations/add_fault_scenarios.py
git commit -m "feat: add fault scenarios for new component types"
```

---

## Task 3: 前端交互优化 - 拓扑图节点详情

**Files:**
- Create: `frontend/src/components/simulator/ComponentDetail.vue`
- Modify: `frontend/src/views/simulator/EnvironmentManagement.vue`

**目标：** 点击拓扑图节点显示组件详情

- [ ] **Step 1: 创建组件详情组件**

创建 `frontend/src/components/simulator/ComponentDetail.vue`：

```vue
<template>
  <el-drawer
    v-model="visible"
    :title="component?.name || '组件详情'"
    direction="rtl"
    size="500px"
    :before-close="handleClose"
  >
    <div v-if="component" class="component-detail">
      <div class="detail-section">
        <h3 class="section-title">基本信息</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="组件名称">{{ component.name }}</el-descriptions-item>
          <el-descriptions-item label="组件类型">
            <el-tag>{{ getComponentTypeLabel(component.component_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ component.ip_address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="component.status === 'active' ? 'success' : 'info'">
              {{ component.status === 'active' ? '运行中' : '已停止' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="detail-section">
        <h3 class="section-title">组件属性</h3>
        <el-descriptions :column="1" border v-if="component.properties">
          <el-descriptions-item
            v-for="(value, key) in component.properties"
            :key="key"
            :label="formatPropertyKey(key)"
          >
            {{ formatPropertyValue(value) }}
          </el-descriptions-item>
        </el-descriptions>
        <el-empty v-else description="暂无属性信息" />
      </div>

      <div class="detail-section">
        <h3 class="section-title">关联组件</h3>
        <el-table :data="relatedComponents" style="width: 100%" v-if="relatedComponents.length > 0">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="relation_type" label="关系类型">
            <template #default="{ row }">
              <el-tag size="small">{{ getRelationTypeLabel(row.relation_type) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无关联组件" />
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { api } from '@/api'

interface Props {
  modelValue: boolean
  component: any
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const relatedComponents = ref([])

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.component) {
    loadRelatedComponents()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
  visible.value = false
}

const loadRelatedComponents = async () => {
  try {
    const response = await api.get(`/simulator/components/${props.component.id}/relations`)
    relatedComponents.value = response.data
  } catch (error) {
    console.error('Failed to load related components:', error)
  }
}

const getComponentTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    host: '主机',
    client: '客户端',
    nginx: 'Nginx',
    app_server: '应用服务器',
    api_gateway: 'API网关',
    firewall: '防火墙',
    redis: 'Redis',
    config_center: '配置中心',
    mysql: 'MySQL',
    kafka: 'Kafka',
  }
  return labels[type] || type
}

const getRelationTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    connects_to: '连接',
    routes_to: '路由',
    protected_by: '被保护',
    depends_on: '依赖',
    publishes_to: '发布到',
    replicates_to: '复制到',
  }
  return labels[type] || type
}

const formatPropertyKey = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatPropertyValue = (value: any) => {
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return value
}
</script>

<style scoped lang="less">
.component-detail {
  padding: 0 20px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.2);
}

:deep(.el-descriptions) {
  .el-descriptions__label {
    background: rgba(30, 40, 60, 0.95);
    color: #ffd700;
    font-weight: 500;
  }

  .el-descriptions__content {
    background: rgba(20, 25, 35, 0.85);
    color: rgba(255, 255, 255, 0.95);
  }
}
</style>
```

- [ ] **Step 2: 在环境管理页面集成组件详情**

在 `frontend/src/views/simulator/EnvironmentManagement.vue` 中添加：

```vue
<template>
  <!-- 现有代码 -->
  
  <ComponentDetail
    v-model="showComponentDetail"
    :component="selectedComponent"
  />
</template>

<script setup lang="ts">
import ComponentDetail from '@/components/simulator/ComponentDetail.vue'

const showComponentDetail = ref(false)
const selectedComponent = ref(null)

const handleNodeClick = (component: any) => {
  selectedComponent.value = component
  showComponentDetail.value = true
}
</script>
```

- [ ] **Step 3: 提交组件详情功能**

```bash
git add frontend/src/components/simulator/ComponentDetail.vue frontend/src/views/simulator/EnvironmentManagement.vue
git commit -m "feat: add component detail drawer for topology nodes"
```

---

## Task 4: 前端交互优化 - 组件状态实时监控

**Files:**
- Modify: `frontend/src/views/simulator/EnvironmentManagement.vue`
- Modify: `frontend/src/api/simulator.ts`

**目标：** 在拓扑图上显示组件的实时状态

- [ ] **Step 1: 添加组件状态API**

在 `frontend/src/api/simulator.ts` 中添加：

```typescript
export const getComponentMetrics = (componentId: number) => {
  return apiClient.get(`/simulator/components/${componentId}/metrics`)
}

export const getEnvironmentStatus = (envId: number) => {
  return apiClient.get(`/simulator/environments/${envId}/status`)
}
```

- [ ] **Step 2: 在后端添加状态API**

在 `backend/apps/simulator/router.py` 中添加：

```python
@router.get("/environments/{env_id}/status")
def get_environment_status(
    env_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    components = db.query(SimulationComponent).filter(SimulationComponent.env_id == env_id).all()
    
    status = {
        "total_components": len(components),
        "active_components": len([c for c in components if c.status == "active"]),
        "inactive_components": len([c for c in components if c.status != "active"]),
        "components": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.component_type,
                "status": c.status,
            }
            for c in components
        ],
    }
    
    return status
```

- [ ] **Step 3: 在前端实现状态轮询**

在 `frontend/src/views/simulator/EnvironmentManagement.vue` 中添加：

```vue
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { getEnvironmentStatus } from '@/api/simulator'

let statusInterval: number | null = null

const loadEnvironmentStatus = async () => {
  if (!environment.value?.id) return
  
  try {
    const response = await getEnvironmentStatus(environment.value.id)
    updateComponentStatus(response.data.components)
  } catch (error) {
    console.error('Failed to load environment status:', error)
  }
}

const updateComponentStatus = (components: any[]) => {
  components.forEach(comp => {
    const node = topologyNodes.value.find(n => n.id === comp.id)
    if (node) {
      node.status = comp.status
    }
  })
}

onMounted(() => {
  loadEnvironmentStatus()
  statusInterval = setInterval(loadEnvironmentStatus, 10000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>
```

- [ ] **Step 4: 提交状态监控功能**

```bash
git add frontend/src/api/simulator.ts frontend/src/views/simulator/EnvironmentManagement.vue backend/apps/simulator/router.py
git commit -m "feat: add real-time component status monitoring"
```

---

## Task 5: 前端交互优化 - 拓扑图缩放和拖拽

**Files:**
- Modify: `frontend/src/views/simulator/EnvironmentManagement.vue`

**目标：** 支持拓扑图的缩放和拖拽功能

- [ ] **Step 1: 添加缩放控制**

在 `frontend/src/views/simulator/EnvironmentManagement.vue` 中添加：

```vue
<template>
  <div class="topology-container">
    <div class="topology-controls">
      <el-button-group>
        <el-button @click="zoomIn" :icon="ZoomIn" />
        <el-button @click="zoomOut" :icon="ZoomOut" />
        <el-button @click="resetZoom" :icon="RefreshRight" />
      </el-button-group>
      <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
    </div>
    
    <div
      class="topology-graph"
      ref="topologyGraph"
      @wheel="handleWheel"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="endDrag"
      @mouseleave="endDrag"
      :style="graphStyle"
    >
      <!-- 拓扑图内容 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ZoomIn, ZoomOut, RefreshRight } from '@element-plus/icons-vue'

const zoomLevel = ref(1)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const graphOffset = ref({ x: 0, y: 0 })

const graphStyle = computed(() => ({
  transform: `scale(${zoomLevel.value}) translate(${graphOffset.value.x}px, ${graphOffset.value.y}px)`,
  cursor: isDragging.value ? 'grabbing' : 'grab',
}))

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value + 0.1, 2)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value - 0.1, 0.5)
}

const resetZoom = () => {
  zoomLevel.value = 1
  graphOffset.value = { x: 0, y: 0 }
}

const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  zoomLevel.value = Math.max(0.5, Math.min(2, zoomLevel.value + delta))
}

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  dragStart.value = { x: e.clientX - graphOffset.value.x, y: e.clientY - graphOffset.value.y }
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  graphOffset.value = {
    x: e.clientX - dragStart.value.x,
    y: e.clientY - dragStart.value.y,
  }
}

const endDrag = () => {
  isDragging.value = false
}
</script>

<style scoped lang="less">
.topology-container {
  position: relative;
  width: 100%;
  height: 600px;
  overflow: hidden;
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
}

.topology-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(26, 26, 46, 0.9);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 215, 0, 0.2);
}

.zoom-level {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  min-width: 50px;
  text-align: center;
}

.topology-graph {
  width: 100%;
  height: 100%;
  transition: transform 0.1s ease;
  transform-origin: center center;
}
</style>
```

- [ ] **Step 2: 提交缩放拖拽功能**

```bash
git add frontend/src/views/simulator/EnvironmentManagement.vue
git commit -m "feat: add zoom and drag functionality for topology graph"
```

---

## Task 6: 可视化增强 - 拓扑图流量动态展示

**Files:**
- Modify: `frontend/src/views/simulator/EnvironmentManagement.vue`

**目标：** 在拓扑图上动态展示流量

- [ ] **Step 1: 添加流量动画效果**

在 `frontend/src/views/simulator/EnvironmentManagement.vue` 中添加：

```vue
<template>
  <div class="topology-graph">
    <!-- 现有拓扑图内容 -->
    
    <!-- 流量动画层 -->
    <svg class="traffic-layer" ref="trafficLayer">
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#ffd700" />
        </marker>
      </defs>
      
      <g v-for="flow in trafficFlows" :key="flow.id">
        <path
          :d="flow.path"
          class="traffic-path"
          :style="{ animationDelay: flow.delay + 's' }"
          marker-end="url(#arrowhead)"
        />
        <circle
          :r="4"
          fill="#ffd700"
          class="traffic-particle"
          :style="{ animationDelay: flow.delay + 's' }"
        >
          <animateMotion
            :dur="flow.duration + 's'"
            repeatCount="indefinite"
            :path="flow.path"
          />
        </circle>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface TrafficFlow {
  id: string
  path: string
  duration: number
  delay: number
}

const trafficFlows = ref<TrafficFlow[]>([])

const generateTrafficFlows = () => {
  const flows: TrafficFlow[] = []
  
  topologyRelations.value.forEach((relation, index) => {
    const source = topologyNodes.value.find(n => n.id === relation.source_id)
    const target = topologyNodes.value.find(n => n.id === relation.target_id)
    
    if (source && target) {
      flows.push({
        id: `flow-${relation.id}`,
        path: `M ${source.x + 50} ${source.y + 25} L ${target.x + 50} ${target.y + 25}`,
        duration: 2 + Math.random() * 2,
        delay: index * 0.5,
      })
    }
  })
  
  trafficFlows.value = flows
}

onMounted(() => {
  generateTrafficFlows()
})
</script>

<style scoped lang="less">
.traffic-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 5;
}

.traffic-path {
  fill: none;
  stroke: rgba(255, 215, 0, 0.3);
  stroke-width: 2;
  stroke-dasharray: 5, 5;
  animation: dash 20s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -100;
  }
}

.traffic-particle {
  filter: drop-shadow(0 0 4px rgba(255, 215, 0, 0.8));
}
</style>
```

- [ ] **Step 2: 提交流量动态展示**

```bash
git add frontend/src/views/simulator/EnvironmentManagement.vue
git commit -m "feat: add dynamic traffic flow visualization on topology graph"
```

---

## Task 7: 可视化增强 - 组件健康状态可视化

**Files:**
- Modify: `frontend/src/views/simulator/EnvironmentManagement.vue`

**目标：** 在拓扑图上用颜色标识组件健康状态

- [ ] **Step 1: 添加健康状态样式**

在 `frontend/src/views/simulator/EnvironmentManagement.vue` 中添加：

```vue
<template>
  <div class="topology-node" :class="`status-${component.health}`">
    <div class="node-icon">
      <el-icon :size="32">
        <component :is="getComponentIcon(component.component_type)" />
      </el-icon>
    </div>
    <div class="node-info">
      <div class="node-name">{{ component.name }}</div>
      <div class="node-status">
        <span class="status-dot" :class="component.health"></span>
        {{ getHealthLabel(component.health) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const getHealthLabel = (health: string) => {
  const labels: Record<string, string> = {
    healthy: '健康',
    warning: '警告',
    critical: '严重',
    unknown: '未知',
  }
  return labels[health] || '未知'
}
</script>

<style scoped lang="less">
.topology-node {
  &.status-healthy {
    border-color: rgba(34, 197, 94, 0.5);
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%);
    
    .status-dot {
      background: #22c55e;
      box-shadow: 0 0 8px rgba(34, 197, 94, 0.8);
    }
  }
  
  &.status-warning {
    border-color: rgba(245, 158, 11, 0.5);
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
    
    .status-dot {
      background: #f59e0b;
      box-shadow: 0 0 8px rgba(245, 158, 11, 0.8);
    }
  }
  
  &.status-critical {
    border-color: rgba(239, 68, 68, 0.5);
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
    animation: pulse-critical 2s infinite;
    
    .status-dot {
      background: #ef4444;
      box-shadow: 0 0 8px rgba(239, 68, 68, 0.8);
    }
  }
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

@keyframes pulse-critical {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
}
</style>
```

- [ ] **Step 2: 提交健康状态可视化**

```bash
git add frontend/src/views/simulator/EnvironmentManagement.vue
git commit -m "feat: add health status visualization for topology nodes"
```

---

## Task 8: 可视化增强 - 告警事件标注

**Files:**
- Modify: `frontend/src/views/simulator/EnvironmentManagement.vue`
- Modify: `frontend/src/api/simulator.ts`

**目标：** 在拓扑图上标注告警事件

- [ ] **Step 1: 添加告警标注组件**

在 `frontend/src/views/simulator/EnvironmentManagement.vue` 中添加：

```vue
<template>
  <div class="topology-node">
    <!-- 现有内容 -->
    
    <!-- 告警标注 -->
    <div v-if="component.alerts && component.alerts.length > 0" class="alert-badge">
      <el-badge :value="component.alerts.length" type="danger">
        <el-icon :size="16" color="#ef4444">
          <Bell />
        </el-icon>
      </el-badge>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bell } from '@element-plus/icons-vue'

const loadComponentAlerts = async () => {
  if (!environment.value?.id) return
  
  try {
    const response = await api.get(`/simulator/environments/${environment.value.id}/alerts`)
    const alerts = response.data
    
    topologyNodes.value.forEach(node => {
      node.alerts = alerts.filter((a: any) => a.component_id === node.id)
    })
  } catch (error) {
    console.error('Failed to load component alerts:', error)
  }
}

onMounted(() => {
  loadComponentAlerts()
  setInterval(loadComponentAlerts, 30000)
})
</script>

<style scoped lang="less">
.alert-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 10;
  animation: shake 0.5s ease-in-out infinite;
}

@keyframes shake {
  0%, 100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-10deg);
  }
  75% {
    transform: rotate(10deg);
  }
}
</style>
```

- [ ] **Step 2: 提交告警标注功能**

```bash
git add frontend/src/views/simulator/EnvironmentManagement.vue frontend/src/api/simulator.ts
git commit -m "feat: add alert event annotations on topology graph"
```

---

## Task 9: 高级功能 - 历史场景回放

**Files:**
- Create: `frontend/src/views/simulator/ScenarioReplay.vue`
- Modify: `backend/apps/simulator/router.py`
- Modify: `backend/apps/simulator/models.py`

**目标：** 支持历史故障场景的回放

- [ ] **Step 1: 添加历史场景数据模型**

在 `backend/apps/simulator/models.py` 中添加：

```python
class ScenarioHistory(Base):
    __tablename__ = "simulator_scenario_history"

    id = Column(Integer, primary_key=True, index=True)
    env_id = Column(Integer, ForeignKey("simulator_environments.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="completed")
    snapshot_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
```

- [ ] **Step 2: 创建回放页面**

创建 `frontend/src/views/simulator/ScenarioReplay.vue`：

```vue
<template>
  <div class="scenario-replay">
    <div class="page-header">
      <h2 class="page-title">历史场景回放</h2>
    </div>

    <div class="config-card">
      <el-table :data="scenarioHistory" style="width: 100%">
        <el-table-column prop="name" label="场景名称" />
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'">
              {{ row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="replayScenario(row)">
              回放
            </el-button>
            <el-button type="danger" link @click="deleteScenario(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="replayDialogVisible" title="场景回放" width="80%">
      <div class="replay-container">
        <div class="replay-controls">
          <el-button @click="startReplay" :disabled="isReplaying">
            <el-icon><VideoPlay /></el-icon>
            开始
          </el-button>
          <el-button @click="pauseReplay" :disabled="!isReplaying">
            <el-icon><VideoPause /></el-icon>
            暂停
          </el-button>
          <el-slider
            v-model="replayProgress"
            :max="100"
            :format-tooltip="formatProgress"
            style="width: 300px; margin: 0 20px;"
          />
          <span class="replay-time">{{ formatTime(currentTime) }} / {{ formatTime(totalTime) }}</span>
        </div>
        
        <div class="replay-view">
          <!-- 回放视图内容 -->
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { api } from '@/api'
import { ElMessage } from 'element-plus'

const scenarioHistory = ref([])
const replayDialogVisible = ref(false)
const isReplaying = ref(false)
const replayProgress = ref(0)
const currentTime = ref(0)
const totalTime = ref(0)

const loadScenarioHistory = async () => {
  try {
    const response = await api.get('/simulator/scenarios/history')
    scenarioHistory.value = response.data
  } catch (error) {
    console.error('Failed to load scenario history:', error)
  }
}

const replayScenario = (scenario: any) => {
  replayDialogVisible.value = true
}

const startReplay = () => {
  isReplaying.value = true
}

const pauseReplay = () => {
  isReplaying.value = false
}

const formatProgress = (value: number) => {
  return `${value}%`
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

onMounted(() => {
  loadScenarioHistory()
})
</script>

<style scoped lang="less">
.replay-container {
  height: 500px;
}

.replay-controls {
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 16px;
}

.replay-time {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  min-width: 120px;
}

.replay-view {
  height: calc(100% - 80px);
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
}
</style>
```

- [ ] **Step 3: 提交历史场景回放功能**

```bash
git add frontend/src/views/simulator/ScenarioReplay.vue backend/apps/simulator/models.py backend/apps/simulator/router.py
git commit -m "feat: add scenario history replay functionality"
```

---

## Task 10: 高级功能 - 拓扑模板保存与加载

**Files:**
- Modify: `backend/apps/simulator/models.py`
- Modify: `backend/apps/simulator/router.py`
- Modify: `frontend/src/views/simulator/EnvironmentManagement.vue`

**目标：** 支持拓扑模板的保存和加载

- [ ] **Step 1: 添加拓扑模板数据模型**

在 `backend/apps/simulator/models.py` 中添加：

```python
class TopologyTemplate(Base):
    __tablename__ = "simulator_topology_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    topology_type = Column(String(50), nullable=False)
    scale = Column(String(50), nullable=False)
    components_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

- [ ] **Step 2: 添加模板API**

在 `backend/apps/simulator/router.py` 中添加：

```python
@router.post("/templates")
def create_template(
    template: TopologyTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_template = TopologyTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/templates")
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(TopologyTemplate).all()

@router.post("/templates/{template_id}/apply")
def apply_template(
    template_id: int,
    env_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    template = db.query(TopologyTemplate).filter(TopologyTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    generator = TopologyGenerator(db)
    env = generator.generate(
        name=env_name,
        topology_type=template.topology_type,
        scale=template.scale,
        components_config=template.components_config,
    )
    
    return env
```

- [ ] **Step 3: 在前端添加模板功能**

在 `frontend/src/views/simulator/EnvironmentManagement.vue` 中添加：

```vue
<template>
  <div class="template-actions">
    <el-button type="primary" @click="saveAsTemplate">
      保存为模板
    </el-button>
    <el-button @click="loadTemplate">
      加载模板
    </el-button>
  </div>

  <el-dialog v-model="saveTemplateDialog" title="保存为模板" width="500px">
    <el-form :model="templateForm" label-width="100px">
      <el-form-item label="模板名称">
        <el-input v-model="templateForm.name" />
      </el-form-item>
      <el-form-item label="模板描述">
        <el-input v-model="templateForm.description" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="saveTemplateDialog = false">取消</el-button>
      <el-button type="primary" @click="confirmSaveTemplate">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="loadTemplateDialog" title="加载模板" width="600px">
    <el-table :data="templates" @row-click="selectTemplate">
      <el-table-column prop="name" label="模板名称" />
      <el-table-column prop="topology_type" label="拓扑类型" />
      <el-table-column prop="scale" label="规模" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
    </el-table>
    <template #footer>
      <el-button @click="loadTemplateDialog = false">取消</el-button>
      <el-button type="primary" @click="confirmLoadTemplate">加载</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
const saveTemplateDialog = ref(false)
const loadTemplateDialog = ref(false)
const templates = ref([])
const selectedTemplate = ref(null)
const templateForm = ref({
  name: '',
  description: '',
})

const saveAsTemplate = () => {
  saveTemplateDialog.value = true
}

const confirmSaveTemplate = async () => {
  try {
    await api.post('/simulator/templates', {
      ...templateForm.value,
      topology_type: environment.value.topology_type,
      scale: environment.value.scale,
      components_config: topologyNodes.value,
    })
    ElMessage.success('模板保存成功')
    saveTemplateDialog.value = false
  } catch (error) {
    ElMessage.error('模板保存失败')
  }
}

const loadTemplate = async () => {
  try {
    const response = await api.get('/simulator/templates')
    templates.value = response.data
    loadTemplateDialog.value = true
  } catch (error) {
    ElMessage.error('加载模板列表失败')
  }
}

const selectTemplate = (row: any) => {
  selectedTemplate.value = row
}

const confirmLoadTemplate = async () => {
  if (!selectedTemplate.value) {
    ElMessage.warning('请选择一个模板')
    return
  }
  
  try {
    await api.post(`/simulator/templates/${selectedTemplate.value.id}/apply`, null, {
      params: { env_name: `环境-${Date.now()}` }
    })
    ElMessage.success('模板加载成功')
    loadTemplateDialog.value = false
    loadEnvironment()
  } catch (error) {
    ElMessage.error('模板加载失败')
  }
}
</script>
```

- [ ] **Step 4: 提交模板功能**

```bash
git add backend/apps/simulator/models.py backend/apps/simulator/router.py frontend/src/views/simulator/EnvironmentManagement.vue
git commit -m "feat: add topology template save and load functionality"
```

---

## Task 11: 高级功能 - 自定义拓扑编辑器

**Files:**
- Create: `frontend/src/views/simulator/TopologyEditor.vue`
- Modify: `frontend/src/router/index.ts`

**目标：** 支持自定义拓扑编辑（基于拖拽）

- [ ] **Step 1: 创建拓扑编辑器页面**

创建 `frontend/src/views/simulator/TopologyEditor.vue`：

```vue
<template>
  <div class="topology-editor">
    <div class="editor-header">
      <h2 class="page-title">拓扑编辑器</h2>
      <div class="editor-actions">
        <el-button @click="clearCanvas">清空画布</el-button>
        <el-button type="primary" @click="saveTopology">保存拓扑</el-button>
      </div>
    </div>

    <div class="editor-container">
      <div class="component-palette">
        <h3 class="palette-title">组件库</h3>
        <div
          v-for="comp in componentTypes"
          :key="comp.type"
          class="palette-item"
          draggable="true"
          @dragstart="dragStart($event, comp)"
        >
          <el-icon :size="24">
            <component :is="comp.icon" />
          </el-icon>
          <span>{{ comp.label }}</span>
        </div>
      </div>

      <div
        class="editor-canvas"
        ref="canvas"
        @dragover.prevent
        @drop="drop"
        @click="selectNode"
      >
        <div
          v-for="node in nodes"
          :key="node.id"
          class="canvas-node"
          :class="{ selected: selectedNode?.id === node.id }"
          :style="{ left: node.x + 'px', top: node.y + 'px' }"
          @mousedown="startDragNode($event, node)"
        >
          <el-icon :size="32">
            <component :is="getComponentIcon(node.type)" />
          </el-icon>
          <div class="node-label">{{ node.name }}</div>
        </div>

        <svg class="connections-layer">
          <line
            v-for="conn in connections"
            :key="conn.id"
            :x1="conn.x1"
            :y1="conn.y1"
            :x2="conn.x2"
            :y2="conn.y2"
            stroke="rgba(255, 215, 0, 0.5)"
            stroke-width="2"
          />
        </svg>
      </div>

      <div class="properties-panel" v-if="selectedNode">
        <h3 class="panel-title">属性</h3>
        <el-form :model="selectedNode" label-width="80px">
          <el-form-item label="名称">
            <el-input v-model="selectedNode.name" />
          </el-form-item>
          <el-form-item label="类型">
            <el-tag>{{ selectedNode.type }}</el-tag>
          </el-form-item>
          <el-form-item label="IP地址">
            <el-input v-model="selectedNode.ip" />
          </el-form-item>
          <el-form-item label="连接到">
            <el-select v-model="selectedNode.connections" multiple placeholder="选择连接目标">
              <el-option
                v-for="node in nodes.filter(n => n.id !== selectedNode.id)"
                :key="node.id"
                :label="node.name"
                :value="node.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
        <el-button type="danger" @click="deleteNode">删除节点</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Monitor,
  Connection,
  Server,
  Grid,
  Platform,
  Lock,
  Coin,
  Setting,
  Database,
  Message,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'

const nodes = ref<any[]>([])
const connections = ref<any[]>([])
const selectedNode = ref<any>(null)
const draggedNode = ref<any>(null)
const isDraggingNode = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

const componentTypes = [
  { type: 'client', label: '客户端', icon: Monitor },
  { type: 'nginx', label: 'Nginx', icon: Connection },
  { type: 'app_server', label: '应用服务器', icon: Server },
  { type: 'api_gateway', label: 'API网关', icon: Grid },
  { type: 'firewall', label: '防火墙', icon: Lock },
  { type: 'redis', label: 'Redis', icon: Coin },
  { type: 'config_center', label: '配置中心', icon: Setting },
  { type: 'mysql', label: 'MySQL', icon: Database },
  { type: 'kafka', label: 'Kafka', icon: Message },
]

const dragStart = (e: DragEvent, comp: any) => {
  e.dataTransfer?.setData('component', JSON.stringify(comp))
}

const drop = (e: DragEvent) => {
  const data = e.dataTransfer?.getData('component')
  if (!data) return

  const comp = JSON.parse(data)
  const canvas = e.currentTarget as HTMLElement
  const rect = canvas.getBoundingClientRect()
  
  const newNode = {
    id: Date.now(),
    type: comp.type,
    name: `${comp.label}-${nodes.value.length + 1}`,
    x: e.clientX - rect.left - 50,
    y: e.clientY - rect.top - 25,
    ip: '',
    connections: [],
  }
  
  nodes.value.push(newNode)
}

const selectNode = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (target.classList.contains('canvas-node') || target.closest('.canvas-node')) {
    return
  }
  selectedNode.value = null
}

const startDragNode = (e: MouseEvent, node: any) => {
  selectedNode.value = node
  isDraggingNode.value = true
  draggedNode.value = node
  dragOffset.value = {
    x: e.clientX - node.x,
    y: e.clientY - node.y,
  }
  
  document.addEventListener('mousemove', onDragNode)
  document.addEventListener('mouseup', endDragNode)
}

const onDragNode = (e: MouseEvent) => {
  if (!isDraggingNode.value || !draggedNode.value) return
  
  draggedNode.value.x = e.clientX - dragOffset.value.x
  draggedNode.value.y = e.clientY - dragOffset.value.y
  
  updateConnections()
}

const endDragNode = () => {
  isDraggingNode.value = false
  draggedNode.value = null
  
  document.removeEventListener('mousemove', onDragNode)
  document.removeEventListener('mouseup', endDragNode)
}

const updateConnections = () => {
  connections.value = []
  
  nodes.value.forEach(node => {
    node.connections?.forEach((targetId: number) => {
      const target = nodes.value.find(n => n.id === targetId)
      if (target) {
        connections.value.push({
          id: `${node.id}-${targetId}`,
          x1: node.x + 50,
          y1: node.y + 25,
          x2: target.x + 50,
          y2: target.y + 25,
        })
      }
    })
  })
}

const deleteNode = () => {
  if (!selectedNode.value) return
  
  nodes.value = nodes.value.filter(n => n.id !== selectedNode.value.id)
  nodes.value.forEach(node => {
    node.connections = node.connections?.filter((id: number) => id !== selectedNode.value.id)
  })
  
  selectedNode.value = null
  updateConnections()
}

const clearCanvas = () => {
  nodes.value = []
  connections.value = []
  selectedNode.value = null
}

const saveTopology = async () => {
  try {
    await api.post('/simulator/environments', {
      name: `自定义拓扑-${Date.now()}`,
      topology_data: { nodes: nodes.value, connections: connections.value },
    })
    ElMessage.success('拓扑保存成功')
  } catch (error) {
    ElMessage.error('拓扑保存失败')
  }
}

const getComponentIcon = (type: string) => {
  const comp = componentTypes.find(c => c.type === type)
  return comp?.icon || Monitor
}
</script>

<style scoped lang="less">
.topology-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.2);
}

.editor-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.component-palette {
  width: 200px;
  background: rgba(26, 26, 46, 0.8);
  border-right: 1px solid rgba(255, 215, 0, 0.2);
  padding: 16px;
}

.palette-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin-bottom: 16px;
}

.palette-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 8px;
  cursor: grab;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 215, 0, 0.2);
    border-color: rgba(255, 215, 0, 0.4);
  }

  span {
    color: rgba(255, 255, 255, 0.8);
    font-size: 14px;
  }
}

.editor-canvas {
  flex: 1;
  position: relative;
  background: rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.canvas-node {
  position: absolute;
  width: 100px;
  height: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(26, 26, 46, 0.9);
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-radius: 8px;
  cursor: move;
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(255, 215, 0, 0.6);
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
  }

  &.selected {
    border-color: #ffd700;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
  }

  .node-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 4px;
  }
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.properties-panel {
  width: 300px;
  background: rgba(26, 26, 46, 0.8);
  border-left: 1px solid rgba(255, 215, 0, 0.2);
  padding: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin-bottom: 16px;
}
</style>
```

- [ ] **Step 2: 添加路由**

在 `frontend/src/router/index.ts` 中添加：

```typescript
{
  path: '/simulator/editor',
  name: 'TopologyEditor',
  component: () => import('@/views/simulator/TopologyEditor.vue'),
  meta: { title: '拓扑编辑器' },
}
```

- [ ] **Step 3: 提交拓扑编辑器**

```bash
git add frontend/src/views/simulator/TopologyEditor.vue frontend/src/router/index.ts
git commit -m "feat: add custom topology editor with drag-and-drop"
```

---

## Task 12: 测试验证所有功能

**目标：** 确保所有功能正常工作

- [ ] **Step 1: 启动后端服务**

```bash
cd backend
python main.py
```

- [ ] **Step 2: 启动前端服务**

```bash
cd frontend
npm run dev
```

- [ ] **Step 3: 测试故障场景适配**

1. 访问故障管理页面
2. 查看新增的故障场景是否正确显示
3. 测试故障场景的启用/禁用功能

- [ ] **Step 4: 测试前端交互优化**

1. 访问环境管理页面
2. 点击拓扑图节点，查看组件详情是否正确显示
3. 测试拓扑图的缩放和拖拽功能
4. 验证组件状态实时监控是否工作

- [ ] **Step 5: 测试可视化增强**

1. 查看拓扑图流量动态展示是否正常
2. 验证组件健康状态颜色是否正确
3. 检查告警事件标注是否显示

- [ ] **Step 6: 测试高级功能**

1. 测试历史场景回放功能
2. 测试拓扑模板保存和加载
3. 测试自定义拓扑编辑器

- [ ] **Step 7: 验证样式一致性**

1. 检查所有对话框的取消按钮是否为深色主题
2. 验证所有组件的样式是否一致
3. 检查是否有白色背景的组件

---

## 总结

本实现计划涵盖了模拟器的所有待办功能，包括：

1. **样式修复**：修复对话框按钮等组件的深色主题样式
2. **故障场景适配**：支持新增组件类型的故障场景
3. **前端交互优化**：节点详情、实时监控、缩放拖拽
4. **可视化增强**：流量动态展示、健康状态可视化、告警标注
5. **高级功能**：历史回放、模板保存加载、自定义编辑器
6. **测试验证**：确保所有功能正常工作

每个任务都包含详细的实现步骤和代码示例，确保可以顺利实施。
