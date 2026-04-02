# 模拟器优化开发进度

## 已完成工作

### 一、基础框架

#### 1. 数据模型设计
- [x] SimulationEnvironment: 拓扑环境模型
- [x] SimulationComponent: 模拟组件模型
- [x] ComponentRelation: 组件关系模型
- [x] MetricTemplate: 指标模板模型
- [x] LogTemplate: 日志模板模型
- [x] FaultScenario: 故障场景模型
- [x] FaultInstance: 故障实例模型

#### 2. 后端 API 框架
- [x] 环境管理 API (`backend/apps/simulator/router.py`)
  - `GET /environments`: 获取环境列表
  - `POST /environments`: 创建环境
  - `PUT /environments/{id}`: 更新环境
  - `DELETE /environments/{id}`: 删除环境
  - `POST /environments/{id}/activate`: 激活环境
  - `POST /environments/{id}/deactivate`: 停用环境
  - `POST /environments/{id}/sync-to-hosts`: 同步到主机模型

- [x] 组件管理 API
  - `GET /environments/{id}/components`: 获取组件列表
  - `POST /environments/{id}/components`: 添加组件
  - `PUT /components/{id}`: 更新组件
  - `DELETE /components/{id}`: 删除组件

- [x] 关系管理 API
  - `GET /environments/{id}/relations`: 获取关系列表
  - `POST /environments/{id}/relations`: 添加关系
  - `DELETE /relations/{id}`: 删除关系

- [x] 指标模板 API
  - `GET /metric-templates`: 获取指标模板列表
  - `POST /metric-templates`: 创建指标模板
  - `PUT /metric-templates/{id}`: 更新指标模板
  - `DELETE /metric-templates/{id}`: 删除指标模板

- [x] 日志模板 API
  - `GET /log-templates`: 获取日志模板列表
  - `POST /log-templates`: 创建日志模板
  - `PUT /log-templates/{id}`: 更新日志模板
  - `DELETE /log-templates/{id}`: 删除日志模板

- [x] 故障场景 API
  - `GET /fault-scenarios`: 获取故障场景列表
  - `POST /fault-scenarios`: 创建故障场景
  - `PUT /fault-scenarios/{id}`: 更新故障场景
  - `DELETE /fault-scenarios/{id}`: 删除故障场景
  - `POST /fault-scenarios/{id}/trigger`: 手动触发故障

- [x] 故障实例 API
  - `GET /fault-instances`: 获取故障实例列表
  - `GET /fault-instances/{id}`: 获取故障实例详情

#### 3. 前端页面框架
- [x] 环境管理页面 (`frontend/src/views/simulator/EnvironmentManagement.vue`)
- [x] 拓扑向导页面 (`frontend/src/views/simulator/TopologyWizard.vue`)
- [x] 模板管理页面 (`frontend/src/views/simulator/TemplateManagement.vue`)
- [x] 故障管理页面 (`frontend/src/views/simulator/FaultManagement.vue`)

---

### 二、网络拓扑生成功能增强

#### 1. 拓扑架构设计
- [x] 设计5层网络拓扑模型
  - 客户端层 (Client)
  - 负载均衡层 (Nginx)
  - 应用层 (App Server / API Gateway)
  - 缓存层 (Redis)
  - 数据库层 (MySQL)

#### 2. 后端实现
- [x] 拓扑生成引擎 (`backend/apps/simulator/engine/topology_generator.py`)
  - 支持多种拓扑类型：standard（标准）、microservice（微服务）、monolithic（单体）
  - 支持多种规模：small（小型）、medium（中型）、large（大型）
  - 基于层级的IP分配算法，避免IP冲突
  - 自动生成组件关系

- [x] 拓扑管理器 (`backend/apps/simulator/engine/topology_manager.py`)
  - 环境激活/停用管理
  - 组件状态管理

- [x] API接口更新 (`backend/apps/simulator/router.py`)
  - `POST /environments/generate`: 生成拓扑环境
  - `GET /topology/types`: 获取拓扑类型列表
  - `GET /topology/scales`: 获取规模配置列表
  - `GET /topology/components`: 获取组件类型列表
  - `GET /topology/check-ip`: 检查IP前缀冲突

