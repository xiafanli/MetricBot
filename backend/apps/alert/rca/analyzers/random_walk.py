import random
from typing import List, Dict, Any, Set
from collections import defaultdict
from sqlalchemy.orm import Session
from apps.alert.models import AlertGroup, AlertGroupMember, AlertEvent
from apps.simulator.models import SimulationComponent, ComponentRelation


class RandomWalkAnalyzer:
    def __init__(self, db: Session, num_walks: int = 1000, walk_length: int = 10):
        self.db = db
        self.num_walks = num_walks
        self.walk_length = walk_length

    def analyze(self, group: AlertGroup) -> Dict[str, Any]:
        members = self.db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group.id).all()
        alert_ids = [m.alert_id for m in members]
        alerts = self.db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
        alert_components = set()
        for alert in alerts:
            if alert.labels:
                host = alert.labels.get("host")
                if host:
                    alert_components.add(host)
        if not alert_components:
            return {"candidates": [], "method": "random_walk"}
        adjacency = self._build_adjacency_graph()
        visit_counts = defaultdict(int)
        for component in alert_components:
            for _ in range(self.num_walks // max(len(alert_components), 1)):
                current = component
                for _ in range(self.walk_length):
                    visit_counts[current] += 1
                    neighbors = adjacency.get(current, [])
                    if not neighbors:
                        break
                    current = random.choice(neighbors)
        sorted_nodes = sorted(visit_counts.items(), key=lambda x: x[1], reverse=True)
        candidates = []
        total_visits = self.num_walks * self.walk_length / max(len(alert_components), 1)
        for node, count in sorted_nodes[:10]:
            candidates.append({
                "component": node,
                "score": min(count / total_visits, 1.0) if total_visits > 0 else 0.0,
                "evidence": {"visit_count": count, "is_alert_component": node in alert_components},
                "method": "random_walk",
                "type": self._get_component_type(node),
            })
        return {
            "candidates": candidates,
            "method": "random_walk",
            "graph_stats": {"nodes": len(adjacency), "alert_components": list(alert_components)},
        }

    def _build_adjacency_graph(self) -> Dict[str, List[str]]:
        adjacency = defaultdict(list)
        relations = self.db.query(ComponentRelation).all()
        for rel in relations:
            source = self._get_component_name(rel.source_id)
            target = self._get_component_name(rel.target_id)
            if source and target:
                adjacency[source].append(target)
                adjacency[target].append(source)
        return dict(adjacency)

    def _get_component_name(self, component_id: int) -> str:
        component = self.db.query(SimulationComponent).filter(SimulationComponent.id == component_id).first()
        return component.name if component else None

    def _get_component_type(self, name: str) -> str:
        component = self.db.query(SimulationComponent).filter(SimulationComponent.name == name).first()
        return component.component_type if component else "unknown"
