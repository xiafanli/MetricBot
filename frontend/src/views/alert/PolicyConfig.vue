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
import axios from 'axios'

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
    const response = await axios.get('/api/v1/alerts/policies')
    policies.value = response.data
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
    if (isEdit.value) {
      await axios.put(`/api/v1/alerts/policies/${form.value.id}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/alerts/policies', form.value)
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
    await axios.put(`/api/v1/alerts/policies/${policy.id}`, { enabled: policy.enabled })
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
    await axios.delete(`/api/v1/alerts/policies/${policy.id}`)
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

<style scoped>
.policy-config {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>