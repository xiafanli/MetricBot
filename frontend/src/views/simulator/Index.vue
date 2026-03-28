<template>
  <div class="simulator-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>生产环境模拟器</span>
        </div>
      </template>
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="环境管理" name="environments">
          <EnvironmentManagement />
        </el-tab-pane>
        <el-tab-pane label="模板管理" name="templates">
          <TemplateManagement />
        </el-tab-pane>
        <el-tab-pane label="故障场景" name="faults">
          <FaultManagement />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import EnvironmentManagement from './EnvironmentManagement.vue'
import TemplateManagement from './TemplateManagement.vue'
import FaultManagement from './FaultManagement.vue'

const activeTab = ref('environments')
</script>

<style scoped>
.simulator-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
