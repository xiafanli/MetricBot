<template>
  <div class="logs-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">日志配置</h2>
        <span class="page-desc">配置和管理日志数据源</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加日志源
        </el-button>
      </div>
    </div>

    <div class="logs-list">
      <div 
        v-for="log in logsources" 
        :key="log.id" 
        class="log-card"
        :class="{ disabled: !log.enabled }"
      >
        <div class="log-header">
          <div class="log-icon" :style="{ background: log.iconBg }">
            <span class="icon-text">{{ log.icon }}</span>
          </div>
          <div class="log-info">
            <div class="log-name">{{ log.name }}</div>
            <div class="log-type">{{ log.type }}</div>
          </div>
          <div class="log-status">
            <el-tag :type="log.status === '正常' ? 'success' : 'info'" size="small">
              {{ log.status }}
            </el-tag>
          </div>
        </div>
        
        <div class="log-details">
          <div class="detail-item">
            <span class="detail-label">地址</span>
            <span class="detail-value">{{ log.url }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">索引/表</span>
            <span class="detail-value">{{ log.index_or_table }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">保留天数</span>
            <span class="detail-value">{{ log.retention_days }}天</span>
          </div>
        </div>
        
        <div class="log-actions">
          <el-button text size="small" @click="testConnection(log)">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
          <el-button text size="small" @click="editLog(log)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button text size="small" class="delete-btn" @click="deleteLog(log)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditing ? '编辑日志源' : '添加日志源'"
      width="500px"
    >
      <el-form :model="logForm" label-width="100px" class="config-form log-form">
        <el-form-item label="日志源名称" required>
          <el-input v-model="logForm.name" placeholder="请输入日志源名称" />
        </el-form-item>
        
        <el-form-item label="类型" required>
          <el-select v-model="logForm.type" placeholder="选择类型">
            <el-option label="Elasticsearch" value="Elasticsearch" />
            <el-option label="StarRocks" value="StarRocks" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="地址" required>
          <el-input v-model="logForm.url" placeholder="例如：http://localhost:9200" />
        </el-form-item>
        
        <el-form-item label="索引/表名">
          <el-input v-model="logForm.index_or_table" placeholder="索引名或表名" />
        </el-form-item>
        
        <el-form-item label="用户名">
          <el-input v-model="logForm.username" placeholder="用户名（可选）" />
        </el-form-item>
        
        <el-form-item label="密码">
          <el-input v-model="logForm.password" type="password" placeholder="密码（可选）" show-password />
        </el-form-item>
        
        <el-form-item label="保留天数">
          <el-input-number v-model="logForm.retention_days" :min="1" :max="365" />
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="logForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button class="cancel-btn" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLog" :loading="saving">保存</el-button>
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
  Connection
} from '@element-plus/icons-vue'
import { api } from '@/api'

interface LogSource {
  id: number
  name: string
  type: string
  icon: string
  iconBg: string
  url: string
  index_or_table: string
  status: string
  retention_days: number
  enabled: boolean
  created_at: string
  updated_at?: string
}

const dialogVisible = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const testing = ref(false)
const logsources = ref<LogSource[]>([])

const typeColors: Record<string, string> = {
  'Elasticsearch': 'linear-gradient(135deg, #fed10a 0%, #e5b800 100%)',
  'StarRocks': 'linear-gradient(135deg, #1f62e0 0%, #1a4db8 100%)'
}

const logForm = ref({
  id: 0,
  name: '',
  type: 'Elasticsearch',
  url: '',
  index_or_table: '',
  username: '',
  password: '',
  retention_days: 30,
  enabled: true
})

const loadLogSources = async () => {
  try {
    const data = await api.getLogSources()
    logsources.value = (data as LogSource[]).map(item => ({
      ...item,
      icon: item.type.charAt(0),
      iconBg: typeColors[item.type] || 'linear-gradient(135deg, #ffd700 0%, #f72585 100%)',
      status: item.enabled ? '已启用' : '已禁用'
    }))
  } catch (error) {
    ElMessage.error('加载日志源列表失败')
    console.error('Load log sources error:', error)
  }
}

const showAddDialog = () => {
  isEditing.value = false
  logForm.value = {
    id: 0,
    name: '',
    type: 'Elasticsearch',
    url: '',
    index_or_table: '',
    username: '',
    password: '',
    retention_days: 30,
    enabled: true
  }
  dialogVisible.value = true
}

const editLog = (log: LogSource) => {
  isEditing.value = true
  logForm.value = { 
    ...log, 
    username: '', 
    password: '' 
  }
  dialogVisible.value = true
}

const deleteLog = async (log: LogSource) => {
  try {
    await ElMessageBox.confirm(`确定要删除日志源 "${log.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteLogSource(log.id)
    ElMessage.success('日志源已删除')
    await loadLogSources()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete log source error:', error)
    }
  }
}

const testConnection = async (log: LogSource) => {
  testing.value = true
  try {
    const result = await api.testLogSourceConnection({
      name: log.name,
      type: log.type,
      url: log.url,
      index_or_table: log.index_or_table,
      username: log.username,
      password: log.password
    })
    
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
    console.error('Test connection error:', error)
  } finally {
    testing.value = false
  }
}

const saveLog = async () => {
  if (!logForm.value.name || !logForm.value.url) {
    ElMessage.warning('请填写必填项')
    return
  }

  saving.value = true
  try {
    if (isEditing.value) {
      await api.updateLogSource(logForm.value.id, logForm.value)
      ElMessage.success('日志源已更新')
    } else {
      await api.createLogSource(logForm.value)
      ElMessage.success('日志源已添加')
    }
    dialogVisible.value = false
    await loadLogSources()
  } catch (error) {
    ElMessage.error(isEditing.value ? '更新日志源失败' : '添加日志源失败')
    console.error('Save log source error:', error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadLogSources()
})
</script>

<style lang="less" scoped>
.logs-container {
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

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.log-card {
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
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

.log-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.log-icon {
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

.log-info {
  flex: 1;
}

.log-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.log-type {
  font-size: 13px;
  color: var(--text-tertiary);
}

.log-status {
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

.log-details {
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

.log-actions {
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

.log-form {
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

  :deep(.el-input-number) {
    width: 100%;

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
