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
          <div class="ds-icon" :style="{ background: ds.iconBg }">
            <span class="icon-text">{{ ds.icon }}</span>
          </div>
          <div class="ds-info">
            <div class="ds-name">{{ ds.name }}</div>
            <div class="ds-type">{{ ds.type }}</div>
          </div>
          <div class="ds-status">
            <el-tag :type="ds.status === '正常' ? 'success' : 'danger'" size="small">
              {{ ds.status }}
            </el-tag>
          </div>
        </div>

        <div class="ds-details">
          <div class="detail-item">
            <span class="detail-label">地址</span>
            <span class="detail-value">{{ ds.url }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">指标数量</span>
            <span class="detail-value">{{ ds.metricCount }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">最后同步</span>
            <span class="detail-value">{{ ds.lastSync }}</span>
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
          <el-select v-model="dsForm.authType" placeholder="选择认证方式">
            <el-option label="无" value="none" />
            <el-option label="Basic Auth" value="basic" />
            <el-option label="Bearer Token" value="bearer" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="dsForm.authType !== 'none'" label="用户名/Token">
          <el-input v-model="dsForm.authValue" :placeholder="dsForm.authType === 'basic' ? '用户名' : 'Token'" />
        </el-form-item>

        <el-form-item v-if="dsForm.authType === 'basic'" label="密码">
          <el-input v-model="dsForm.password" type="password" placeholder="密码" show-password />
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch v-model="dsForm.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDatasource">保存</el-button>
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
  Connection,
  Refresh
} from '@element-plus/icons-vue'

interface Datasource {
  id: number
  name: string
  type: string
  icon: string
  iconBg: string
  url: string
  status: string
  metricCount: number
  lastSync: string
  enabled: boolean
}

const dialogVisible = ref(false)
const isEditing = ref(false)

const datasources = ref<Datasource[]>([
  {
    id: 1,
    name: '生产环境 Prometheus',
    type: 'Prometheus',
    icon: 'P',
    iconBg: 'linear-gradient(135deg, #e6522c 0%, #c94a26 100%)',
    url: 'http://prometheus.prod:9090',
    status: '正常',
    metricCount: 1234,
    lastSync: '2分钟前',
    enabled: true
  },
  {
    id: 2,
    name: '测试环境 Zabbix',
    type: 'Zabbix',
    icon: 'Z',
    iconBg: 'linear-gradient(135deg, #d40000 0%, #b30000 100%)',
    url: 'http://zabbix.test:8080',
    status: '正常',
    metricCount: 856,
    lastSync: '5分钟前',
    enabled: true
  },
  {
    id: 3,
    name: '监控大盘 Grafana',
    type: 'Grafana',
    icon: 'G',
    iconBg: 'linear-gradient(135deg, #f46800 0%, #e05a00 100%)',
    url: 'http://grafana:3000',
    status: '异常',
    metricCount: 0,
    lastSync: '1小时前',
    enabled: false
  }
])

const dsForm = ref({
  id: 0,
  name: '',
  type: 'Prometheus',
  url: '',
  authType: 'none',
  authValue: '',
  password: '',
  enabled: true
})

const showAddDialog = () => {
  isEditing.value = false
  dsForm.value = {
    id: 0,
    name: '',
    type: 'Prometheus',
    url: '',
    authType: 'none',
    authValue: '',
    password: '',
    enabled: true
  }
  dialogVisible.value = true
}

const editDatasource = (ds: Datasource) => {
  isEditing.value = true
  dsForm.value = { ...ds, authType: 'none', authValue: '', password: '' }
  dialogVisible.value = true
}

const deleteDatasource = async (ds: Datasource) => {
  try {
    await ElMessageBox.confirm(`确定要删除数据源 "${ds.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = datasources.value.findIndex(d => d.id === ds.id)
    if (index > -1) {
      datasources.value.splice(index, 1)
      ElMessage.success('数据源已删除')
    }
  } catch {
    // 取消删除
  }
}

const testConnection = (ds: Datasource) => {
  ElMessage.info(`正在测试连接 ${ds.name}...`)
  setTimeout(() => {
    ElMessage.success('连接测试成功！')
  }, 1500)
}

const syncData = (ds: Datasource) => {
  ElMessage.info(`正在同步 ${ds.name} 数据...`)
  setTimeout(() => {
    ElMessage.success('数据同步完成！')
  }, 2000)
}

const saveDatasource = () => {
  if (!dsForm.value.name || !dsForm.value.url) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (isEditing.value) {
    const index = datasources.value.findIndex(d => d.id === dsForm.value.id)
    if (index > -1) {
      datasources.value[index] = {
        ...datasources.value[index],
        name: dsForm.value.name,
        type: dsForm.value.type,
        url: dsForm.value.url,
        enabled: dsForm.value.enabled
      }
    }
    ElMessage.success('数据源已更新')
  } else {
    datasources.value.push({
      id: Date.now(),
      name: dsForm.value.name,
      type: dsForm.value.type,
      icon: dsForm.value.type.charAt(0),
      iconBg: 'linear-gradient(135deg, #ffd700 0%, #f72585 100%)',
      url: dsForm.value.url,
      status: '正常',
      metricCount: 0,
      lastSync: '未同步',
      enabled: dsForm.value.enabled
    })
    ElMessage.success('数据源已添加')
  }
  
  dialogVisible.value = false
}
</script>

<style lang="less" scoped>
.datasources-container {
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

.datasources-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
}

.icon-text {
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.ds-info {
  flex: 1;
}

.ds-name {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.ds-type {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.ds-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid rgba(255, 215, 0, 0.1);
  border-bottom: 1px solid rgba(255, 215, 0, 1);
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

.ds-actions {
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

.ds-form {
  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
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

  :deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.8);
  }
}
</style>
