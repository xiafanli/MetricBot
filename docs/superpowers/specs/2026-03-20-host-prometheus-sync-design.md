# 主机模型 + Prometheus 同步设计文档

> 创建时间：2026-03-20
> 作者：Metric Bot Team
> 状态：设计中

---

## 概述

本文档描述主机模型功能，包括手工录入和 Prometheus 批量同步两种方式。

### 目标
- 支持主机信息的手工录入
- 支持从 Prometheus 指标标签批量同步主机
- 记录主机来源（from_type/from_name）

---

## 功能设计

### 1. 数据库模型更新

#### Host 表新增字段

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| `from_type` | VARCHAR(50) | 来源类型 | `manual`, `prometheus`, `cmdb` |
| `from_name` | VARCHAR(255) | 来源名称 | Prometheus 数据源名 |

---

### 2. 后端 API 设计

#### 2.1 新增：Prometheus 同步 API

**端点**：`POST /api/v1/hosts/sync/prometheus`

**认证**：需要 Bearer Token

**请求体**：
```json
{
  "datasource_id": 1,
  "metric": "node_cpu_seconds_total",
  "label": "instance",
  "preview_only": true
}
```

**字段说明**：
| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `datasource_id` | integer | ✅ | Prometheus 数据源 ID |
| `metric` | string | ✅ | PromQL 指标名 |
| `label` | string | ✅ | 要提取的标签名 |
| `preview_only` | boolean | ❌ | 只预览不导入，默认 true |

**响应（preview_only=true）**：
```json
{
  "preview": [
    "prod-web-01:9100",
    "prod-web-02:9100",
    "prod-db-01:9100"
  ],
  "total": 3
}
```

**响应（preview_only=false）**：
```json
{
  "imported": 3,
  "hosts": [
    {
      "id": 1,
      "name": "prod-web-01:9100",
      "ip": "prod-web-01",
      "from_type": "prometheus",
      "from_name": "生产环境 Prometheus",
      "created_at": "2026-03-20T10:00:00Z"
    }
  ]
}
```

---

### 3. 前端设计

#### 3.1 Hosts.vue 更新

**功能变更**：
1. 去掉统计卡片（在线/离线/告警中）
2. 去掉表格中的实时监控列（CPU/内存/磁盘）
3. 添加「从 Prometheus 同步」按钮
4. 同步对话框：
   - 选择 Prometheus 数据源（下拉框）
   - 输入指标名
   - 输入标签名
   - 「预览」按钮
   - 预览列表（最多 10 条）
   - 「导入」按钮

---

## 实现计划

| 阶段 | 任务 |
|------|------|
| **1. 数据库** | 更新 Host 模型，添加 from_type/from_name |
| **2. 后端** | 添加 Prometheus 同步 API |
| **3. 前端 API** | 添加 host/relation 接口 |
| **4. 前端 UI** | 更新 Hosts.vue 对接后端 + 同步 UI |

---

## 附录

### A. 数据来源说明

| from_type | 说明 |
|-----------|------|
| `manual` | 手工录入 |
| `prometheus` | Prometheus 同步 |
| `cmdb` | CMDB API 同步（下一阶段） |

---

**文档结束**
