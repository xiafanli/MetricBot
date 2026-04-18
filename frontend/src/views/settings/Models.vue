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
        :class="{ disabled: !model.is_enabled }"
      >
        <div class="model-header">
          <div class="model-icon" :style="{ background: getIconBg(model.provider) }">
            <span class="icon-text">{{ model.provider.charAt(0) }}</span>
          </div>
          <div class="model-info">
            <div class="model-name">
              {{ model.name }}
              <el-tag v-if="model.is_default" type="success" size="small" effect="dark">默认</el-tag>
            </div>
            <div class="model-provider">{{ model.provider }}</div>
          </div>
          <el-switch 
            v-model="model.is_enabled" 
            size="small"
            @change="toggleModel(model)"
          />
        </div>
        
        <div class="model-params">
          <div class="param-item">
            <span class="param-label">基础模型</span>
            <span class="param-value">{{ model.base_model }}</span>
          </div>
          <div class="param-item">
            <span class="param-label">协议类型</span>
            <span class="param-value">{{ model.protocol }}</span>
          </div>
        </div>
        
        <div class="model-actions">
          <el-button text size="small" @click="editModel(model)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button 
            v-if="!model.is_default"
            text 
            size="small" 
            @click="setDefault(model)"
          >
            <el-icon><Star /></el-icon>
            设为默认
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
            <el-option label="Azure" value="Azure" />
            <el-option label="Anthropic" value="Anthropic" />
            <el-option label="Qwen" value="Qwen" />
            <el-option label="Zhipu" value="Zhipu" />
            <el-option label="Ollama" value="Ollama" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="基础模型" required>
          <el-input v-model="modelForm.base_model" placeholder="例如：gpt-4, qwen-max" />
        </el-form-item>
        
        <el-form-item label="协议类型">
          <el-select v-model="modelForm.protocol" placeholder="选择协议">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Ollama" value="ollama" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API域名">
          <el-input v-model="modelForm.api_domain" placeholder="例如：https://api.openai.com/v1" />
        </el-form-item>
        
        <el-form-item label="API密钥">
          <el-input v-model="modelForm.api_key" type="password" placeholder="请输入API密钥" show-password />
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="modelForm.is_enabled" />
        </el-form-item>
        
        <el-form-item label="设为默认">
          <el-switch v-model="modelForm.is_default" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button class="cancel-btn" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveModel" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Star } from '@element-plus/icons-vue'
import { api } from '@/api'

interface Model {
  id: number
  name: string
  provider: string
  base_model: string
  protocol: string
  api_key?: string
  api_domain?: string
  config?: any
  is_default: boolean
  is_enabled: boolean
  created_at: string
  updated_at?: string
}

const models = ref<Model[]>([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const saving = ref(false)

const modelForm = ref({
  id: 0,
  name: '',
  provider: 'OpenAI',
  base_model: '',
  protocol: 'openai',
  api_key: '',
  api_domain: '',
  config: null,
  is_default: false,
  is_enabled: true
})

const providerColors: Record<string, string> = {
  'OpenAI': 'linear-gradient(135deg, #10a37f 0%, #1a7f64 100%)',
  'Azure': 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)',
  'Anthropic': 'linear-gradient(135deg, #7957d6 0%, #5c3cbf 100%)',
  'Qwen': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
  'Zhipu': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
  'Ollama': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
}

const getIconBg = (provider: string) => {
  return providerColors[provider] || 'linear-gradient(135deg, #ffd700 0%, #f72585 100%)'
}

const loadModels = async () => {
  try {
    const data = await api.getModels()
    models.value = ((data as unknown) as Model[]) || []
  } catch (error) {
    ElMessage.error('加载模型列表失败')
    console.error('Load models error:', error)
  }
}

const showAddDialog = () => {
  isEditing.value = false
  modelForm.value = {
    id: 0,
    name: '',
    provider: 'OpenAI',
    base_model: '',
    protocol: 'openai',
    api_key: '',
    api_domain: '',
    config: null,
    is_default: false,
    is_enabled: true
  }
  dialogVisible.value = true
}

const editModel = (model: Model) => {
  isEditing.value = true
  modelForm.value = {
    id: model.id,
    name: model.name,
    provider: model.provider,
    base_model: model.base_model,
    protocol: model.protocol,
    api_key: '',
    api_domain: model.api_domain || '',
    config: null,
    is_default: model.is_default,
    is_enabled: model.is_enabled
  }
  dialogVisible.value = true
}

const deleteModel = async (model: Model) => {
  try {
    await ElMessageBox.confirm(`确定要删除模型 "${model.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteModel(model.id)
    ElMessage.success('模型已删除')
    await loadModels()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete model error:', error)
    }
  }
}

const toggleModel = async (model: Model) => {
  try {
    await api.updateModel(model.id, { is_enabled: model.is_enabled })
    ElMessage.success(model.is_enabled ? '模型已启用' : '模型已禁用')
  } catch (error) {
    model.is_enabled = !model.is_enabled
    ElMessage.error('操作失败')
    console.error('Toggle model error:', error)
  }
}

const setDefault = async (model: Model) => {
  try {
    await api.setDefaultModel(model.id)
    ElMessage.success('已设为默认模型')
    await loadModels()
  } catch (error) {
    ElMessage.error('设置默认模型失败')
    console.error('Set default error:', error)
  }
}

const saveModel = async () => {
  if (!modelForm.value.name || !modelForm.value.base_model) {
    ElMessage.warning('请填写必填项')
    return
  }

  saving.value = true
  try {
    if (isEditing.value) {
      await api.updateModel(modelForm.value.id, modelForm.value)
      ElMessage.success('模型已更新')
    } else {
      await api.createModel(modelForm.value)
      ElMessage.success('模型已添加')
    }
    dialogVisible.value = false
    await loadModels()
  } catch (error) {
    ElMessage.error(isEditing.value ? '更新模型失败' : '添加模型失败')
    console.error('Save model error:', error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadModels()
})
</script>

<style lang="less" scoped>
.models-container {
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

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.model-card {
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  padding: 20px;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--border-medium);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 245, 255, 0.1);
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.icon-text {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.model-info {
  flex: 1;
}

.model-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-provider {
  font-size: 12px;
  color: var(--text-tertiary);
}

.model-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid var(--border-light);
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 16px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.param-label {
  color: var(--text-tertiary);
}

.param-value {
  color: var(--text-primary);
}

.model-actions {
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

.model-form {
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

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  border: none;

  &.el-tag--success {
    background: rgba(0, 255, 136, 0.15);
    color: var(--neon-green);
  }
}
</style>
