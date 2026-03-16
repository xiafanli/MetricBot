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
            <el-tag :type="log.status === '正常' ? 'success' : 'danger'" size="small">
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
            <span class="detail-value">{{ log.index }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">日志量</span>
            <span class="detail-value">{{ log.volume }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">保留天数</span>
            <span class="detail-value">{{ log.retention }}天</span>
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
            <el-option label="ClickHouse" value="ClickHouse" />
            <el-option label="StarRocks" value="StarRocks" />
            <el-option label="Loki" value="Loki" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="地址" required>
          <el-input v-model="logForm.url" placeholder="例如：http://localhost:9200" />
        </el-form-item>
        
        <el-form-item label="索引/表名">
          <el-input v-model="logForm.index" placeholder="索引或表名" />
        </el-form-item>
        
        <el-form-item label="用户名">
          <el-input v-model="logForm.username" placeholder="用户名（可选）" />
        </el-form-item>
        
        <el-form-item label="密码">
          <el-input v-model="logForm.password" type="password" placeholder="密码（可选）" show-password />
        </el-form-item>
        
        <el-form-item label="保留天数">
          <el-input-number v-model="logForm.retention" :min="1" :max="365" />
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="logForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLog">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  Connection
} from '@element-plus/icons-vue'

interface LogSource {
  id: number
  name: string
  type: string
  icon: string
  iconBg: string
  url: string
  index: string
  status: string
  volume: string
  retention: number
  enabled: boolean
}

const dialogVisible = ref(false)
const isEditing = ref(false)

const logsources = ref<LogSource[]>([
  {
    id: 1,
    name: '应用日志 ES',
    type: 'Elasticsearch',
    icon: 'E',
    iconBg: 'linear-gradient(135deg, #fed10a 0%, #e5b800 100%)',
    url: 'http://es.prod:9200',
    index: 'app-logs-*',
    status: '正常',
    volume: '50GB/天',
    retention: 30,
    enabled: true
  },
  {
    id: 2,
    name: '系统日志 ClickHouse',
    type: 'ClickHouse',
    icon: 'C',
    iconBg: 'linear-gradient(135deg, #ffcc00 0%, #ff9500 100%)',
    url: 'http://ck.prod:8123',
    index: 'sys_logs',
    status: '正常',
    volume: '120GB/天',
    retention: 90,
    enabled: true
  },
  {
    id: 3,
    name: 'Kubernetes日志 Loki',
    type: 'Loki',
    icon: 'L',
    iconBg: 'linear-gradient(135deg, #1f62e0 0%, #1a4db8 100%)',
    url: 'http://loki:3100',
    index: 'k8s-logs',
    status: '正常',
    volume: '80GB/天',
    retention: 15,
    enabled: true
  }
])

const logForm = ref({
  id: 0,
  name: '',
  type: 'Elasticsearch',
  url: '',
  index: '',
  username: '',
  password: '',
  retention: 30,
  enabled: true
})

const showAddDialog = () => {
  isEditing.value = false
  logForm.value = {
    id: 0,
    name: '',
    type: 'Elasticsearch',
    url: '',
    index: '',
    username: '',
    password: '',
    retention: 30,
    enabled: true
  }
  dialogVisible.value = true
}

const editLog = (log: LogSource) => {
  isEditing.value = true
  logForm.value = { ...log, username: '', password: '' }
  dialogVisible.value = true
}

const deleteLog = async (log: LogSource) => {
  try {
    await ElMessageBox.confirm(`确定要删除日志源 "${log.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = logsources.value.findIndex(l => l.id === log.id)
    if (index > -1) {
      logsources.value.splice(index, 1)
      ElMessage.success('日志源已删除')
    }
  } catch {
    // 取消删除
  }
}

const testConnection = (log: LogSource) => {
  ElMessage.info(`正在测试连接 ${log.name}...`)
  setTimeout(() => {
    ElMessage.success('连接测试成功！')
  }, 1500)
}

const saveLog = () => {
  if (!logForm.value.name || !logForm.value.url) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (isEditing.value) {
    const index = logsources.value.findIndex(l => l.id === logForm.value.id)
    if (index > -1) {
      logsources.value[index] = {
        ...logsources.value[index],
        ...logForm.value,
        icon: logForm.value.type.charAt(0)
      }
    }
    ElMessage.success('日志源已更新')
  } else {
    logsources.value.push({
      id: Date.now(),
      name: logForm.value.name,
      type: logForm.value.type,
      icon: logForm.value.type.charAt(0),
      iconBg: 'linear-gradient(135deg, #ffd700 0%, #f72585 100%)',
      url: logForm.value.url,
      index: logForm.value.index,
      status: '正常',
      volume: '0',
      retention: logForm.value.retention,
      enabled: logForm.value.enabled
    })
    ElMessage.success('日志源已添加')
  }
  
  dialogVisible.value = false
}
</script>

<style lang="less" scoped>
.logs-container {
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

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.log-card {
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  padding: 20px;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(255, 215, 0, 0.3);
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
}

.icon-text {
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.log-info {
  flex: 1;
}

.log-name {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.log-type {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.log-details {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid rgba(255, 215, 0, 0.1);
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.detail-value {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.log-actions {
  display: flex;
  gap: 8px;

  .el-button {
    color: rgba(255, 215, 0, 0.6);
    background: transparent !important;
    border: none !important;

    &:hover {
      color: #ffd700;
      background: rgba(255, 215, 0, 0.1) !important;
    }
  }

  .delete-btn:hover {
    color: #ef4444 !important;
    background: rgba(239, 68, 68, 0.1) !important;
  }
}

.log-form {
  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 215, 0, 0.2);
    box-shadow: none;

    .el-input__inner {
      color: white;
    }
  }

  :deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.8);
  }
}
</style>
