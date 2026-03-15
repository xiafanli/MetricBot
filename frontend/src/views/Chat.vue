<template>
  <div class="chat-container">
    <div class="chat-main">
      <div v-if="messages.length === 0" class="welcome-section">
        <div class="welcome-content">
          <div class="welcome-icon">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="45" stroke="url(#chatGrad)" stroke-width="2" fill="none"/>
              <circle cx="50" cy="50" r="35" stroke="url(#chatGrad)" stroke-width="1.5" fill="none" opacity="0.7"/>
              <circle cx="50" cy="50" r="25" stroke="url(#chatGrad)" stroke-width="1" fill="none" opacity="0.5"/>
              <path d="M20 50 L40 50 M60 50 L80 50 M50 20 L50 40 M50 60 L50 80" stroke="url(#chatGrad)" stroke-width="2" stroke-linecap="round"/>
              <circle cx="50" cy="50" r="8" fill="url(#chatGrad)"/>
              <defs>
                <linearGradient id="chatGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#ffd700"/>
                  <stop offset="50%" style="stop-color:#ff6b35"/>
                  <stop offset="100%" style="stop-color:#f72585"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="welcome-title">你好，我是 Metric Bot</h1>
          <p class="welcome-desc">我可以帮你查询监控数据、分析告警、生成报表，用自然语言告诉我你想了解什么吧～</p>
          
          <div class="quick-questions">
            <div class="quick-title">快速提问</div>
            <div class="quick-list">
              <div 
                v-for="(question, index) in quickQuestions" 
                :key="index" 
                class="quick-item"
                @click="askQuestion(question)"
              >
                <el-icon class="quick-icon"><ChatDotRound /></el-icon>
                <span>{{ question }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="messages-section" ref="messagesRef">
        <div class="messages-list">
          <div 
            v-for="(message, index) in messages" 
            :key="index" 
            class="message-item"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar v-if="message.role === 'user'" :size="36" class="user-avatar">
                {{ userStore.getUsername?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div v-else class="ai-avatar">
                <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="50" cy="50" r="45" stroke="url(#msgGrad)" stroke-width="2" fill="none"/>
                  <circle cx="50" cy="50" r="8" fill="url(#msgGrad)"/>
                  <defs>
                    <linearGradient id="msgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#ffd700"/>
                      <stop offset="100%" style="stop-color:#f72585"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-name">{{ message.role === 'user' ? userStore.getUsername : 'Metric Bot' }}</span>
                <span class="message-time">{{ message.time }}</span>
              </div>
              <div class="message-body">
                <div v-if="message.role === 'assistant'" class="ai-response">
                  <div class="response-text">{{ message.content }}</div>
                  <div v-if="message.chart" class="response-chart">
                    <div class="chart-header">
                      <span class="chart-title">{{ message.chart.title }}</span>
                    </div>
                    <div class="chart-preview">
                      <div class="mock-line-chart">
                        <svg viewBox="0 0 300 100" preserveAspectRatio="none">
                          <polyline
                            :points="message.chart.points"
                            fill="none"
                            stroke="url(#lineGrad)"
                            stroke-width="2"
                          />
                          <defs>
                            <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                              <stop offset="0%" style="stop-color:#ffd700"/>
                              <stop offset="100%" style="stop-color:#f72585"/>
                            </linearGradient>
                          </defs>
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div v-if="message.sql" class="response-sql">
                    <div class="sql-header">
                      <span>生成的查询语句</span>
                      <el-button type="primary" link size="small" @click="copySQL(message.sql)">
                        <el-icon><CopyDocument /></el-icon>
                        复制
                      </el-button>
                    </div>
                    <pre class="sql-code">{{ message.sql }}</pre>
                  </div>
                </div>
                <div v-else class="user-text">{{ message.content }}</div>
              </div>
              <div v-if="message.role === 'assistant'" class="message-actions">
                <el-button text size="small" @click="regenerate(message)">
                  <el-icon><RefreshRight /></el-icon>
                  重新生成
                </el-button>
                <el-button text size="small" @click="copyResponse(message)">
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="input-section">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 6 }"
            placeholder="输入你的问题，例如：查询最近一小时的CPU使用率..."
            @keydown.enter.exact.prevent="sendMessage"
            class="chat-input"
          />
          <div class="input-actions">
            <el-tooltip content="清空对话" placement="top">
              <el-button circle text @click="clearMessages">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
            <el-button 
              type="primary" 
              circle 
              :loading="isSending"
              :disabled="!inputMessage.trim()"
              @click="sendMessage"
            >
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="input-tips">
          <span>按 Enter 发送，Shift + Enter 换行</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound,
  CopyDocument,
  RefreshRight,
  Delete,
  Promotion
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

interface Message {
  role: 'user' | 'assistant'
  content: string
  time: string
  sql?: string
  chart?: {
    title: string
    points: string
  }
}

const userStore = useUserStore()
const messagesRef = ref<HTMLElement | null>(null)
const messages = ref<Message[]>([])
const inputMessage = ref('')
const isSending = ref(false)

const quickQuestions = ref([
  '查询最近1小时的CPU使用率趋势',
  '分析当前活跃的告警分布情况',
  '对比本周和上周的系统性能',
  '帮我找出内存使用率最高的主机'
])

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isSending.value) return
  
  const userMessage: Message = {
    role: 'user',
    content: inputMessage.value.trim(),
    time: getCurrentTime()
  }
  
  messages.value.push(userMessage)
  inputMessage.value = ''
  isSending.value = true
  scrollToBottom()
  
  setTimeout(() => {
    const aiMessage: Message = {
      role: 'assistant',
      content: generateMockResponse(userMessage.content),
      time: getCurrentTime(),
      sql: generateMockSQL(userMessage.content),
      chart: {
        title: 'CPU使用率趋势',
        points: '0,80 30,65 60,75 90,55 120,70 150,45 180,60 210,50 240,65 270,55 300,70'
      }
    }
    messages.value.push(aiMessage)
    isSending.value = false
    scrollToBottom()
  }, 1500)
}

const askQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

const generateMockResponse = (question: string): string => {
  if (question.includes('CPU')) {
    return '根据查询结果，最近1小时的CPU使用率平均为 65.3%，峰值达到 89.2%。整体趋势平稳，但在 10:30 左右出现了一次明显的使用率上升，建议关注该时间段的进程活动。'
  } else if (question.includes('告警')) {
    return '当前共有 75 条活跃告警，其中严重级别 5 条，警告级别 23 条，信息级别 47 条。主要集中在 CPU 使用率过高和内存不足两类问题。'
  } else if (question.includes('内存')) {
    return '内存使用率最高的主机是 server-01，当前使用率为 92.3%。其次是 server-03 (87.5%) 和 server-07 (82.1%)。建议对这些主机进行内存扩容或优化。'
  }
  return '我已收到您的问题，正在分析相关数据。根据当前监控数据，系统整体运行正常，各项指标均在合理范围内。'
}

const generateMockSQL = (question: string): string => {
  if (question.includes('CPU')) {
    return `SELECT 
  time, 
  avg(cpu_usage) as cpu_usage 
FROM metrics 
WHERE metric = 'cpu_usage' 
  AND time > now() - interval '1 hour' 
GROUP BY time 
ORDER BY time;`
  }
  return `SELECT * FROM alerts WHERE status = 'active' ORDER BY created_at DESC;`
}

const clearMessages = () => {
  messages.value = []
  ElMessage.success('对话已清空')
}

const copySQL = (sql: string) => {
  navigator.clipboard.writeText(sql)
  ElMessage.success('已复制到剪贴板')
}

const copyResponse = (message: Message) => {
  navigator.clipboard.writeText(message.content)
  ElMessage.success('已复制到剪贴板')
}

const regenerate = (message: Message) => {
  ElMessage.info('正在重新生成回答...')
}
</script>

