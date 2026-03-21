import json
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
    HostRelationResponse
)
from apps.auth.security import get_current_active_user
from apps.auth.models import User

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
        "metadata": json.loads(host.metadata) if host.metadata else None,
        "source": host.source,
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
        "metadata": json.loads(rel.metadata) if rel.metadata else None,
        "source": rel.source,
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
    metadata_json = json.dumps(host.metadata) if host.metadata else None
    
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
        metadata=metadata_json,
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
    
    if "metadata" in update_data:
        update_data["metadata"] = json.dumps(update_data["metadata"]) if update_data["metadata"] else None
    
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
    metadata_json = json.dumps(relation.metadata) if relation.metadata else None
    
    db_rel = HostRelation(
        source_host_id=relation.source_host_id,
        target_host_id=relation.target_host_id,
        relation_type=relation.relation_type,
        description=relation.description,
        metadata=metadata_json,
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
    
    if "metadata" in update_data:
        update_data["metadata"] = json.dumps(update_data["metadata"]) if update_data["metadata"] else None
    
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
