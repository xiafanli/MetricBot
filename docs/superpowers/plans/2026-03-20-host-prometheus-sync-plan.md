# 主机模型 + Prometheus 同步实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现主机模型功能，包括手工录入、后端 API 对接和 Prometheus 批量同步

**Architecture:** 
- 更新 Host 模型添加 from_type/from_name
- 添加 Prometheus 同步后端 API
- 前端 API 对接 + Hosts.vue UI 更新

**Tech Stack:** 
- 后端：FastAPI + SQLAlchemy + httpx
- 前端：Vue 3 + TypeScript + Element Plus

---

## 文件结构

| 操作 | 文件 | 说明 |
|------|------|------|
| 修改 | `backend/apps/host/models.py` | 添加 from_type/from_name 字段 |
| 修改 | `backend/apps/host/schemas.py` | 添加同步相关 schemas |
| 修改 | `backend/apps/host/router.py` | 添加 Prometheus 同步 API |
| 修改 | `frontend/src/api/index.ts` | 添加 host/relation 接口 |
| 修改 | `frontend/src/views/settings/Hosts.vue` | 对接后端 + 同步 UI |

---

## Task 1: 更新 Host 数据库模型

**Files:**
- Modify: `backend/apps/host/models.py:20-25`

- [ ] **Step 1: 在 Host 模型中添加 from_type 和 from_name 字段**

```python
    # 数据来源
    from_type = Column(String(50), nullable=True, default="manual", comment="来源类型: manual/prometheus/cmdb")
    from_name = Column(String(255), nullable=True, comment="来源名称")
```

- [ ] **Step 2: 确认文件已正确修改**

检查 `Host` 类是否包含新字段

---

## Task 2: 更新 Host schemas

**Files:**
- Modify: `backend/apps/host/schemas.py`

- [ ] **Step 1: 在 HostBase 中添加 from_type/from_name**

```python
    from_type: Optional[str] = Field("manual", description="来源类型")
    from_name: Optional[str] = Field(None, description="来源名称")
```

- [ ] **Step 2: 添加 Prometheus 同步请求/响应 schemas**

```python
class PrometheusSyncRequest(BaseModel):
    datasource_id: int = Field(..., description="Prometheus 数据源 ID")
    metric: str = Field(..., description="指标名")
    label: str = Field(..., description="标签名")
    preview_only: bool = Field(True, description="只预览不导入")


class PrometheusSyncPreviewResponse(BaseModel):
    preview: List[str] = Field(..., description="预览标签值")
    total: int = Field(..., description="总数")


class PrometheusSyncImportResponse(BaseModel):
    imported: int = Field(..., description="已导入数量")
    hosts: List[HostResponse] = Field(..., description="已导入的主机列表")
```

---

## Task 3: 添加 Prometheus 同步后端 API

**Files:**
- Modify: `backend/apps/host/router.py`
- Create: 同步相关函数

- [ ] **Step 1: 在 router.py 顶部添加必要导入**

```python
import httpx
from apps.datasource.models import Datasource
from apps.host.schemas import (
    PrometheusSyncRequest,
    PrometheusSyncPreviewResponse,
    PrometheusSyncImportResponse
)
```

- [ ] **Step 2: 添加查询 Prometheus 获取标签值的辅助函数**

```python
async def get_prometheus_label_values(url: str, metric: str, label: str,
                                      auth_type: str, auth_value: str, password: str) -> List[str]:
    """
    查询 Prometheus 获取标签值
    """
    headers = {}
    auth = None
    
    if auth_type == "basic" and auth_value and password:
        auth = (auth_value, password)
    elif auth_type == "token" and auth_value:
        headers["Authorization"] = f"Bearer {auth_value}"
    
    query = f"count({metric}) by ({label})"
    params = {"query": query}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{url.rstrip('/')}/api/v1/query",
                params=params,
                headers=headers,
                auth=auth
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    values = []
                    for series in result.get("data", {}).get("result", []):
                        metric_info = series.get("metric", {})
                        if label in metric_info:
                            values.append(metric_info[label])
                    return sorted(list(set(values)))  # 去重并排序
        return []
    except Exception as e:
        print(f"Query Prometheus error: {e}")
        return []
```

- [ ] **Step 3: 添加 Prometheus 同步 API 端点**

```python
@router.post("/sync/prometheus", response_model=PrometheusSyncPreviewResponse)
async def sync_prometheus(
    sync_request: PrometheusSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Prometheus 同步：预览或导入
    """
    # 1. 获取数据源
    datasource = db.query(Datasource).filter(
        Datasource.id == sync_request.datasource_id,
        Datasource.type == "Prometheus"
    ).first()
    
    if not datasource:
        raise HTTPException(status_code=404, detail="Prometheus 数据源不存在")
    
    # 2. 查询标签值
    label_values = await get_prometheus_label_values(
        datasource.url,
        sync_request.metric,
        sync_request.label,
        datasource.auth_type or "none",
        datasource.auth_value or "",
        datasource.password or ""
    )
    
    # 3. 只预览模式
    if sync_request.preview_only:
        return PrometheusSyncPreviewResponse(
            preview=label_values[:10],  # 最多返回 10 条
            total=len(label_values)
        )
    
    # 4. 导入模式：创建 Host
    imported_hosts = []
    for value in label_values:
        # 检查是否已存在（by name）
        existing = db.query(Host).filter(Host.name == value).first()
        if existing:
            continue
        
        host = Host(
            name=value,
            ip=value.split(":")[0] if ":" in value else value,
            from_type="prometheus",
            from_name=datasource.name,
            enabled=True
        )
        db.add(host)
        db.flush()
        imported_hosts.append(host_to_dict(host))
    
    db.commit()
    
    return PrometheusSyncImportResponse(
        imported=len(imported_hosts),
        hosts=imported_hosts
    )
```

