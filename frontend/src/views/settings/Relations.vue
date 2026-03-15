<template>
  <div class="relations-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">关系模型</h2>
        <span class="page-desc">配置和管理主机、服务间的关联关系</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加关系
        </el-button>
      </div>
    </div>

    <div class="relations-section">
      <div class="section-header">
        <span class="section-title">关系列表</span>
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="list">列表视图</el-radio-button>
          <el-radio-button label="graph">拓扑视图</el-radio-button>
        </el-radio-group>
      </div>

      <div v-if="viewMode === 'list'" class="relations-list">
        <div 
          v-for="relation in relations" 
          :key="relation.id" 
          class="relation-card"
        >
          <div class="relation-flow">
            <div class="node source">
              <div class="node-icon">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="node-info">
                <div class="node-name">{{ relation.source }}</div>
                <div class="node-type">{{ relation.sourceType }}</div>
              </div>
            </div>
            
            <div class="relation-arrow">
              <div class="arrow-line"></div>
              <div class="arrow-label">{{ relation.type }}</div>
              <div class="arrow-head"></div>
            </div>
            
            <div class="node target">
              <div class="node-icon">
                <el-icon><Service /></el-icon>
              </div>
              <div class="node-info">
                <div class="node-name">{{ relation.target }}</div>
                <div class="node-type">{{ relation.targetType }}</div>
              </div>
            </div>
          </div>
          
          <div class="relation-meta">
            <div class="meta-item">
              <span class="meta-label">数据来源</span>
              <el-tag size="small">{{ relation.source }}</el-tag>
            </div>
            <div class="meta-item">
              <span class="meta-label">发现时间</span>
              <span class="meta-value">{{ relation.discoveredAt }}</span>
            </div>
          </div>
          
          <div class="relation-actions">
            <el-button text size="small" @click="editRelation(relation)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button text size="small" class="delete-btn" @click="deleteRelation(relation)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="relations-graph">
        <div class="graph-placeholder">
          <div class="graph-nodes">
            <div v-for="node in graphNodes" :key="node.id" 
                 class="graph-node"
                 :style="{ left: node.x + 'px', top: node.y + 'px' }"
            >
              <div class="node-circle" :style="{ background: node.color }">
                {{ node.name.charAt(0) }}
              </div>
              <div class="node-label">{{ node.name }}</div>
            </div>
          </div>
          <svg class="graph-lines">
            <line v-for="line in graphLines" :key="line.id"
                  :x1="line.x1" :y1="line.y1"
                  :x2="line.x2" :y2="line.y2"
                  stroke="rgba(255, 215, 0, 0.3)"
                  stroke-width="2"
            />
          </svg>
        </div>
      </div>
    </div>

    <el-dialog 
      v-model="dialogVisible" 
      title="添加关系"
      width="500px"
    >
      <el-form :model="relationForm" label-width="100px" class="config-form relation-form">
        <el-form-item label="源节点" required>
          <el-select v-model="relationForm.source" placeholder="选择源节点">
            <el-option label="prod-web-01" value="prod-web-01" />
            <el-option label="prod-web-02" value="prod-web-02" />
            <el-option label="prod-db-01" value="prod-db-01" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关系类型" required>
          <el-select v-model="relationForm.type" placeholder="选择关系类型">
            <el-option label="依赖" value="依赖" />
            <el-option label="调用" value="调用" />
            <el-option label="包含" value="包含" />
            <el-option label="连接" value="连接" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标节点" required>
          <el-select v-model="relationForm.target" placeholder="选择目标节点">
            <el-option label="prod-db-01" value="prod-db-01" />
            <el-option label="prod-cache-01" value="prod-cache-01" />
            <el-option label="prod-web-02" value="prod-web-02" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="数据来源">
          <el-select v-model="relationForm.dataSource" placeholder="选择来源">
            <el-option label="自动发现" value="自动发现" />
            <el-option label="API上报" value="API上报" />
            <el-option label="手工配置" value="手工配置" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input v-model="relationForm.remark" type="textarea" :rows="2" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRelation">保存</el-button>
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
  Monitor,
  Service
} from '@element-plus/icons-vue'

interface Relation {
  id: number
  source: string
  sourceType: string
  target: string
  targetType: string
  type: string
  dataSource: string
  discoveredAt: string
}

const viewMode = ref('list')
const dialogVisible = ref(false)

