# 生产环境模拟器设计文档

> 最后更新时间：2026-03-28  
> 项目状态：设计完成，准备实现

---

## 概述

Metric Bot 生产环境模拟器是一个集成在 MetricBot 中的模块，用于模拟真实生产环境的拓扑、指标、日志和故障，为 MetricBot 的监控、告警、根因分析等功能提供测试数据。

---

## 架构设计

### 整体架构

采用单进程一体化架构，模拟器作为 MetricBot 后端的一个模块运行：

```
MetricBot (单进程)
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Simulator Module                                             │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │  API Layer (router.py)                                  │ │ │
│  │  ├─────────────────────────────────────────────────────────┤ │ │
│  │  │  Engine Layer                                            │ │ │
│  │  │  ├── Topology Manager      (拓扑管理)                   │ │ │
│  │  │  ├── Metric Generator      (指标生成)                   │ │ │
│  │  │  ├── Log Generator         (日志生成)                   │ │ │
│  │  │  └── Fault Engine          (故障引擎)                   │ │ │
│  │  ├─────────────────────────────────────────────────────────┤ │ │
│  │  │  Scheduler (APScheduler)    (定时任务调度)              │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────────────────────────────────┐ │
│  │  MySQL       │  │  File System (simulator/logs/)          │ │
│  │  (共享)      │  │  (日志存储)                              │ │
│  └──────────────┘  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         ↓                          ↓
   Pushgateway              MetricBot Host/Relation API
         ↓                          ↓
   Prometheus                  主机/关系上报
```

### 核心流程

1. **拓扑配置** → 用户通过前端配置拓扑图和组件属性
2. **启动模拟** → 调度器启动定时任务
3. **指标生成** → 每分钟生成指标并推送到 Pushgateway
4. **日志生成** → 按频率生成日志文件到 `simulator/logs/`
5. **故障模拟** → 按配置触发故障，影响指标和日志
6. **数据上报** → 可选，将模拟的主机和关系上报到 MetricBot

---

## 数据模型设计

### 1. SimulationEnvironment（拓扑环境）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| name | String(100) | NOT NULL | 环境名称 |
| description | Text | NULLABLE | 环境描述 |
| topology_data | JSON | NULLABLE | 拓扑图数据（AntV X6 格式） |
| is_active | Boolean | DEFAULT FALSE | 是否激活 |
| pushgateway_url | String(255) | NULLABLE | Pushgateway 地址 |
| log_path | String(255) | NULLABLE | 日志存储路径 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE NOW | 更新时间 |

### 2. SimulationComponent（模拟组件）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| env_id | Integer | FK, NOT NULL | 所属环境 ID |
| component_type | String(50) | NOT NULL | 组件类型：host/java_app/database/nginx/container |
| name | String(100) | NOT NULL | 组件名称 |
| properties | JSON | NULLABLE | 组件属性（CPU、内存、存储等） |
| position_x | Float | NULLABLE | 拓扑图 X 坐标 |
| position_y | Float | NULLABLE | 拓扑图 Y 坐标 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3. ComponentRelation（组件关系）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| env_id | Integer | FK, NOT NULL | 所属环境 ID |
| source_id | Integer | FK, NOT NULL | 源组件 ID |
| target_id | Integer | FK, NOT NULL | 目标组件 ID |
| relation_type | String(50) | NOT NULL | 关系类型：calls/depends_on/contains |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 4. MetricTemplate（指标模板）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| component_type | String(50) | NOT NULL | 适用组件类型 |
| metric_name | String(100) | NOT NULL | 指标名称 |
| metric_type | String(20) | NOT NULL | 指标类型：gauge/counter/histogram |
| description | String(255) | NULLABLE | 指标描述 |
| min_value | Float | NULLABLE | 最小值 |
| max_value | Float | NULLABLE | 最大值 |
| base_value | Float | NULLABLE | 基准值 |
| fluctuation | Float | DEFAULT 0.1 | 波动幅度（0-1） |
| unit | String(50) | NULLABLE | 单位 |
| labels | JSON | NULLABLE | 默认标签 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 5. LogTemplate（日志模板）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| component_type | String(50) | NOT NULL | 适用组件类型 |
| log_format | String(50) | DEFAULT log4j | 日志格式：log4j/json/nginx |
| log_levels | JSON | NULLABLE | 日志级别分布 |
| template | Text | NULLABLE | 日志内容模板 |
| frequency | Integer | DEFAULT 10 | 生成频率（条/分钟） |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 6. FaultScenario（故障场景）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| name | String(100) | NOT NULL | 场景名称 |
| description | Text | NULLABLE | 场景描述 |
| fault_type | String(50) | NOT NULL | 故障类型 |
| target_component_type | String(50) | NULLABLE | 目标组件类型 |
| config | JSON | NULLABLE | 故障配置（持续时间、影响范围等） |
| probability | Float | DEFAULT 0.01 | 触发概率（0-1） |
| is_enabled | Boolean | DEFAULT FALSE | 是否启用 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 7. FaultInstance（故障实例）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| scenario_id | Integer | FK, NOT NULL | 故障场景 ID |
| component_id | Integer | FK, NOT NULL | 目标组件 ID |
| start_time | DateTime | NOT NULL | 开始时间 |
| end_time | DateTime | NULLABLE | 结束时间 |
| status | String(20) | DEFAULT pending | 状态：pending/active/completed |
| impact_data | JSON | NULLABLE | 影响数据 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