<style lang="less" scoped>
.chat-container {
  height: calc(100vh - 108px);
  display: flex;
  flex-direction: column;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.welcome-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.welcome-content {
  text-align: center;
  max-width: 600px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.7;
  margin: 0 0 32px;
}

.quick-questions {
  text-align: left;
  background: rgba(26, 26, 46, 0.4);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 215, 0, 0.1);
}

.quick-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
}

.quick-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 215, 0, 0.03);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);

  &:hover {
    background: rgba(255, 215, 0, 0.08);
    border-color: rgba(255, 215, 0, 0.3);
    color: white;
  }

  .quick-icon {
    color: #ffd700;
  }
}

.messages-section {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;

  &.user {
    flex-direction: row-reverse;

    .message-content {
      align-items: flex-end;
    }

    .message-body {
      background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(247, 37, 133, 0.15) 100%);
      border-radius: 16px 16px 4px 16px;
    }
  }
}

.message-avatar {
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #ffd700 0%, #f72585 100%);
}

.ai-avatar {
  width: 36px;
  height: 36px;
  background: rgba(255, 215, 0, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  svg {
    width: 24px;
    height: 24px;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 70%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}

.message-name {
  font-size: 13px;
  font-weight: 600;
  color: white;
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.message-body {
  padding: 14px 18px;
  background: rgba(26, 26, 46, 0.6);
  border-radius: 16px 16px 16px 4px;
  border: 1px solid rgba(255, 215, 0, 0.1);
}

.user-text {
  font-size: 14px;
  color: white;
  line-height: 1.6;
}

.ai-response {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.response-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.7;
}

.response-chart {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.chart-header {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  color: white;
}

.chart-preview {
  padding: 16px;
}

.mock-line-chart {
  height: 80px;

  svg {
    width: 100%;
    height: 100%;
  }
}

.response-sql {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.sql-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(255, 215, 0, 0.05);
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.sql-code {
  margin: 0;
  padding: 14px;
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 12px;
  color: #ffd700;
  overflow-x: auto;
  white-space: pre-wrap;
}

.message-actions {
  display: flex;
  gap: 8px;
  padding: 0 4px;

  .el-button {
    color: rgba(255, 215, 0, 0.6);

    &:hover {
      color: #ffd700;
    }
  }
}

.input-section {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 215, 0, 0.1);
  background: rgba(26, 26, 46, 0.4);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  max-width: 900px;
  margin: 0 auto;
}

.chat-input {
  flex: 1;

  :deep(.el-textarea__inner) {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 215, 0, 0.2);
    border-radius: 12px;
    color: white;
    font-size: 14px;
    padding: 14px 16px;
    resize: none;
    line-height: 1.5;
    min-height: 44px;
    box-shadow: none;
    transition: all 0.2s;

    &::placeholder {
      color: rgba(255, 255, 255, 0.3);
    }

    &:focus {
      border-color: rgba(255, 215, 0, 0.5);
      box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.1);
      background: rgba(0, 0, 0, 0.5);
    }

    &:hover:not(:focus) {
      border-color: rgba(255, 215, 0, 0.3);
    }
  }
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 4px;

  .el-button {
    &.is-circle {
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  .el-button--primary {
    background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
    border: none;
    color: #0a0a0a;
    font-weight: 600;

    &:hover {
      box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
      transform: translateY(-1px);
    }

    &:active {
      transform: translateY(0);
    }

    &.is-disabled {
      opacity: 0.5;
      cursor: not-allowed;

      &:hover {
        box-shadow: none;
        transform: none;
      }
    }
  }

  .el-button.is-text {
    color: rgba(255, 215, 0, 0.6);
    background: rgba(255, 215, 0, 0.05);
    border: 1px solid rgba(255, 215, 0, 0.2);

    &:hover {
      color: #ffd700;
      background: rgba(255, 215, 0, 0.1);
      border-color: rgba(255, 215, 0, 0.4);
    }

    &:active {
      transform: scale(0.95);
    }
  }
}

.input-tips {
  max-width: 900px;
  margin: 8px auto 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
}
</style>
