<template>
  <div class="monitor-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">告警规则管理</h2>
        <span class="page-desc">配置和管理智能告警规则</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索规则..."
          prefix-icon="Search"
          clearable
          class="search-input"
        />
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          新建规则
        </el-button>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-value">{{ rulesStats.total }}</div>
        <div class="stat-label">规则总数</div>
      </div>
      <div class="stat-item active">
        <div class="stat-value">{{ rulesStats.active }}</div>
        <div class="stat-label">已启用</div>
      </div>
      <div class="stat-item inactive">
        <div class="stat-value">{{ rulesStats.inactive }}</div>
        <div class="stat-label">已禁用</div>
      </div>
      <div class="stat-item triggered">
        <div class="stat-value">{{ rulesStats.triggered }}</div>
        <div class="stat-label">今日触发</div>
      </div>
    </div>

    <div class="rules-section">
      <div class="rules-list">
        <div 
          v-for="rule in filteredRules" 
          :key="rule.id" 
          class="rule-card"
          :class="{ inactive: !rule.enabled }"
        >
          <div class="rule-header">
            <div class="rule-info">
              <div class="rule-name">
                <el-switch 
                  v-model="rule.enabled" 
                  size="small"
                  @change="toggleRule(rule)"
                />
                <span class="name-text">{{ rule.name }}</span>
                <el-tag :type="getLevelType(rule.level)" size="small" effect="dark">
                  {{ rule.level }}
                </el-tag>
              </div>
              <div class="rule-meta">
                <span class="meta-item">
                  <el-icon><TrendCharts /></el-icon>
                  {{ rule.datasource }}
                </span>
                <span class="meta-item">
                  <el-icon><Timer /></el-icon>
                  {{ rule.interval }}
                </span>
              </div>
            </div>
            <div class="rule-actions">
              <el-button text @click="editRule(rule)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button text @click="duplicateRule(rule)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
              <el-button text class="delete-btn" @click="deleteRule(rule)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          
          <div class="rule-condition">
            <div class="condition-label">触发条件</div>
            <div class="condition-content">
              <code>{{ rule.condition }}</code>
            </div>
          </div>
          
          <div class="rule-footer">
            <div class="footer-item">
              <span class="footer-label">持续时间:</span>
              <span class="footer-value">{{ rule.duration }}</span>
            </div>
            <div class="footer-item">
              <span class="footer-label">通知渠道:</span>
              <span class="footer-value">{{ rule.channels.join(', ') }}</span>
            </div>
            <div class="footer-item">
              <span class="footer-label">今日触发:</span>
              <span class="footer-value trigger-count">{{ rule.triggerCount }}次</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditing ? '编辑规则' : '新建规则'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="ruleForm" label-width="100px" class="rule-form">
        <el-form-item label="规则名称" required>
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        
        <el-form-item label="告警级别" required>
          <el-select v-model="ruleForm.level" placeholder="选择告警级别">
            <el-option label="严重" value="严重" />
            <el-option label="警告" value="警告" />
            <el-option label="信息" value="信息" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="数据源" required>
          <el-select v-model="ruleForm.datasource" placeholder="选择数据源">
            <el-option label="Prometheus" value="Prometheus" />
            <el-option label="Zabbix" value="Zabbix" />
            <el-option label="自定义" value="自定义" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="触发条件" required>
          <el-input 
            v-model="ruleForm.condition" 
            type="textarea" 
            :rows="3"
            placeholder="例如：cpu_usage > 80"
          />
        </el-form-item>
        
        <el-form-item label="检查间隔">
          <el-select v-model="ruleForm.interval" placeholder="选择检查间隔">
            <el-option label="1分钟" value="1m" />
            <el-option label="5分钟" value="5m" />
            <el-option label="10分钟" value="10m" />
            <el-option label="30分钟" value="30m" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="持续时间">
          <el-input v-model="ruleForm.duration" placeholder="例如：5m" />
        </el-form-item>
        
        <el-form-item label="通知渠道">
          <el-checkbox-group v-model="ruleForm.channels">
            <el-checkbox label="邮件" />
            <el-checkbox label="钉钉" />
            <el-checkbox label="企业微信" />
            <el-checkbox label="短信" />
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="ruleForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  CopyDocument,
  TrendCharts,
  Timer
} from '@element-plus/icons-vue'

interface Rule {
  id: number
  name: string
  level: string
  datasource: string
  condition: string
  interval: string
  duration: string
  channels: string[]
  enabled: boolean
  triggerCount: number
}

const searchKeyword = ref('')
const dialogVisible = ref(false)
const isEditing = ref(false)

const rulesStats = ref({
  total: 12,
  active: 9,
  inactive: 3,
  triggered: 28
})

