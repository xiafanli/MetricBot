# MetricBot - 智能运维监控平台

> 最后更新：2026-04-01  
> 项目版本：v0.3.0

---

## 项目简介

MetricBot 是一个基于大语言模型的智能运维监控平台，提供自然语言交互、智能告警、AI诊断、环境模拟等核心功能，帮助运维人员高效管理和分析监控数据。

---

## 核心功能

### 📊 监控面板
- 实时告警状态展示
- 告警趋势可视化图表
- 关键指标监控

### 💬 智能对话
- 自然语言查询监控数据
- 多轮对话上下文管理
- 支持多种大模型切换

### 🚨 智能监控
- **告警规则管理**：配置告警阈值和触发条件
- **告警列表**：查看所有告警记录
- **AI智能诊断**：基于大模型的告警根因分析
- **告警聚合**：时间窗口、拓扑关联、语义相似三种聚合策略
- **根因分析**：随机游走、时序相关性、LLM推理三种分析器
- **告警统计**：多维度告警数据分析

### 🔧 配置中心
- **模型管理**：配置 OpenAI、Azure、Ollama 等大模型
- **监控数据源**：管理 Prometheus 等监控数据源
- **日志配置**：配置 Elasticsearch、StarRocks 日志数据源
- **主机模型**：主机信息管理和自动同步
- **关系模型**：拓扑关系配置和可视化

### 🧪 环境模拟器
- **环境管理**：创建和管理模拟环境
- **组件配置**：配置模拟组件和指标模板
- **故障注入**：模拟各类故障场景
- **指标推送**：自动推送模拟指标到 Pushgateway

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                          前端 (Vue 3)                            │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard  │  Chat  │  Alerts  │  Settings  │  Simulator       │
├─────────────────────────────────────────────────────────────────┤
│                    Element Plus + Axios + Pinia                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端 (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│  Auth  │  Model  │  Datasource  │  Alert  │  Host  │  Simulator │
├─────────────────────────────────────────────────────────────────┤
│                    SQLAlchemy + MySQL                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         外部系统                                 │
│  Prometheus  │  Pushgateway  │  Elasticsearch  │  LLM Service   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 项目结构

```
MetricBot/
├── backend/                    # 后端服务
│   ├── apps/                   # 应用模块
│   │   ├── auth/               # 用户认证
│   │   ├── model/              # 模型管理
│   │   ├── datasource/         # 数据源管理
│   │   ├── alert/              # 告警管理
│   │   │   ├── engine/         # 告警评估引擎
│   │   │   ├── diagnosis/      # AI诊断模块
│   │   │   └── router.py       # API路由
│   │   ├── log/                # 日志配置
│   │   ├── host/               # 主机管理
│   │   └── simulator/          # 环境模拟器
│   ├── common/                 # 公共模块
│   ├── main.py                 # 后端入口
│   ├── pyproject.toml          # 项目配置
│   └── .env.example            # 环境变量示例
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── alert/          # 告警相关页面
│   │   │   ├── settings/       # 配置中心页面
│   │   │   └── simulator/      # 模拟器页面
│   │   ├── api/                # API接口
│   │   ├── stores/             # 状态管理
│   │   └── router/             # 路由配置
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # 文档
│   ├── PROJECT_MODULES.md      # 模块规划
│   ├── ALERT_ENGINE_DESIGN.md  # 告警引擎设计
│   ├── ALERT_MODULE_PROGRESS.md # 告警模块进度
│   └── RCA_ALGORITHMS_REPORT.md # 根因分析报告
└── README.md
```

---

## 技术栈

### 后端
- **框架**：Python 3.11+ / FastAPI
- **ORM**：SQLAlchemy
- **数据库**：MySQL (utf8mb4)
- **认证**：JWT
- **任务调度**：APScheduler
- **HTTP客户端**：httpx

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **UI组件**：Element Plus
- **状态管理**：Pinia
- **路由**：Vue Router
- **HTTP**：Axios

---

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 16+
- MySQL 5.7+
- Prometheus + Pushgateway (可选)

### 后端启动

```bash
cd backend

# 激活虚拟环境
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .

# 配置环境变量
copy .env.example .env
# 编辑 .env 配置数据库连接等

# 启动服务
python main.py
```

后端服务地址：http://localhost:8000
- Swagger文档：http://localhost:8000/docs
- ReDoc文档：http://localhost:8000/redoc

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务地址：http://localhost:5173

### 默认账号
- 用户名：`admin`
- 密码：`admin123`

---

## 功能模块状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 用户认证 | ✅ 完成 | 登录、注册、JWT认证 |
| 模型管理 | ✅ 完成 | 多模型配置、测试连接 |
| 数据源管理 | ✅ 完成 | Prometheus数据源管理 |
| 日志配置 | ✅ 完成 | ES/StarRocks日志源 |
| 主机模型 | ✅ 完成 | 主机信息管理 |
| 关系模型 | ✅ 完成 | 拓扑关系配置 |
| 智能对话 | ✅ 完成 | 自然语言查询 |
| 环境模拟器 | ✅ 完成 | 故障模拟、指标推送 |
| 告警规则管理 | ✅ 完成 | 规则CRUD、启用/禁用 |
| 告警列表 | ✅ 完成 | 告警查询、确认、恢复 |
| AI诊断 | ✅ 完成 | 告警根因分析 |
| 告警聚合 | ✅ 完成 | 时间窗口、拓扑关联、语义相似聚合 |
| 根因分析 | ✅ 完成 | 随机游走、时序相关性、LLM推理 |
| 异常检测 | 🔲 计划中 | 智能异常检测 |

---

## API 接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/api/v1/auth/*` | 登录、注册、获取用户信息 |
| 模型 | `/api/v1/models/*` | 模型CRUD、设为默认 |
| 数据源 | `/api/v1/datasources/*` | 数据源CRUD、测试连接 |
| 告警规则 | `/api/v1/alerts/rules/*` | 规则CRUD |
| 告警事件 | `/api/v1/alerts/events/*` | 告警查询、统计 |
| 告警聚合 | `/api/v1/alerts/groups/*` | 聚合告警管理 |
| 聚合策略 | `/api/v1/alerts/policies/*` | 聚合策略配置 |
| 根因分析 | `/api/v1/alerts/groups/{id}/rca` | RCA报告生成 |
| 诊断 | `/api/v1/alerts/diagnosis/*` | AI诊断接口 |
| 主机 | `/api/v1/hosts/*` | 主机管理、关系管理 |
| 日志 | `/api/v1/logs/*` | 日志源管理 |
| 模拟器 | `/api/v1/simulator/*` | 环境、组件、故障管理 |

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [PROJECT_MODULES.md](docs/PROJECT_MODULES.md) | 项目模块规划 |
| [ALERT_ENGINE_DESIGN.md](docs/ALERT_ENGINE_DESIGN.md) | 告警引擎设计 |
| [ALERT_MODULE_PROGRESS.md](docs/ALERT_MODULE_PROGRESS.md) | 告警模块开发进度 |
| [RCA_ALGORITHMS_REPORT.md](docs/RCA_ALGORITHMS_REPORT.md) | 根因分析算法报告 |

---

## 开发进度

详细进度请查看 [ALERT_MODULE_PROGRESS.md](docs/ALERT_MODULE_PROGRESS.md)

### Phase 1 (已完成)
- ✅ 基础告警功能
- ✅ 前端页面
- ✅ AI诊断

### Phase 2 (已完成)
- ✅ 告警聚合与降噪
- ✅ 根因分析

### Phase 3 (计划中)
- 🔲 智能异常检测
- 🔲 高级诊断功能

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
