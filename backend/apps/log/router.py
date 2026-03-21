import json
import httpx
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.core.database import get_db
from apps.log.models import LogSource
from apps.log.schemas import (
    LogSourceCreate,
    LogSourceUpdate,
    LogSourceResponse,
    LogTestRequest,
    LogTestResponse
)
from apps.auth.security import get_current_active_user
from apps.auth.models import User

router = APIRouter(prefix="/logs", tags=["日志管理"])


def log_source_to_dict(ls: LogSource) -> dict:
    return {
        "id": ls.id,
        "name": ls.name,
        "type": ls.type,
        "url": ls.url,
        "index_or_table": ls.index_or_table,
        "username": ls.username,
        "password": ls.password,
        "retention_days": ls.retention_days,
        "config": json.loads(ls.config) if ls.config else None,
        "enabled": ls.enabled,
        "created_at": ls.created_at,
        "updated_at": ls.updated_at,
    }


async def test_elasticsearch(url: str, index_or_table: str, username: str, password: str) -> bool:
    """测试 Elasticsearch 连接"""
    try:
        auth = None
        if username and password:
            auth = (username, password)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url.rstrip('/')}/_cluster/health", auth=auth)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") in ["green", "yellow"]
        return False
    except Exception:
        return False


async def test_starrocks(url: str, index_or_table: str, username: str, password: str) -> bool:
    """测试 StarRocks 连接"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url.rstrip('/')}/api/health")
            return response.status_code == 200
    except Exception:
        return False


# ==================== 日志源 API ====================

@router.get("", response_model=List[LogSourceResponse])
def get_log_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    enabled_only: bool = False
):
    query = db.query(LogSource)
    if enabled_only:
        query = query.filter(LogSource.enabled == True)
    log_sources = query.order_by(LogSource.created_at.desc()).all()
    return [log_source_to_dict(ls) for ls in log_sources]


@router.get("/{log_id}", response_model=LogSourceResponse)
def get_log_source(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ls = db.query(LogSource).filter(LogSource.id == log_id).first()
    if not ls:
        raise HTTPException(status_code=404, detail="日志源不存在")
    return log_source_to_dict(ls)


@router.post("", response_model=LogSourceResponse, status_code=status.HTTP_201_CREATED)
def create_log_source(
    log_source: LogSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    config_json = json.dumps(log_source.config) if log_source.config else None
    
    db_ls = LogSource(
        name=log_source.name,
        type=log_source.type,
        url=log_source.url,
        index_or_table=log_source.index_or_table,
        username=log_source.username,
        password=log_source.password,
        retention_days=log_source.retention_days,
        config=config_json,
        enabled=log_source.enabled,
    )
    db.add(db_ls)
    db.commit()
    db.refresh(db_ls)
    
    return log_source_to_dict(db_ls)


@router.put("/{log_id}", response_model=LogSourceResponse)
def update_log_source(
    log_id: int,
    log_update: LogSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_ls = db.query(LogSource).filter(LogSource.id == log_id).first()
    if not db_ls:
        raise HTTPException(status_code=404, detail="日志源不存在")
    
    update_data = log_update.model_dump(exclude_unset=True)
    
    if "config" in update_data:
        update_data["config"] = json.dumps(update_data["config"]) if update_data["config"] else None
    
    for field, value in update_data.items():
        setattr(db_ls, field, value)
    
    db.commit()
    db.refresh(db_ls)
    
    return log_source_to_dict(db_ls)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log_source(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_ls = db.query(LogSource).filter(LogSource.id == log_id).first()
    if not db_ls:
        raise HTTPException(status_code=404, detail="日志源不存在")
    
    db.delete(db_ls)
    db.commit()
    return None


@router.post("/test", response_model=LogTestResponse)
async def test_log_source_connection(
    test_request: LogTestRequest,
    current_user: User = Depends(get_current_active_user),
):
    success = False
    message = ""
    
    if test_request.type == "Elasticsearch":
        success = await test_elasticsearch(
            test_request.url,
            test_request.index_or_table or "",
            test_request.username or "",
            test_request.password or ""
        )
        message = "Elasticsearch 连接成功" if success else "Elasticsearch 连接失败"
    elif test_request.type == "StarRocks":
        success = await test_starrocks(
            test_request.url,
            test_request.index_or_table or "",
            test_request.username or "",
            test_request.password or ""
        )
        message = "StarRocks 连接成功" if success else "StarRocks 连接失败"
    else:
        message = f"{test_request.type} 测试暂不支持"
    
    return LogTestResponse(
        success=success,
        message=message
    )
