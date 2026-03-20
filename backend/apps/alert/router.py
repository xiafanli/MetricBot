from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.core.database import get_db
from apps.alert.models import AlertRule, Alert
from apps.alert.schemas import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertTestRequest,
    AlertTestResponse,
    AlertStatsResponse
)
from apps.auth.security import get_current_active_user
from apps.auth.models import User

router = APIRouter(prefix="/alerts", tags=["告警管理"])


# ==================== 告警规则 API ====================

def alert_rule_to_dict(rule: AlertRule) -> dict:
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "datasource_id": rule.datasource_id,
        "datasource_type": rule.datasource_type,
        "metric_query": rule.metric_query,
        "condition_type": rule.condition_type,
        "threshold": float(rule.threshold) if rule.threshold else None,
        "severity": rule.severity,
        "evaluation_interval": rule.evaluation_interval,
        "enabled": rule.enabled,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
    }


@router.get("/rules", response_model=List[AlertRuleResponse])
def get_alert_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    enabled_only: bool = False
):
    query = db.query(AlertRule)
    if enabled_only:
        query = query.filter(AlertRule.enabled == True)
    rules = query.order_by(AlertRule.severity.desc(), AlertRule.created_at.desc()).all()
    return [alert_rule_to_dict(r) for r in rules]


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")
    return alert_rule_to_dict(rule)


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    rule: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_rule = AlertRule(
        name=rule.name,
        description=rule.description,
        datasource_id=rule.datasource_id,
        datasource_type=rule.datasource_type,
        metric_query=rule.metric_query,
        condition_type=rule.condition_type,
        threshold=rule.threshold,
        severity=rule.severity,
        evaluation_interval=rule.evaluation_interval,
        enabled=rule.enabled,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return alert_rule_to_dict(db_rule)


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    rule_id: int,
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")
    
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rule, field, value)
    
    db.commit()
    db.refresh(db_rule)
    return alert_rule_to_dict(db_rule)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")
    
    db.delete(db_rule)
    db.commit()
    return None


@router.post("/rules/{rule_id}/test", response_model=AlertTestResponse)
def test_alert_rule(
    rule_id: int,
    test_request: AlertTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")
    
    triggered = False
    message = ""
    
    threshold = float(db_rule.threshold) if db_rule.threshold else 0
    test_value = test_request.test_value
    
    if db_rule.condition_type == "greater_than":
        triggered = test_value > threshold
        message = f"{db_rule.name}: {test_value} > {threshold}" if triggered else f"{db_rule.name}: {test_value} <= {threshold}"
    elif db_rule.condition_type == "less_than":
        triggered = test_value < threshold
        message = f"{db_rule.name}: {test_value} < {threshold}" if triggered else f"{db_rule.name}: {test_value} >= {threshold}"
    elif db_rule.condition_type == "equal_to":
        triggered = test_value == threshold
        message = f"{db_rule.name}: {test_value} == {threshold}" if triggered else f"{db_rule.name}: {test_value} != {threshold}"
    
    return AlertTestResponse(
        triggered=triggered,
        test_value=test_value,
        threshold=threshold,
        severity=db_rule.severity,
        message=message
    )


# ==================== 告警记录 API ====================

def alert_to_dict(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "rule_id": alert.rule_id,
        "rule_name": alert.rule_name,
        "severity": alert.severity,
        "metric_value": float(alert.metric_value) if alert.metric_value else None,
        "threshold": float(alert.threshold) if alert.threshold else None,
        "message": alert.message,
        "resolved": alert.resolved,
        "resolved_at": alert.resolved_at,
        "datasource_id": alert.datasource_id,
        "created_at": alert.created_at,
    }


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    resolved_only: bool = False,
    active_only: bool = False,
    limit: int = 100
):
    query = db.query(Alert)
    
    if resolved_only:
        query = query.filter(Alert.resolved == True)
    if active_only:
        query = query.filter(Alert.resolved == False)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return [alert_to_dict(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")
    return alert_to_dict(alert)


@router.put("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")
    
    alert.resolved = True
    alert.resolved_at = datetime.now()
    db.commit()
    db.refresh(alert)
    return alert_to_dict(alert)


@router.get("/stats", response_model=AlertStatsResponse)
def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    total = db.query(Alert).count()
    critical = db.query(Alert).filter(Alert.severity == "critical").count()
    warning = db.query(Alert).filter(Alert.severity == "warning").count()
    info = db.query(Alert).filter(Alert.severity == "info").count()
    resolved = db.query(Alert).filter(Alert.resolved == True).count()
    active = db.query(Alert).filter(Alert.resolved == False).count()
    
    return AlertStatsResponse(
        total=total,
        critical=critical,
        warning=warning,
        info=info,
        resolved=resolved,
        active=active
    )