const relations = ref<Relation[]>([
  {
    id: 1,
    source: 'prod-web-01',
    sourceType: '主机',
    target: 'MySQL服务',
    targetType: '服务',
    type: '依赖',
    dataSource: '自动发现',
    discoveredAt: '2026-03-15 10:30'
  },
  {
    id: 2,
    source: 'prod-web-01',
    sourceType: '主机',
    target: 'Redis集群',
    targetType: '服务',
    type: '连接',
    dataSource: 'API上报',
    discoveredAt: '2026-03-15 09:15'
  },
  {
    id: 3,
    source: 'prod-web-02',
    sourceType: '主机',
    target: 'MySQL服务',
    targetType: '服务',
    type: '依赖',
    dataSource: '手工配置',
    discoveredAt: '2026-03-14 16:20'
  }
])

const graphNodes = ref([
  { id: 1, name: 'prod-web-01', x: 100, y: 100, color: 'linear-gradient(135deg, #ffd700 0%, #ff6b35 100%)' },
  { id: 2, name: 'prod-web-02', x: 100, y: 250, color: 'linear-gradient(135deg, #ffd700 0%, #ff6b35 100%)' },
  { id: 3, name: 'MySQL服务', x: 350, y: 175, color: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' },
  { id: 4, name: 'Redis集群', x: 350, y: 50, color: 'linear-gradient(135deg, #f72585 0%, #b5179e 100%)' }
])

const graphLines = ref([
  { id: 1, x1: 150, y1: 120, x2: 320, y2: 175 },
  { id: 2, x1: 150, y1: 100, x2: 320, y2: 70 },
  { id: 3, x1: 150, y1: 270, x2: 320, y2: 175 }
])

const relationForm = ref({
  source: '',
  type: '依赖',
  target: '',
  dataSource: '手工配置',
  remark: ''
})

const showAddDialog = () => {
  relationForm.value = {
    source: '',
    type: '依赖',
    target: '',
    dataSource: '手工配置',
    remark: ''
  }
  dialogVisible.value = true
}

const editRelation = (relation: Relation) => {
  ElMessage.info(`编辑关系: ${relation.source} -> ${relation.target}`)
}

const deleteRelation = async (relation: Relation) => {
  try {
    await ElMessageBox.confirm(`确定要删除此关系吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = relations.value.findIndex(r => r.id === relation.id)
    if (index > -1) {
      relations.value.splice(index, 1)
      ElMessage.success('关系已删除')
    }
  } catch {
    // 取消删除
  }
}

const saveRelation = () => {
  if (!relationForm.value.source || !relationForm.value.target) {
    ElMessage.warning('请填写必填项')
    return
  }

  relations.value.unshift({
    id: Date.now(),
    source: relationForm.value.source,
    sourceType: '主机',
    target: relationForm.value.target,
    targetType: '服务',
    type: relationForm.value.type,
    dataSource: relationForm.value.dataSource,
    discoveredAt: new Date().toLocaleString('zh-CN')
  })
  
  ElMessage.success('关系已添加')
  dialogVisible.value = false
}
</script>

<style lang="less" scoped>
.relations-container {
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

.relations-section {
  border-radius: 12px;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(255, 215, 0, 0.1);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.relations-list {
  display: flex;
  flex-direction: column;
}

.relation-card {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.05);

  &:last-child {
    border-bottom: none;
  }
}

.relation-flow {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
}

.node {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(255, 215, 0, 0.05);
  border: 1px solid rgba(255, 215, 0, 0.2);
  min-width: 140px;
}

.node-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(255, 215, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffd700;
  font-size: 18px;
}

.node-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.node-name {
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.node-type {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.relation-arrow {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

.arrow-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, rgba(255, 215, 0, 0.3) 0%, rgba(247, 37, 133, 0.3) 100%);
}

.arrow-label {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  padding: 4px 12px;
  background: rgba(26, 26, 46, 0.9);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  font-size: 12px;
  color: #ffd700;
  white-space: nowrap;
}

.arrow-head {
  width: 0;
  height: 0;
  border-left: 8px solid rgba(247, 37, 133, 0.5);
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
}

.relation-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.meta-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.relation-actions {
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

.relations-graph {
  padding: 40px;
  min-height: 400px;
}

.graph-placeholder {
  position: relative;
  height: 350px;
}

.graph-nodes {
  position: relative;
  height: 100%;
}

.graph-node {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.node-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.node-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  white-space: nowrap;
}

.graph-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.relation-form {
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
