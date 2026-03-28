<template>
  <div class="fault-management">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">故障管理</h2>
        <span class="page-desc">管理故障场景和故障实例</span>
      </div>
    </div>

    <div class="config-card">
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="故障场景" name="scenarios">
          <div class="tab-content">
            <el-table :data="faultScenarios" style="width: 100%" :header-cell-style="tableHeaderStyle" :cell-style="tableCellStyle">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="name" label="故障名称" width="150" />
              <el-table-column prop="fault_type" label="故障类型" width="150" />
              <el-table-column prop="target_component_type" label="目标组件" width="120" />
              <el-table-column prop="probability" label="触发概率" width="100">
                <template #default="{ row }">
                  {{ (row.probability * 100).toFixed(2) }}%
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.is_enabled ? 'success' : 'info'">
                    {{ row.is_enabled ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small">编辑</el-button>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="故障实例" name="instances">
          <div class="tab-content">
            <el-table :data="faultInstances" style="width: 100%" :header-cell-style="tableHeaderStyle" :cell-style="tableCellStyle">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="scenario_id" label="场景ID" width="100" />
              <el-table-column prop="component_id" label="组件ID" width="100" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'danger' : 'success'">
                    {{ row.status === 'active' ? '进行中' : row.status === 'pending' ? '待处理' : '已恢复' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="start_time" label="触发时间" width="180" />
              <el-table-column prop="end_time" label="恢复时间" width="180" />
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
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

onMounted(() => {
  loadFaultScenarios()
  loadFaultInstances()
})
</script>

<style lang="less" scoped>
.fault-management {
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

.config-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.tab-content {
  padding: 20px 0;
}

:deep(.el-tabs--border-card) {
  background: transparent !important;
  border: none !important;

  > .el-tabs__header {
    background: rgba(0, 0, 0, 0.3) !important;
    border-bottom: 1px solid rgba(255, 215, 0, 0.15) !important;
    margin: 0 !important;
  }

  .el-tabs__content {
    background: rgba(0, 0, 0, 0.2) !important;
    padding: 24px !important;
  }
}

:deep(.el-tabs--border-card .el-tabs__item) {
  &:hover:not(.is-active) {
    background: rgba(0, 0, 0, 0.2) !important;
  }

  &.is-active {
    background: rgba(0, 0, 0, 0.3) !important;
  }
}

:deep(.el-tabs__nav-wrap::after) {
  display: none !important;
}
</style>