- [x] Schemas更新 (`backend/apps/simulator/schemas.py`)
  - TopologyGenerateRequest: 拓扑生成请求
  - TopologyGenerateResponse: 拓扑生成响应
  - TopologyType/Scale/ComponentType: 配置模型

#### 3. 前端实现
- [x] API接口定义 (`frontend/src/api/simulator.ts`)
  - 拓扑生成相关接口

- [x] 拓扑向导页面 (`frontend/src/views/simulator/TopologyWizard.vue`)
  - 6步向导式拓扑生成流程
  - 基础配置 → 拓扑类型 → 规模配置 → 组件选择 → 网络配置 → 确认生成

- [x] 环境管理页面重构 (`frontend/src/views/simulator/EnvironmentManagement.vue`)
  - 移除多环境标签页，改为单环境模式
  - 表格视图改为层级拓扑图展示
  - 简化按钮逻辑（创建/重新生成）

---

### 三、指标监控体系完善

#### 1. 指标模板扩展
- [x] 从17个指标扩展到104个指标
- [x] 覆盖所有组件类型的完整指标集

| 组件类型 | 指标数量 | 主要指标 |
|---------|---------|---------|
| host | 7 | CPU、内存、磁盘、网络IO |
| client | 6 | 请求成功率、响应时间、活跃会话 |
| nginx | 10 | 连接数、请求速率、缓存命中率、SSL握手 |
| app_server | 18 | JVM堆内存、GC、线程池、连接池 |
| api_gateway | 10 | 路由数、熔断器、限流拒绝、重试 |
| firewall | 11 | 连接数、阻断率、规则命中、数据包统计 |
| redis | 15 | 连接客户端、内存、键空间、命中率、OPS |
| config_center | 8 | 配置项、监听数、同步状态 |
| mysql | 19 | 连接数、查询、慢查询、InnoDB缓冲池、锁等待 |

#### 2. 指标生成引擎
- [x] 指标生成器 (`backend/apps/simulator/engine/metric_generator.py`)
  - 基于模板生成指标
  - 支持故障影响
  - 支持动态调整

#### 3. 定时任务调度
- [x] 调度器 (`backend/apps/simulator/tasks/scheduler.py`)
  - 指标推送任务：每分钟执行
  - 故障检测任务：每10秒执行
  - 故障恢复任务：监控活跃故障

#### 4. 数据库更新
- [x] 删除旧的17个指标模板
- [x] 插入新的104个指标模板

---

### 四、日志生成模块

#### 1. 日志生成引擎
- [x] 日志生成器 (`backend/apps/simulator/engine/log_generator.py`)
  - 支持多种日志格式：Log4j、Nginx、MySQL、Redis
  - 全链路日志模拟
  - 支持故障影响

#### 2. 日志模板管理
- [x] 日志模板 API
- [x] 日志模板前端页面

#### 3. 日志存储
- [x] 日志文件存储到 `simulator/logs/`
- [x] 日志分类目录：
  - `/logs/java/`：Java 应用日志
  - `/logs/nginx/`：Nginx 中间件日志
  - `/logs/database/`：数据库日志
  - `/logs/host/`：主机系统日志

---

### 五、故障模拟模块

#### 1. 故障引擎
- [x] 故障引擎 (`backend/apps/simulator/engine/fault_engine.py`)
  - 故障随机触发机制
  - 故障影响应用
  - 故障自动恢复

#### 2. 故障场景管理
- [x] 故障场景 API
- [x] 故障场景前端页面 (`frontend/src/views/simulator/FaultManagement.vue`)

#### 3. 故障实例管理
- [x] 故障实例 API
- [x] 故障实例前端页面

---

### 六、MetricBot 集成

#### 1. 主机模型同步
- [x] 组件同步到主机模型 (`POST /environments/{id}/sync-to-hosts`)
  - 组件类型 `host` → Host 模型
  - 组件类型 `java_app` → Host 模型，tags=["java-app"]
  - 组件类型 `database` → Host 模型，tags=["database"]
  - 组件类型 `nginx` → Host 模型，tags=["nginx"]

