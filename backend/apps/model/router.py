import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.core.database import get_db
from apps.model.models import Model
from apps.model.schemas import ModelCreate, ModelUpdate, ModelResponse
from apps.auth.security import get_current_active_user
from apps.auth.models import User

router = APIRouter(prefix="/models", tags=["模型管理"])


def model_to_dict(model: Model) -> dict:
    data = {
        "id": model.id,
        "name": model.name,
        "provider": model.provider,
        "base_model": model.base_model,
        "api_key": model.api_key,
        "api_domain": model.api_domain,
        "protocol": model.protocol,
        "config": json.loads(model.config) if model.config else None,
        "is_default": model.is_default,
        "is_enabled": model.is_enabled,
        "created_at": model.created_at,
        "updated_at": model.updated_at,
    }
    return data


@router.get("", response_model=List[ModelResponse])
def get_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    enabled_only: bool = False
):
    query = db.query(Model)
    if enabled_only:
        query = query.filter(Model.is_enabled == True)
    models = query.order_by(Model.is_default.desc(), Model.created_at.desc()).all()
    
    return [model_to_dict(m) for m in models]


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    return model_to_dict(model)


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if model.is_default:
        db.query(Model).filter(Model.is_default == True).update({"is_default": False})
    
    config_json = json.dumps(model.config) if model.config else None
    
    db_model = Model(
        name=model.name,
        provider=model.provider,
        base_model=model.base_model,
        api_key=model.api_key,
        api_domain=model.api_domain,
        protocol=model.protocol,
        config=config_json,
        is_default=model.is_default,
        is_enabled=model.is_enabled,
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return model_to_dict(db_model)


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    if model_update.is_default:
        db.query(Model).filter(Model.id != model_id, Model.is_default == True).update({"is_default": False})
    
    update_data = model_update.model_dump(exclude_unset=True)
    
    if "config" in update_data:
        update_data["config"] = json.dumps(update_data["config"]) if update_data["config"] else None
    
    for field, value in update_data.items():
        setattr(db_model, field, value)
    
    db.commit()
    db.refresh(db_model)
    
    return model_to_dict(db_model)


@router.put("/{model_id}/default", response_model=ModelResponse)
def set_default_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    db.query(Model).filter(Model.is_default == True).update({"is_default": False})
    db_model.is_default = True
    db.commit()
    db.refresh(db_model)
    
    return model_to_dict(db_model)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    if db_model.is_default:
        raise HTTPException(status_code=400, detail="默认模型无法删除")
    
    db.delete(db_model)
    db.commit()
    return None
