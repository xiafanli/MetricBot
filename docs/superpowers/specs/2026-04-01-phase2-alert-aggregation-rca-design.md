# Phase 2 设计文档：告警聚合与根因分析

> 创建时间：2026-04-01
> 文档版本：v1.0

---

## 一、概述

### 1.1 目标

实现 Phase 2 的两个核心功能：
1. **告警聚合与降噪** - 减少告警噪音，让运维人员聚焦关键告警
2. **根因分析** - 自动化根因定位，帮助快速定位故障原因

### 1.2 架构方案

采用独立模块方案，与现有告警引擎解耦：

```
┌─────────────────────────────────────────────────────────────┐
│                    告警评估引擎 (现有)                        │
│                    ↓ 产生原始告警                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │   告警聚合模块       │    │   根因分析模块       │        │
│  ├─────────────────────┤    ├─────────────────────┤        │
│  │ • 时间窗口聚合器     │    │ • 随机游走分析器     │        │
│  │ • 拓扑关联聚合器     │    │ • 时序相关性分析器   │        │
│  │ • 语义相似聚合器     │    │ • LLM 推理分析器     │        │
│  └─────────────────────┘    └─────────────────────┘        │
│           ↓                           ↓                     │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │   聚合告警表         │    │   根因分析报告表     │        │
│  └─────────────────────┘    └─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、告警聚合模块

### 2.1 目录结构

```
backend/apps/alert/aggregation/
├── __init__.py
├── engine.py           # 聚合引擎主逻辑
├── strategies/
│   ├── __init__.py
│   ├── time_window.py  # 时间窗口聚合策略
│   ├── topology.py     # 拓扑关联聚合策略
│   └── semantic.py     # 语义相似聚合策略
├── scheduler.py        # 聚合任务调度器
└── models.py           # 聚合相关数据模型
```

### 2.2 聚合策略

#### 2.2.1 时间窗口聚合

在指定时间窗口内，对相同规则的告警进行合并。

**配置参数**：
- `window_seconds`: 时间窗口大小，默认 300 秒
- `group_by_fields`: 分组字段，如 `["rule_id", "host"]`

**聚合逻辑**：
1. 按分组字段生成聚合键
2. 在时间窗口内的相同聚合键告警合并为一组
3. 更新组的统计信息（告警数、首末告警时间等）

#### 2.2.2 拓扑关联聚合

根据拓扑关系，将上下游组件的关联告警聚合在一起。

**配置参数**：
- `max_depth`: 最大拓扑深度，默认 3

**聚合逻辑**：
1. 获取告警涉及的组件
2. 查询组件间的拓扑关系
3. 将拓扑路径上的告警聚合为一组

#### 2.2.3 语义相似聚合

基于告警内容的语义相似度进行聚合。

**配置参数**：
- `similarity_threshold`: 相似度阈值，默认 0.8

**聚合逻辑**：
1. 提取告警的文本特征
2. 计算告警间的语义相似度
3. 相似度超过阈值的告警聚合为一组

### 2.3 数据库表

```sql
-- 聚合告警组
CREATE TABLE alert_groups (
    id INT PRIMARY KEY AUTO_INCREMENT,
    group_key VARCHAR(255) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    alert_count INT DEFAULT 1,
    first_alert_id INT,
    first_alert_time DATETIME,
    last_alert_id INT,
    last_alert_time DATETIME,
    topology_path TEXT,
    affected_components JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    INDEX idx_group_key (group_key),
    INDEX idx_status (status)
);

-- 告警与聚合组关联
CREATE TABLE alert_group_members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    group_id INT NOT NULL,
    alert_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_group_alert (group_id, alert_id),
    INDEX idx_group_id (group_id),
    INDEX idx_alert_id (alert_id)
);

-- 聚合策略配置
CREATE TABLE aggregation_policies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    window_seconds INT DEFAULT 300,
    group_by_fields JSON,
    max_depth INT DEFAULT 3,
    similarity_threshold DECIMAL(3,2) DEFAULT 0.8,
    enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 三、根因分析模块

### 3.1 目录结构

```
backend/apps/alert/rca/
├── __init__.py
├── engine.py           # 根因分析引擎主逻辑
├── analyzers/
│   ├── __init__.py
│   ├── random_walk.py  # 随机游走分析器
│   ├── correlation.py  # 时序相关性分析器
│   └── llm_analyzer.py # LLM 推理分析器
├── models.py           # 根因分析数据模型
└── utils.py            # 工具函数
```

### 3.2 分析算法

#### 3.2.1 随机游走分析

基于拓扑图，从告警节点出发随机游走，访问次数最多的节点为根因候选。

