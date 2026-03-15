<template>
  <div class="hosts-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">主机模型</h2>
        <span class="page-desc">管理和维护主机信息</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索主机..."
          prefix-icon="Search"
          clearable
          class="search-input"
        />
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加主机
        </el-button>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-value">{{ hostsStats.total }}</div>
        <div class="stat-label">主机总数</div>
      </div>
      <div class="stat-item online">
        <div class="stat-value">{{ hostsStats.online }}</div>
        <div class="stat-label">在线</div>
      </div>
      <div class="stat-item offline">
        <div class="stat-value">{{ hostsStats.offline }}</div>
        <div class="stat-label">离线</div>
      </div>
      <div class="stat-item warning">
        <div class="stat-value">{{ hostsStats.warning }}</div>
        <div class="stat-label">告警中</div>
      </div>
    </div>

    <div class="config-card">
      <el-table
        :data="filteredHosts"
        style="width: 100%"
        :header-cell-style="tableHeaderStyle"
        :cell-style="tableCellStyle"
      >
        <el-table-column prop="hostname" label="主机名" min-width="150">
          <template #default="{ row }">
            <div class="hostname-cell">
              <el-icon :class="['status-dot', row.status]"><Monitor /></el-icon>
              <span>{{ row.hostname }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column prop="os" label="操作系统" width="140" />
        <el-table-column prop="cpu" label="CPU" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.cpu > 80 }">{{ row.cpu }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="memory" label="内存" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.memory > 80 }">{{ row.memory }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="disk" label="磁盘" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.disk > 80 }">{{ row.disk }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="180">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags.slice(0, 2)" :key="tag" size="small" class="tag-item">
              {{ tag }}
            </el-tag>
            <span v-if="row.tags.length > 2" class="more-tags">+{{ row.tags.length - 2 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editHost(row)">
              编辑
            </el-button>
            <el-button type="primary" link size="small" @click="viewHost(row)">
              详情
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
          <el-input v-model="hostForm.hostname" placeholder="请输入主机名" />
        </el-form-item>
        
        <el-form-item label="IP地址" required>
          <el-input v-model="hostForm.ip" placeholder="请输入IP地址" />
        </el-form-item>
        
        <el-form-item label="操作系统">
          <el-input v-model="hostForm.os" placeholder="例如：CentOS 7.9" />
        </el-form-item>
        
        <el-form-item label="CPU核心数">
          <el-input-number v-model="hostForm.cpuCores" :min="1" :max="256" />
        </el-form-item>
        
        <el-form-item label="内存大小">
          <el-input v-model="hostForm.memorySize" placeholder="例如：32GB" />
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
        
        <el-form-item label="数据来源">
          <el-select v-model="hostForm.source" placeholder="选择来源">
            <el-option label="自动同步" value="自动同步" />
            <el-option label="API上报" value="API上报" />
            <el-option label="手工录入" value="手工录入" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveHost">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Monitor
} from '@element-plus/icons-vue'

interface Host {
  id: number
  hostname: string
  ip: string
  os: string
  cpu: number
  memory: number
  disk: number
  tags: string[]
  source: string
  status: string
}

const searchKeyword = ref('')
const dialogVisible = ref(false)
const isEditing = ref(false)

const hostsStats = ref({
  total: 128,
  online: 115,
  offline: 8,
  warning: 5
})

const hosts = ref<Host[]>([
  { id: 1, hostname: 'prod-web-01', ip: '192.168.1.101', os: 'CentOS 7.9', cpu: 45, memory: 62, disk: 35, tags: ['生产环境', 'Web服务'], source: '自动同步', status: 'online' },
  { id: 2, hostname: 'prod-web-02', ip: '192.168.1.102', os: 'CentOS 7.9', cpu: 78, memory: 85, disk: 42, tags: ['生产环境', 'Web服务'], source: '自动同步', status: 'warning' },
  { id: 3, hostname: 'prod-db-01', ip: '192.168.1.201', os: 'Ubuntu 20.04', cpu: 32, memory: 71, disk: 68, tags: ['生产环境', '数据库'], source: '自动同步', status: 'online' },
  { id: 4, hostname: 'prod-cache-01', ip: '192.168.1.301', os: 'CentOS 7.9', cpu: 15, memory: 45, disk: 22, tags: ['生产环境', '缓存'], source: 'API上报', status: 'online' },
  { id: 5, hostname: 'test-web-01', ip: '192.168.2.101', os: 'CentOS 7.9', cpu: 0, memory: 0, disk: 50, tags: ['测试环境', 'Web服务'], source: '手工录入', status: 'offline' }
])

const hostForm = ref({
  id: 0,
  hostname: '',
  ip: '',
  os: '',
  cpuCores: 4,
  memorySize: '',
  tags: [] as string[],
  source: '手工录入'
})

const filteredHosts = computed(() => {
  if (!searchKeyword.value) return hosts.value
  const keyword = searchKeyword.value.toLowerCase()
  return hosts.value.filter(host => 
    host.hostname.toLowerCase().includes(keyword) ||
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

const showAddDialog = () => {
  isEditing.value = false
  hostForm.value = {
    id: 0,
    hostname: '',
    ip: '',
    os: '',
    cpuCores: 4,
    memorySize: '',
    tags: [],
    source: '手工录入'
  }
  dialogVisible.value = true
}

const editHost = (host: Host) => {
  isEditing.value = true
  hostForm.value = { ...host, cpuCores: 4, memorySize: '16GB' }
  dialogVisible.value = true
}

const viewHost = (host: Host) => {
  ElMessage.info(`查看主机详情: ${host.hostname}`)
}

const deleteHost = async (host: Host) => {
  try {
    await ElMessageBox.confirm(`确定要删除主机 "${host.hostname}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = hosts.value.findIndex(h => h.id === host.id)
    if (index > -1) {
      hosts.value.splice(index, 1)
      ElMessage.success('主机已删除')
    }
  } catch {
    // 取消删除
  }
}

const saveHost = () => {
  if (!hostForm.value.hostname || !hostForm.value.ip) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (isEditing.value) {
    const index = hosts.value.findIndex(h => h.id === hostForm.value.id)
    if (index > -1) {
      hosts.value[index] = {
        ...hosts.value[index],
        hostname: hostForm.value.hostname,
        ip: hostForm.value.ip,
        os: hostForm.value.os,
        tags: hostForm.value.tags,
        source: hostForm.value.source
      }
    }
    ElMessage.success('主机已更新')
  } else {
    hosts.value.unshift({
      id: Date.now(),
      hostname: hostForm.value.hostname,
      ip: hostForm.value.ip,
      os: hostForm.value.os,
      cpu: 0,
      memory: 0,
      disk: 0,
      tags: hostForm.value.tags,
      source: hostForm.value.source,
      status: 'offline'
    })
    ElMessage.success('主机已添加')
  }
  
  dialogVisible.value = false
}
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

.search-input {
  width: 240px;

  :deep(.el-input__wrapper) {
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
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  padding: 20px;
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  text-align: center;

  &.online .stat-value { color: #22c55e; }
  &.offline .stat-value { color: #9ca3af; }
  &.warning .stat-value { color: #f59e0b; }
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: white;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
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
  &.warning { color: #f59e0b; }
}

.text-warning {
  color: #f59e0b;
  font-weight: 600;
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
</style>