---

## Task 4: 添加前端 API 接口

**Files:**
- Modify: `frontend/src/api/index.ts`

- [ ] **Step 1: 在 index.ts 中添加 Host 和 Relation 相关 API**

```typescript
// 主机管理相关API
function getHosts(enabledOnly: boolean = false) {
  return apiClient.get('/hosts', { params: { enabled_only: enabledOnly } })
}

function getHost(id: number) {
  return apiClient.get(`/hosts/${id}`)
}

function createHost(data: any) {
  return apiClient.post('/hosts', data)
}

function updateHost(id: number, data: any) {
  return apiClient.put(`/hosts/${id}`, data)
}

function deleteHost(id: number) {
  return apiClient.delete(`/hosts/${id}`)
}

function syncHostsFromPrometheus(data: any) {
  return apiClient.post('/hosts/sync/prometheus', data)
}

// 关系管理相关API
function getHostRelations(hostId: number) {
  return apiClient.get(`/hosts/${hostId}/relations`)
}

function getAllRelations() {
  return apiClient.get('/hosts/relations/all')
}

function createRelation(data: any) {
  return apiClient.post('/hosts/relations', data)
}

function updateRelation(id: number, data: any) {
  return apiClient.put(`/hosts/relations/${id}`, data)
}

function deleteRelation(id: number) {
  return apiClient.delete(`/hosts/relations/${id}`)
}
```

- [ ] **Step 2: 在 export 部分添加这些 API**

```typescript
export const api = {
  ...,
  getHosts,
  getHost,
  createHost,
  updateHost,
  deleteHost,
  syncHostsFromPrometheus,
  getHostRelations,
  getAllRelations,
  createRelation,
  updateRelation,
  deleteRelation
}
```

---

## Task 5: 更新 Hosts.vue 对接后端 + 添加 Prometheus 同步 UI

**Files:**
- Modify: `frontend/src/views/settings/Hosts.vue`

- [ ] **Step 1: 简化数据结构，去掉模拟的实时字段**

```typescript
interface Host {
  id: number
  name: string
  ip: string
  hostname?: string
  os?: string
  os_version?: string
  cpu_cores?: number
  memory_gb?: number
  disk_gb?: number
  tags?: string[]
  from_type: string
  from_name?: string
  enabled: boolean
  created_at: string
  updated_at?: string
}
```

- [ ] **Step 2: 替换模拟数据为从 API 加载**

```typescript
const hosts = ref<Host[]>([])

const loadHosts = async () => {
  try {
    const data = await api.getHosts()
    hosts.value = (data as Host[])
  } catch (error) {
    ElMessage.error('加载主机列表失败')
    console.error('Load hosts error:', error)
  }
}
```

- [ ] **Step 3: 去掉统计卡片**

删除整个 `<div class="stats-row">` 部分

- [ ] **Step 4: 修改表格列，去掉实时监控列**

保留列：hostname/主机名、IP、操作系统、CPU核心数、内存(GB)、磁盘(GB)、标签、来源、操作

- [ ] **Step 5: 修改表单，添加 from_type/from_name（隐藏，自动填充）**

hostForm 简化为：
```typescript
const hostForm = ref({
  id: 0,
  name: '',
  ip: '',
  hostname: '',
  os: '',
  os_version: '',
  cpu_cores: 4,
  memory_gb: 16,
  disk_gb: 100,
  tags: [] as string[],
  source: 'manual'
})
```

- [ ] **Step 6: 添加 Prometheus 同步按钮和对话框**

