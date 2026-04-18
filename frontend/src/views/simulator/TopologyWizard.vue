<template>
  <div class="topology-wizard">
    <el-card class="wizard-card">
      <template #header>
        <div class="card-header">
          <span class="title">拓扑生成向导</span>
          <el-button text @click="handleClose">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" simple class="wizard-steps">
        <el-step title="基础配置" />
        <el-step title="拓扑类型" />
        <el-step title="规模配置" />
        <el-step title="组件选择" />
        <el-step title="网络配置" />
        <el-step title="确认生成" />
      </el-steps>

      <div class="step-content">
        <div v-show="currentStep === 0" class="step-panel">
          <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
            <el-form-item label="环境名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入环境名称" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述（可选）" />
            </el-form-item>
            <el-form-item label="Pushgateway" prop="pushgateway_url">
              <el-input v-model="form.pushgateway_url" placeholder="http://localhost:9091" />
            </el-form-item>
            <el-form-item label="日志路径" prop="log_path">
              <el-input v-model="form.log_path" placeholder="simulator/logs" />
            </el-form-item>
          </el-form>
        </div>

        <div v-show="currentStep === 1" class="step-panel">
          <div v-if="topologyTypes.length === 0" class="empty-state">
            <el-empty description="加载中..." />
          </div>
          <div v-else class="topology-type-list">
            <div
              v-for="item in topologyTypes"
              :key="item.type"
              class="topology-type-card"
              :class="{ active: form.topology_type === item.type }"
              @click="form.topology_type = item.type"
            >
              <div class="type-header">
                <el-icon v-if="form.topology_type === item.type" class="check-icon"><CircleCheckFilled /></el-icon>
                <span class="type-name">{{ item.name }}</span>
              </div>
              <div class="type-desc">{{ item.description }}</div>
              <div class="type-layers">
                <el-tag v-for="layer in item.layers" :key="layer" size="small" class="layer-tag">
                  {{ layer }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <div v-show="currentStep === 2" class="step-panel">
          <div v-if="scales.length === 0" class="empty-state">
            <el-empty description="加载中..." />
          </div>
          <div v-else class="scale-list">
            <div
              v-for="item in scales"
              :key="item.scale"
              class="scale-card"
              :class="{ active: form.scale === item.scale }"
              @click="form.scale = item.scale"
            >
              <div class="scale-header">
                <el-icon v-if="form.scale === item.scale" class="check-icon"><CircleCheckFilled /></el-icon>
                <span class="scale-name">{{ item.name }}</span>
              </div>
              <div class="scale-desc">{{ item.description }}</div>
              <div class="scale-config">
                <div v-for="(count, type) in item.config" :key="type" class="config-item">
                  <span class="config-type">{{ type }}:</span>
                  <span class="config-count">{{ count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-show="currentStep === 3" class="step-panel">
          <div v-if="componentTypes.length === 0" class="empty-state">
            <el-empty description="加载中..." />
          </div>
          <div v-else class="component-selection">
            <el-checkbox-group v-model="form.include_components">
              <div class="component-grid">
                <div
                  v-for="item in componentTypes"
                  :key="item.type"
                  class="component-card"
                  :class="{ selected: form.include_components.includes(item.type) }"
                >
                  <el-checkbox :label="item.type">
                    <div class="component-info">
                      <span class="component-name">{{ item.name }}</span>
                      <el-tag size="small" type="info">Layer {{ item.layer }}</el-tag>
                    </div>
                  </el-checkbox>
                </div>
              </div>
            </el-checkbox-group>
            <div class="selection-tip">
              <el-text type="info">不选择则使用拓扑类型默认组件</el-text>
            </div>
          </div>
        </div>

        <div v-show="currentStep === 4" class="step-panel">
          <el-form :model="form" label-width="120px">
            <el-form-item label="IP前缀" prop="ip_prefix">
              <el-input v-model="form.ip_prefix" placeholder="192.168.1" @blur="checkIPConflict" />
              <div class="ip-tip">
                生成的IP格式: {{ form.ip_prefix }}.{layer}.{index}
              </div>
            </el-form-item>
            <el-form-item v-if="ipCheckResult" label="">
              <el-alert
                :title="ipCheckResult.message"
                :type="ipCheckResult.has_conflict ? 'warning' : 'success'"
                :closable="false"
                show-icon
              />
            </el-form-item>
          </el-form>
        </div>

        <div v-show="currentStep === 5" class="step-panel">
          <div class="preview-section">
            <h4>生成预览</h4>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="环境名称">{{ form.name }}</el-descriptions-item>
              <el-descriptions-item label="拓扑类型">{{ getTopologyTypeName(form.topology_type) }}</el-descriptions-item>
              <el-descriptions-item label="规模">{{ getScaleName(form.scale) }}</el-descriptions-item>
              <el-descriptions-item label="IP前缀">{{ form.ip_prefix }}</el-descriptions-item>
              <el-descriptions-item label="组件数量">{{ getEstimatedComponentCount() }}</el-descriptions-item>
              <el-descriptions-item label="Pushgateway">{{ form.pushgateway_url }}</el-descriptions-item>
            </el-descriptions>

            <div v-if="form.include_components.length > 0" class="selected-components">
              <h5>已选组件</h5>
              <el-tag v-for="type in form.include_components" :key="type" class="component-tag">
                {{ getComponentTypeName(type) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button v-if="currentStep < 5" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="currentStep === 5" type="success" :loading="generating" @click="handleGenerate">
          生成环境
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Close, CircleCheckFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import {
  simulatorApi,
  type TopologyType,
  type TopologyScale,
  type TopologyComponentType,
  type TopologyIPCheckResponse,
} from '@/api/simulator'

const router = useRouter()
const emit = defineEmits(['close', 'generated'])

const currentStep = ref(0)
const generating = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  description: '',
  topology_type: 'standard',
  scale: 'medium',
  ip_prefix: '192.168.1',
  pushgateway_url: 'http://localhost:9091',
  log_path: 'simulator/logs',
  include_components: [] as string[],
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  pushgateway_url: [{ required: true, message: '请输入Pushgateway地址', trigger: 'blur' }],
}

const topologyTypes = ref<TopologyType[]>([])
const scales = ref<TopologyScale[]>([])
const componentTypes = ref<TopologyComponentType[]>([])
const ipCheckResult = ref<TopologyIPCheckResponse | null>(null)

const fetchData = async () => {
  try {
    const [typesRes, scalesRes, componentsRes] = await Promise.all([
      simulatorApi.getTopologyTypes(),
      simulatorApi.getTopologyScales(),
      simulatorApi.getTopologyComponents(),
    ])
    topologyTypes.value = typesRes
    scales.value = scalesRes
    componentTypes.value = componentsRes
  } catch (error) {
    console.error('获取配置数据失败:', error)
    ElMessage.error('获取配置数据失败')
  }
}

const checkIPConflict = async () => {
  if (!form.ip_prefix) return
  try {
    ipCheckResult.value = await simulatorApi.checkIPPrefix(form.ip_prefix)
  } catch (error) {
    console.error('检查IP冲突失败:', error)
  }
}

const getTopologyTypeName = (type: string): string => {
  const item = topologyTypes.value.find((t) => t.type === type)
  return item?.name || type
}

const getScaleName = (scale: string): string => {
  const item = scales.value.find((s) => s.scale === scale)
  return item?.name || scale
}

const getComponentTypeName = (type: string): string => {
  const item = componentTypes.value.find((c) => c.type === type)
  return item?.name || type
}

const getEstimatedComponentCount = (): number => {
  const scaleConfig = scales.value.find((s) => s.scale === form.scale)
  if (!scaleConfig) return 0

  if (form.include_components.length > 0) {
    return form.include_components.reduce((sum, type) => {
      return sum + (scaleConfig.config[type] || 1)
    }, 0)
  }

  const topologyConfig = topologyTypes.value.find((t) => t.type === form.topology_type)
  if (!topologyConfig) return 0

  return topologyConfig.layers.reduce((sum, type) => {
    return sum + (scaleConfig.config[type] || 1)
  }, 0)
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const nextStep = async () => {
  if (currentStep.value === 0) {
    const valid = await formRef.value?.validate().catch(() => false)
    if (!valid) return
  }
  if (currentStep.value < 5) {
    currentStep.value++
  }
}

const handleGenerate = async () => {
  try {
    generating.value = true
    const data = {
      name: form.name,
      description: form.description || undefined,
      topology_type: form.topology_type,
      scale: form.scale,
      ip_prefix: form.ip_prefix,
      pushgateway_url: form.pushgateway_url,
      log_path: form.log_path,
      include_components: form.include_components.length > 0 ? form.include_components : undefined,
    }
    const result = await simulatorApi.generateTopology(data)
    ElMessage.success(`环境创建成功，共 ${result.summary.total_components} 个组件`)
    emit('generated', result)
    handleClose()
  } catch (error: unknown) {
    console.error('生成拓扑失败:', error)
    const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '生成拓扑失败'
    ElMessage.error(errorMessage)
  } finally {
    generating.value = false
  }
}

const handleClose = () => {
  emit('close')
  router.push('/simulator')
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="less" scoped>
.topology-wizard {
  padding: 20px;
  background: var(--bg-primary);
  min-height: 100%;
  font-family: var(--font-body);
}

.wizard-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;

  :deep(.el-card__header) {
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-light);
    padding: 16px 20px;
  }

  :deep(.el-card__body) {
    padding: 20px;
    background: var(--bg-secondary);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .title {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 600;
    color: var(--neon-blue);
  }

  .el-button {
    color: var(--text-tertiary);

    &:hover {
      color: var(--neon-blue);
    }
  }
}

.wizard-steps {
  margin-bottom: 10px;

  :deep(.el-steps) {
    background: transparent;
  }

  :deep(.el-steps--simple) {
    background: var(--bg-tertiary) !important;
    border-radius: 8px;
    padding: 13px 20px;
    border: 1px solid var(--border-light);
  }

  :deep(.el-step__title) {
    color: var(--text-tertiary) !important;
    font-size: 14px;

    &.is-process {
      color: var(--neon-blue) !important;
      font-weight: 600;
    }

    &.is-success {
      color: var(--neon-green) !important;
    }

    &.is-wait {
      color: var(--text-tertiary) !important;
    }
  }

  :deep(.el-step__head) {
    &.is-process {
      color: var(--neon-blue);
      border-color: var(--neon-blue);
    }

    &.is-success {
      color: var(--neon-green);
      border-color: var(--neon-green);
    }

    &.is-wait {
      color: var(--text-tertiary);
      border-color: var(--border-light);
    }
  }

  :deep(.el-step__icon) {
    background: transparent !important;
  }

  :deep(.el-step__icon-inner) {
    color: var(--text-tertiary);

    .is-process & {
      color: var(--neon-blue);
    }

    .is-success & {
      color: var(--neon-green);
    }
  }

  :deep(.el-step__arrow) {
    &::before,
    &::after {
      background: var(--border-light);
    }
  }

  :deep(.el-step.is-success .el-step__arrow::before),
  :deep(.el-step.is-success .el-step__arrow::after) {
    background: var(--neon-green);
  }

  :deep(.el-step.is-process .el-step__arrow::before),
  :deep(.el-step.is-process .el-step__arrow::after) {
    background: var(--neon-blue);
  }
}

.step-content {
  margin: 30px 0;
  min-height: 350px;
}

.step-panel {
  padding: 20px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;

  :deep(.el-empty__description) {
    color: var(--text-tertiary);
  }
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);

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

    &.el-button--success {
      background: rgba(0, 255, 136, 0.15);
      border: 1px solid var(--neon-green);
      color: var(--neon-green);

      &:hover {
        background: rgba(0, 255, 136, 0.25);
      }
    }
  }
}

.topology-type-list,
.scale-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.topology-type-card,
.scale-card {
  flex: 1;
  min-width: 280px;
  max-width: 400px;
  padding: 20px;
  border: 2px solid var(--border-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--bg-tertiary);

  &:hover {
    border-color: var(--border-medium);
    transform: translateY(-2px);
  }

  &.active {
    border-color: var(--neon-blue);
    background: rgba(0, 245, 255, 0.05);
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
  }
}

.type-header,
.scale-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.check-icon {
  color: var(--neon-green);
  font-size: 20px;
}

.type-name,
.scale-name {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
}

.type-desc,
.scale-desc {
  color: var(--text-tertiary);
  margin-bottom: 15px;
}

.type-layers {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.layer-tag {
  margin: 2px;
  background: rgba(0, 245, 255, 0.15);
  color: var(--neon-blue);
  border: none;
  border-radius: 4px;
}

.scale-config {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 10px;
  background: var(--bg-secondary);
  border-radius: 4px;
  border: 1px solid var(--border-light);
}

.config-type {
  color: var(--text-tertiary);
  font-size: 12px;
}

.config-count {
  font-weight: bold;
  color: var(--neon-blue);
}

.component-selection {
  padding: 10px;
}

.component-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.component-card {
  padding: 15px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  transition: all 0.3s;
  background: var(--bg-tertiary);

  &:hover {
    border-color: var(--border-medium);
  }

  &.selected {
    border-color: var(--neon-blue);
    background: rgba(0, 245, 255, 0.05);
  }

  :deep(.el-checkbox__label) {
    color: var(--text-primary);
  }

  :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: var(--neon-blue);
    border-color: var(--neon-blue);
  }
}

.component-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.component-name {
  font-weight: 500;
  color: var(--text-primary);
}

.selection-tip {
  margin-top: 20px;
  text-align: center;

  :deep(.el-text) {
    color: var(--text-tertiary);
  }
}

.ip-tip {
  margin-top: 10px;
  color: var(--text-tertiary);
  font-size: 12px;
}

.preview-section {
  padding: 20px;

  h4 {
    margin-bottom: 20px;
    font-family: var(--font-display);
    color: var(--neon-blue);
    font-weight: 600;
  }

  :deep(.el-descriptions) {
    .el-descriptions__label {
      background: var(--bg-tertiary);
      color: var(--text-secondary);
      font-weight: 500;
    }

    .el-descriptions__content {
      background: var(--bg-secondary);
      color: var(--text-primary);
    }

    .el-descriptions__cell {
      border-color: var(--border-light);
    }
  }
}

.selected-components {
  margin-top: 20px;

  h5 {
    margin-bottom: 10px;
    color: var(--text-secondary);
  }
}

.component-tag {
  margin-right: 10px;
  margin-bottom: 10px;
  background: rgba(0, 245, 255, 0.15);
  color: var(--neon-blue);
  border: none;
  border-radius: 4px;
}

:deep(.el-form) {
  .el-form-item__label {
    color: var(--text-primary);
    font-weight: 500;
  }

  .el-input__wrapper {
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

  .el-textarea__inner {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-light);
    color: var(--text-primary);
    border-radius: 8px;

    &:hover {
      border-color: var(--border-medium);
    }

    &:focus {
      border-color: var(--neon-blue);
      box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
    }
  }
}

:deep(.el-alert) {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);

  &.el-alert--success {
    background: rgba(0, 255, 136, 0.1);
    border-color: rgba(0, 255, 136, 0.3);

    .el-alert__title {
      color: var(--neon-green);
    }
  }

  &.el-alert--warning {
    background: rgba(255, 165, 0, 0.1);
    border-color: rgba(255, 165, 0, 0.3);

    .el-alert__title {
      color: var(--neon-orange);
    }
  }
}

:deep(.el-tag) {
  border-radius: 4px;
  font-weight: 500;

  &.el-tag--info {
    background: rgba(0, 245, 255, 0.15);
    color: var(--neon-blue);
    border: none;
  }
}
</style>