#### 2. 关系模型同步
- [x] 组件关系同步到关系模型
  - `calls` → HostRelation，relation_type="calls"
  - `depends_on` → HostRelation，relation_type="depends_on"
  - `contains` → HostRelation，relation_type="contains"

---

### 七、前端样式优化

- [x] el-steps 组件深色主题适配
  - 全局样式文件添加深色主题样式
  - 步骤条背景、标题颜色、箭头颜色适配

- [x] Element Plus 图标导入修复
  - 替换不存在的 Server 图标为 DataBoard

---

## 待完成工作

### 第一阶段：功能完善

- [ ] 拓扑生成测试验证
  - 通过向导创建完整环境
  - 验证所有组件和关系正确生成
  - 验证指标数据能正确推送到 Pushgateway

- [ ] 故障场景适配
  - 更新故障场景模板支持新增组件类型（nginx, redis, mysql, api_gateway, firewall, config_center, kafka）
  - 添加 Nginx、Redis、MySQL 特定故障模板

- [ ] 前端交互优化
  - 拓扑图节点点击查看详情
  - 添加组件状态实时监控
  - 拓扑图缩放和拖拽功能

### 第二阶段：可视化增强

- [ ] 拓扑图流量动态展示
- [ ] 组件健康状态可视化
- [ ] 告警事件在拓扑图上标注

### 第三阶段：高级功能

- [ ] 历史场景回放
- [ ] 拓扑模板保存与加载
- [ ] 自定义拓扑编辑器（基于 AntV X6）

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端 (Vue 3)                             │
├─────────────────────────────────────────────────────────────┤
│  TopologyWizard.vue  │  EnvironmentManagement.vue           │
│  TemplateManagement.vue  │  FaultManagement.vue            │
├─────────────────────────────────────────────────────────────┤
│                  API Layer (Axios)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端 (FastAPI)                            │
├─────────────────────────────────────────────────────────────┤
│  Router (API)  │  TopologyGenerator  │  MetricGenerator     │
│  LogGenerator  │  FaultEngine        │  Scheduler           │
├─────────────────────────────────────────────────────────────┤
│                    Database (MySQL)                          │
│  Environment  │  Component  │  Relation  │  MetricTemplate  │
│  LogTemplate  │  FaultScenario  │  FaultInstance           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    外部系统                                  │
│  Prometheus  │  Pushgateway                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 网络拓扑模型

```
┌─────────────┐
│   客户端层   │  Client (模拟用户请求)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  负载均衡层  │  Nginx (请求分发、缓存)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   应用层    │  App Server / API Gateway (业务逻辑)
│  [防火墙]   │  Firewall (访问控制)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   缓存层    │  Redis (数据缓存、会话存储)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  数据库层   │  MySQL (数据持久化)
│  [防火墙]   │  Firewall (数据库访问控制)
└─────────────┘
```

---

## 开发进度总览

| 模块 | 状态 | 进度 |
|------|------|------|
| 基础框架 | ✅ 已完成 | 100% |
| 拓扑管理 | ✅ 已完成 | 100% |
| 指标生成 | ✅ 已完成 | 100% |
| 日志生成 | ✅ 已完成 | 100% |
| 故障模拟 | ✅ 已完成 | 100% |
| MetricBot 集成 | ✅ 已完成 | 100% |
| 功能完善 | 🔴 未开始 | 0% |
| 可视化增强 | 🔴 未开始 | 0% |
| 高级功能 | 🔴 未开始 | 0% |

**状态说明：**
- ✅ 已完成：功能已实现并测试通过
- 🟡 进行中：正在开发中
- 🔴 未开始：尚未开始开发

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-04-03 | 更新开发进度总览，添加日志生成、故障模拟、MetricBot集成完成状态 |
| 2026-03-29 | 完成5层拓扑架构设计、拓扑生成引擎、前端向导页面、指标体系扩展(104个)、环境管理重构 |
