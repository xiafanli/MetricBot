from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apps.alert.models import AlertEvent, AlertGroup, AggregationPolicy
from apps.alert.aggregation.engine import AggregationEngine


class TimeWindowStrategy:
    def __init__(self, db: Session):
        self.db = db

    def aggregate(self, alerts: List[AlertEvent], policy: AggregationPolicy) -> List[AlertGroup]:
        groups = []
        group_by_fields = policy.group_by_fields or ["rule_id"]
        window_start = datetime.now() - timedelta(seconds=policy.window_seconds)
        active_groups = self.db.query(AlertGroup).filter(
            AlertGroup.status == "active",
            AlertGroup.strategy == "time_window",
            AlertGroup.created_at >= window_start,
        ).all()
        group_map = {g.group_key: g for g in active_groups}
        engine = AggregationEngine(self.db)
        for alert in alerts:
            group_key = self._generate_group_key(alert, group_by_fields)
            if group_key in group_map:
                group = engine.add_alert_to_group(group_map[group_key], alert)
                groups.append(group)
            else:
                group = engine.create_group(alert, "time_window", group_key)
                group_map[group_key] = group
                groups.append(group)
        return groups

    def _generate_group_key(self, alert: AlertEvent, fields: List[str]) -> str:
        key_parts = []
        for field in fields:
            value = getattr(alert, field, None)
            if value is not None:
                key_parts.append(str(value))
        return ":".join(key_parts) if key_parts else str(alert.id)
