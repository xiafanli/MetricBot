<template>
  <div class="hosts-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">主机模型</h2>
        <span class="page-desc">管理和维护主机信息</span>
      </div>
      <div class="header-right">
        <el-button type="success" @click="showSyncDialog">
          <el-icon><Prometheus /></el-icon>
          从 Prometheus 同步
        </el-button>
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加主机
        </el-button>
      </div>
    </div>

    <div class="config-card">
      <el-table
        :data="filteredHosts"
        style="width: 100%"
        :header-cell-style="tableHeaderStyle"
        :cell-style="tableCellStyle"
      >
        <el-table-column prop="name" label="主机名" min-width="150">
          <template #default="{ row }">
            <div class="hostname-cell">
              <el-icon :class="['status-dot', row.enabled ? 'online' : 'offline']"><Monitor /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column prop="os" label="操作系统" width="140">
          <template #default="{ row }">
            {{ row.os }} {{ row.os_version }}
          </template>
        </el-table-column>
        <el-table-column prop="cpu_cores" label="CPU核心" width="100" />
        <el-table-column prop="memory_gb" label="内存(GB)" width="100" />
        <el-table-column prop="disk_gb" label="磁盘(GB)" width="100" />
        <el-table-column prop="tags" label="标签" width="180">
          <template #default="{ row }">
            <el-tag v-for="tag in (row.tags || []).slice(0, 2)" :key="tag" size="small" class="tag-item">
              {{ tag }}
            </el-tag>
            <span v-if="(row.tags || []).length > 2" class="more-tags">+{{ (row.tags || []).length - 2 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="row.from_type === 'prometheus' ? 'success' : 'info'">
              {{ row.from_type || 'manual' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editHost(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="deleteHost(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditing ? '编辑主机' : '添加主机'"
      width="500px"
    >
      <el-form :model="hostForm" label-width="100px" class="config-form host-form">
        <el-form-item label="主机名" required>
          <el-input v-model="hostForm.name" placeholder="请输入主机名" />
        </el-form-item>
        
        <el-form-item label="IP地址" required>
          <el-input v-model="hostForm.ip" placeholder="请输入IP地址" />
        </el-form-item>
        
        <el-form-item label="主机名(系统)">
          <el-input v-model="hostForm.hostname" placeholder="例如：server-01" />
        </el-form-item>
        
        <el-form-item label="操作系统">
          <el-input v-model="hostForm.os" placeholder="例如：Ubuntu" />
        </el-form-item>
        
        <el-form-item label="系统版本">
          <el-input v-model="hostForm.os_version" placeholder="例如：22.04" />
        </el-form-item>
        
        <el-form-item label="CPU核心数">
          <el-input-number v-model="hostForm.cpu_cores" :min="1" :max="256" />
        </el-form-item>
        
        <el-form-item label="内存(GB)">
          <el-input-number v-model="hostForm.memory_gb" :min="1" :max="1024" />
        </el-form-item>
        
        <el-form-item label="磁盘(GB)">
          <el-input-number v-model="hostForm.disk_gb" :min="1" :max="10000" />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select v-model="hostForm.tags" multiple placeholder="选择标签" allow-create>
            <el-option label="生产环境" value="生产环境" />
            <el-option label="测试环境" value="测试环境" />
            <el-option label="Web服务" value="Web服务" />
            <el-option label="数据库" value="数据库" />
            <el-option label="缓存" value="缓存" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="hostForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button class="cancel-btn" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveHost" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog 
      v-model="syncDialogVisible" 
      title="从 Prometheus 同步"
      width="600px"
    >
      <el-form :model="syncForm" label-width="120px" class="config-form">
        <el-form-item label="选择数据源" required>
          <el-select v-model="syncForm.datasource_id" placeholder="选择 Prometheus 数据源">
            <el-option 
              v-for="ds in prometheusDatasources" 
              :key="ds.id" 
              :label="ds.name" 
              :value="ds.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="指标名" required>
          <el-input v-model="syncForm.metric" placeholder="例如：node_cpu_seconds_total" />
        </el-form-item>
        
        <el-form-item label="标签名" required>
          <el-input v-model="syncForm.label" placeholder="例如：instance" />
        </el-form-item>
      </el-form>
      
      <div v-if="syncPreview.length > 0" class="preview-section">
        <div class="preview-title">预览（最多显示 10 条）</div>
        <div class="preview-list">
          <el-tag v-for="item in syncPreview" :key="item" class="preview-tag">
            {{ item }}
          </el-tag>
        </div>
        <div class="preview-total">共 {{ syncPreviewTotal }} 条</div>
      </div>
      
      <template #footer>
        <el-button @click="cancelSync">取消</el-button>
        <el-button @click="doPreview" :loading="previewing">预览</el-button>
        <el-button 
          v-if="syncPreview.length > 0" 
          type="primary" 
          @click="doImport" 
          :loading="importing"
        >
          导入 {{ syncPreviewTotal }} 条
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Monitor,
  Prometheus
} from '@element-plus/icons-vue'
import { api } from '@/api'

interface Host {
  id: number
  name: string
  ip: string
  hostname?: string
  os?: string
  os_version?: string
  cpu_cores?: number
  memory_gb?: number
  disk_gb?: number
  tags?: string[]
  from_type: string
  from_name?: string
  enabled: boolean
  created_at: string
  updated_at?: string
}

const dialogVisible = ref(false)
const syncDialogVisible = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const previewing = ref(false)
const importing = ref(false)
const searchKeyword = ref('')
const hosts = ref<Host[]>([])
const prometheusDatasources = ref<any[]>([])

const syncPreview = ref<string[]>([])
const syncPreviewTotal = ref(0)

const hostForm = ref({
  id: 0,
  name: '',
  ip: '',
  hostname: '',
  os: '',
  os_version: '',
  cpu_cores: 4,
  memory_gb: 16,
  disk_gb: 100,
  tags: [] as string[],
  enabled: true
})

const syncForm = ref({
  datasource_id: 0,
  metric: '',
  label: '',
  preview_only: true
})

const filteredHosts = computed(() => {
  if (!searchKeyword.value) return hosts.value
  const keyword = searchKeyword.value.toLowerCase()
  return hosts.value.filter(host => 
    host.name.toLowerCase().includes(keyword) ||
    host.ip.includes(keyword)
  )
})

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

const loadHosts = async () => {
  try {
    const data = await api.getHosts()
    hosts.value = (data as Host[])
  } catch (error) {
    ElMessage.error('加载主机列表失败')
    console.error('Load hosts error:', error)
  }
}

const loadPrometheusDatasources = async () => {
  try {
    const data = await api.getDatasources()
    prometheusDatasources.value = (data as any[]).filter((ds: any) => ds.type === 'Prometheus')
  } catch (error) {
    console.error('Load datasources error:', error)
  }
}

const showAddDialog = () => {
  isEditing.value = false
  hostForm.value = {
    id: 0,
    name: '',
    ip: '',
    hostname: '',
    os: '',
    os_version: '',
    cpu_cores: 4,
    memory_gb: 16,
    disk_gb: 100,
    tags: [],
    enabled: true
  }
  dialogVisible.value = true
}

const editHost = (host: Host) => {
  isEditing.value = true
  hostForm.value = { ...host }
  dialogVisible.value = true
}

const deleteHost = async (host: Host) => {
  try {
    await ElMessageBox.confirm(`确定要删除主机 "${host.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteHost(host.id)
    ElMessage.success('主机已删除')
    await loadHosts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete host error:', error)
    }
  }
}

const saveHost = async () => {
  if (!hostForm.value.name || !hostForm.value.ip) {
    ElMessage.warning('请填写必填项')
    return
  }

  saving.value = true
  try {
    if (isEditing.value) {
      await api.updateHost(hostForm.value.id, hostForm.value)
      ElMessage.success('主机已更新')
    } else {
      await api.createHost(hostForm.value)
      ElMessage.success('主机已添加')
    }
    dialogVisible.value = false
    await loadHosts()
  } catch (error) {
    ElMessage.error(isEditing.value ? '更新主机失败' : '添加主机失败')
    console.error('Save host error:', error)
  } finally {
    saving.value = false
  }
}

const showSyncDialog = () => {
  syncForm.value = {
    datasource_id: 0,
    metric: '',
    label: '',
    preview_only: true
  }
  syncPreview.value = []
  syncPreviewTotal.value = 0
  loadPrometheusDatasources()
  syncDialogVisible.value = true
}

const cancelSync = () => {
  syncPreview.value = []
  syncDialogVisible.value = false
}

const doPreview = async () => {
  if (!syncForm.value.datasource_id || !syncForm.value.metric || !syncForm.value.label) {
    ElMessage.warning('请填写完整')
    return
  }
  
  previewing.value = true
  try {
    const result = await api.syncHostsFromPrometheus({
      ...syncForm.value,
      preview_only: true
    })
    syncPreview.value = result.preview
    syncPreviewTotal.value = result.total
  } catch (error) {
    ElMessage.error('预览失败')
    console.error('Preview error:', error)
  } finally {
    previewing.value = false
  }
}

const doImport = async () => {
  importing.value = true
  try {
    const result = await api.syncHostsFromPrometheus({
      ...syncForm.value,
      preview_only: false
    })
    ElMessage.success(`成功导入 ${result.imported} 条主机`)
    syncDialogVisible.value = false
    await loadHosts()
  } catch (error) {
    ElMessage.error('导入失败')
    console.error('Import error:', error)
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  loadHosts()
})
</script>

<style lang="less" scoped>
.hosts-container {
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

.hostname-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  font-size: 16px;

  &.online { color: #22c55e; }
  &.offline { color: #9ca3af; }
}

.tag-item {
  margin-right: 4px;
  background: rgba(255, 215, 0, 0.1);
  border-color: rgba(255, 215, 0, 0.3);
  color: #ffd700;
}

.more-tags {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.host-form {
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

.preview-section {
  margin-top: 16px;
  padding: 16px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: white;
  margin-bottom: 12px;
}

.preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.preview-tag {
  background: rgba(255, 215, 0, 0.1);
  border-color: rgba(255, 215, 0, 0.3);
  color: #ffd700;
}

.preview-total {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
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
