from typing import List, Dict, Any
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from apps.alert.models import AlertGroup, AlertGroupMember, AlertEvent
import logging

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    def __init__(self, db: Session, lookback_minutes: int = 30, correlation_threshold: float = 0.7):
        self.db = db
        self.lookback_minutes = lookback_minutes
        self.correlation_threshold = correlation_threshold

    def analyze(self, group: AlertGroup) -> Dict[str, Any]:
        members = self.db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group.id).all()
        alert_ids = [m.alert_id for m in members]
        alerts = self.db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
        if not alerts:
            return {"candidates": [], "method": "correlation"}
        alert_times = [a.created_at for a in alerts]
        first_alert_time = min(alert_times)
        lookback_start = first_alert_time - timedelta(minutes=self.lookback_minutes)
        related_alerts = self.db.query(AlertEvent).filter(
            AlertEvent.created_at >= lookback_start,
            AlertEvent.created_at <= first_alert_time,
        ).all()
        if len(related_alerts) < 2:
            return {"candidates": [], "method": "correlation"}
        component_timeline = self._build_timeline(related_alerts, lookback_start, first_alert_time)
        correlations = self._calculate_correlations(component_timeline)
        candidates = []
        for component, score in sorted(correlations.items(), key=lambda x: x[1], reverse=True)[:10]:
            candidates.append({
                "component": component,
                "score": float(score),
                "evidence": {"correlation_score": float(score), "alert_count": len(related_alerts)},
                "method": "correlation",
                "type": "unknown",
            })
        return {
            "candidates": candidates,
            "method": "correlation",
            "timeline_stats": {"duration_minutes": self.lookback_minutes, "alert_count": len(related_alerts)},
        }

    def _build_timeline(self, alerts: List[AlertEvent], start: datetime, end: datetime) -> Dict[str, List[int]]:
        duration = (end - start).total_seconds()
        bucket_count = max(int(duration / 60), 1)
        timeline = {}
        for alert in alerts:
            component = alert.labels.get("host", "unknown") if alert.labels else "unknown"
            if component not in timeline:
                timeline[component] = [0] * bucket_count
            bucket = int((alert.created_at - start).total_seconds() / 60)
            if 0 <= bucket < bucket_count:
                timeline[component][bucket] += 1
        return timeline

    def _calculate_correlations(self, timeline: Dict[str, List[int]]) -> Dict[str, float]:
        correlations = {}
        components = list(timeline.keys())
        if len(components) < 2:
            return {c: 1.0 for c in components}
        for i, comp_a in enumerate(components):
            scores = []
            for j, comp_b in enumerate(components):
                if i != j:
                    score = self._pearson_correlation(timeline[comp_a], timeline[comp_b])
                    if not np.isnan(score):
                        scores.append(score)
            correlations[comp_a] = float(np.mean(scores)) if scores else 0.0
        return correlations

    def _pearson_correlation(self, a: List[int], b: List[int]) -> float:
        a_arr = np.array(a)
        b_arr = np.array(b)
        if np.std(a_arr) == 0 or np.std(b_arr) == 0:
            return 0.0
        return float(np.corrcoef(a_arr, b_arr)[0, 1])
