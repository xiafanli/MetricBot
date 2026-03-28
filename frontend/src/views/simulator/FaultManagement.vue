<template>
  <div class="fault-management">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="故障场景" name="scenarios">
        <div>
          <el-table :data="faultScenarios" style="margin-top: 20px">
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
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="故障实例" name="instances">
        <div>
          <el-table :data="faultInstances" style="margin-top: 20px">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="scenario_name" label="故障场景" width="150" />
            <el-table-column prop="component_name" label="受影响组件" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'danger' : 'success'">
                  {{ row.is_active ? '进行中' : '已恢复' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="triggered_at" label="触发时间" width="180" />
            <el-table-column prop="resolved_at" label="恢复时间" width="180" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
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
  scenario_name: string
  component_name: string
  is_active: boolean
  triggered_at: string
  resolved_at: string | null
}

const activeTab = ref('scenarios')
const faultScenarios = ref<FaultScenario[]>([])
const faultInstances = ref<FaultInstance[]>([])

const loadFaultScenarios = async () => {
  try {
    const data = await api.getFaultScenarios()
    faultScenarios.value = data
  } catch (error) {
    ElMessage.error('加载故障场景失败')
  }
}

const loadFaultInstances = async () => {
  try {
    const data = await api.getFaultInstances()
    faultInstances.value = data
  } catch (error) {
    ElMessage.error('加载故障实例失败')
  }
}

onMounted(() => {
  loadFaultScenarios()
  loadFaultInstances()
})
</script>

<style scoped>
.fault-management {
  padding: 20px;
}
</style>