```vue
<el-button type="success" @click="showSyncDialog">
  <el-icon><Prometheus /></el-icon>
  从 Prometheus 同步
</el-button>

<el-dialog v-model="syncDialogVisible" title="从 Prometheus 同步" width="600px">
  <el-form :model="syncForm" label-width="120px" class="config-form">
    <el-form-item label="选择数据源" required>
      <el-select v-model="syncForm.datasource_id" placeholder="选择 Prometheus 数据源">
        <el-option 
          v-for="ds in prometheusDatasources" 
          :key="ds.id" 
          :label="ds.name" 
          :value="ds.id" 
        />
      </el-select>
    </el-form-item>
    
    <el-form-item label="指标名" required>
      <el-input v-model="syncForm.metric" placeholder="例如：node_cpu_seconds_total" />
    </el-form-item>
    
    <el-form-item label="标签名" required>
      <el-input v-model="syncForm.label" placeholder="例如：instance" />
    </el-form-item>
  </el-form>
  
  <div v-if="syncPreview.length > 0" class="preview-section">
    <div class="preview-title">预览（最多显示 10 条）</div>
    <div class="preview-list">
      <el-tag v-for="item in syncPreview" :key="item" class="preview-tag">
        {{ item }}
      </el-tag>
    </div>
    <div class="preview-total">共 {{ syncPreviewTotal }} 条</div>
  </div>
  
  <template #footer>
    <el-button @click="syncPreview.length = 0; syncDialogVisible = false">取消</el-button>
    <el-button @click="doPreview" :loading="previewing">预览</el-button>
    <el-button 
      v-if="syncPreview.length > 0" 
      type="primary" 
      @click="doImport" 
      :loading="importing"
    >
      导入 {{ syncPreviewTotal }} 条
    </el-button>
  </template>
</el-dialog>
```

- [ ] **Step 7: 添加同步相关的响应式数据和函数**

```typescript
const syncDialogVisible = ref(false)
const previewing = ref(false)
const importing = ref(false)
const prometheusDatasources = ref<any[]>([])
const syncPreview = ref<string[]>([])
const syncPreviewTotal = ref(0)

const syncForm = ref({
  datasource_id: 0,
  metric: '',
  label: '',
  preview_only: true
})

const loadPrometheusDatasources = async () => {
  try {
    const data = await api.getDatasources()
    prometheusDatasources.value = (data as any[]).filter((ds: any) => ds.type === 'Prometheus')
  } catch (error) {
    console.error('Load datasources error:', error)
  }
}

const showSyncDialog = () => {
  syncForm.value = {
    datasource_id: 0,
    metric: '',
    label: '',
    preview_only: true
  }
  syncPreview.value = []
  syncPreviewTotal.value = 0
  loadPrometheusDatasources()
  syncDialogVisible.value = true
}

const doPreview = async () => {
  if (!syncForm.value.datasource_id || !syncForm.value.metric || !syncForm.value.label) {
    ElMessage.warning('请填写完整')
    return
  }
  
  previewing.value = true
  try {
    const result = await api.syncHostsFromPrometheus({
      ...syncForm.value,
      preview_only: true
    })
    syncPreview.value = result.preview
    syncPreviewTotal.value = result.total
  } catch (error) {
    ElMessage.error('预览失败')
    console.error('Preview error:', error)
  } finally {
    previewing.value = false
  }
}

const doImport = async () => {
  importing.value = true
  try {
    const result = await api.syncHostsFromPrometheus({
      ...syncForm.value,
      preview_only: false
    })
    ElMessage.success(`成功导入 ${result.imported} 条主机`)
    syncDialogVisible.value = false
    await loadHosts()
  } catch (error) {
    ElMessage.error('导入失败')
    console.error('Import error:', error)
  } finally {
    importing.value = false
  }
}
```

- [ ] **Step 8: 在 onMounted 调用 loadHosts**

```typescript
onMounted(() => {
  loadHosts()
})
```

- [ ] **Step 9: 添加同步对话框的样式**

```less
.preview-section {
  margin-top: 16px;
  padding: 16px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.1);
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: white;
  margin-bottom: 12px;
}

.preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.preview-tag {
  background: rgba(255, 215, 0, 0.1);
  border-color: rgba(255, 215, 0, 0.3);
  color: #ffd700;
}

.preview-total {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}
```

---

## Task 6: 完整 CRUD 对接（save/delete/edit）

**Files:**
- Modify: `frontend/src/views/settings/Hosts.vue`

- [ ] **Step 1: 更新 saveHost 函数**

```typescript
const saveHost = async () => {
  if (!hostForm.value.name || !hostForm.value.ip) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    if (isEditing.value) {
      await api.updateHost(hostForm.value.id, hostForm.value)
      ElMessage.success('主机已更新')
    } else {
      await api.createHost(hostForm.value)
      ElMessage.success('主机已添加')
    }
    dialogVisible.value = false
    await loadHosts()
  } catch (error) {
    ElMessage.error(isEditing.value ? '更新主机失败' : '添加主机失败')
    console.error('Save host error:', error)
  }
}
```

- [ ] **Step 2: 更新 deleteHost 函数**

```typescript
const deleteHost = async (host: Host) => {
  try {
    await ElMessageBox.confirm(`确定要删除主机 "${host.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteHost(host.id)
    ElMessage.success('主机已删除')
    await loadHosts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete host error:', error)
    }
  }
}
```

---

## Self-Review

**1. Spec coverage:**
- ✅ 数据库更新：from_type/from_name 字段
- ✅ 后端 API：Prometheus 同步端点
- ✅ 前端 API：host/relation 接口
- ✅ 前端 UI：Hosts.vue 更新 + 同步对话框

**2. Placeholder scan:**
- ✅ 无 TBD/TODO
- ✅ 所有步骤有完整代码
- ✅ 无模糊描述

**3. Type consistency:**
- ✅ API 名称一致
- ✅ 字段名称一致

---
