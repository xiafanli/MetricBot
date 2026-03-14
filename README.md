# PrometheusBot

基于大语言模型的 Prometheus 监控查询助手

## 项目结构

```
PrometheusBot/
├── backend/          # 后端服务（Python + FastAPI）
│   ├── prometheusbot/    # 后端源代码
│   ├── pyproject.toml    # Python项目配置
│   ├── main.py            # 后端入口文件
│   └── .env.example       # 环境变量示例
├── frontend/         # 前端服务（Vue3 + TypeScript + Vite）
│   ├── src/              # 前端源代码
│   ├── public/           # 静态资源
│   ├── package.json      # Node项目配置
│   ├── vite.config.ts    # Vite配置
│   └── tsconfig.json     # TypeScript配置
└── docs/             # 文档
```

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- Uvicorn - ASGI服务器
- Pydantic - 数据验证

### 前端
- Vue 3 - 前端框架
- TypeScript - 类型安全
- Vite - 构建工具
- Element Plus - UI组件库
- Pinia - 状态管理
- Vue Router - 路由管理
- Axios - HTTP客户端

## 快速开始

### 后端启动

```bash
cd backend
# 安装依赖
pip install -e .
# 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

### 前端启动

```bash
cd frontend
# 安装依赖
npm install
# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc