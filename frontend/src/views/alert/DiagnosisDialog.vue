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

<style scoped>
.diagnosis-content {
  max-height: 60vh;
  overflow-y: auto;
}

.alert-info {
  margin-bottom: 20px;
}

.diagnosis-report h4 {
  margin-bottom: 15px;
  color: #303133;
}

.report-content {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  line-height: 1.8;
}

.report-content :deep(h4) {
  margin: 15px 0 10px;
  color: #409eff;
}

.report-content :deep(h5) {
  margin: 10px 0 8px;
  color: #67c23a;
}

.report-content :deep(strong) {
  color: #e6a23c;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  color: #909399;
}

.no-report {
  padding: 20px;
}

.chat-section h4 {
  margin-bottom: 15px;
  color: #303133;
}

.chat-messages {
  height: 200px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background: #fafafa;
}

.message {
  margin-bottom: 10px;
}

.message.user {
  text-align: right;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

.message.assistant .message-content {
  background: #e4e7ed;
  color: #303133;
}

.message-content {
  display: inline-block;
  padding: 8px 15px;
  border-radius: 8px;
  max-width: 80%;
  word-break: break-word;
}

.chat-input {
  display: flex;
  gap: 10px;
}
</style>
