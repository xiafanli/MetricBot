from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.core.database import get_db
from apps.alert.models import AlertRule, Alert, DiagnosisReport, AlertGroup, AlertGroupMember, AlertEvent, AggregationPolicy, RcaReport, RcaCandidate
from apps.alert.schemas import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertTestRequest,
    AlertTestResponse,
    AlertStatsResponse,
    DiagnosisReportResponse,
    DiagnosisChatRequest,
    DiagnosisChatResponse,
    AlertGroupCreate,
    AlertGroupResponse,
    AggregationPolicyCreate,
    AggregationPolicyUpdate,
    AggregationPolicyResponse,
    RcaReportCreate,
    RcaReportResponse,
    RcaCandidateResponse,
)
from apps.alert.diagnosis import DiagnosisAnalyzer
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


# ==================== AI 诊断 API ====================

@router.post("/{alert_id}/diagnosis", response_model=DiagnosisReportResponse)
async def generate_diagnosis(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    analyzer = DiagnosisAnalyzer(db)
    report = await analyzer.generate_diagnosis(alert_id)
    if not report:
        raise HTTPException(status_code=404, detail="告警不存在")
    return DiagnosisReportResponse(
        id=report.id,
        alert_id=report.alert_id,
        report=report.report,
        created_at=report.created_at
    )


@router.get("/{alert_id}/diagnosis", response_model=DiagnosisReportResponse)
def get_diagnosis(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    report = db.query(DiagnosisReport).filter(DiagnosisReport.alert_id == alert_id).order_by(DiagnosisReport.created_at.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="诊断报告不存在")
    return DiagnosisReportResponse(
        id=report.id,
        alert_id=report.alert_id,
        report=report.report,
        created_at=report.created_at
    )


@router.post("/{alert_id}/chat", response_model=DiagnosisChatResponse)
async def diagnosis_chat(
    alert_id: int,
    chat_request: DiagnosisChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    analyzer = DiagnosisAnalyzer(db)
    result = await analyzer.chat(alert_id, current_user.id, chat_request.message)
    if not result:
        raise HTTPException(status_code=404, detail="告警不存在")
    return DiagnosisChatResponse(
        id=result["id"],
        alert_id=result["alert_id"],
        message=result["message"],
        created_at=result["created_at"]
    )


@router.get("/{alert_id}/conversations")
def get_conversations(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    analyzer = DiagnosisAnalyzer(db)
    messages = analyzer.get_conversation(alert_id, current_user.id)
    return {"messages": messages}


# ==================== 告警聚合 API ====================

def alert_group_to_dict(group: AlertGroup) -> dict:
    affected = None
    if group.affected_components:
        import json
        affected = json.loads(group.affected_components) if isinstance(group.affected_components, str) else group.affected_components
    return {
        "id": group.id,
        "group_key": group.group_key,
        "strategy": group.strategy,
        "severity": group.severity,
        "status": group.status,
        "alert_count": group.alert_count,
        "first_alert_id": group.first_alert_id,
        "first_alert_time": group.first_alert_time,
        "last_alert_id": group.last_alert_id,
        "last_alert_time": group.last_alert_time,
        "affected_components": affected,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
        "resolved_at": group.resolved_at,
    }


@router.get("/groups", response_model=List[AlertGroupResponse])
def get_alert_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status: str = None,
    strategy: str = None,
    limit: int = 100
):
    query = db.query(AlertGroup)
    if status:
        query = query.filter(AlertGroup.status == status)
    if strategy:
        query = query.filter(AlertGroup.strategy == strategy)
    groups = query.order_by(AlertGroup.created_at.desc()).limit(limit).all()
    return [alert_group_to_dict(g) for g in groups]


@router.get("/groups/{group_id}", response_model=AlertGroupResponse)
def get_alert_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    group = db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="聚合组不存在")
    return alert_group_to_dict(group)


@router.put("/groups/{group_id}/acknowledge", response_model=AlertGroupResponse)
def acknowledge_alert_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    group = db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="聚合组不存在")
    group.status = "acknowledged"
    db.commit()
    db.refresh(group)
    return alert_group_to_dict(group)


@router.put("/groups/{group_id}/resolve", response_model=AlertGroupResponse)
def resolve_alert_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    group = db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="聚合组不存在")
    group.status = "resolved"
    group.resolved_at = datetime.now()
    db.commit()
    db.refresh(group)
    return alert_group_to_dict(group)


@router.get("/groups/{group_id}/alerts")
def get_group_alerts(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    members = db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group_id).all()
    alert_ids = [m.alert_id for m in members]
    alerts = db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
    return {"alerts": [{"id": a.id, "title": a.title, "severity": a.severity, "created_at": a.created_at} for a in alerts]}


# ==================== 聚合策略 API ====================

def aggregation_policy_to_dict(policy: AggregationPolicy) -> dict:
    return {
        "id": policy.id,
        "name": policy.name,
        "strategy": policy.strategy,
        "window_seconds": policy.window_seconds,
        "group_by_fields": policy.group_by_fields,
        "max_depth": policy.max_depth,
        "similarity_threshold": float(policy.similarity_threshold) if policy.similarity_threshold else 0.8,
        "enabled": policy.enabled,
        "created_at": policy.created_at,
    }


@router.get("/policies", response_model=List[AggregationPolicyResponse])
def get_aggregation_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    enabled_only: bool = False
):
    query = db.query(AggregationPolicy)
    if enabled_only:
        query = query.filter(AggregationPolicy.enabled == True)
    policies = query.order_by(AggregationPolicy.created_at.desc()).all()
    return [aggregation_policy_to_dict(p) for p in policies]


@router.post("/policies", response_model=AggregationPolicyResponse, status_code=status.HTTP_201_CREATED)
def create_aggregation_policy(
    policy: AggregationPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    import json
    db_policy = AggregationPolicy(
        name=policy.name,
        strategy=policy.strategy,
        window_seconds=policy.window_seconds,
        group_by_fields=json.dumps(policy.group_by_fields) if policy.group_by_fields else None,
        max_depth=policy.max_depth,
        similarity_threshold=policy.similarity_threshold,
        enabled=policy.enabled,
    )
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return aggregation_policy_to_dict(db_policy)


@router.put("/policies/{policy_id}", response_model=AggregationPolicyResponse)
def update_aggregation_policy(
    policy_id: int,
    policy_update: AggregationPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_policy = db.query(AggregationPolicy).filter(AggregationPolicy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="聚合策略不存在")
    update_data = policy_update.model_dump(exclude_unset=True)
    import json
    if "group_by_fields" in update_data and update_data["group_by_fields"] is not None:
        update_data["group_by_fields"] = json.dumps(update_data["group_by_fields"])
    for field, value in update_data.items():
        setattr(db_policy, field, value)
    db.commit()
    db.refresh(db_policy)
    return aggregation_policy_to_dict(db_policy)


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aggregation_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_policy = db.query(AggregationPolicy).filter(AggregationPolicy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="聚合策略不存在")
    db.delete(db_policy)
    db.commit()
    return None


# ==================== 根因分析 API ====================

def rca_report_to_dict(report: RcaReport) -> dict:
    import json
    root_causes = None
    if report.root_causes:
        root_causes = json.loads(report.root_causes) if isinstance(report.root_causes, str) else report.root_causes
    recommendations = None
    if report.recommendations:
        recommendations = json.loads(report.recommendations) if isinstance(report.recommendations, str) else report.recommendations
    return {
        "id": report.id,
        "group_id": report.group_id,
        "status": report.status,
        "root_causes": root_causes,
        "confidence": float(report.confidence) if report.confidence else None,
        "recommendations": recommendations,
        "created_at": report.created_at,
        "completed_at": report.completed_at,
    }


@router.post("/groups/{group_id}/rca", response_model=RcaReportResponse)
async def generate_rca_report(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    group = db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="聚合组不存在")
    from apps.alert.rca.engine import RcaEngine
    from apps.alert.rca.analyzers.random_walk import RandomWalkAnalyzer
    from apps.alert.rca.analyzers.correlation import CorrelationAnalyzer
    from apps.alert.rca.analyzers.llm_analyzer import LlmAnalyzer
    engine = RcaEngine(db)
    engine.register_analyzer("random_walk", RandomWalkAnalyzer)
    engine.register_analyzer("correlation", CorrelationAnalyzer)
    engine.register_analyzer("llm", LlmAnalyzer)
    report = engine.analyze(group)
    return rca_report_to_dict(report)


@router.get("/groups/{group_id}/rca", response_model=RcaReportResponse)
def get_rca_report(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    report = db.query(RcaReport).filter(RcaReport.group_id == group_id).order_by(RcaReport.created_at.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="根因分析报告不存在")
    return rca_report_to_dict(report)


@router.get("/rca/{report_id}/candidates", response_model=List[RcaCandidateResponse])
def get_rca_candidates(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    candidates = db.query(RcaCandidate).filter(RcaCandidate.report_id == report_id).order_by(RcaCandidate.rank_order).all()
    import json
    result = []
    for c in candidates:
        evidence = None
        if c.evidence:
            evidence = json.loads(c.evidence) if isinstance(c.evidence, str) else c.evidence
        result.append({
            "id": c.id,
            "report_id": c.report_id,
            "component_name": c.component_name,
            "component_type": c.component_type,
            "score": float(c.score) if c.score else None,
            "evidence": evidence,
            "analysis_method": c.analysis_method,
            "rank_order": c.rank_order,
            "created_at": c.created_at,
        })
    return result
