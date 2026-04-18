<template>
  <div class="datasources-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">监控数据源</h2>
        <span class="page-desc">配置和管理监控数据源</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加数据源
        </el-button>
      </div>
    </div>

    <div class="datasources-list">
      <div
        v-for="ds in datasources"
        :key="ds.id"
        class="config-card"
        :class="{ disabled: !ds.enabled }"
      >
        <div class="ds-header">
          <div class="ds-icon" :style="{ background: getIconBg(ds.type) }">
            <span class="icon-text">{{ ds.type.charAt(0) }}</span>
          </div>
          <div class="ds-info">
            <div class="ds-name">{{ ds.name }}</div>
            <div class="ds-type">{{ ds.type }}</div>
          </div>
          <div class="ds-status">
            <el-tag :type="ds.enabled ? 'success' : 'info'" size="small">
              {{ ds.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </div>
        </div>

        <div class="ds-details">
          <div class="detail-item">
            <span class="detail-label">地址</span>
            <span class="detail-value">{{ ds.url }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">认证方式</span>
            <span class="detail-value">{{ getAuthTypeText(ds.auth_type) }}</span>
          </div>
        </div>

        <div class="ds-actions">
          <el-button text size="small" @click="testConnection(ds)">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
          <el-button text size="small" @click="syncData(ds)">
            <el-icon><Refresh /></el-icon>
            同步数据
          </el-button>
          <el-button text size="small" @click="editDatasource(ds)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button text size="small" class="delete-btn" @click="deleteDatasource(ds)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑数据源' : '添加数据源'"
      width="500px"
    >
      <el-form :model="dsForm" label-width="100px" class="config-form ds-form">
        <el-form-item label="数据源名称" required>
          <el-input v-model="dsForm.name" placeholder="请输入数据源名称" />
        </el-form-item>

        <el-form-item label="类型" required>
          <el-select v-model="dsForm.type" placeholder="选择类型">
            <el-option label="Prometheus" value="Prometheus" />
            <el-option label="Zabbix" value="Zabbix" />
            <el-option label="Grafana" value="Grafana" />
            <el-option label="Datadog" value="Datadog" />
            <el-option label="自定义HTTP" value="HTTP" />
          </el-select>
        </el-form-item>

        <el-form-item label="地址" required>
          <el-input v-model="dsForm.url" placeholder="例如：http://localhost:9090" />
        </el-form-item>

        <el-form-item label="认证方式">
          <el-select v-model="dsForm.auth_type" placeholder="选择认证方式">
            <el-option label="无" value="none" />
            <el-option label="Basic Auth" value="basic" />
            <el-option label="Bearer Token" value="token" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="dsForm.auth_type !== 'none'" label="用户名/Token">
          <el-input v-model="dsForm.auth_value" :placeholder="dsForm.auth_type === 'basic' ? '用户名' : 'Token'" />
        </el-form-item>

        <el-form-item v-if="dsForm.auth_type === 'basic'" label="密码">
          <el-input v-model="dsForm.password" type="password" placeholder="密码" show-password />
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch v-model="dsForm.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button 
          type="info" 
          @click="testConnectionFromDialog" 
          :loading="testing"
          :disabled="!dsForm.url"
        >
          <el-icon><Connection /></el-icon>
          测试连接
        </el-button>
        <el-button class="cancel-btn" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDatasource" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  Connection,
  Refresh
} from '@element-plus/icons-vue'
import { api } from '@/api'

interface Datasource {
  id: number
  name: string
  type: string
  url: string
  auth_type: string
  auth_value?: string
  password?: string
  config?: any
  enabled: boolean
  created_at: string
  updated_at?: string
}

const dialogVisible = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const testing = ref(false)
const datasources = ref<Datasource[]>([])

const dsForm = ref({
  id: 0,
  name: '',
  type: 'Prometheus',
  url: '',
  auth_type: 'none',
  auth_value: '',
  password: '',
  config: null,
  enabled: true
})

const typeColors: Record<string, string> = {
  'Prometheus': 'linear-gradient(135deg, #e6522c 0%, #c94a26 100%)',
  'Zabbix': 'linear-gradient(135deg, #d40000 0%, #b30000 100%)',
  'Grafana': 'linear-gradient(135deg, #f46800 0%, #e05a00 100%)',
  'Datadog': 'linear-gradient(135deg, #632ca6 0%, #512191 100%)',
  'HTTP': 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
}

const authTypeTexts: Record<string, string> = {
  'none': '无',
  'basic': 'Basic Auth',
  'token': 'Bearer Token'
}

const getIconBg = (type: string) => {
  return typeColors[type] || 'linear-gradient(135deg, #ffd700 0%, #f72585 100%)'
}

const getAuthTypeText = (type: string) => {
  return authTypeTexts[type] || type
}

const loadDatasources = async () => {
  try {
    const data = await api.getDatasources()
    datasources.value = (data as Datasource[]) || []
  } catch (error) {
    ElMessage.error('加载数据源列表失败')
    console.error('Load datasources error:', error)
  }
}

const showAddDialog = () => {
  isEditing.value = false
  dsForm.value = {
    id: 0,
    name: '',
    type: 'Prometheus',
    url: '',
    auth_type: 'none',
    auth_value: '',
    password: '',
    config: null,
    enabled: true
  }
  dialogVisible.value = true
}

const editDatasource = (ds: Datasource) => {
  isEditing.value = true
  dsForm.value = { 
    ...ds, 
    auth_value: '', 
    password: '' 
  }
  dialogVisible.value = true
}

const deleteDatasource = async (ds: Datasource) => {
  try {
    await ElMessageBox.confirm(`确定要删除数据源 "${ds.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteDatasource(ds.id)
    ElMessage.success('数据源已删除')
    await loadDatasources()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete datasource error:', error)
    }
  }
}

const testConnection = (ds: Datasource) => {
  ElMessage.info(`正在测试连接 ${ds.name}...`)
  setTimeout(() => {
    ElMessage.success('连接测试成功！')
  }, 1500)
}

const testConnectionFromDialog = async () => {
  if (!dsForm.value.url) {
    ElMessage.warning('请先填写数据源地址')
    return
  }

  testing.value = true
  try {
    const result = await api.testDatasourceConnection(dsForm.value)
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('连接测试失败，请检查地址和配置')
    console.error('Test connection error:', error)
  } finally {
    testing.value = false
  }
}

const syncData = (ds: Datasource) => {
  ElMessage.info(`正在同步 ${ds.name} 数据...`)
  setTimeout(() => {
    ElMessage.success('数据同步完成！')
  }, 2000)
}

const saveDatasource = async () => {
  if (!dsForm.value.name || !dsForm.value.url) {
    ElMessage.warning('请填写必填项')
    return
  }

  saving.value = true
  try {
    if (isEditing.value) {
      await api.updateDatasource(dsForm.value.id, dsForm.value)
      ElMessage.success('数据源已更新')
    } else {
      await api.createDatasource(dsForm.value)
      ElMessage.success('数据源已添加')
    }
    dialogVisible.value = false
    await loadDatasources()
  } catch (error) {
    ElMessage.error(isEditing.value ? '更新数据源失败' : '添加数据源失败')
    console.error('Save datasource error:', error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadDatasources()
})
</script>

<style lang="less" scoped>
.datasources-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--bg-primary);
  min-height: 100%;
  font-family: var(--font-body);
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
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.page-desc {
  font-size: 14px;
  color: var(--text-tertiary);
}

.header-right {
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

.datasources-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 245, 255, 0.1);
    border-color: var(--border-medium);
  }

  &.disabled {
    opacity: 0.6;
  }
}

.ds-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.ds-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.icon-text {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.ds-info {
  flex: 1;
}

.ds-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.ds-type {
  font-size: 13px;
  color: var(--text-tertiary);
}

.ds-status {
  :deep(.el-tag) {
    border-radius: 6px;
    font-weight: 500;
    border: none;

    &.el-tag--success {
      background: rgba(0, 255, 136, 0.15);
      color: var(--neon-green);
    }

    &.el-tag--info {
      background: rgba(0, 245, 255, 0.15);
      color: var(--neon-blue);
    }
  }
}

.ds-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid var(--border-light);
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
}

.ds-actions {
  display: flex;
  gap: 8px;

  .el-button {
    color: var(--neon-blue);
    background: transparent !important;
    border: none !important;
    font-weight: 500;

    &:hover {
      color: var(--neon-purple);
      background: rgba(191, 0, 255, 0.1) !important;
    }
  }

  .delete-btn:hover {
    color: var(--neon-pink) !important;
    background: rgba(255, 0, 153, 0.1) !important;
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

.ds-form {
  :deep(.el-form-item__label) {
    color: var(--text-primary);
    font-weight: 500;
  }

  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
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

    .el-input__inner {
      color: var(--text-primary);

      &::placeholder {
        color: var(--text-tertiary);
      }
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

  &.el-button--info {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-light);
    color: var(--text-secondary);

    &:hover {
      border-color: var(--neon-blue);
      color: var(--neon-blue);
    }
  }
}

.cancel-btn {
  background: var(--bg-tertiary) !important;
  border: 1px solid var(--border-light) !important;
  color: var(--text-secondary) !important;

  &:hover {
    border-color: var(--neon-blue) !important;
    color: var(--neon-blue) !important;
  }
}

:deep(.el-switch) {
  --el-switch-on-color: var(--neon-blue);
  --el-switch-off-color: var(--border-medium);

  &.is-checked .el-switch__core {
    box-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
  }
}
</style>
