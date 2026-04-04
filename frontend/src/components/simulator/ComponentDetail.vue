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
        <el-descriptions :column="1" border v-if="component.properties && Object.keys(component.properties).length > 0">
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
    relatedComponents.value = []
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
  if (typeof value === 'object') {
    return JSON.stringify(value)
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
