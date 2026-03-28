<template>
  <div class="environment-management">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">环境管理</h2>
        <span class="page-desc">创建和管理模拟生产环境</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建环境
        </el-button>
      </div>
    </div>

    <div class="config-card">
      <el-table :data="environments" style="width: 100%" :header-cell-style="tableHeaderStyle" :cell-style="tableCellStyle">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="环境名称" width="200" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            <el-button type="warning" link size="small" v-if="!row.is_active" @click="handleActivate(row)">
              激活
            </el-button>
            <el-button type="danger" link size="small" v-if="row.is_active" @click="handleDeactivate(row)">
              停止
            </el-button>
            <el-button type="info" link size="small" @click="handleSyncToHosts(row)">
              同步到主机
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑环境' : '创建环境'"
      width="500px"
      class="config-dialog"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="config-form">
        <el-form-item label="环境名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入环境名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="Pushgateway地址" prop="pushgateway_url">
          <el-input v-model="form.pushgateway_url" placeholder="http://localhost:9091" />
        </el-form-item>
        <el-form-item label="日志路径" prop="log_path">
          <el-input v-model="form.log_path" placeholder="simulator/logs" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="cancel-btn" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api } from '@/api'

interface Environment {
  id: number
  name: string
  description: string
  is_active: boolean
  pushgateway_url: string
  log_path: string
  topology_data: any
  created_at: string
  updated_at: string
}

const environments = ref<Environment[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const currentId = ref<number | null>(null)

const form = ref({
  name: '',
  description: '',
  pushgateway_url: '',
  log_path: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  pushgateway_url: [{ required: true, message: '请输入Pushgateway地址', trigger: 'blur' }],
  log_path: [{ required: true, message: '请输入日志路径', trigger: 'blur' }]
}

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

const loadEnvironments = async () => {
  try {
    const data = await api.getSimulationEnvironments()
    environments.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载环境列表失败:', error)
    ElMessage.error('加载环境列表失败')
    environments.value = []
  }
}

const handleCreate = () => {
  isEdit.value = false
  currentId.value = null
  form.value = {
    name: '',
    description: '',
    pushgateway_url: 'http://localhost:9091',
    log_path: 'simulator/logs'
  }
  dialogVisible.value = true
}

const handleView = (row: Environment) => {
  ElMessage.info(`查看环境: ${row.name}`)
}

const handleEdit = (row: Environment) => {
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    name: row.name,
    description: row.description,
    pushgateway_url: row.pushgateway_url,
    log_path: row.log_path
  }
  dialogVisible.value = true
}

const handleDelete = async (row: Environment) => {
  try {
    await ElMessageBox.confirm(`确定要删除环境 "${row.name}" 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteSimulationEnvironment(row.id)
    ElMessage.success('删除成功')
    await loadEnvironments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value && currentId.value) {
          await api.updateSimulationEnvironment(currentId.value, form.value)
          ElMessage.success('更新成功')
        } else {
          await api.createSimulationEnvironment(form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        await loadEnvironments()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const handleActivate = async (row: Environment) => {
  try {
    await ElMessageBox.confirm(`确定要激活环境 "${row.name}" 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.activateSimulationEnvironment(row.id, {})
    ElMessage.success('环境激活成功')
    await loadEnvironments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('环境激活失败')
    }
  }
}

const handleDeactivate = async (row: Environment) => {
  try {
    await ElMessageBox.confirm(`确定要停止环境 "${row.name}" 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deactivateSimulationEnvironment(row.id)
    ElMessage.success('环境已停止')
    await loadEnvironments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停止环境失败')
    }
  }
}

const handleSyncToHosts = async (row: Environment) => {
  try {
    await ElMessageBox.confirm(`确定要将环境 "${row.name}" 同步到主机模型吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await api.syncEnvironmentToHosts(row.id)
    ElMessage.success('同步成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('同步失败')
    }
  }
}

onMounted(() => {
  loadEnvironments()
})
</script>

<style lang="less" scoped>
.environment-management {
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

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.config-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.config-dialog {
  :deep(.el-dialog__header) {
    background: rgba(0, 0, 0, 0.1);
    border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  }

  :deep(.el-dialog__title) {
    color: white;
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }

  :deep(.el-dialog__footer) {
    border-top: 1px solid rgba(255, 215, 0, 0.1);
    padding: 16px 24px;
  }
}

.config-form {
  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper),
  :deep(.el-textarea__inner) {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 215, 0, 0.2);
    box-shadow: none;
    transition: all 0.3s ease;

    &.is-focus {
      border-color: rgba(255, 215, 0, 0.5);
    }

    .el-input__inner {
      color: white;
    }
  }

  :deep(.el-textarea__inner) {
    color: white;
  }

  :deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.8);
  }
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 215, 0, 0.2) !important;
  color: rgba(255, 255, 255, 0.8) !important;

  &:hover {
    background: rgba(255, 215, 0, 0.1) !important;
    border-color: rgba(255, 215, 0, 0.4) !important;
    color: white !important;
  }
}
</style>
