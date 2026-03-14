<template>
  <div class="home">
    <el-container>
      <el-header>
        <h1>PrometheusBot</h1>
        <p>基于大语言模型的 Prometheus 监控查询助手</p>
      </el-header>
      <el-main>
        <el-card>
          <template #header>
            <div class="card-header">
              <span>欢迎使用 PrometheusBot</span>
            </div>
          </template>
          <p>这是一个简单的项目框架，更多功能正在开发中...</p>
          <el-button type="primary" @click="checkHealth">检查后端连接</el-button>
          <div v-if="healthStatus" class="status">
            <el-alert
              :title="healthStatus.message"
              type="success"
              :closable="false"
              show-icon
            />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/api'

const healthStatus = ref<any>(null)

const checkHealth = async () => {
  try {
    const response = await api.healthCheck()
    healthStatus.value = response
  } catch (error) {
    console.error('Health check failed:', error)
  }
}
</script>

<style scoped>
.home {
  height: 100vh;
}

.el-header {
  background-color: #409eff;
  color: white;
  text-align: center;
  padding: 20px;
}

.el-header h1 {
  margin: 0 0 10px 0;
}

.el-header p {
  margin: 0;
  opacity: 0.9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status {
  margin-top: 20px;
}
</style>