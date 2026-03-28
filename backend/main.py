__version__ = "0.1.0"

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from apps.auth.router import router as auth_router
from apps.model.router import router as model_router
from apps.datasource.router import router as datasource_router
from apps.alert.router import router as alert_router
from apps.log.router import router as log_router
from apps.host.router import router as host_router
from apps.simulator import router as simulator_router
from apps.simulator.tasks import scheduler
from apps.alert.engine import alert_scheduler
from common.core.database import engine, Base

# 导入所有模型以确保它们被注册到 Base.metadata
from apps.auth.models import User
from apps.model.models import Model
from apps.datasource.models import Datasource
from apps.alert.models import AlertRule, Alert
from apps.log.models import LogSource
from apps.host.models import Host, HostRelation
from apps.simulator.models import (
    SimulationEnvironment,
    SimulationComponent,
    ComponentRelation,
    MetricTemplate,
    LogTemplate,
    FaultScenario,
    FaultInstance,
)

# 创建所有表
Base.metadata.create_all(bind=engine)

# 创建API路由
api_router = APIRouter(prefix="/api/v1")

app = FastAPI(title="Metric Bot", description="智能运维监控平台", version=__version__)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Metric Bot!"}


@api_router.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}


# 注册API路由
api_router.include_router(auth_router)
api_router.include_router(model_router)
api_router.include_router(datasource_router)
api_router.include_router(alert_router)
api_router.include_router(log_router)
api_router.include_router(host_router)
api_router.include_router(simulator_router)
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    scheduler.start()
    alert_scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    alert_scheduler.stop()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)