# Metric Bot - 告警评估引擎设计文档

> 最后更新时间：2026-03-20
> 文档版本：v1.0

---

## 目录

- [一、概述](#一概述)
- [二、核心架构](#二核心架构)
- [三、优化方案](#三优化方案)
- [四、数据库设计](#四数据库设计)
- [五、API 设计](#五api-设计)
- [六、实现计划](#六实现计划)

---

## 一、概述

### 1.1 问题
告警规则数量增多后，评估效率下降。

### 1.2 目标
- 支持 1000+ 告警规则
- 评估延迟 < 5 秒
- 支持横向扩展

---

## 二、核心架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────┐
│                   Metric Bot 告警引擎                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐               │
│  │ 规则管理    │    │ 告警列表    │               │
│  │ (CRUD)      │    │ (展示/统计) │               │
│  └──────────────┘    └──────────────┘               │
│         │                    │                        │
│         └──────────┬─────────┘                        │
│                    │                                  │
│         ┌──────────▼──────────┐                      │
│         │   告警评估引擎      │                      │
│         │                     │                      │
│         │  1. 批量查询       │                      │
│         │  2. 缓存策略       │                      │
│         │  3. 并行/分片      │                      │
│         │  4. 差异化频率     │                      │
│         │  5. 优先级队列     │                      │
│         └──────────┬──────────┘                      │
│                    │                                  │
│         ┌──────────▼──────────┐                      │
│         │   数据源适配器     │                      │
│         │  (Prometheus/Zabbix)│                     │
│         └──────────┬──────────┘                      │
│                    │                                  │
│         ┌──────────▼──────────┐                      │
│         │   告警存储/通知    │                      │
│         └─────────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

---

## 三、优化方案

### 3.1 方案一：批量查询（优先实现）⭐⭐⭐⭐⭐

#### 原理
- 聚合相同指标查询，一次查询多个规则
- 本地匹配规则，减少网络请求

#### 性能对比
| 规则数 | 优化前 | 优化后 |
|--------|--------|--------|
| 100 | 100 次查询 | 10-20 次查询 |
| 500 | 500 次查询 | 30-50 次查询 |
| 1000 | 1000 次查询 | 50-100 次查询 |

#### 伪代码
```python
class BatchQueryOptimizer:
    def evaluate_rules_batch(self, rules):
        # 1. 聚合查询
        query_groups = self._aggregate_queries(rules)
        
        # 2. 并行批量查询
        metric_results = self._batch_query(query_groups)
        
        # 3. 本地匹配
        results = []
        for rule in rules:
            if self._match_local(rule, metric_results):
                results.append(rule)
        
        return results
```

---

### 3.2 方案二：差异化拉取频率（优先实现）⭐⭐⭐⭐⭐

#### 原理
不同严重程度的规则，拉取频率不同

| 严重程度 | 推荐频率 | 说明 |
|---------|---------|------|
| **critical** | 10-15 秒 | 最高优先级，快速响应 |
| **warning** | 30-60 秒 | 中等优先级 |
| **info** | 2-5 分钟 | 低优先级，节省资源 |

#### 伪代码
```python
class DifferentialEvaluator:
    def evaluate_by_severity(self):
        now = time.time()
        
        # Critical: 15 秒
        if self._should_evaluate("critical", 15, now):
            self._evaluate_critical()
        
        # Warning: 30 秒
        if self._should_evaluate("warning", 30, now):
            self._evaluate_warning()
        
        # Info: 120 秒
        if self._should_evaluate("info", 120, now):
            self._evaluate_info()
```

---

### 3.3 方案三：缓存策略 ⭐⭐⭐

#### 缓存层级
```
1. 指标数据缓存（15 秒）
   └─ 避免重复查询相同指标
   
2. 规则评估结果缓存（短期）
   └─ 避免重复评估相同规则
```

#### 伪代码
```python
class CachedEvaluator:
    def get_metric_cached(self, query):
        # 检查缓存
        if query in self.cache and not expired():
            return self.cache[query]
        
        # 查询并缓存
        value = self._query(query)
        self.cache[query] = value
        return value
```

---

### 3.4 方案四：并行/分片 ⭐⭐⭐⭐

#### 原理
- 规则分片（4-8 个分片）
- 线程池并行评估

#### 伪代码
```python
class ParallelEvaluator:
    def evaluate_parallel(self, rules):
        # 分片
        chunks = self._split_chunks(rules, 4)
        
        # 并行评估
        with ThreadPoolExecutor(4) as executor:
            futures = [executor.submit(self._eval_chunk, chunk) for chunk in chunks]
            results = [f.result() for f in futures]
        
        return results
```

---

## 四、数据库设计

### 4.1 告警规则表

```sql
CREATE TABLE alert_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL COMMENT '规则名称',
    description TEXT COMMENT '描述',
    
    -- 数据源
    datasource_id INT NOT NULL COMMENT '数据源ID',
    datasource_type VARCHAR(50) NOT NULL COMMENT '数据源类型: Prometheus/Zabbix',
    metric_query VARCHAR(500) NOT NULL COMMENT '指标查询语句',
    
    -- 条件
    condition_type VARCHAR(50) NOT NULL DEFAULT 'greater_than'
        COMMENT '条件类型: greater_than/less_than/equal_to/anomaly',
    threshold DECIMAL(10,2) COMMENT '阈值',
    
    -- 级别
    severity VARCHAR(50) NOT NULL DEFAULT 'warning'
        COMMENT '级别: info/warning/critical',
    
    -- 评估配置
    evaluation_interval INT DEFAULT 30 COMMENT '评估间隔(秒)',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    
    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_datasource_id (datasource_id),
    INDEX idx_enabled (enabled),
    INDEX idx_severity (severity)
);
```

---

### 4.2 告警记录表

```sql
CREATE TABLE alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rule_id INT NOT NULL COMMENT '规则ID',
    rule_name VARCHAR(255) COMMENT '规则名称（快照）',
    
    -- 告警信息
    severity VARCHAR(50) NOT NULL COMMENT '级别',
    metric_value DECIMAL(10,2) COMMENT '指标值',
    threshold DECIMAL(10,2) COMMENT '阈值',
    message TEXT COMMENT '告警消息',
    
    -- 状态
    resolved BOOLEAN DEFAULT FALSE COMMENT '是否已恢复',
    resolved_at DATETIME NULL COMMENT '恢复时间',
    
    -- 关联
    datasource_id INT COMMENT '数据源ID',
    
    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_rule_id (rule_id),
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved),
    INDEX idx_created_at (created_at)
);
```

---

## 五、API 设计

### 5.1 规则管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/alerts/rules` | 获取规则列表 |
| GET | `/api/v1/alerts/rules/{id}` | 获取规则详情 |
| POST | `/api/v1/alerts/rules` | 创建规则 |
| PUT | `/api/v1/alerts/rules/{id}` | 更新规则 |
| DELETE | `/api/v1/alerts/rules/{id}` | 删除规则 |
| POST | `/api/v1/alerts/rules/{id}/test` | 测试规则 |

---

### 5.2 告警查询 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/alerts` | 获取告警列表 |
| GET | `/api/v1/alerts/{id}` | 获取告警详情 |
| PUT | `/api/v1/alerts/{id}/resolve` | 标记恢复 |
| GET | `/api/v1/alerts/stats` | 告警统计 |

---

### 5.3 测试 API

```python
POST /api/v1/alerts/rules/{id}/test

Request:
{
  "test_value": 150
}

Response:
{
  "triggered": true,
  "test_value": 150,
  "threshold": 80,
  "severity": "critical",
  "message": "CPU 使用率过高: 150 > 80"
}
```

---

## 六、实现计划

### Phase 1: MVP（1-2 周）⭐⭐⭐⭐⭐

**目标**：基础功能 + 核心优化

| 任务 | 说明 |
|------|------|
| ✅ 数据库表设计 | alert_rules, alerts 表 |
| ✅ 规则 CRUD API | 创建/查询/更新/删除 |
| ✅ 告警列表 API | 告警查询/统计 |
| ✅ 批量查询优化 | 一次查询多个规则 |
| ✅ 差异化拉取 | critical/15s, warning/30s, info/120s |
| ✅ 测试按钮 | 快速验证规则 |

---

### Phase 2: 优化（2-3 周）⭐⭐⭐

**目标**：性能优化 + 完善功能

| 任务 | 说明 |
|------|------|
| ⬜ 缓存策略 | 指标缓存 15 秒 |
| ⬜ 并行/分片 | 4-8 个 worker 并行 |
| ⬜ 告警通知 | 钉钉/邮件/企业微信 |
| ⬜ 告警历史 | 历史记录查询 |

---

### Phase 3: 高级（持续）⭐⭐

**目标**：高级功能 + 性能优化

| 任务 | 说明 |
|------|------|
| ⬜ 优先级队列 | 高优先级规则先评估 |
| ⬜ PromQL 优化 | 查询优化 |
| ⬜ 告警静默 | 维护期间静默 |
| ⬜ 告警聚合 | 时间窗口聚合 |

---

## 七、性能目标

### 7.1 评估性能

| 指标 | 目标 |
|------|------|
| **100 规则** | < 2 秒 |
| **500 规则** | < 5 秒 |
| **1000 规则** | < 10 秒 |

### 7.2 资源目标

| 资源 | 目标 |
|------|------|
| **CPU 使用率** | < 50% |
| **内存使用** | < 500MB |
| **网络请求** | 减少 80%（批量查询） |

---

## 附录

### A. 参考资料
- Prometheus Alertmanager
- Grafana Alerting
- 告警系统设计最佳实践

### B. 相关文档
- 根因分析算法报告：`RCA_ALGORITHMS_REPORT.md`

---

**文档结束**
