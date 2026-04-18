<template>
  <div class="policy-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>聚合策略配置</span>
          <el-button type="primary" @click="openCreateDialog">新增策略</el-button>
        </div>
      </template>

      <el-table :data="policies" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="策略名称" min-width="150" />
        <el-table-column prop="strategy" label="策略类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getStrategyTagType(row.strategy)">
              {{ getStrategyLabel(row.strategy) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="window_seconds" label="时间窗口(秒)" width="130" />
        <el-table-column prop="max_depth" label="最大深度" width="100" />
        <el-table-column prop="similarity_threshold" label="相似度阈值" width="120">
          <template #default="{ row }">
            {{ (row.similarity_threshold * 100).toFixed(0) }}%
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="togglePolicy(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editPolicy(row)">编辑</el-button>
            <el-button type="danger" link @click="deletePolicy(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑策略' : '新增策略'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型" prop="strategy">
          <el-select v-model="form.strategy" placeholder="请选择策略类型">
            <el-option label="时间窗口" value="time_window" />
            <el-option label="拓扑关联" value="topology" />
            <el-option label="语义相似" value="semantic" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间窗口(秒)" prop="window_seconds" v-if="form.strategy === 'time_window'">
          <el-input-number v-model="form.window_seconds" :min="30" :max="3600" :step="30" />
        </el-form-item>
        <el-form-item label="分组字段" prop="group_by_fields" v-if="form.strategy === 'time_window'">
          <el-select v-model="form.group_by_fields" multiple placeholder="选择分组字段">
            <el-option label="规则ID" value="rule_id" />
            <el-option label="严重级别" value="severity" />
            <el-option label="主机" value="host" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大拓扑深度" prop="max_depth" v-if="form.strategy === 'topology'">
          <el-input-number v-model="form.max_depth" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="相似度阈值" prop="similarity_threshold" v-if="form.strategy === 'semantic'">
          <el-slider v-model="form.similarity_threshold" :min="0.5" :max="1" :step="0.05" show-stops />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import apiClient from '@/api'

interface Policy {
  id: number
  name: string
  strategy: string
  window_seconds: number
  group_by_fields: string[]
  max_depth: number
  similarity_threshold: number
  enabled: boolean
  created_at: string
}

const policies = ref<Policy[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = ref({
  id: 0,
  name: '',
  strategy: 'time_window',
  window_seconds: 300,
  group_by_fields: [] as string[],
  max_depth: 3,
  similarity_threshold: 0.8,
  enabled: true,
})

const rules = {
  name: [{ required: true, message: '请输入策略名称', trigger: 'blur' }],
  strategy: [{ required: true, message: '请选择策略类型', trigger: 'change' }],
}

const loadPolicies = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/alerts/policies')
    policies.value = response
  } catch (error) {
    ElMessage.error('加载策略失败')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  form.value = {
    id: 0,
    name: '',
    strategy: 'time_window',
    window_seconds: 300,
    group_by_fields: [],
    max_depth: 3,
    similarity_threshold: 0.8,
    enabled: true,
  }
  dialogVisible.value = true
}

const editPolicy = (policy: Policy) => {
  isEdit.value = true
  form.value = {
    id: policy.id,
    name: policy.name,
    strategy: policy.strategy,
    window_seconds: policy.window_seconds,
    group_by_fields: policy.group_by_fields || [],
    max_depth: policy.max_depth,
    similarity_threshold: policy.similarity_threshold,
    enabled: policy.enabled,
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    const submitData = { ...form.value }
    if (!isEdit.value) {
      delete submitData.id
    }
    if (isEdit.value) {
      await apiClient.put(`/alerts/policies/${form.value.id}`, submitData)
      ElMessage.success('更新成功')
    } else {
      await apiClient.post('/alerts/policies', submitData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadPolicies()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const togglePolicy = async (policy: Policy) => {
  try {
    await apiClient.put(`/alerts/policies/${policy.id}`, { enabled: policy.enabled })
    ElMessage.success('状态已更新')
  } catch (error) {
    ElMessage.error('更新失败')
    loadPolicies()
  }
}

const deletePolicy = async (policy: Policy) => {
  try {
    await ElMessageBox.confirm(`确定删除策略 "${policy.name}" 吗?`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await apiClient.delete(`/alerts/policies/${policy.id}`)
    ElMessage.success('删除成功')
    loadPolicies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getStrategyTagType = (strategy: string) => {
  const types: Record<string, string> = {
    time_window: 'primary',
    topology: 'success',
    semantic: 'warning',
  }
  return types[strategy] || 'info'
}

const getStrategyLabel = (strategy: string) => {
  const labels: Record<string, string> = {
    time_window: '时间窗口',
    topology: '拓扑关联',
    semantic: '语义相似',
  }
  return labels[strategy] || strategy
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

onMounted(() => {
  loadPolicies()
})
</script>

<style scoped lang="less">
.policy-config {
  padding: 24px;
  background: var(--bg-primary);
  min-height: 100%;
  font-family: var(--font-body);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  span {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .el-button--primary {
    background: var(--gradient-neon);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 20px;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
  }
}

:deep(.el-card) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);

  .el-card__header {
    background: transparent;
    border-bottom: 1px solid var(--border-light);
    padding: 16px 20px;
  }
}

:deep(.el-table) {
  background: transparent;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-tertiary);
  --el-table-row-hover-bg-color: rgba(0, 245, 255, 0.05);
  --el-table-border-color: var(--border-light);

  th.el-table__cell {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  td.el-table__cell {
    color: var(--text-secondary);
  }

  .el-table__row:hover td {
    background: rgba(0, 245, 255, 0.05);
  }
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  border: none;

  &.el-tag--primary {
    background: rgba(0, 245, 255, 0.15);
    color: var(--neon-blue);
  }

  &.el-tag--success {
    background: rgba(0, 255, 136, 0.15);
    color: var(--neon-green);
  }

  &.el-tag--warning {
    background: rgba(255, 102, 0, 0.15);
    color: var(--neon-orange);
  }

  &.el-tag--info {
    background: rgba(0, 245, 255, 0.15);
    color: var(--neon-blue);
  }
}

:deep(.el-switch) {
  --el-switch-on-color: var(--neon-blue);
  --el-switch-off-color: var(--border-medium);

  &.is-checked .el-switch__core {
    box-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
  }
}

:deep(.el-button--primary.is-link) {
  color: var(--neon-blue);
  font-weight: 500;

  &:hover {
    color: var(--neon-purple);
  }
}

:deep(.el-button--danger.is-link) {
  color: var(--neon-pink);
  font-weight: 500;

  &:hover {
    color: #ff3399;
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

  .el-input__wrapper {
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
  }

  .el-input__inner {
    color: var(--text-primary);

    &::placeholder {
      color: var(--text-tertiary);
    }
  }

  .el-select {
    width: 100%;

    .el-input__wrapper {
      background: var(--bg-tertiary);
    }
  }

  .el-input-number {
    width: 100%;

    .el-input__wrapper {
      background: var(--bg-tertiary);
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
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;

  &.el-button--default {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-light);
    color: var(--text-secondary);

    &:hover {
      border-color: var(--neon-blue);
      color: var(--neon-blue);
    }
  }

  &.el-button--primary {
    background: var(--gradient-neon);
    border: none;
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
  }
}
</style>