# 智能告警模块设计文档

> 创建时间：2026-03-28
> 版本：v1.0

---

## 一、概述

### 1.1 背景
传统阈值告警存在告警风暴、噪音多、缺乏上下文、难以定位根因等问题。

### 1.2 目标
构建智能告警系统，实现：
- 告警聚合与降噪
- 根因分析
- AI 辅助诊断

### 1.3 实施策略
采用渐进式实现，分三个阶段：

| 阶段 | 内容 | 价值 |
|------|------|------|
| **Phase 1** | 基础告警 + 前端页面 + AI 诊断 | 可用的智能告警系统 |
| **Phase 2** | 告警聚合 + 根因分析 | 智能降噪 |
| **Phase 3** | 异常检测 + 高级诊断 | 智能检测 |

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      智能告警系统                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 告警规则    │  │ 异常检测    │  │ 告警列表    │            │
│  │ 管理        │  │ 配置        │  │ 展示        │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│              ┌─────────────────────┐                           │
│              │   告警评估引擎      │                           │
│              │  - 阈值规则评估     │                           │
│              │  - 异常检测评估     │                           │
│              │  - 批量查询优化     │                           │
│              └──────────┬──────────┘                           │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                           │
│              │   智能分析引擎      │                           │
│              │  - 告警聚合         │                           │
│              │  - 根因分析         │                           │
│              │  - AI 诊断          │                           │
│              └──────────┬──────────┘                           │
│                         │                                       │
│         ┌───────────────┼───────────────┐                      │
│         ▼               ▼               ▼                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ 告警事件    │ │ 诊断报告    │ │ 通知渠道    │              │
│  │ 存储        │ │ 存储        │ │ 推送        │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、Phase 1 详细设计

### 3.1 数据库设计

#### 3.1.1 保留现有表

**alert_rules** - 告警规则（已有，不变）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(255) | 规则名称 |
| datasource_id | INT | 数据源ID |
| datasource_type | VARCHAR(50) | 数据源类型 |
| metric_query | VARCHAR(500) | 指标查询 |
| condition_type | VARCHAR(50) | 条件类型 |
| threshold | DECIMAL(10,2) | 阈值 |
| severity | VARCHAR(50) | 严重程度 |
| evaluation_interval | INT | 评估间隔(秒) |
| enabled | BOOLEAN | 是否启用 |

**alerts** - 告警记录（已有，不变）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| rule_id | INT | 规则ID |
| rule_name | VARCHAR(255) | 规则名称快照 |
| severity | VARCHAR(50) | 严重程度 |
| metric_value | DECIMAL(10,2) | 指标值 |
| threshold | DECIMAL(10,2) | 阈值 |
| message | TEXT | 告警消息 |
| resolved | BOOLEAN | 是否已恢复 |
| resolved_at | DATETIME | 恢复时间 |

#### 3.1.2 新增表

**alert_events** - 告警事件（聚合后的告警）

```sql
CREATE TABLE alert_events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL COMMENT '事件标题',
    severity VARCHAR(50) NOT NULL COMMENT '严重程度',
    alert_ids JSON COMMENT '关联告警ID列表',
    status VARCHAR(50) DEFAULT 'active' COMMENT '状态: active/resolved',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL COMMENT '恢复时间',
    
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

**diagnosis_reports** - AI 诊断报告

```sql
CREATE TABLE diagnosis_reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alert_id INT NOT NULL COMMENT '告警ID',
    report TEXT COMMENT '诊断报告内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_alert_id (alert_id)
);
```

**diagnosis_conversations** - 诊断对话记录

```sql
CREATE TABLE diagnosis_conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alert_id INT NOT NULL COMMENT '告警ID',
    user_id INT NOT NULL COMMENT '用户ID',
    messages JSON COMMENT '对话消息列表',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_alert_id (alert_id),
    INDEX idx_user_id (user_id)
);
```

### 3.2 API 设计

#### 3.2.1 已有 API（保留）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/alerts/rules` | 获取规则列表 |
| GET | `/api/v1/alerts/rules/{id}` | 获取规则详情 |
| POST | `/api/v1/alerts/rules` | 创建规则 |
| PUT | `/api/v1/alerts/rules/{id}` | 更新规则 |
| DELETE | `/api/v1/alerts/rules/{id}` | 删除规则 |
| POST | `/api/v1/alerts/rules/{id}/test` | 测试规则 |
| GET | `/api/v1/alerts` | 获取告警列表 |
| GET | `/api/v1/alerts/{id}` | 获取告警详情 |
| PUT | `/api/v1/alerts/{id}/resolve` | 标记恢复 |
| GET | `/api/v1/alerts/stats` | 告警统计 |

