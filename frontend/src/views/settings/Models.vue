<template>
  <div class="models-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">模型管理</h2>
        <span class="page-desc">配置和管理大语言模型</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加模型
        </el-button>
      </div>
    </div>

    <div class="models-grid">
      <div 
        v-for="model in models" 
        :key="model.id" 
        class="model-card"
        :class="{ disabled: !model.enabled }"
      >
        <div class="model-header">
          <div class="model-icon" :style="{ background: model.iconBg }">
            <span class="icon-text">{{ model.icon }}</span>
          </div>
          <div class="model-info">
            <div class="model-name">{{ model.name }}</div>
            <div class="model-provider">{{ model.provider }}</div>
          </div>
          <el-switch 
            v-model="model.enabled" 
            size="small"
            @change="toggleModel(model)"
          />
        </div>
        
        <div class="model-params">
          <div class="param-item">
            <span class="param-label">模型类型</span>
            <span class="param-value">{{ model.type }}</span>
          </div>
          <div class="param-item">
            <span class="param-label">温度系数</span>
            <span class="param-value">{{ model.temperature }}</span>
          </div>
          <div class="param-item">
            <span class="param-label">最大Token</span>
            <span class="param-value">{{ model.maxTokens }}</span>
          </div>
        </div>
        
        <div class="model-stats">
          <div class="stat-item">
            <span class="stat-value">{{ model.callCount }}</span>
            <span class="stat-label">调用次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ model.avgLatency }}ms</span>
            <span class="stat-label">平均延迟</span>
          </div>
        </div>
        
        <div class="model-actions">
          <el-button text size="small" @click="editModel(model)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button text size="small" @click="testModel(model)">
            <el-icon><Connection /></el-icon>
            测试
          </el-button>
          <el-button text size="small" class="delete-btn" @click="deleteModel(model)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>
    </div>

    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditing ? '编辑模型' : '添加模型'"
      width="500px"
    >
      <el-form :model="modelForm" label-width="100px" class="config-form model-form">
        <el-form-item label="模型名称" required>
          <el-input v-model="modelForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        
        <el-form-item label="提供商" required>
          <el-select v-model="modelForm.provider" placeholder="选择提供商">
            <el-option label="OpenAI" value="OpenAI" />
            <el-option label="Azure OpenAI" value="Azure" />
            <el-option label="通义千问" value="Qwen" />
            <el-option label="文心一言" value="Ernie" />
            <el-option label="智谱AI" value="Zhipu" />
            <el-option label="Ollama" value="Ollama" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模型类型" required>
          <el-input v-model="modelForm.type" placeholder="例如：gpt-4, qwen-max" />
        </el-form-item>
        
        <el-form-item label="API地址">
          <el-input v-model="modelForm.endpoint" placeholder="自定义API地址（可选）" />
        </el-form-item>
        
        <el-form-item label="API密钥">
          <el-input v-model="modelForm.apiKey" type="password" placeholder="请输入API密钥" show-password />
        </el-form-item>
        
        <el-form-item label="温度系数">
          <el-slider v-model="modelForm.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
        
        <el-form-item label="最大Token">
          <el-input-number v-model="modelForm.maxTokens" :min="100" :max="128000" :step="100" />
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="modelForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveModel">保存</el-button>
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

interface Model {
  id: number
  name: string
  provider: string
  type: string
  icon: string
  iconBg: string
  temperature: number
  maxTokens: number
  enabled: boolean
  callCount: number
  avgLatency: number
}

const dialogVisible = ref(false)
const isEditing = ref(false)

const models = ref<Model[]>([
  {
    id: 1,
    name: 'GPT-4',
    provider: 'OpenAI',
    type: 'gpt-4-turbo',
    icon: 'G',
    iconBg: 'linear-gradient(135deg, #10a37f 0%, #1a7f64 100%)',
    temperature: 0.7,
    maxTokens: 4096,
    enabled: true,
    callCount: 1234,
    avgLatency: 850
  },
  {
    id: 2,
    name: '通义千问',
    provider: 'Qwen',
    type: 'qwen-max',
    icon: '通',
    iconBg: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    temperature: 0.8,
    maxTokens: 8000,
    enabled: true,
    callCount: 856,
    avgLatency: 620
  },
  {
    id: 3,
    name: '智谱AI',
    provider: 'Zhipu',
    type: 'glm-4',
    icon: '智',
    iconBg: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    temperature: 0.7,
    maxTokens: 4096,
    enabled: false,
    callCount: 0,
    avgLatency: 0
  }
])

const modelForm = ref({
  id: 0,
  name: '',
  provider: 'OpenAI',
  type: '',
  endpoint: '',
  apiKey: '',
  temperature: 0.7,
  maxTokens: 4096,
  enabled: true
})

const showAddDialog = () => {
  isEditing.value = false
  modelForm.value = {
    id: 0,
    name: '',
    provider: 'OpenAI',
    type: '',
    endpoint: '',
    apiKey: '',
    temperature: 0.7,
    maxTokens: 4096,
    enabled: true
  }
  dialogVisible.value = true
}

const editModel = (model: Model) => {
  isEditing.value = true
  modelForm.value = { ...model, endpoint: '', apiKey: '' }
  dialogVisible.value = true
}

const deleteModel = async (model: Model) => {
  try {
    await ElMessageBox.confirm(`确定要删除模型 "${model.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = models.value.findIndex(m => m.id === model.id)
    if (index > -1) {
      models.value.splice(index, 1)
      ElMessage.success('模型已删除')
    }
  } catch {
    // 取消删除
  }
}

const toggleModel = (model: Model) => {
  ElMessage.success(model.enabled ? '模型已启用' : '模型已禁用')
}

const testModel = (model: Model) => {
  ElMessage.info(`正在测试模型 ${model.name}...`)
  setTimeout(() => {
    ElMessage.success('模型连接测试成功！')
  }, 1500)
}

const saveModel = () => {
  if (!modelForm.value.name || !modelForm.value.type) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (isEditing.value) {
    const index = models.value.findIndex(m => m.id === modelForm.value.id)
    if (index > -1) {
      models.value[index] = {
        ...models.value[index],
        ...modelForm.value
      }
    }
    ElMessage.success('模型已更新')
  } else {
    models.value.push({
      id: Date.now(),
      name: modelForm.value.name,
      provider: modelForm.value.provider,
      type: modelForm.value.type,
      icon: modelForm.value.name.charAt(0),
      iconBg: 'linear-gradient(135deg, #ffd700 0%, #f72585 100%)',
      temperature: modelForm.value.temperature,
      maxTokens: modelForm.value.maxTokens,
      enabled: modelForm.value.enabled,
      callCount: 0,
      avgLatency: 0
    })
    ElMessage.success('模型已添加')
  }
  
  dialogVisible.value = false
}
</script>

<style lang="less" scoped>
.models-container {
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

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.model-card {
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  padding: 20px;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(255, 215, 0, 0.3);
    transform: translateY(-2px);
  }

  &.disabled {
    opacity: 0.6;
  }
}

.model-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.model-icon {
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

.model-info {
  flex: 1;
}

.model-name {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.model-provider {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.model-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid rgba(255, 215, 0, 0.1);
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  margin-bottom: 16px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.param-label {
  color: rgba(255, 255, 255, 0.5);
}

.param-value {
  color: rgba(255, 255, 255, 0.9);
}

.model-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #ffd700;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.model-actions {
  display: flex;
  gap: 8px;

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

.model-form {
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
