<template>
  <div class="alert-rules">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警规则管理</span>
          <el-button type="primary" @click="showCreateDialog">新建规则</el-button>
        </div>
      </template>

      <el-table :data="rules" v-loading="loading" stripe>
        <el-table-column prop="name" label="规则名称" min-width="150" />
        <el-table-column prop="datasource_type" label="数据源类型" width="120" />
        <el-table-column prop="metric_query" label="指标查询" min-width="200" show-overflow-tooltip />
        <el-table-column prop="condition_type" label="条件" width="100">
          <template #default="{ row }">
            {{ conditionMap[row.condition_type] || row.condition_type }}
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="severityMap[row.severity]?.type || 'info'">
              {{ severityMap[row.severity]?.label || row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evaluation_interval" label="评估间隔" width="100">
          <template #default="{ row }">
            {{ row.evaluation_interval }}秒
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="toggleEnabled(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showEditDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑规则' : '新建规则'" width="600px">
      <el-form :model="form" :rules="rules_form" ref="formRef" label-width="100px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="数据源" prop="datasource_id">
          <el-select v-model="form.datasource_id" placeholder="请选择数据源" style="width: 100%">
            <el-option
              v-for="ds in datasources"
              :key="ds.id"
              :label="ds.name"
              :value="ds.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数据源类型" prop="datasource_type">
          <el-select v-model="form.datasource_type" placeholder="请选择数据源类型" style="width: 100%">
            <el-option label="Prometheus" value="prometheus" />
            <el-option label="Zabbix" value="zabbix" />
          </el-select>
        </el-form-item>
        <el-form-item label="指标查询" prop="metric_query">
          <el-input v-model="form.metric_query" placeholder="请输入指标查询语句" />
        </el-form-item>
        <el-form-item label="条件类型" prop="condition_type">
          <el-select v-model="form.condition_type" placeholder="请选择条件类型" style="width: 100%">
            <el-option label="大于" value="greater_than" />
            <el-option label="小于" value="less_than" />
            <el-option label="等于" value="equal_to" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值" prop="threshold">
          <el-input-number v-model="form.threshold" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="严重程度" prop="severity">
          <el-select v-model="form.severity" placeholder="请选择严重程度" style="width: 100%">
            <el-option label="严重" value="critical" />
            <el-option label="警告" value="warning" />
            <el-option label="信息" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="评估间隔" prop="evaluation_interval">
          <el-input-number v-model="form.evaluation_interval" :min="10" :max="3600" style="width: 100%" />
          <span style="margin-left: 10px">秒</span>
        </el-form-item>
        <el-form-item label="启用" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  getAlertRules,
  createAlertRule,
  updateAlertRule,
  deleteAlertRule,
  type AlertRule,
  type AlertRuleCreate,
  type AlertRuleUpdate
} from '@/api/alert'
import { getDatasources, type Datasource } from '@/api/datasource'

const loading = ref(false)
const rules = ref<AlertRule[]>([])
const datasources = ref<Datasource[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const currentRuleId = ref<number | null>(null)

const form = reactive<AlertRuleCreate & { id?: number }>({
  name: '',
  description: '',
  datasource_id: 0,
  datasource_type: 'prometheus',
  metric_query: '',
  condition_type: 'greater_than',
  threshold: 0,
  severity: 'warning',
  evaluation_interval: 30,
  enabled: true
})

const rules_form: FormRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  datasource_id: [{ required: true, message: '请选择数据源', trigger: 'change' }],
  datasource_type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }],
  metric_query: [{ required: true, message: '请输入指标查询语句', trigger: 'blur' }],
  condition_type: [{ required: true, message: '请选择条件类型', trigger: 'change' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }]
}

const conditionMap: Record<string, string> = {
  greater_than: '大于',
  less_than: '小于',
  equal_to: '等于'
}

const severityMap: Record<string, { label: string; type: string }> = {
  critical: { label: '严重', type: 'danger' },
  warning: { label: '警告', type: 'warning' },
  info: { label: '信息', type: 'info' }
}

const loadRules = async () => {
  loading.value = true
  try {
    const data = await getAlertRules()
    rules.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载告警规则失败:', error)
    rules.value = []
  } finally {
    loading.value = false
  }
}

const loadDatasources = async () => {
  try {
    const data = await getDatasources()
    datasources.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载数据源失败:', error)
    datasources.value = []
  }
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  form.datasource_id = 0
  form.datasource_type = 'prometheus'
  form.metric_query = ''
  form.condition_type = 'greater_than'
  form.threshold = 0
  form.severity = 'warning'
  form.evaluation_interval = 30
  form.enabled = true
  form.id = undefined
  currentRuleId.value = null
}

const showCreateDialog = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const showEditDialog = (rule: AlertRule) => {
  isEdit.value = true
  currentRuleId.value = rule.id
  form.name = rule.name
  form.description = rule.description || ''
  form.datasource_id = rule.datasource_id
  form.datasource_type = rule.datasource_type
  form.metric_query = rule.metric_query
  form.condition_type = rule.condition_type
  form.threshold = rule.threshold || 0
  form.severity = rule.severity
  form.evaluation_interval = rule.evaluation_interval
  form.enabled = rule.enabled
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value && currentRuleId.value) {
        await updateAlertRule(currentRuleId.value, form as AlertRuleUpdate)
        ElMessage.success('更新成功')
      } else {
        await createAlertRule(form as AlertRuleCreate)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadRules()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const toggleEnabled = async (rule: AlertRule) => {
  try {
    await updateAlertRule(rule.id, { enabled: rule.enabled })
    ElMessage.success(rule.enabled ? '已启用' : '已禁用')
  } catch (error: any) {
    rule.enabled = !rule.enabled
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const handleDelete = async (rule: AlertRule) => {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '提示', {
      type: 'warning'
    })
    await deleteAlertRule(rule.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadRules()
  loadDatasources()
})
</script>

<style scoped lang="less">
.alert-rules {
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

  &.el-tag--danger {
    background: rgba(255, 0, 153, 0.15);
    color: var(--neon-pink);
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
    .el-input__wrapper {
      background: var(--bg-tertiary);
    }
  }

  .el-input-number {
    .el-input__wrapper {
      background: var(--bg-tertiary);
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
