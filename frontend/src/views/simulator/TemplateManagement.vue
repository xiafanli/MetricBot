<template>
  <div class="template-management">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="指标模板" name="metrics">
        <div>
          <el-table :data="metricTemplates" style="margin-top: 20px">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="component_type" label="组件类型" width="120" />
            <el-table-column prop="metric_name" label="指标名称" width="150" />
            <el-table-column prop="metric_type" label="指标类型" width="100" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="base_value" label="基准值" width="100" />
            <el-table-column prop="unit" label="单位" width="80" />
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="日志模板" name="logs">
        <div>
          <el-table :data="logTemplates" style="margin-top: 20px">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="component_type" label="组件类型" width="150" />
            <el-table-column prop="log_format" label="日志格式" width="120" />
            <el-table-column prop="frequency" label="频率(秒)" width="100" />
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

interface MetricTemplate {
  id: number
  component_type: string
  metric_name: string
  metric_type: string
  description: string
  min_value: number
  max_value: number
  base_value: number
  fluctuation: number
  unit: string
  created_at: string
  updated_at: string
}

interface LogTemplate {
  id: number
  component_type: string
  log_format: string
  frequency: number
  created_at: string
  updated_at: string
}

const activeTab = ref('metrics')
const metricTemplates = ref<MetricTemplate[]>([])
const logTemplates = ref<LogTemplate[]>([])

const loadMetricTemplates = async () => {
  try {
    const data = await api.getMetricTemplates()
    metricTemplates.value = data
  } catch (error) {
    ElMessage.error('加载指标模板失败')
  }
}

const loadLogTemplates = async () => {
  try {
    const data = await api.getLogTemplates()
    logTemplates.value = data
  } catch (error) {
    ElMessage.error('加载日志模板失败')
  }
}

onMounted(() => {
  loadMetricTemplates()
  loadLogTemplates()
})
</script>

<style scoped>
.template-management {
  padding: 20px;
}
</style>