---

## 功能模块设计

### 1. 拓扑图生成与环境模拟模块

**功能说明：**
- 可视化拓扑图编辑器（基于 AntV X6）
- 支持组件类型：数据库服务器、Java 应用服务器、物理/虚拟主机、容器实例、中间件（Nginx）
- 组件间关联关系配置
- 组件属性配置界面（CPU、内存、存储等）

**API 端点：**
- `GET /api/v1/simulator/environments` - 获取环境列表
- `POST /api/v1/simulator/environments` - 创建环境
- `PUT /api/v1/simulator/environments/{id}` - 更新环境
- `DELETE /api/v1/simulator/environments/{id}` - 删除环境
- `POST /api/v1/simulator/environments/{id}/activate` - 激活环境
- `POST /api/v1/simulator/environments/{id}/deactivate` - 停用环境
- `GET /api/v1/simulator/environments/{id}/components` - 获取组件列表
- `POST /api/v1/simulator/environments/{id}/components` - 添加组件
- `PUT /api/v1/simulator/components/{id}` - 更新组件
- `DELETE /api/v1/simulator/components/{id}` - 删除组件
- `GET /api/v1/simulator/environments/{id}/relations` - 获取关系列表
- `POST /api/v1/simulator/environments/{id}/relations` - 添加关系
- `DELETE /api/v1/simulator/relations/{id}` - 删除关系
- `POST /api/v1/simulator/environments/{id}/sync-to-hosts` - 同步到 MetricBot 主机模型

### 2. 指标生成与推送模块

**功能说明：**
- 为所有组件生成模拟指标
- 系统层：CPU 使用率、内存占用、磁盘 I/O、网络流量
- 应用层：响应时间、请求量、错误率、JVM 指标
- 数据库：连接数、查询响应时间、缓存命中率、锁等待时间
- 中间件：请求吞吐量、连接数、缓存命中率
- 每分钟向 Pushgateway 推送指标
- 支持指标阈值配置和动态调整
- 支持指标模板自定义

**API 端点：**
- `GET /api/v1/simulator/metric-templates` - 获取指标模板列表
- `POST /api/v1/simulator/metric-templates` - 创建指标模板
- `PUT /api/v1/simulator/metric-templates/{id}` - 更新指标模板
- `DELETE /api/v1/simulator/metric-templates/{id}` - 删除指标模板
- `GET /api/v1/simulator/components/{id}/metrics` - 获取组件当前指标
- `POST /api/v1/simulator/components/{id}/metrics/push` - 手动推送指标

### 3. 日志模拟与存储模块

**功能说明：**
- 全链路日志模拟
- 访问 Spring Boot 应用时，相关组件生成联动日志
- 日志分类目录存储：
  - `/logs/java/`：Java 应用日志
  - `/logs/nginx/`：Nginx 中间件日志
  - `/logs/database/`：数据库日志
  - `/logs/host/`：主机系统日志
- 支持自定义日志格式、日志级别和日志生成频率
- Java 应用使用标准 Log4j 格式
- 日志轮转和归档机制

**API 端点：**
- `GET /api/v1/simulator/log-templates` - 获取日志模板列表
- `POST /api/v1/simulator/log-templates` - 创建日志模板
- `PUT /api/v1/simulator/log-templates/{id}` - 更新日志模板
- `DELETE /api/v1/simulator/log-templates/{id}` - 删除日志模板
- `GET /api/v1/simulator/components/{id}/logs` - 获取组件日志列表
- `GET /api/v1/simulator/components/{id}/logs/download` - 下载日志文件

### 4. 故障模拟与影响分析模块

**功能说明：**
- 多样化故障模拟：
  - Java 应用故障：GC 异常、内存泄漏、线程阻塞、接口超时
  - 主机故障：CPU 过载、内存耗尽、磁盘空间满、网络延迟
  - 数据库故障：连接池耗尽、慢查询、死锁
  - 中间件故障：连接拒绝、缓存穿透、配置错误
- 故障随机触发机制
- 支持自定义故障概率和时间间隔
- 模拟故障发生后的连锁反应
- 故障场景管理功能

**API 端点：**
- `GET /api/v1/simulator/fault-scenarios` - 获取故障场景列表
- `POST /api/v1/simulator/fault-scenarios` - 创建故障场景
- `PUT /api/v1/simulator/fault-scenarios/{id}` - 更新故障场景
- `DELETE /api/v1/simulator/fault-scenarios/{id}` - 删除故障场景
- `POST /api/v1/simulator/fault-scenarios/{id}/trigger` - 手动触发故障
- `GET /api/v1/simulator/fault-instances` - 获取故障实例列表
- `GET /api/v1/simulator/fault-instances/{id}` - 获取故障实例详情

---

## 技术实现细节

### 定时任务调度

使用 APScheduler 进行定时任务调度：

- **指标推送任务**：每分钟执行一次
- **日志生成任务**：根据每个组件的配置频率执行
- **故障检测任务**：每 10 秒检查一次是否触发故障
- **故障恢复任务**：监控活跃故障，到期自动恢复

### 指标生成算法

```python
def generate_metric(base_value, min_value, max_value, fluctuation, fault_impact=1.0):
    """
    生成指标值
    
    Args:
        base_value: 基准值
        min_value: 最小值
        max_value: 最大值
        fluctuation: 波动幅度 (0-1)
        fault_impact: 故障影响系数 (1.0=正常, >1.0=异常)
    
    Returns:
        生成的指标值
    """
    import random
    
    # 基础波动
    fluctuation_range = base_value * fluctuation
    random_offset = random.uniform(-fluctuation_range, fluctuation_range)
    
    # 应用故障影响
    value = (base_value + random_offset) * fault_impact
    
    # 限制在合理范围内
    value = max(min_value, min(value, max_value))
    
    return value
```

### 日志生成格式

**Log4j 格式示例：**
```
2026-03-28 10:30:45,123 INFO  [com.example.Application] - Request processed in 45ms
2026-03-28 10:30:45,234 DEBUG [com.example.Service] - Query executed: SELECT * FROM users
2026-03-28 10:30:45,345 WARN  [com.example.Cache] - Cache miss for key: user_123
2026-03-28 10:30:45,456 ERROR [com.example.Controller] - NullPointerException at line 42
```

**Nginx 格式示例：**
```
192.168.1.100 - - [28/Mar/2026:10:30:45 +0800] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [28/Mar/2026:10:30:46 +0800] "POST /api/login HTTP/1.1" 401 123 "-" "curl/7.68.0"
```

### 目录结构

```
MetricBot/
├── backend/
│   ├── apps/
│   │   └── simulator/              # 新增：模拟器模块
│   │       ├── __init__.py
│   │       ├── models.py            # 数据模型
│   │       ├── schemas.py           # Pydantic schemas
│   │       ├── router.py            # API 路由
│   │       ├── engine/              # 模拟器引擎
│   │       │   ├── __init__.py
│   │       │   ├── topology_manager.py    # 拓扑管理
│   │       │   ├── metric_generator.py    # 指标生成
│   │       │   ├── log_generator.py       # 日志生成
│   │       │   └── fault_engine.py        # 故障引擎
│   │       └── tasks/               # 定时任务
│   │           ├── __init__.py
│   │           └── scheduler.py           # 调度器
├── simulator/                      # 新增：模拟器目录
│   ├── logs/                       # 日志文件存储
│   │   ├── java/
│   │   ├── nginx/
│   │   ├── database/
│   │   └── host/
│   └── configs/                    # 场景配置文件
└── frontend/
    └── src/
        ├── views/
        │   └── simulator/          # 新增：模拟器页面
        │       ├── EnvironmentList.vue
        │       ├── TopologyEditor.vue
        │       ├── MetricConfig.vue
        │       ├── LogConfig.vue
        │       └── FaultSimulator.vue
        ├── router/
        │   └── index.ts            # 添加模拟器路由
        └── api/
            └── index.ts            # 添加模拟器 API
```

---

