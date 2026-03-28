<template>
  <div class="simulator-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">生产环境模拟器</h2>
        <span class="page-desc">模拟真实生产环境的指标、日志和故障场景</span>
      </div>
    </div>
    <div class="config-card">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import EnvironmentManagement from './EnvironmentManagement.vue'
import TemplateManagement from './TemplateManagement.vue'
import FaultManagement from './FaultManagement.vue'

const activeTab = ref('environments')
</script>

<style lang="less" scoped>
.simulator-container {
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

.config-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
  border-radius: 12px;

  :deep(.el-tabs__header) {
    background: rgba(0, 0, 0, 0.1);
    border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  }

  :deep(.el-tabs__item) {
    color: rgba(255, 255, 255, 0.6);

    &.is-active {
      color: #ffd700;
    }
  }

  :deep(.el-tabs__active-bar) {
    background: linear-gradient(135deg, #ffd700, #f72585);
  }

  :deep(.el-tabs__content) {
    padding: 24px;
  }
}
</style>
