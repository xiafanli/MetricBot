# 智能告警模块开发进度

## 已完成工作 (Phase 1)

### 后端实现
- [x] 数据库模型更新 (`backend/apps/alert/models.py`)
  - AlertEvent: 告警事件模型
  - DiagnosisReport: 诊断报告模型
  - DiagnosisConversation: 诊断对话模型

- [x] Pydantic Schemas (`backend/apps/alert/schemas.py`)
  - 告警规则和事件的请求/响应模型

- [x] 告警评估引擎
  - `backend/apps/alert/engine/evaluator.py`: 规则评估逻辑
  - `backend/apps/alert/engine/scheduler.py`: 定时调度器

- [x] AI诊断模块 (`backend/apps/alert/diagnosis/analyzer.py`)
  - 集成大模型进行告警诊断分析

- [x] API路由更新 (`backend/apps/alert/router.py`)
  - 告警规则 CRUD 接口
  - 告警列表查询接口
  - 告警统计接口
  - AI诊断接口

- [x] 调度器集成 (`backend/main.py`)
  - 应用启动时初始化告警评估调度器

### 前端实现
- [x] API接口定义 (`frontend/src/api/alert.ts`)
  - 告警规则、告警列表、诊断相关接口

- [x] 路由配置 (`frontend/src/router/index.ts`)
  - `/alerts/rules`: 告警规则页面
  - `/alerts/list`: 告警列表页面

- [x] 告警规则管理页面 (`frontend/src/views/alert/AlertRules.vue`)
  - 规则列表展示
  - 新建/编辑/删除规则
  - 启用/禁用规则

- [x] 告警列表页面 (`frontend/src/views/alert/AlertList.vue`)
  - 告警列表展示
  - 状态筛选
  - 告警确认/恢复

- [x] AI诊断对话框 (`frontend/src/views/alert/DiagnosisDialog.vue`)
  - 诊断报告展示
  - 多轮对话交互

- [x] 侧边栏菜单更新 (`frontend/src/views/Layout.vue`)
  - "智能监控"改为子菜单形式
  - 包含"告警规则"和"告警列表"子项

### Bug修复
- [x] 修复 `frontend/src/api/index.ts` 缺少默认导出问题
- [x] 修复 `EnvironmentManagement.vue` 类型导入语法问题

---

## 待完成工作

### Phase 2: 告警聚合与根因分析
- [ ] 告警聚合算法实现
  - 相似告警合并
  - 告警风暴检测
  - 告警降噪策略

- [ ] 根因分析模块
  - 基于拓扑的关联分析
  - 时序相关性分析
  - 根因定位算法

### Phase 3: 智能异常检测
- [ ] 异常检测引擎
  - 基于统计的异常检测
  - 时序预测模型
  - 动态阈值调整

- [ ] 高级诊断功能
  - 自动化诊断报告
  - 修复建议生成
  - 历史案例匹配

### 其他优化项
- [ ] 告警通知渠道集成 (邮件、钉钉、企业微信等)
- [ ] 告警静默/维护窗口功能
- [ ] 告警升级策略
- [ ] 诊断历史记录查询
- [ ] 告警趋势分析图表

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                          │
├─────────────────────────────────────────────────────────────┤
│  AlertRules.vue    │  AlertList.vue    │  DiagnosisDialog  │
├─────────────────────────────────────────────────────────────┤
│                     API Layer (Axios)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     后端 (FastAPI)                           │
├─────────────────────────────────────────────────────────────┤
│  Router (API)  │  Evaluator  │  Scheduler  │  Analyzer      │
├─────────────────────────────────────────────────────────────┤
│                     Database (MySQL)                         │
│  AlertRule  │  AlertEvent  │  DiagnosisReport  │  ...       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   外部系统                                   │
│  Prometheus  │  Pushgateway  │  Model Service (LLM)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-03-29 | Phase 1 基础告警功能完成，侧边栏菜单优化，Bug修复 |
