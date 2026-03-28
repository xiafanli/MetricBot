<template>
  <div class="environment-management">
    <el-button type="primary" @click="handleCreate">
      <el-icon><Plus /></el-icon>
      创建环境
    </el-button>
    <el-table :data="environments" style="margin-top: 20px">
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
      <el-table-column label="操作" width="300">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="warning" v-if="!row.is_active" @click="handleActivate(row)">
            激活
          </el-button>
          <el-button size="small" type="danger" v-if="row.is_active" @click="handleDeactivate(row)">
            停止
          </el-button>
          <el-button size="small" type="info" @click="handleSyncToHosts(row)">
            同步到主机
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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

const loadEnvironments = async () => {
  try {
    const data = await api.getSimulationEnvironments()
    environments.value = data
  } catch (error) {
    ElMessage.error('加载环境列表失败')
  }
}

const handleCreate = () => {
  ElMessage.info('创建环境功能待实现')
}

const handleView = (row: Environment) => {
  ElMessage.info(`查看环境: ${row.name}`)
}

const handleEdit = (row: Environment) => {
  ElMessage.info(`编辑环境: ${row.name}`)
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

<style scoped>
.environment-management {
  padding: 20px;
}
</style>
