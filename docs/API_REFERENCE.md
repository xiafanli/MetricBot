# Metric Bot API 接口文档

> 最后更新时间：2026-03-20
> 文档版本：v1.0

---

## 目录

- [一、接口概览](#一接口概览)
- [二、认证接口](#二认证接口)
- [三、模型管理接口](#三模型管理接口)
- [四、数据源管理接口](#四数据源管理接口)
- [五、告警管理接口](#五告警管理接口)
- [六、通用接口](#六通用接口)

---

## 一、接口概览

### 基础信息
| 项 | 说明 |
|----|------|
| Base URL | `http://localhost:8000/api/v1` |
| 认证方式 | Bearer Token |
| 数据格式 | JSON |

### 认证说明
除登录/注册接口外，所有接口都需要在 Header 中携带：
```
Authorization: Bearer <token>
```

---

## 二、认证接口

### 2.1 用户注册

| 属性 | 说明 |
|------|------|
| **路径** | `POST /auth/register` |
| **用途** | 注册新用户 |
| **认证** | 不需要 |

#### 请求
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "admin123"
}
```

#### 响应
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2026-03-20T10:00:00Z"
}
```

---

### 2.2 用户登录

| 属性 | 说明 |
|------|------|
| **路径** | `POST /auth/login` |
| **用途** | 登录获取 Token |
| **认证** | 不需要 |
| **Content-Type** | `multipart/form-data` |

#### 请求
```
username: admin
password: admin123
```

#### 响应
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 2.3 获取当前用户

| 属性 | 说明 |
|------|------|
| **路径** | `GET /auth/me` |
| **用途** | 获取当前登录用户信息 |
| **认证** | 需要 |

#### 响应
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2026-03-20T10:00:00Z"
}
```

---

## 三、模型管理接口

### 3.1 获取模型列表

| 属性 | 说明 |
|------|------|
| **路径** | `GET /models` |
| **用途** | 获取所有模型 |
| **认证** | 需要 |

#### Query 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `enabled_only` | boolean | 只返回启用的模型 |

#### 响应
```json
[
  {
    "id": 1,
    "name": "GPT-4",
    "provider": "OpenAI",
    "base_model": "gpt-4-turbo",
    "protocol": "openai",
    "api_key": "sk-...",
    "api_domain": "https://api.openai.com/v1",
    "config": null,
    "is_default": true,
    "is_enabled": true,
    "created_at": "2026-03-20T10:00:00Z",
    "updated_at": "2026-03-20T10:00:00Z"
  }
]
```

---

### 3.2 获取单个模型

| 属性 | 说明 |
|------|------|
| **路径** | `GET /models/{id}` |
| **用途** | 获取单个模型详情 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 模型 ID |

#### 响应
```json
{
  "id": 1,
  "name": "GPT-4",
  "provider": "OpenAI",
  "base_model": "gpt-4-turbo",
  "protocol": "openai",
  "api_key": "sk-...",
  "api_domain": "https://api.openai.com/v1",
  "config": null,
  "is_default": true,
  "is_enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z"
}
```

---

### 3.3 创建模型

| 属性 | 说明 |
|------|------|
| **路径** | `POST /models` |
| **用途** | 创建新模型 |
| **认证** | 需要 |

#### 请求
```json
{
  "name": "GPT-4",
  "provider": "OpenAI",
  "base_model": "gpt-4-turbo",
  "protocol": "openai",
  "api_key": "sk-...",
  "api_domain": "https://api.openai.com/v1",
  "config": null,
  "is_default": false,
  "is_enabled": true
}
```

#### 响应
```json
{
  "id": 2,
  "name": "GPT-4",
  "provider": "OpenAI",
  "base_model": "gpt-4-turbo",
  "protocol": "openai",
  "api_key": "sk-...",
  "api_domain": "https://api.openai.com/v1",
  "config": null,
  "is_default": false,
  "is_enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": null
}
```

---

### 3.4 更新模型

| 属性 | 说明 |
|------|------|
| **路径** | `PUT /models/{id}` |
| **用途** | 更新模型信息 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 模型 ID |

#### 请求
```json
{
  "name": "GPT-4 更新",
  "is_enabled": false
}
```

#### 响应
```json
{
  "id": 1,
  "name": "GPT-4 更新",
  "provider": "OpenAI",
  "base_model": "gpt-4-turbo",
  "protocol": "openai",
  "api_key": "sk-...",
  "api_domain": "https://api.openai.com/v1",
  "config": null,
  "is_default": true,
  "is_enabled": false,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:30:00Z"
}
```

---

### 3.5 设置默认模型

| 属性 | 说明 |
|------|------|
| **路径** | `PUT /models/{id}/default` |
| **用途** | 设置模型为默认 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 模型 ID |

#### 响应
```json
{
  "id": 1,
  "name": "GPT-4",
  "provider": "OpenAI",
  "base_model": "gpt-4-turbo",
  "protocol": "openai",
  "api_key": "sk-...",
  "api_domain": "https://api.openai.com/v1",
  "config": null,
  "is_default": true,
  "is_enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:30:00Z"
}
```

---

### 3.6 删除模型

| 属性 | 说明 |
|------|------|
| **路径** | `DELETE /models/{id}` |
| **用途** | 删除模型 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 模型 ID |

#### 响应
- 状态码: `204 No Content`
- 无响应体

---

## 四、数据源管理接口

### 4.1 获取数据源列表

| 属性 | 说明 |
|------|------|
| **路径** | `GET /datasources` |
| **用途** | 获取所有数据源 |
| **认证** | 需要 |

#### Query 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `enabled_only` | boolean | 只返回启用的数据源 |

#### 响应
```json
[
  {
    "id": 1,
    "name": "生产环境 Prometheus",
    "type": "Prometheus",
    "url": "http://prometheus.prod:9090",
    "auth_type": "none",
    "auth_value": null,
    "password": null,
    "config": null,
    "enabled": true,
    "created_at": "2026-03-20T10:00:00Z",
    "updated_at": "2026-03-20T10:00:00Z"
  }
]
```

---

### 4.2 获取单个数据源

| 属性 | 说明 |
|------|------|
| **路径** | `GET /datasources/{id}` |
| **用途** | 获取单个数据源详情 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 数据源 ID |

#### 响应
```json
{
  "id": 1,
  "name": "生产环境 Prometheus",
  "type": "Prometheus",
  "url": "http://prometheus.prod:9090",
  "auth_type": "none",
  "auth_value": null,
  "password": null,
  "config": null,
  "enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z"
}
```

---

### 4.3 创建数据源

| 属性 | 说明 |
|------|------|
| **路径** | `POST /datasources` |
| **用途** | 创建新数据源 |
| **认证** | 需要 |

#### 请求
```json
{
  "name": "生产环境 Prometheus",
  "type": "Prometheus",
  "url": "http://prometheus.prod:9090",
  "auth_type": "none",
  "auth_value": null,
  "password": null,
  "config": null,
  "enabled": true
}
```

#### 响应
```json
{
  "id": 2,
  "name": "生产环境 Prometheus",
  "type": "Prometheus",
  "url": "http://prometheus.prod:9090",
  "auth_type": "none",
  "auth_value": null,
  "password": null,
  "config": null,
  "enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": null
}
```

---

### 4.4 更新数据源

| 属性 | 说明 |
|------|------|
| **路径** | `PUT /datasources/{id}` |
| **用途** | 更新数据源信息 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 数据源 ID |

#### 请求
```json
{
  "name": "生产环境 Prometheus 更新",
  "enabled": false
}
```

#### 响应
```json
{
  "id": 1,
  "name": "生产环境 Prometheus 更新",
  "type": "Prometheus",
  "url": "http://prometheus.prod:9090",
  "auth_type": "none",
  "auth_value": null,
  "password": null,
  "config": null,
  "enabled": false,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:30:00Z"
}
```

---

### 4.5 删除数据源

| 属性 | 说明 |
|------|------|
| **路径** | `DELETE /datasources/{id}` |
| **用途** | 删除数据源 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 数据源 ID |

#### 响应
- 状态码: `204 No Content`
- 无响应体

---

### 4.6 测试数据源连接

| 属性 | 说明 |
|------|------|
| **路径** | `POST /datasources/test` |
| **用途** | 测试数据源连接 |
| **认证** | 需要 |

#### 请求
```json
{
  "name": "生产环境 Prometheus",
  "type": "Prometheus",
  "url": "http://prometheus.prod:9090",
  "auth_type": "none",
  "auth_value": null,
  "password": null,
  "config": null,
  "enabled": true
}
```

#### 响应
```json
{
  "success": true,
  "message": "Prometheus 连接成功"
}
```

---

## 五、告警管理接口

### 5.1 获取告警规则列表

| 属性 | 说明 |
|------|------|
| **路径** | `GET /alerts/rules` |
| **用途** | 获取所有告警规则 |
| **认证** | 需要 |

#### Query 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `enabled_only` | boolean | 只返回启用的规则 |

#### 响应
```json
[
  {
    "id": 1,
    "name": "CPU 使用率过高",
    "description": "CPU 使用率超过阈值",
    "datasource_id": 1,
    "datasource_type": "Prometheus",
    "metric_query": "cpu_usage_percent",
    "condition_type": "greater_than",
    "threshold": 80,
    "severity": "warning",
    "evaluation_interval": 30,
    "enabled": true,
    "created_at": "2026-03-20T10:00:00Z",
    "updated_at": "2026-03-20T10:00:00Z"
  }
]
```

---

### 5.2 获取单个告警规则

| 属性 | 说明 |
|------|------|
| **路径** | `GET /alerts/rules/{id}` |
| **用途** | 获取单个告警规则详情 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 规则 ID |

#### 响应
```json
{
  "id": 1,
  "name": "CPU 使用率过高",
  "description": "CPU 使用率超过阈值",
  "datasource_id": 1,
  "datasource_type": "Prometheus",
  "metric_query": "cpu_usage_percent",
  "condition_type": "greater_than",
  "threshold": 80,
  "severity": "warning",
  "evaluation_interval": 30,
  "enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z"
}
```

---

### 5.3 创建告警规则

| 属性 | 说明 |
|------|------|
| **路径** | `POST /alerts/rules` |
| **用途** | 创建新告警规则 |
| **认证** | 需要 |

#### 请求
```json
{
  "name": "CPU 使用率过高",
  "description": "CPU 使用率超过阈值",
  "datasource_id": 1,
  "datasource_type": "Prometheus",
  "metric_query": "cpu_usage_percent",
  "condition_type": "greater_than",
  "threshold": 80,
  "severity": "warning",
  "evaluation_interval": 30,
  "enabled": true
}
```

#### 响应
```json
{
  "id": 2,
  "name": "CPU 使用率过高",
  "description": "CPU 使用率超过阈值",
  "datasource_id": 1,
  "datasource_type": "Prometheus",
  "metric_query": "cpu_usage_percent",
  "condition_type": "greater_than",
  "threshold": 80,
  "severity": "warning",
  "evaluation_interval": 30,
  "enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": null
}
```

---

### 5.4 更新告警规则

| 属性 | 说明 |
|------|------|
| **路径** | `PUT /alerts/rules/{id}` |
| **用途** | 更新告警规则 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 规则 ID |

#### 请求
```json
{
  "name": "CPU 使用率过高 - 更新",
  "threshold": 90
}
```

#### 响应
```json
{
  "id": 1,
  "name": "CPU 使用率过高 - 更新",
  "description": "CPU 使用率超过阈值",
  "datasource_id": 1,
  "datasource_type": "Prometheus",
  "metric_query": "cpu_usage_percent",
  "condition_type": "greater_than",
  "threshold": 90,
  "severity": "warning",
  "evaluation_interval": 30,
  "enabled": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:30:00Z"
}
```

---

### 5.5 删除告警规则

| 属性 | 说明 |
|------|------|
| **路径** | `DELETE /alerts/rules/{id}` |
| **用途** | 删除告警规则 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 规则 ID |

#### 响应
- 状态码: `204 No Content`
- 无响应体

---

### 5.6 测试告警规则

| 属性 | 说明 |
|------|------|
| **路径** | `POST /alerts/rules/{id}/test` |
| **用途** | 测试告警规则是否触发 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 规则 ID |

#### 请求
```json
{
  "test_value": 95
}
```

#### 响应
```json
{
  "triggered": true,
  "test_value": 95,
  "threshold": 80,
  "severity": "warning",
  "message": "CPU 使用率过高: 95 > 80"
}
```

---

### 5.7 获取告警列表

| 属性 | 说明 |
|------|------|
| **路径** | `GET /alerts` |
| **用途** | 获取告警列表 |
| **认证** | 需要 |

#### Query 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `resolved_only` | boolean | 只返回已恢复的 |
| `active_only` | boolean | 只返回进行中的 |
| `limit` | integer | 返回数量限制，默认 100 |

#### 响应
```json
[
  {
    "id": 1,
    "rule_id": 1,
    "rule_name": "CPU 使用率过高",
    "severity": "warning",
    "metric_value": 95,
    "threshold": 80,
    "message": "CPU 使用率过高: 95 > 80",
    "resolved": false,
    "resolved_at": null,
    "datasource_id": 1,
    "created_at": "2026-03-20T10:00:00Z"
  }
]
```

---

### 5.8 获取单个告警

| 属性 | 说明 |
|------|------|
| **路径** | `GET /alerts/{id}` |
| **用途** | 获取单个告警详情 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 告警 ID |

#### 响应
```json
{
  "id": 1,
  "rule_id": 1,
  "rule_name": "CPU 使用率过高",
  "severity": "warning",
  "metric_value": 95,
  "threshold": 80,
  "message": "CPU 使用率过高: 95 > 80",
  "resolved": false,
  "resolved_at": null,
  "datasource_id": 1,
  "created_at": "2026-03-20T10:00:00Z"
}
```

---

### 5.9 标记告警恢复

| 属性 | 说明 |
|------|------|
| **路径** | `PUT /alerts/{id}/resolve` |
| **用途** | 标记告警为已恢复 |
| **认证** | 需要 |

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 告警 ID |

#### 响应
```json
{
  "id": 1,
  "rule_id": 1,
  "rule_name": "CPU 使用率过高",
  "severity": "warning",
  "metric_value": 95,
  "threshold": 80,
  "message": "CPU 使用率过高: 95 > 80",
  "resolved": true,
  "resolved_at": "2026-03-20T10:30:00Z",
  "datasource_id": 1,
  "created_at": "2026-03-20T10:00:00Z"
}
```

---

### 5.10 告警统计

| 属性 | 说明 |
|------|------|
| **路径** | `GET /alerts/stats` |
| **用途** | 获取告警统计信息 |
| **认证** | 需要 |

#### 响应
```json
{
  "total": 100,
  "critical": 10,
  "warning": 50,
  "info": 40,
  "resolved": 80,
  "active": 20
}
```

---

## 六、通用接口

### 6.1 健康检查

| 属性 | 说明 |
|------|------|
| **路径** | `GET /health` |
| **用途** | 检查后端服务状态 |
| **认证** | 不需要 |

#### 响应
```json
{
  "status": "healthy",
  "message": "Backend is running"
}
```

---

### 6.2 根路径

| 属性 | 说明 |
|------|------|
| **路径** | `GET /` |
| **用途** | 欢迎信息 |
| **认证** | 不需要 |

#### 响应
```json
{
  "message": "Welcome to Metric Bot!"
}
```

---

## 附录

### A. 错误码说明

| HTTP 状态码 | 说明 |
|------------|------|
| `200` | 成功 |
| `201` | 创建成功 |
| `204` | 删除成功（无响应体） |
| `400` | 请求参数错误 |
| `401` | 未授权 |
| `404` | 资源不存在 |
| `500` | 服务器内部错误 |

---

### B. 严重级别说明

| 级别 | 说明 |
|------|------|
| `info` | 信息 |
| `warning` | 警告 |
| `critical` | 严重 |

---

### C. 条件类型说明

| 类型 | 说明 |
|------|------|
| `greater_than` | 大于阈值 |
| `less_than` | 小于阈值 |
| `equal_to` | 等于阈值 |
| `anomaly` | 异常检测 |

---

### D. 数据源类型说明

| 类型 | 说明 |
|------|------|
| `Prometheus` | Prometheus 监控系统 |
| `Zabbix` | Zabbix 监控系统 |
| `Grafana` | Grafana |
| `Datadog` | Datadog |
| `HTTP` | 自定义 HTTP 数据源 |

---

### E. 认证类型说明

| 类型 | 说明 |
|------|------|
| `none` | 无认证 |
| `basic` | Basic Auth |
| `token` | Bearer Token |

---

**文档结束**
