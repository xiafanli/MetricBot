<template>
  <div class="template-management">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">模板管理</h2>
        <span class="page-desc">管理指标和日志生成模板</span>
      </div>
    </div>

    <div class="config-card">
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="指标模板" name="metrics">
          <div class="tab-content">
            <el-table :data="metricTemplates" style="width: 100%" :header-cell-style="tableHeaderStyle" :cell-style="tableCellStyle">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="component_type" label="组件类型" width="120" />
              <el-table-column prop="metric_name" label="指标名称" width="150" />
              <el-table-column prop="metric_type" label="指标类型" width="100" />
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column prop="base_value" label="基准值" width="100" />
              <el-table-column prop="unit" label="单位" width="80" />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small">编辑</el-button>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="日志模板" name="logs">
          <div class="tab-content">
            <el-table :data="logTemplates" style="width: 100%" :header-cell-style="tableHeaderStyle" :cell-style="tableCellStyle">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="component_type" label="组件类型" width="150" />
              <el-table-column prop="log_format" label="日志格式" width="120" />
              <el-table-column prop="template" label="模板内容" show-overflow-tooltip />
              <el-table-column prop="frequency" label="频率(秒)" width="100" />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small">编辑</el-button>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-table-column>
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
  log_levels: any
  template: string
  frequency: number
  created_at: string
  updated_at: string
}

const activeTab = ref('metrics')
const metricTemplates = ref<MetricTemplate[]>([])
const logTemplates = ref<LogTemplate[]>([])

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

const loadMetricTemplates = async () => {
  try {
    const data = await api.getMetricTemplates()
    metricTemplates.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载指标模板失败:', error)
    ElMessage.error('加载指标模板失败')
    metricTemplates.value = []
  }
}

const loadLogTemplates = async () => {
  try {
    const data = await api.getLogTemplates()
    logTemplates.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载日志模板失败:', error)
    ElMessage.error('加载日志模板失败')
    logTemplates.value = []
  }
}

onMounted(() => {
  loadMetricTemplates()
  loadLogTemplates()
})
</script>

<style lang="less" scoped>
.template-management {
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
