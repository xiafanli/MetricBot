import json
import httpx
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.core.database import get_db
from apps.datasource.models import Datasource
from apps.datasource.schemas import DatasourceCreate, DatasourceUpdate, DatasourceResponse
from apps.auth.security import get_current_active_user
from apps.auth.models import User

router = APIRouter(prefix="/datasources", tags=["监控数据源"])


async def test_prometheus(url: str, auth_type: str, auth_value: str, password: str) -> bool:
    headers = {}
    auth = None
    
    if auth_type == "basic":
        auth = (auth_value, password)
    elif auth_type == "token" and auth_value:
        headers["Authorization"] = f"Bearer {auth_value}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url.rstrip('/')}/api/v1/targets", headers=headers, auth=auth)
            return response.status_code == 200
    except Exception:
        return False


async def test_zabbix(url: str, auth_type: str, auth_value: str, password: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "apiinfo.version",
                "params": [],
                "id": 1
            }
            response = await client.post(url.rstrip('/') + "/api_jsonrpc.php", json=payload)
            return response.status_code == 200
    except Exception:
        return False


@router.post("/test", status_code=status.HTTP_200_OK)
async def test_datasource_connection(
    datasource: DatasourceCreate,
    current_user: User = Depends(get_current_active_user),
):
    success = False
    message = ""
    
    if datasource.type == "Prometheus":
        success = await test_prometheus(
            datasource.url,
            datasource.auth_type,
            datasource.auth_value or "",
            datasource.password or ""
        )
        message = "Prometheus 连接成功" if success else "Prometheus 连接失败"
    elif datasource.type == "Zabbix":
        success = await test_zabbix(
            datasource.url,
            datasource.auth_type,
            datasource.auth_value or "",
            datasource.password or ""
        )
        message = "Zabbix 连接成功" if success else "Zabbix 连接失败"
    else:
        message = f"{datasource.type} 测试暂不支持"
    
    return {"success": success, "message": message}


def datasource_to_dict(ds: Datasource) -> dict:
    data = {
        "id": ds.id,
        "name": ds.name,
        "type": ds.type,
        "url": ds.url,
        "auth_type": ds.auth_type,
        "auth_value": ds.auth_value,
        "password": ds.password,
        "config": json.loads(ds.config) if ds.config else None,
        "enabled": ds.enabled,
        "created_at": ds.created_at,
        "updated_at": ds.updated_at,
    }
    return data


@router.get("", response_model=List[DatasourceResponse])
def get_datasources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    enabled_only: bool = False
):
    query = db.query(Datasource)
    if enabled_only:
        query = query.filter(Datasource.enabled == True)
    datasources = query.order_by(Datasource.created_at.desc()).all()
    return [datasource_to_dict(ds) for ds in datasources]


@router.get("/{datasource_id}", response_model=DatasourceResponse)
def get_datasource(
    datasource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ds = db.query(Datasource).filter(Datasource.id == datasource_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return datasource_to_dict(ds)


@router.post("", response_model=DatasourceResponse, status_code=status.HTTP_201_CREATED)
def create_datasource(
    datasource: DatasourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    config_json = json.dumps(datasource.config) if datasource.config else None
    
    db_ds = Datasource(
        name=datasource.name,
        type=datasource.type,
        url=datasource.url,
        auth_type=datasource.auth_type,
        auth_value=datasource.auth_value,
        password=datasource.password,
        config=config_json,
        enabled=datasource.enabled,
    )
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)
    
    return datasource_to_dict(db_ds)


@router.put("/{datasource_id}", response_model=DatasourceResponse)
def update_datasource(
    datasource_id: int,
    datasource_update: DatasourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_ds = db.query(Datasource).filter(Datasource.id == datasource_id).first()
    if not db_ds:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    update_data = datasource_update.model_dump(exclude_unset=True)
    
    if "config" in update_data:
        update_data["config"] = json.dumps(update_data["config"]) if update_data["config"] else None
    
    for field, value in update_data.items():
        setattr(db_ds, field, value)
    
    db.commit()
    db.refresh(db_ds)
    
    return datasource_to_dict(db_ds)


@router.delete("/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_datasource(
    datasource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_ds = db.query(Datasource).filter(Datasource.id == datasource_id).first()
    if not db_ds:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    db.delete(db_ds)
    db.commit()
    return None
