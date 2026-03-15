__version__ = "0.1.0"

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from apps.auth.router import router as auth_router

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
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)