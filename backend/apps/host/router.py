import json
import httpx
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.core.database import get_db
from apps.host.models import Host, HostRelation
from apps.host.schemas import (
    HostCreate,
    HostUpdate,
    HostResponse,
    HostRelationCreate,
    HostRelationUpdate,
    HostRelationResponse,
    PrometheusSyncRequest,
    PrometheusSyncPreviewResponse,
    PrometheusSyncImportResponse
)
from apps.auth.security import get_current_active_user
from apps.auth.models import User
from apps.datasource.models import Datasource

router = APIRouter(prefix="/hosts", tags=["主机管理"])


def host_to_dict(host: Host) -> dict:
    return {
        "id": host.id,
        "name": host.name,
        "ip": host.ip,
        "hostname": host.hostname,
        "os": host.os,
        "os_version": host.os_version,
        "cpu_cores": host.cpu_cores,
        "memory_gb": float(host.memory_gb) if host.memory_gb else None,
        "disk_gb": float(host.disk_gb) if host.disk_gb else None,
        "tags": json.loads(host.tags) if host.tags else None,
        "extra_data": json.loads(host.extra_data) if host.extra_data else None,
        "from_type": host.from_type,
        "from_name": host.from_name,
        "enabled": host.enabled,
        "created_at": host.created_at,
        "updated_at": host.updated_at,
    }


def host_relation_to_dict(rel: HostRelation) -> dict:
    return {
        "id": rel.id,
        "source_host_id": rel.source_host_id,
        "target_host_id": rel.target_host_id,
        "relation_type": rel.relation_type,
        "description": rel.description,
        "extra_data": json.loads(rel.extra_data) if rel.extra_data else None,
        "created_at": rel.created_at,
        "updated_at": rel.updated_at,
    }


# ==================== 主机 API ====================

@router.get("", response_model=List[HostResponse])
def get_hosts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    enabled_only: bool = False
):
    query = db.query(Host)
    if enabled_only:
        query = query.filter(Host.enabled == True)
    hosts = query.order_by(Host.created_at.desc()).all()
    return [host_to_dict(h) for h in hosts]


@router.get("/{host_id}", response_model=HostResponse)
def get_host(
    host_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=404, detail="主机不存在")
    return host_to_dict(host)