#### 3.2.2 新增 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/alerts/events` | 获取告警事件列表 |
| GET | `/api/v1/alerts/events/{id}` | 获取事件详情 |
| POST | `/api/v1/alerts/{id}/diagnose` | 生成 AI 诊断报告 |
| GET | `/api/v1/alerts/{id}/diagnosis` | 获取诊断报告 |
| POST | `/api/v1/alerts/{id}/chat` | 诊断对话 |

**诊断 API 请求/响应示例：**

```json
POST /api/v1/alerts/{id}/diagnose

Response:
{
  "id": 1,
  "alert_id": 123,
  "report": "## 诊断报告\n\n**告警信息**\n- 规则: CPU使用率过高\n- 当前值: 95%\n- 阈值: 80%\n\n**可能原因**\n1. 进程 CPU 密集型任务\n2. 系统资源不足\n3. 应用程序死循环\n\n**建议操作**\n1. 检查 top 命令查看高 CPU 进程\n2. 检查应用日志是否有异常\n3. 考虑扩容或优化代码",
  "created_at": "2026-03-28T10:00:00Z"
}
```

```json
POST /api/v1/alerts/{id}/chat

Request:
{
  "message": "如何查看是哪个进程导致的 CPU 高？"
}

Response:
{
  "id": 1,
  "alert_id": 123,
  "message": "可以使用以下命令查看：\n\n1. `top -c` - 显示完整命令行\n2. `htop` - 更友好的界面\n3. `ps aux --sort=-%cpu | head -10` - 显示 CPU 占用最高的 10 个进程\n\n根据您的告警信息，建议先执行 `top -c` 查看具体进程。",
  "created_at": "2026-03-28T10:05:00Z"
}
```

### 3.3 后端模块结构

```
backend/apps/alert/
├── __init__.py
├── models.py              # 数据模型（已有 + 新增）
├── schemas.py             # Pydantic 模型（已有 + 新增）
├── router.py              # API 路由（已有 + 新增）
├── engine/                # 告警评估引擎（新增）
│   ├── __init__.py
│   ├── evaluator.py       # 规则评估器
│   └── aggregator.py      # 告警聚合器
└── diagnosis/             # AI 诊断模块（新增）
    ├── __init__.py
    └── analyzer.py        # AI 分析器
```

### 3.4 前端页面结构

```
frontend/src/views/
├── monitor/
│   ├── Index.vue           # 智能监控入口
│   ├── AlertRules.vue      # 告警规则管理
│   ├── AlertList.vue       # 告警列表
│   └── DiagnosisDialog.vue # AI 诊断对话框

frontend/src/api/
└── alert.ts                # 告警 API 接口
```

---

## 四、实现步骤

### 4.1 Phase 1 实现计划

| 步骤 | 内容 | 说明 |
|------|------|------|
| 1 | 数据库表更新 | 新增 alert_events、diagnosis_reports、diagnosis_conversations 表 |
| 2 | 后端模型更新 | 新增 Pydantic schemas |
| 3 | 告警评估引擎 | 定时评估规则，生成告警 |
| 4 | AI 诊断 API | 对接大模型，生成诊断报告 |
| 5 | 前端告警页面 | 规则管理、告警列表、诊断界面 |

### 4.2 关键技术点

**告警评估引擎：**
- 使用 APScheduler 定时调度
- 批量查询 Prometheus 指标
- 差异化评估频率（critical 15s, warning 30s, info 120s）

**AI 诊断：**
- 复用现有的模型管理配置
- 构建诊断 Prompt 模板
- 支持流式响应

---

## 五、后续规划

### 5.1 Phase 2：告警聚合 + 根因分析

- 告警时间窗口聚合
- 基于关系模型的根因分析
- 故障传播链路可视化

### 5.2 Phase 3：异常检测 + 高级诊断

- 基于历史数据的异常检测
- 多指标关联分析
- 自动修复建议

---

## 六、参考文档

- [告警评估引擎设计文档](./ALERT_ENGINE_DESIGN.md)
- [根因分析算法报告](./RCA_ALGORITHMS_REPORT.md)