**输入**：
- 拓扑关系图
- 告警节点列表

**输出**：
- 根因候选列表，按得分排序

**参数**：
- `num_walks`: 游走次数，默认 1000
- `walk_length`: 每次游走长度，默认 10

#### 3.2.2 时序相关性分析

分析指标间的时序相关性，找出导致其他指标异常的源头指标。

**输入**：
- 相关指标时序数据
- 告警时间点

**输出**：
- 相关性得分列表

**参数**：
- `lookback_minutes`: 回溯时间，默认 30 分钟
- `correlation_threshold`: 相关性阈值，默认 0.7

#### 3.2.3 LLM 推理分析

结合拓扑、历史案例、知识库，使用大模型进行根因推理。

**输入**：
- 告警信息
- 拓扑关系
- 历史案例
- 其他分析器结果

**输出**：
- 根因推理结果
- 排查建议

### 3.3 数据库表

```sql
-- 根因分析报告
CREATE TABLE rca_reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    group_id INT,
    status VARCHAR(50) DEFAULT 'analyzing',
    root_causes JSON,
    analysis_path TEXT,
    confidence DECIMAL(3,2),
    random_walk_result JSON,
    correlation_result JSON,
    llm_result JSON,
    recommendations JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    INDEX idx_group_id (group_id),
    INDEX idx_status (status)
);

-- 根因候选
CREATE TABLE rca_candidates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    component_name VARCHAR(255),
    component_type VARCHAR(50),
    score DECIMAL(5,4),
    evidence JSON,
    analysis_method VARCHAR(50),
    rank_order INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_report_id (report_id)
);
```

---

## 四、API 设计

### 4.1 告警聚合 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/alerts/groups` | 获取聚合告警组列表 |
| GET | `/api/v1/alerts/groups/{id}` | 获取聚合告警组详情 |
| GET | `/api/v1/alerts/groups/{id}/alerts` | 获取组内告警列表 |
| POST | `/api/v1/alerts/groups/{id}/acknowledge` | 确认聚合告警组 |
| POST | `/api/v1/alerts/groups/{id}/resolve` | 解决聚合告警组 |
| GET | `/api/v1/alerts/aggregation/policies` | 获取聚合策略配置 |
| POST | `/api/v1/alerts/aggregation/policies` | 创建聚合策略 |

### 4.2 根因分析 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/alerts/rca/analyze` | 触发根因分析 |
| GET | `/api/v1/alerts/rca/reports/{id}` | 获取根因分析报告 |
| GET | `/api/v1/alerts/rca/reports` | 获取根因分析报告列表 |
| GET | `/api/v1/alerts/groups/{id}/rca` | 获取聚合组的根因分析 |

---

## 五、前端页面

### 5.1 新增页面

1. **聚合告警列表页** (`/alerts/groups`)
   - 聚合告警组列表展示
   - 按策略/状态筛选
   - 告警数量统计

2. **聚合告警详情页** (`/alerts/groups/{id}`)
   - 聚合组基本信息
   - 组内告警列表
   - 根因分析结果
   - 拓扑关联图

3. **聚合策略配置页** (`/alerts/aggregation`)
   - 策略列表管理
   - 策略参数配置

### 5.2 前端目录结构

```
frontend/src/views/alert/
├── AlertGroups.vue        # 聚合告警列表页
├── AlertGroupDetail.vue   # 聚合告警详情页
├── AggregationPolicies.vue # 聚合策略配置页
└── RcaReportDialog.vue    # 根因分析报告弹窗
```

---

## 六、实现计划

### Phase 2.1: 告警聚合模块（预计 5 个任务）

1. 数据库模型和迁移
2. 聚合引擎核心逻辑
3. 三种聚合策略实现
4. API 接口实现
5. 前端页面实现

### Phase 2.2: 根因分析模块（预计 5 个任务）

1. 数据库模型和迁移
2. 根因分析引擎核心逻辑
3. 三种分析器实现
4. API 接口实现
5. 前端页面实现

### Phase 2.3: 集成测试（预计 2 个任务）

1. 端到端测试
2. 文档更新

---

## 七、依赖关系

- 依赖现有告警模块 (`backend/apps/alert/`)
- 依赖拓扑关系数据 (`backend/apps/host/`)
- 依赖 LLM 服务（已有配置）
- 依赖模拟器环境（用于测试）

---

## 八、风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 语义聚合性能问题 | 使用缓存，限制批量大小 |
| LLM 分析延迟 | 异步处理，显示进度 |
| 拓扑数据不完整 | 提供手动配置入口 |