const rules = ref<Rule[]>([
  {
    id: 1,
    name: 'CPU使用率过高告警',
    level: '严重',
    datasource: 'Prometheus',
    condition: 'avg(cpu_usage) > 90',
    interval: '1m',
    duration: '5m',
    channels: ['邮件', '钉钉'],
    enabled: true,
    triggerCount: 5
  },
  {
    id: 2,
    name: '内存使用率告警',
    level: '警告',
    datasource: 'Prometheus',
    condition: 'avg(memory_usage) > 85',
    interval: '5m',
    duration: '10m',
    channels: ['邮件'],
    enabled: true,
    triggerCount: 3
  },
  {
    id: 3,
    name: '磁盘空间不足告警',
    level: '严重',
    datasource: 'Zabbix',
    condition: 'disk_free < 10GB',
    interval: '10m',
    duration: '0',
    channels: ['邮件', '企业微信'],
    enabled: true,
    triggerCount: 2
  },
  {
    id: 4,
    name: '服务响应时间过长',
    level: '警告',
    datasource: 'Prometheus',
    condition: 'avg(response_time) > 1000',
    interval: '5m',
    duration: '5m',
    channels: ['钉钉'],
    enabled: false,
    triggerCount: 0
  },
  {
    id: 5,
    name: '网络连接数异常',
    level: '信息',
    datasource: 'Prometheus',
    condition: 'connection_count > 10000',
    interval: '30m',
    duration: '15m',
    channels: ['邮件'],
    enabled: true,
    triggerCount: 1
  }
])

const ruleForm = ref({
  id: 0,
  name: '',
  level: '警告',
  datasource: 'Prometheus',
  condition: '',
  interval: '5m',
  duration: '5m',
  channels: ['邮件'] as string[],
  enabled: true
})

const filteredRules = computed(() => {
  if (!searchKeyword.value) return rules.value
  const keyword = searchKeyword.value.toLowerCase()
  return rules.value.filter(rule => 
    rule.name.toLowerCase().includes(keyword) ||
    rule.condition.toLowerCase().includes(keyword)
  )
})

const getLevelType = (level: string) => {
  const types: Record<string, string> = {
    '严重': 'danger',
    '警告': 'warning',
    '信息': 'info'
  }
  return types[level] || 'info'
}

const showAddDialog = () => {
  isEditing.value = false
  ruleForm.value = {
    id: 0,
    name: '',
    level: '警告',
    datasource: 'Prometheus',
    condition: '',
    interval: '5m',
    duration: '5m',
    channels: ['邮件'],
    enabled: true
  }
  dialogVisible.value = true
}

const editRule = (rule: Rule) => {
  isEditing.value = true
  ruleForm.value = { ...rule }
  dialogVisible.value = true
}

const duplicateRule = (rule: Rule) => {
  const newRule = {
    ...rule,
    id: Date.now(),
    name: `${rule.name} (副本)`,
    triggerCount: 0
  }
  rules.value.unshift(newRule)
  ElMessage.success('规则已复制')
}

const deleteRule = async (rule: Rule) => {
  try {
    await ElMessageBox.confirm(`确定要删除规则 "${rule.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = rules.value.findIndex(r => r.id === rule.id)
    if (index > -1) {
      rules.value.splice(index, 1)
      ElMessage.success('规则已删除')
    }
  } catch {
    // 取消删除
  }
}

const toggleRule = (rule: Rule) => {
  ElMessage.success(rule.enabled ? '规则已启用' : '规则已禁用')
}

const saveRule = () => {
  if (!ruleForm.value.name || !ruleForm.value.condition) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (isEditing.value) {
    const index = rules.value.findIndex(r => r.id === ruleForm.value.id)
    if (index > -1) {
      rules.value[index] = { ...ruleForm.value, triggerCount: rules.value[index].triggerCount }
    }
    ElMessage.success('规则已更新')
  } else {
    rules.value.unshift({
      ...ruleForm.value,
      id: Date.now(),
      triggerCount: 0
    })
    ElMessage.success('规则已创建')
  }
  
  dialogVisible.value = false
}
</script>

<style lang="less" scoped>
.monitor-container {
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

    .el-input__inner {
      color: white;

      &::placeholder {
        color: rgba(255, 255, 255, 0.3);
      }
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

  &.active {
    border-color: rgba(34, 197, 94, 0.3);
    .stat-value { color: #22c55e; }
  }

  &.inactive {
    border-color: rgba(156, 163, 175, 0.3);
    .stat-value { color: #9ca3af; }
  }

  &.triggered {
    border-color: rgba(255, 215, 0, 0.3);
    .stat-value { color: #ffd700; }
  }
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

.rules-section {
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  overflow: hidden;
}

.rules-list {
  display: flex;
  flex-direction: column;
}

.rule-card {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.05);
  transition: background 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(255, 215, 0, 0.02);
  }

  &.inactive {
    opacity: 0.6;
  }
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.rule-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-name {
  display: flex;
  align-items: center;
  gap: 12px;

  .name-text {
    font-size: 16px;
    font-weight: 600;
    color: white;
  }
}

.rule-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);

  .el-icon {
    color: #ffd700;
  }
}

.rule-actions {
  display: flex;
  gap: 4px;

  .el-button {
    color: rgba(255, 215, 0, 0.6);

    &:hover {
      color: #ffd700;
    }
  }

  .delete-btn:hover {
    color: #ef4444;
  }
}

.rule-condition {
  margin-bottom: 16px;
}

.condition-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 8px;
}

.condition-content {
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(255, 215, 0, 0.1);

  code {
    font-family: 'Fira Code', 'Monaco', monospace;
    font-size: 13px;
    color: #ffd700;
  }
}

.rule-footer {
  display: flex;
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 215, 0, 0.05);
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.footer-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.footer-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);

  &.trigger-count {
    color: #ffd700;
    font-weight: 600;
  }
}

.rule-form {
  :deep(.el-input__wrapper),
  :deep(.el-textarea__inner),
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

  :deep(.el-checkbox__label) {
    color: rgba(255, 255, 255, 0.8);
  }
}
</style>