@router.post("", response_model=HostResponse, status_code=status.HTTP_201_CREATED)
def create_host(
    host: HostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    tags_json = json.dumps(host.tags) if host.tags else None
    extra_data_json = json.dumps(host.extra_data) if host.extra_data else None
    
    db_host = Host(
        name=host.name,
        ip=host.ip,
        hostname=host.hostname,
        os=host.os,
        os_version=host.os_version,
        cpu_cores=host.cpu_cores,
        memory_gb=host.memory_gb,
        disk_gb=host.disk_gb,
        tags=tags_json,
        extra_data=extra_data_json,
        source=host.source,
        enabled=host.enabled,
    )
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return host_to_dict(db_host)


@router.put("/{host_id}", response_model=HostResponse)
def update_host(
    host_id: int,
    host_update: HostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_host = db.query(Host).filter(Host.id == host_id).first()
    if not db_host:
        raise HTTPException(status_code=404, detail="主机不存在")
    
    update_data = host_update.model_dump(exclude_unset=True)
    
    if "tags" in update_data:
        update_data["tags"] = json.dumps(update_data["tags"]) if update_data["tags"] else None
    
    if "extra_data" in update_data:
        update_data["extra_data"] = json.dumps(update_data["extra_data"]) if update_data["extra_data"] else None
    
    for field, value in update_data.items():
        setattr(db_host, field, value)
    
    db.commit()
    db.refresh(db_host)
    return host_to_dict(db_host)


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_host(
    host_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_host = db.query(Host).filter(Host.id == host_id).first()
    if not db_host:
        raise HTTPException(status_code=404, detail="主机不存在")
    
    db.delete(db_host)
    db.commit()
    return None


# ==================== 主机关系 API ====================

@router.get("/{host_id}/relations", response_model=List[HostRelationResponse])
def get_host_relations(
    host_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    relations = db.query(HostRelation).filter(
        (HostRelation.source_host_id == host_id) | (HostRelation.target_host_id == host_id)
    ).all()
    return [host_relation_to_dict(r) for r in relations]


@router.get("/relations/all", response_model=List[HostRelationResponse])
def get_all_relations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    relations = db.query(HostRelation).order_by(HostRelation.created_at.desc()).all()
    return [host_relation_to_dict(r) for r in relations]


@router.post("/relations", response_model=HostRelationResponse, status_code=status.HTTP_201_CREATED)
def create_host_relation(
    relation: HostRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    extra_data_json = json.dumps(relation.extra_data) if relation.extra_data else None
    
    db_rel = HostRelation(
        source_host_id=relation.source_host_id,
        target_host_id=relation.target_host_id,
        relation_type=relation.relation_type,
        description=relation.description,
        extra_data=extra_data_json,
        source=relation.source,
    )
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return host_relation_to_dict(db_rel)


@router.put("/relations/{rel_id}", response_model=HostRelationResponse)
def update_host_relation(
    rel_id: int,
    rel_update: HostRelationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_rel = db.query(HostRelation).filter(HostRelation.id == rel_id).first()
    if not db_rel:
        raise HTTPException(status_code=404, detail="关系不存在")
    
    update_data = rel_update.model_dump(exclude_unset=True)
    
    if "extra_data" in update_data:
        update_data["extra_data"] = json.dumps(update_data["extra_data"]) if update_data["extra_data"] else None
    
    for field, value in update_data.items():
        setattr(db_rel, field, value)
    
    db.commit()
    db.refresh(db_rel)
    return host_relation_to_dict(db_rel)


@router.delete("/relations/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_host_relation(
    rel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_rel = db.query(HostRelation).filter(HostRelation.id == rel_id).first()
    if not db_rel:
        raise HTTPException(status_code=404, detail="关系不存在")
    
    db.delete(db_rel)
    db.commit()
    return None


async def get_prometheus_label_values(url: str, metric: str, label: str,
                                      auth_type: str, auth_value: str, password: str) -> List[str]:
    """
    查询 Prometheus 获取标签值
    """
    headers = {}
    auth = None
    
    if auth_type == "basic" and auth_value and password:
        auth = (auth_value, password)
    elif auth_type == "token" and auth_value:
        headers["Authorization"] = f"Bearer {auth_value}"
    
    query = f"count({metric}) by ({label})"
    params = {"query": query}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{url.rstrip('/')}/api/v1/query",
                params=params,
                headers=headers,
                auth=auth
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    values = []
                    for series in result.get("data", {}).get("result", []):
                        metric_info = series.get("metric", {})
                        if label in metric_info:
                            values.append(metric_info[label])
                    return sorted(list(set(values)))
        return []
    except Exception as e:
        print(f"Query Prometheus error: {e}")
        return []


@router.post("/sync/prometheus", response_model=PrometheusSyncPreviewResponse)
async def sync_prometheus(
    sync_request: PrometheusSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Prometheus 同步：预览或导入
    """
    # 1. 获取数据源
    datasource = db.query(Datasource).filter(
        Datasource.id == sync_request.datasource_id,
        Datasource.type == "Prometheus"
    ).first()
    
    if not datasource:
        raise HTTPException(status_code=404, detail="Prometheus 数据源不存在")
    
    # 2. 查询标签值
    label_values = await get_prometheus_label_values(
        datasource.url,
        sync_request.metric,
        sync_request.label,
        datasource.auth_type or "none",
        datasource.auth_value or "",
        datasource.password or ""
    )
    
    # 3. 只预览模式
    if sync_request.preview_only:
        return PrometheusSyncPreviewResponse(
            preview=label_values[:10],
            total=len(label_values)
        )
    
    # 4. 导入模式：创建 Host
    imported_hosts = []
    for value in label_values:
        # 检查是否已存在（by name）
        existing = db.query(Host).filter(Host.name == value).first()
        if existing:
            continue
        
        host = Host(
            name=value,
            ip=value.split(":")[0] if ":" in value else value,
            from_type="prometheus",
            from_name=datasource.name,
            enabled=True
        )
        db.add(host)
        db.flush()
        imported_hosts.append(host_to_dict(host))
    
    db.commit()
    
    return PrometheusSyncImportResponse(
        imported=len(imported_hosts),
        hosts=imported_hosts
    )
