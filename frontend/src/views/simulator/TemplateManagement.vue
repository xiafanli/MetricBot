<template>
  <div class="template-management">
    <div class="config-card">
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="指标模板" name="metrics">
          <div class="tab-content">
            <el-table :data="metricTemplates" style="width: 100%">
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
            <el-table :data="logTemplates" style="width: 100%">
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
}

.tab-content {
  padding: 20px 0;
}

:deep(.el-tabs--border-card) {
  background: transparent !important;
  border: none !important;
  height: 100%;
  display: flex;
  flex-direction: column;

  > .el-tabs__header {
    background: var(--bg-tertiary) !important;
    border-bottom: 1px solid var(--border-light) !important;
    margin: 0 !important;
  }

  .el-tabs__content {
    background: var(--bg-secondary) !important;
    padding: 24px !important;
    flex: 1;
    overflow: auto;
  }
}

:deep(.el-tabs--border-card .el-tabs__item) {
  color: var(--text-tertiary);
  font-weight: 500;

  &:hover:not(.is-active) {
    color: var(--neon-blue);
    background: rgba(0, 245, 255, 0.05) !important;
  }

  &.is-active {
    color: var(--neon-blue);
    background: var(--bg-secondary) !important;
    border-right-color: var(--border-light);
    border-left-color: var(--border-light);
  }
}

:deep(.el-tabs__nav-wrap::after) {
  display: none !important;
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

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;

  &.is-link {
    color: var(--neon-blue);
    background: transparent;
    border: none;

    &:hover {
      color: var(--neon-purple);
    }
  }
}
</style>
