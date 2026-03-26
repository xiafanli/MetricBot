# Metric Bot - Intelligent Ops Monitoring Platform

> Last Updated: 2026-03-27  
> Project Version: v0.1.0

---

## Project Overview

Metric Bot is an intelligent operations monitoring platform powered by large language models, providing the following core features:

- 📊 **Monitoring Dashboard** - Real-time alert display and trend analysis
- 💬 **Intelligent Chat** - Natural language querying of operations data
- 🚨 **Smart Monitoring** - Alert rule configuration and management
- ⚙️ **Configuration Center** - Model, data source, log, host, and relation management
- 🔍 **Root Cause Analysis** - Algorithm and LLM-based fault localization

---

## Project Structure

```
Metric Bot/
├── backend/                    # Backend service (Python + FastAPI)
│   ├── apps/                  # Application modules
│   │   ├── auth/               # User authentication
│   │   ├── model/              # Model management
│   │   ├── datasource/         # Data source management
│   │   └── alert/              # Alert management
│   ├── common/                # Common modules
│   │   └── core/              # Core functionality
│   ├── main.py                # Backend entry point
│   ├── pyproject.toml         # Python project configuration
│   └── .env.example           # Environment variable example
├── frontend/                   # Frontend service (Vue3 + TypeScript + Vite)
│   ├── src/                   # Frontend source code
│   │   ├── views/              # Page components
│   │   ├── api/                # API interfaces
│   │   ├── stores/             # State management
│   │   └── router/             # Routing configuration
│   ├── package.json            # Node project configuration
│   └── vite.config.ts          # Vite configuration
├── docs/                       # Documentation
│   ├── PROJECT_MODULES.md      # Project module planning
│   ├── API_REFERENCE.md        # API interface documentation
│   ├── ALERT_ENGINE_DESIGN.md  # Alert engine design
│   └── RCA_ALGORITHMS_REPORT.md # Root cause analysis algorithm report
├── README.md                   # This document
└── README_cn.md               # Chinese version documentation
```

---

## Feature Modules

### ✅ Completed Modules

| Module | Status | Description |
|--------|--------|-------------|
| User Authentication | ✅ | Login, registration, JWT authentication |
| Model Management | ✅ | Model CRUD, set as default, test connection |
| Data Source Management | ✅ | Data source CRUD, test connection |
| Alert Management (Backend) | ✅ | Alert rule CRUD, alert query, statistics, testing |

### 🟡 In Progress Modules

| Module | Status | Description |
|--------|--------|-------------|
| Alert Engine Optimization | 🟡 | Batch queries, caching, parallelism, differential frequency |
| Frontend Alert Page | 🟡 | Rule management, alert list, statistics |
| Log Configuration | 🟡 | Log data source management |
| Host Model | 🟡 | Host information management |
| Relation Model | 🟡 | Topology relation management |

---

## Tech Stack

### Backend Tech Stack
- Python 3.8+
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - ORM
- Pydantic - Data validation
- MySQL - Database
- JWT - Authentication

### Frontend Tech Stack
- Vue 3 - Frontend framework
- TypeScript - Type safety
- Vite - Build tool
- Element Plus - UI component library
- Pinia - State management
- Vue Router - Routing management
- Axios - HTTP client

---

## Quick Start

### Requirements
- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### Backend Setup

```bash
cd backend

# 1. Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env to configure database connection, etc.

# 4. Initialize database
python init_db.py

# 5. Start service
python main.py
```

Backend service will start at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start development server
npm run dev
```

Frontend service will start at http://localhost:5173

### Default Account
- Username: `admin`
- Password: `admin123`

---

## API Documentation

### Online Documentation
After starting the backend service, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Interface Documentation
For detailed API interface documentation, see:
- [API_REFERENCE.md](docs/API_REFERENCE.md)

### Interface Overview
| Module | Path | Description |
|--------|------|-------------|
| Authentication | `/api/v1/auth/*` | Login, registration, get current user |
| Models | `/api/v1/models/*` | Model CRUD, set as default |
| Data Sources | `/api/v1/datasources/*` | Data source CRUD, test connection |
| Alerts | `/api/v1/alerts/*` | Alert rules, alert query, statistics |

---

## Design Documents

| Document | Description |
|----------|-------------|
| [PROJECT_MODULES.md](docs/PROJECT_MODULES.md) | Project module planning |
| [ALERT_ENGINE_DESIGN.md](docs/ALERT_ENGINE_DESIGN.md) | Alert evaluation engine design |
| [RCA_ALGORITHMS_REPORT.md](docs/RCA_ALGORITHMS_REPORT.md) | Root cause analysis algorithm in-depth report |

---

## Development Progress

### Overall Progress

| Module | Progress | Status |
|--------|----------|--------|
| User Authentication | 100% | ✅ Completed |
| Model Management | 80% | 🟡 Backend complete |
| Data Source Management | 80% | 🟡 Backend complete |
| Alert Management | 70% | 🟡 Backend complete |
| Monitoring Dashboard | 50% | 🟡 Frontend complete |
| Intelligent Chat | 50% | 🟡 Frontend complete |
| Smart Monitoring | 50% | 🟡 Frontend complete |
| Log Configuration | 50% | 🟡 Frontend complete |
| Host Model | 50% | 🟡 Frontend complete |
| Relation Model | 50% | 🟡 Frontend complete |

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

If you have any questions or suggestions, please submit an Issue or Pull Request.

---

**README End**
