from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from apps.alert.models import AlertGroup, AlertGroupMember, AlertEvent, RcaReport, RcaCandidate
import json
import logging

logger = logging.getLogger(__name__)


class RcaEngine:
    def __init__(self, db: Session):
        self.db = db
        self.analyzers = {}

    def register_analyzer(self, name: str, analyzer_class):
        self.analyzers[name] = analyzer_class(self.db)

    def analyze(self, group: AlertGroup) -> RcaReport:
        report = RcaReport(
            group_id=group.id,
            status="analyzing",
        )
        self.db.add(report)
        self.db.commit()
        try:
            results = {}
            all_candidates = []
            for name, analyzer in self.analyzers.items():
                try:
                    result = analyzer.analyze(group)
                    results[f"{name}_result"] = result
                    if "candidates" in result:
                        all_candidates.extend(result["candidates"])
                except Exception as e:
                    logger.error(f"Analyzer {name} failed: {e}")
                    results[f"{name}_result"] = {"error": str(e)}
            sorted_candidates = sorted(all_candidates, key=lambda x: x.get("score", 0), reverse=True)
            for i, candidate in enumerate(sorted_candidates[:10]):
                rca_candidate = RcaCandidate(
                    report_id=report.id,
                    component_name=candidate.get("component"),
                    component_type=candidate.get("type"),
                    score=candidate.get("score"),
                    evidence=json.dumps(candidate.get("evidence", {})),
                    analysis_method=candidate.get("method"),
                    rank_order=i + 1,
                )
                self.db.add(rca_candidate)
            report.root_causes = json.dumps([c for c in sorted_candidates[:5]])
            report.confidence = self._calculate_confidence(sorted_candidates)
            report.recommendations = json.dumps(self._generate_recommendations(sorted_candidates[:3]))
            report.status = "completed"
            report.completed_at = datetime.now()
            for key, value in results.items():
                setattr(report, key, json.dumps(value))
        except Exception as e:
            logger.error(f"RCA analysis failed: {e}")
            report.status = "failed"
        self.db.commit()
        return report

    def _calculate_confidence(self, candidates: List[Dict]) -> float:
        if not candidates:
            return 0.0
        scores = [c.get("score", 0) for c in candidates[:3]]
        return sum(scores) / len(scores) if scores else 0.0

    def _generate_recommendations(self, candidates: List[Dict]) -> List[Dict]:
        recommendations = []
        for candidate in candidates:
            component = candidate.get("component", "unknown")
            recommendations.append({
                "component": component,
                "action": f"检查 {component} 的状态和日志",
                "priority": "high" if candidate.get("score", 0) > 0.7 else "medium",
            })
        return recommendations

    def get_group_alerts(self, group: AlertGroup) -> List[AlertEvent]:
        members = self.db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group.id).all()
        alert_ids = [m.alert_id for m in members]
        return self.db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