## 默认数据

### 默认指标模板

| 组件类型 | 指标名称 | 类型 | 基准值 | 最小值 | 最大值 | 波动 |
|----------|----------|------|--------|--------|--------|------|
| host | cpu_usage | gauge | 30 | 0 | 100 | 0.2 |
| host | memory_usage | gauge | 60 | 0 | 100 | 0.1 |
| host | disk_usage | gauge | 40 | 0 | 100 | 0.05 |
| host | network_in | counter | 1000 | 0 | 10000 | 0.3 |
| host | network_out | counter | 800 | 0 | 10000 | 0.3 |
| java_app | request_count | counter | 100 | 0 | 1000 | 0.2 |
| java_app | error_rate | gauge | 1 | 0 | 100 | 0.5 |
| java_app | response_time | gauge | 50 | 10 | 500 | 0.3 |
| java_app | jvm_heap_used | gauge | 512 | 0 | 2048 | 0.15 |
| java_app | jvm_gc_count | counter | 5 | 0 | 100 | 0.4 |
| database | connection_count | gauge | 20 | 0 | 100 | 0.1 |
| database | query_response_time | gauge | 10 | 1 | 1000 | 0.5 |
| database | cache_hit_rate | gauge | 90 | 0 | 100 | 0.05 |
| database | lock_wait_time | gauge | 5 | 0 | 1000 | 0.8 |
| nginx | request_throughput | counter | 200 | 0 | 2000 | 0.25 |
| nginx | connection_count | gauge | 50 | 0 | 500 | 0.15 |
| nginx | cache_hit_rate | gauge | 80 | 0 | 100 | 0.1 |

### 默认故障场景

| 故障名称 | 类型 | 目标组件 | 影响 | 概率 |
|----------|------|----------|------|------|
| CPU 过载 | host_cpu_overload | host | CPU 使用率 → 95% | 0.01 |
| 内存泄漏 | java_memory_leak | java_app | 堆内存持续增长 | 0.005 |
| 慢查询 | database_slow_query | database | 查询响应时间 ×10 | 0.008 |
| GC 异常 | java_gc_overhead | java_app | GC 次数 ×5，响应时间 ×3 | 0.006 |
| 网络延迟 | host_network_latency | host | 响应时间 ×2，错误率 ×5 | 0.007 |

---

## 与 MetricBot 集成

### 主机模型同步

将模拟组件同步到 MetricBot 的主机模型：

- 组件类型 `host` → Host 模型，`from_type="simulator"`
- 组件类型 `java_app` → Host 模型，`from_type="simulator"`, `tags=["java-app"]`
- 组件类型 `database` → Host 模型，`from_type="simulator"`, `tags=["database"]`
- 组件类型 `nginx` → Host 模型，`from_type="simulator"`, `tags=["nginx"]`

### 关系模型同步

将模拟组件关系同步到 MetricBot 的关系模型：

- `calls` → HostRelation，`relation_type="calls"`
- `depends_on` → HostRelation，`relation_type="depends_on"`
- `contains` → HostRelation，`relation_type="contains"`

---

## 依赖项

### Python 依赖

- `apscheduler` - 定时任务调度
- `prometheus-client` - Prometheus 指标生成和推送
- `faker` - 生成随机日志内容

### 前端依赖

- `@antv/x6` - 拓扑图编辑器
- `@antv/x6-vue-shape` - Vue 3 形状组件

---

## 开发阶段

### 第一阶段：基础框架
- 数据模型创建
- 基础 API 框架
- 前端页面框架

### 第二阶段：拓扑管理
- 拓扑图编辑器（AntV X6）
- 组件 CRUD
- 关系 CRUD
- 环境激活/停用

### 第三阶段：指标生成
- 指标模板管理
- 指标生成引擎
- Pushgateway 推送
- 定时任务调度

### 第四阶段：日志生成
- 日志模板管理
- 日志生成引擎
- 日志文件存储
- 日志轮转

### 第五阶段：故障模拟
- 故障场景管理
- 故障引擎
- 故障影响应用
- 故障连锁反应

### 第六阶段：MetricBot 集成
- 主机模型同步
- 关系模型同步
- 完整测试

---

## 总结

本文档详细描述了 MetricBot 生产环境模拟器的设计，包括：
- 整体架构
- 数据模型
- 四个核心功能模块
- 技术实现细节
- 与 MetricBot 的集成方案

该模拟器将为 MetricBot 提供完整的测试数据，支持监控、告警、根因分析等功能的开发和测试。
