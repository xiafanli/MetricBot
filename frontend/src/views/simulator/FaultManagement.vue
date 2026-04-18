<template>
  <div class="fault-management">
    <div class="config-card">
      <el-tabs v-model="activeTab" class="fault-tabs">
        <el-tab-pane label="故障场景" name="scenarios">
          <template #label>
            <div class="tab-label-wrapper">
              <span>故障场景</span>
              <el-button type="primary" size="small" class="tab-action-btn" @click.stop="showCreateDialog">
                <el-icon><Plus /></el-icon>
                创建
              </el-button>
            </div>
          </template>
          <div class="table-wrapper">
            <el-table 
              :data="faultScenarios" 
              style="width: 100%"
              table-layout="fixed"
            >
              <el-table-column prop="id" label="ID" width="60" align="center" />
              <el-table-column prop="name" label="故障名称" min-width="150" />
              <el-table-column prop="fault_type" label="故障类型" min-width="150" />
              <el-table-column prop="target_component_type" label="目标组件" min-width="120" />
              <el-table-column prop="probability" label="触发概率" width="100" align="center">
                <template #default="{ row }">
                  {{ (row.probability * 100).toFixed(1) }}%
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_enabled ? 'success' : 'info'" size="small">
                    {{ row.is_enabled ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180" align="center">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
                  <el-button 
                    :type="row.is_enabled ? 'warning' : 'success'" 
                    link 
                    size="small" 
                    @click="handleToggle(row)"
                  >
                    {{ row.is_enabled ? '禁用' : '启用' }}
                  </el-button>
                  <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="故障实例" name="instances">
          <div class="table-wrapper">
            <el-table 
              :data="faultInstances" 
              style="width: 100%"
              table-layout="fixed"
            >
              <el-table-column prop="id" label="ID" width="60" align="center" />
              <el-table-column prop="scenario_id" label="场景ID" width="80" align="center" />
              <el-table-column prop="component_id" label="组件ID" width="80" align="center" />
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag 
                    :type="row.status === 'active' ? 'danger' : row.status === 'pending' ? 'warning' : 'success'" 
                    size="small"
                  >
                    {{ row.status === 'active' ? '进行中' : row.status === 'pending' ? '待处理' : '已恢复' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="start_time" label="触发时间" min-width="160" />
              <el-table-column prop="end_time" label="恢复时间" min-width="160">
                <template #default="{ row }">
                  {{ row.end_time || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button 
                    v-if="row.status === 'active'"
                    type="success" 
                    link 
                    size="small" 
                    @click="handleRecover(row)"
                  >
                    恢复
                  </el-button>
                  <span v-else class="text-muted">-</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog 
      v-model="createDialogVisible" 
      :title="editingScenario ? '编辑故障场景' : '创建故障场景'" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="scenarioForm" :rules="scenarioRules" ref="formRef" label-width="100px">
        <el-form-item label="故障名称" prop="name">
          <el-input v-model="scenarioForm.name" placeholder="请输入故障名称" />
        </el-form-item>
        <el-form-item label="故障类型" prop="fault_type">
          <el-select v-model="scenarioForm.fault_type" placeholder="请选择故障类型" style="width: 100%">
            <el-option label="CPU过载" value="host_cpu_overload" />
            <el-option label="内存耗尽" value="host_memory_exhaust" />
            <el-option label="磁盘满" value="host_disk_full" />
            <el-option label="网络延迟" value="host_network_latency" />
            <el-option label="Nginx连接溢出" value="nginx_connection_overflow" />
            <el-option label="Nginx上游超时" value="nginx_upstream_timeout" />
            <el-option label="应用内存泄漏" value="app_memory_leak" />
            <el-option label="API超时" value="app_api_timeout" />
            <el-option label="Redis连接耗尽" value="redis_connection_exhaust" />
            <el-option label="MySQL慢查询" value="mysql_slow_query" />
            <el-option label="MySQL死锁" value="mysql_deadlock" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标组件" prop="target_component_type">
          <el-select v-model="scenarioForm.target_component_type" placeholder="请选择目标组件类型" style="width: 100%">
            <el-option label="客户端" value="client" />
            <el-option label="负载均衡" value="nginx" />
            <el-option label="应用服务" value="app" />
            <el-option label="缓存" value="redis" />
            <el-option label="数据库" value="mysql" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发概率" prop="probability">
          <el-slider 
            v-model="scenarioForm.probability" 
            :min="0" 
            :max="1" 
            :step="0.01" 
            show-input
            :show-input-controls="false"
          />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="scenarioForm.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api } from '@/api'

interface FaultScenario {
  id: number
  name: string
  fault_type: string
  target_component_type: string
  config: any
  probability: number
  is_enabled: boolean
  created_at: string
  updated_at: string
}

interface FaultInstance {
  id: number
  scenario_id: number
  component_id: number
  start_time: string
  end_time: string | null
  status: string
  impact_data: any
  created_at: string
}

const activeTab = ref('scenarios')
const faultScenarios = ref<FaultScenario[]>([])
const faultInstances = ref<FaultInstance[]>([])
const createDialogVisible = ref(false)
const editingScenario = ref<FaultScenario | null>(null)
const submitting = ref(false)
const formRef = ref()

const scenarioForm = ref({
  name: '',
  fault_type: '',
  target_component_type: '',
  probability: 0.5,
  is_enabled: true
})

const scenarioRules = {
  name: [{ required: true, message: '请输入故障名称', trigger: 'blur' }],
  fault_type: [{ required: true, message: '请选择故障类型', trigger: 'change' }],
  target_component_type: [{ required: true, message: '请选择目标组件类型', trigger: 'change' }]
}

const loadFaultScenarios = async () => {
  try {
    const data = await api.getFaultScenarios()
    faultScenarios.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载故障场景失败:', error)
    ElMessage.error('加载故障场景失败')
    faultScenarios.value = []
  }
}

const loadFaultInstances = async () => {
  try {
    const data = await api.getFaultInstances()
    faultInstances.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载故障实例失败:', error)
    ElMessage.error('加载故障实例失败')
    faultInstances.value = []
  }
}

const showCreateDialog = () => {
  editingScenario.value = null
  scenarioForm.value = {
    name: '',
    fault_type: '',
    target_component_type: '',
    probability: 0.5,
    is_enabled: true
  }
  createDialogVisible.value = true
}

const handleEdit = (row: FaultScenario) => {
  editingScenario.value = row
  scenarioForm.value = {
    name: row.name,
    fault_type: row.fault_type,
    target_component_type: row.target_component_type,
    probability: row.probability,
    is_enabled: row.is_enabled
  }
  createDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingScenario.value) {
        await api.updateFaultScenario(editingScenario.value.id, scenarioForm.value)
        ElMessage.success('更新成功')
      } else {
        await api.createFaultScenario(scenarioForm.value)
        ElMessage.success('创建成功')
      }
      createDialogVisible.value = false
      loadFaultScenarios()
    } catch (error) {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleToggle = async (row: FaultScenario) => {
  try {
    await api.updateFaultScenario(row.id, { is_enabled: !row.is_enabled })
    ElMessage.success(row.is_enabled ? '已禁用' : '已启用')
    loadFaultScenarios()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row: FaultScenario) => {
  try {
    await ElMessageBox.confirm('确定要删除该故障场景吗？', '提示', {
      type: 'warning'
    })
    await api.deleteFaultScenario(row.id)
    ElMessage.success('删除成功')
    loadFaultScenarios()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleRecover = async (row: FaultInstance) => {
  try {
    await api.recoverFaultInstance(row.id)
    ElMessage.success('故障已恢复')
    loadFaultInstances()
  } catch (error) {
    console.error('恢复失败:', error)
    ElMessage.error('恢复失败')
  }
}

onMounted(() => {
  loadFaultScenarios()
  loadFaultInstances()
})
</script>

<style lang="less" scoped>
.fault-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  background: var(--bg-primary);
  font-family: var(--font-body);
}

.config-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.table-wrapper {
  padding: 16px;
}

.text-muted {
  color: var(--text-tertiary);
}

.tab-label-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tab-action-btn {
  padding: 4px 8px;
  font-size: 12px;
  background: var(--gradient-neon) !important;
  border: none !important;
  color: white !important;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.4);
  }
}

:deep(.fault-tabs) {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .el-tabs__header {
    margin: 0;
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-light);
  }
  
  .el-tabs__nav-wrap::after {
    display: none;
  }
  
  .el-tabs__item {
    color: var(--text-tertiary);
    font-weight: 500;
    
    &:hover {
      color: var(--neon-blue);
    }
    
    &.is-active {
      color: var(--neon-blue);
    }
  }
  
  .el-tabs__active-bar {
    background-color: var(--neon-blue);
  }
  
  .el-tabs__content {
    flex: 1;
    overflow: auto;
  }
  
  .el-tab-pane {
    height: 100%;
  }
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

  &.el-tag--danger {
    background: rgba(255, 0, 153, 0.15);
    color: var(--neon-pink);
  }

  &.el-tag--warning {
    background: rgba(255, 165, 0, 0.15);
    color: var(--neon-orange);
  }
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;

  &.el-button--primary {
    background: var(--gradient-neon);
    border: none;
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
  }

  &.el-button--success {
    background: rgba(0, 255, 136, 0.15);
    border: 1px solid var(--neon-green);
    color: var(--neon-green);

    &:hover {
      background: rgba(0, 255, 136, 0.25);
    }
  }

  &.el-button--danger {
    background: rgba(255, 0, 153, 0.15);
    border: 1px solid var(--neon-pink);
    color: var(--neon-pink);

    &:hover {
      background: rgba(255, 0, 153, 0.25);
    }
  }

  &.el-button--warning {
    background: rgba(255, 165, 0, 0.15);
    border: 1px solid var(--neon-orange);
    color: var(--neon-orange);

    &:hover {
      background: rgba(255, 165, 0, 0.25);
    }
  }

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

:deep(.el-form) {
  .el-form-item__label {
    color: var(--text-primary);
    font-weight: 500;
  }

  .el-input__wrapper,
  .el-select .el-input__wrapper {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-light);
    box-shadow: none;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--border-medium);
    }

    &.is-focus {
      border-color: var(--neon-blue);
      box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
    }

    .el-input__inner {
      color: var(--text-primary);

      &::placeholder {
        color: var(--text-tertiary);
      }
    }
  }

  .el-slider {
    .el-slider__runway {
      background: var(--bg-tertiary);
    }

    .el-slider__bar {
      background: var(--gradient-neon);
    }

    .el-slider__button {
      border-color: var(--neon-blue);
    }
  }

  .el-switch {
    --el-switch-on-color: var(--neon-blue);
    --el-switch-off-color: var(--border-medium);

    &.is-checked .el-switch__core {
      box-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
  }
}
</style>
