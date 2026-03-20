# Metric Bot - 智能运维监控平台

> 最后更新时间：2026-03-20
> 项目版本：v0.1.0

---

## 项目简介

Metric Bot 是一个基于大语言模型的智能运维监控平台，提供以下核心功能：

- 📊 **监控面板** - 实时告警展示和趋势分析
- 💬 **智能对话** - 自然语言查询运维数据
- 🚨 **智能监控** - 告警规则配置和管理
- ⚙️ **配置中心** - 模型、数据源、日志、主机、关系管理
- 🔍 **根因分析** - 基于算法和大模型的故障定位

---

## 项目结构

```
Metric Bot/
├── backend/                    # 后端服务（Python + FastAPI）
│   ├── apps/                  # 应用模块
│   │   ├── auth/               # 用户认证
│   │   ├── model/              # 模型管理
│   │   ├── datasource/         # 数据源管理
│   │   └── alert/              # 告警管理
│   ├── common/                # 公共模块
│   │   └── core/              # 核心功能
│   ├── main.py                # 后端入口
│   ├── pyproject.toml         # Python项目配置
│   └── .env.example           # 环境变量示例
├── frontend/                   # 前端服务（Vue3 + TypeScript + Vite）
│   ├── src/                   # 前端源代码
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API接口
│   │   ├── stores/             # 状态管理
│   │   └── router/             # 路由配置
│   ├── package.json            # Node项目配置
│   └── vite.config.ts          # Vite配置
├── docs/                       # 文档
│   ├── PROJECT_MODULES.md      # 项目模块规划
│   ├── API_REFERENCE.md        # API接口文档
│   ├── ALERT_ENGINE_DESIGN.md  # 告警引擎设计
│   └── RCA_ALGORITHMS_REPORT.md # 根因分析算法报告
└── README.md                   # 本文档
```

---

## 功能模块

### ✅ 已完成模块

| 模块 | 状态 | 说明 |
|------|------|------|
| 用户认证 | ✅ | 登录、注册、JWT认证 |
| 模型管理 | ✅ | 模型CRUD、设为默认、测试连接 |
| 数据源管理 | ✅ | 数据源CRUD、测试连接 |
| 告警管理（后端） | ✅ | 告警规则CRUD、告警查询、统计、测试 |

### 🟡 进行中模块

| 模块 | 状态 | 说明 |
|------|------|------|
| 告警引擎优化 | 🟡 | 批量查询、缓存、并行、差异化频率 |
| 前端告警页面 | 🟡 | 规则管理、告警列表、统计 |
| 日志配置 | 🟡 | 日志数据源管理 |
| 主机模型 | 🟡 | 主机信息管理 |
| 关系模型 | 🟡 | 拓扑关系管理 |

---

## 技术栈

### 后端技术栈
- Python 3.8+
- FastAPI - Web 框架
- Uvicorn - ASGI 服务器
- SQLAlchemy - ORM
- Pydantic - 数据验证
- MySQL - 数据库
- JWT - 认证

### 前端技术栈
- Vue 3 - 前端框架
- TypeScript - 类型安全
- Vite - 构建工具
- Element Plus - UI 组件库
- Pinia - 状态管理
- Vue Router - 路由管理
- Axios - HTTP 客户端

---

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 后端启动

```bash
cd backend

# 1. 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，配置数据库连接等

# 4. 初始化数据库
python init_db.py

# 5. 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

### 前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 默认账号
- 用户名: `admin`
- 密码: `admin123`

---

## API 文档

### 在线文档
启动后端服务后，访问以下地址查看：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 接口文档
详细的 API 接口文档请查看：
- [API_REFERENCE.md](docs/API_REFERENCE.md)

### 接口概览
| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/api/v1/auth/*` | 登录、注册、获取当前用户 |
| 模型 | `/api/v1/models/*` | 模型 CRUD、设为默认 |
| 数据源 | `/api/v1/datasources/*` | 数据源 CRUD、测试连接 |
| 告警 | `/api/v1/alerts/*` | 告警规则、告警查询、统计 |

---

## 设计文档

| 文档 | 说明 |
|------|------|
| [PROJECT_MODULES.md](docs/PROJECT_MODULES.md) | 项目模块规划 |
| [ALERT_ENGINE_DESIGN.md](docs/ALERT_ENGINE_DESIGN.md) | 告警评估引擎设计 |
| [RCA_ALGORITHMS_REPORT.md](docs/RCA_ALGORITHMS_REPORT.md) | 根因分析算法深度报告 |

---

## 开发进度

### 总进度概览

| 模块 | 进度 | 状态 |
|------|------|------|
| 用户认证 | 100% | ✅ 已完成 |
| 模型管理 | 80% | 🟡 后端完成 |
| 数据源管理 | 80% | 🟡 后端完成 |
| 告警管理 | 70% | 🟡 后端完成 |
| 监控面板 | 50% | 🟡 前端完成 |
| 智能对话 | 50% | 🟡 前端完成 |
| 智能监控 | 50% | 🟡 前端完成 |
| 日志配置 | 50% | 🟡 前端完成 |
| 主机模型 | 50% | 🟡 前端完成 |
| 关系模型 | 50% | 🟡 前端完成 |

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

---

**README 结束**
