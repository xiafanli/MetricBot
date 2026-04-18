<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="AI 智能诊断"
    width="800px"
    class="diagnosis-dialog"
  >
    <div class="diagnosis-content">
      <div v-if="alert" class="alert-info">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="规则名称">{{ alert.rule_name }}</el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="severityMap[alert.severity]?.type || 'info'" size="small">
              {{ severityMap[alert.severity]?.label || alert.severity }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="指标值">{{ alert.metric_value?.toFixed(2) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="阈值">{{ alert.threshold?.toFixed(2) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="触发时间" :span="2">{{ formatTime(alert.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="告警消息" :span="2">{{ alert.message }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider />

      <div class="diagnosis-report" v-if="report">
        <h4>诊断报告</h4>
        <div class="report-content" v-html="formatReport(report.report)"></div>
      </div>
      <div v-else-if="loadingReport" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在生成诊断报告...</span>
      </div>
      <div v-else class="no-report">
        <el-empty description="暂无诊断报告">
          <el-button type="primary" @click="generateReport">生成诊断报告</el-button>
        </el-empty>
      </div>

      <el-divider />

      <div class="chat-section">
        <h4>继续对话</h4>
        <div class="chat-messages" ref="messagesContainer">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <div v-if="sendingMessage" class="message assistant">
            <div class="message-content">
              <el-icon class="is-loading"><Loading /></el-icon>
              正在思考...
            </div>
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="userInput"
            placeholder="输入问题继续诊断..."
            @keyup.enter="sendMessage"
            :disabled="sendingMessage"
          >
            <template #append>
              <el-button @click="sendMessage" :loading="sendingMessage">发送</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import {
  generateDiagnosis,
  getDiagnosis,
  diagnosisChat,
  getConversations,
  type Alert,
  type DiagnosisReport,
  type ConversationMessage
} from '@/api/alert'

const props = defineProps<{
  modelValue: boolean
  alert: Alert | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

const report = ref<DiagnosisReport | null>(null)
const loadingReport = ref(false)
const messages = ref<ConversationMessage[]>([])
const userInput = ref('')
const sendingMessage = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

const severityMap: Record<string, { label: string; type: string }> = {
  critical: { label: '严重', type: 'danger' },
  warning: { label: '警告', type: 'warning' },
  info: { label: '信息', type: 'info' }
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const formatReport = (content: string | null) => {
  if (!content) return ''
  return content
    .replace(/\n/g, '<br>')
    .replace(/### (.*)/g, '<h5>$1</h5>')
    .replace(/## (.*)/g, '<h4>$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

const loadReport = async () => {
  if (!props.alert) return
  
  loadingReport.value = true
  try {
    const data = await getDiagnosis(props.alert.id)
    report.value = data
  } catch (error) {
    report.value = null
  } finally {
    loadingReport.value = false
  }
}

const generateReport = async () => {
  if (!props.alert) return
  
  loadingReport.value = true
  try {
    const data = await generateDiagnosis(props.alert.id)
    report.value = data
    ElMessage.success('诊断报告生成成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '生成失败')
  } finally {
    loadingReport.value = false
  }
}

const loadConversations = async () => {
  if (!props.alert) return
  
  try {
    const data = await getConversations(props.alert.id)
    messages.value = data.messages || []
    scrollToBottom()
  } catch (error) {
    messages.value = []
  }
}

const sendMessage = async () => {
  if (!props.alert || !userInput.value.trim() || sendingMessage.value) return
  
  const message = userInput.value.trim()
  userInput.value = ''
  
  messages.value.push({ role: 'user', content: message })
  scrollToBottom()
  
  sendingMessage.value = true
  try {
    const data = await diagnosisChat(props.alert.id, message)
    messages.value.push({ role: 'assistant', content: data.message })
    scrollToBottom()
  } catch (error: any) {
    messages.value.push({
      role: 'assistant',
      content: `错误: ${error.response?.data?.detail || '请求失败'}`
    })
  } finally {
    sendingMessage.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(() => props.modelValue, (val) => {
  if (val && props.alert) {
    loadReport()
    loadConversations()
  } else {
    report.value = null
    messages.value = []
    userInput.value = ''
  }
})
</script>

<style scoped lang="less">
.diagnosis-content {
  max-height: 60vh;
  overflow-y: auto;
  font-family: var(--font-body);
}

.alert-info {
  margin-bottom: 20px;

  :deep(.el-descriptions) {
    .el-descriptions__label {
      background: var(--bg-tertiary);
      color: var(--neon-blue);
      font-weight: 600;
      font-family: var(--font-display);
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

:deep(.el-divider) {
  border-color: var(--border-light);
}

.diagnosis-report h4 {
  margin-bottom: 15px;
  color: var(--text-primary);
  font-family: var(--font-display);
  font-weight: 600;
}

.report-content {
  background: var(--bg-tertiary);
  padding: 20px;
  border-radius: 12px;
  line-height: 1.8;
  color: var(--text-secondary);
  border: 1px solid var(--border-light);

  :deep(h4) {
    margin: 15px 0 10px;
    color: var(--neon-blue);
    font-family: var(--font-display);
  }

  :deep(h5) {
    margin: 10px 0 8px;
    color: var(--neon-green);
    font-family: var(--font-display);
  }

  :deep(strong) {
    color: var(--neon-orange);
  }
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-tertiary);

  .el-icon {
    color: var(--neon-blue);
    font-size: 20px;
  }
}

.no-report {
  padding: 20px;

  :deep(.el-empty__description) {
    color: var(--text-tertiary);
  }

  :deep(.el-button--primary) {
    background: var(--gradient-neon);
    border: none;
    color: white;
    font-weight: 600;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
  }
}

.chat-section h4 {
  margin-bottom: 15px;
  color: var(--text-primary);
  font-family: var(--font-display);
  font-weight: 600;
}

.chat-messages {
  height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  background: var(--bg-tertiary);
}

.message {
  margin-bottom: 12px;
}

.message.user {
  text-align: right;
}

.message.user .message-content {
  background: var(--gradient-neon);
  color: white;
}

.message.assistant .message-content {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}

.message-content {
  display: inline-block;
  padding: 10px 16px;
  border-radius: 12px;
  max-width: 80%;
  font-size: 14px;
  line-height: 1.5;
}

.chat-input {
  :deep(.el-input__wrapper) {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-light);
    box-shadow: none;
    border-radius: 8px;

    &:hover {
      border-color: var(--border-medium);
    }

    &.is-focus {
      border-color: var(--neon-blue);
      box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
    }
  }

  :deep(.el-input__inner) {
    color: var(--text-primary);

    &::placeholder {
      color: var(--text-tertiary);
    }
  }

  :deep(.el-input-group__append) {
    background: var(--gradient-neon);
    border: none;
    padding: 0;

    .el-button {
      background: transparent;
      border: none;
      color: white;
      font-weight: 600;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }
    }
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
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  border: none;

  &.el-tag--danger {
    background: rgba(255, 0, 153, 0.15);
    color: var(--neon-pink);
  }

  &.el-tag--warning {
    background: rgba(255, 102, 0, 0.15);
    color: var(--neon-orange);
  }

  &.el-tag--info {
    background: rgba(0, 136, 255, 0.15);
    color: var(--neon-blue);
  }
}

.chat-messages {
  word-break: break-word;
}

.chat-input {
  display: flex;
  gap: 10px;
}
</style>
