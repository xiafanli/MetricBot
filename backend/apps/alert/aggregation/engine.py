from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from apps.alert.models import AlertEvent, AlertGroup, AlertGroupMember, AggregationPolicy


class AggregationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.strategies = {}

    def register_strategy(self, name: str, strategy_class):
        self.strategies[name] = strategy_class(self.db)

    def aggregate(self, alerts: List[AlertEvent], policy: AggregationPolicy) -> List[AlertGroup]:
        strategy = self.strategies.get(policy.strategy)
        if not strategy:
            raise ValueError(f"Unknown strategy: {policy.strategy}")
        return strategy.aggregate(alerts, policy)

    def add_alert_to_group(self, group: AlertGroup, alert: AlertEvent) -> AlertGroup:
        group.alert_count += 1
        group.last_alert_id = alert.id
        group.last_alert_time = alert.created_at
        if alert.severity in ["critical", "warning"]:
            if group.severity == "info" or (alert.severity == "critical" and group.severity != "critical"):
                group.severity = alert.severity
        member = AlertGroupMember(group_id=group.id, alert_id=alert.id)
        self.db.add(member)
        self.db.commit()
        return group

    def create_group(self, alert: AlertEvent, strategy: str, group_key: str) -> AlertGroup:
        group = AlertGroup(
            group_key=group_key,
            strategy=strategy,
            severity=alert.severity,
            alert_count=1,
            first_alert_id=alert.id,
            first_alert_time=alert.created_at,
            last_alert_id=alert.id,
            last_alert_time=alert.created_at,
        )
        self.db.add(group)
        self.db.flush()
        member = AlertGroupMember(group_id=group.id, alert_id=alert.id)
        self.db.add(member)
        self.db.commit()
        return group

    def resolve_group(self, group_id: int) -> Optional[AlertGroup]:
        group = self.db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
        if group:
            group.status = "resolved"
            group.resolved_at = datetime.now()
            self.db.commit()
        return group

    def acknowledge_group(self, group_id: int) -> Optional[AlertGroup]:
        group = self.db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
        if group:
            group.status = "acknowledged"
            self.db.commit()
        return group

    def get_group_alerts(self, group_id: int) -> List[AlertEvent]:
        members = self.db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group_id).all()
        alert_ids = [m.alert_id for m in members]
        return self.db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
