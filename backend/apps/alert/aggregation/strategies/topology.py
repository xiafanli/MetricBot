from typing import List, Dict, Set
from sqlalchemy.orm import Session
from apps.alert.models import AlertEvent, AlertGroup, AggregationPolicy
from apps.alert.aggregation.engine import AggregationEngine
from apps.simulator.models import SimulationComponent, ComponentRelation
import json


class TopologyStrategy:
    def __init__(self, db: Session):
        self.db = db

    def aggregate(self, alerts: List[AlertEvent], policy: AggregationPolicy) -> List[AlertGroup]:
        groups = []
        max_depth = policy.max_depth or 3
        engine = AggregationEngine(self.db)
        component_alerts = self._group_by_component(alerts)
        topology_groups = self._find_topology_groups(component_alerts, max_depth)
        for topology_key, alert_list in topology_groups.items():
            if len(alert_list) > 1:
                first_alert = min(alert_list, key=lambda a: a.created_at)
                group = engine.create_group(first_alert, "topology", topology_key)
                for alert in alert_list[1:]:
                    engine.add_alert_to_group(group, alert)
                affected = list(set(
                    a.labels.get("host", "unknown") if a.labels else "unknown"
                    for a in alert_list
                ))
                group.affected_components = json.dumps(affected)
                self.db.commit()
                groups.append(group)
        return groups

    def _group_by_component(self, alerts: List[AlertEvent]) -> Dict[str, List[AlertEvent]]:
        result = {}
        for alert in alerts:
            component = alert.labels.get("host", "unknown") if alert.labels else "unknown"
            if component not in result:
                result[component] = []
            result[component].append(alert)
        return result

    def _find_topology_groups(
        self, component_alerts: Dict[str, List[AlertEvent]], max_depth: int
    ) -> Dict[str, List[AlertEvent]]:
        topology_groups = {}
        visited_components = set()
        for component in component_alerts:
            if component in visited_components:
                continue
            related = self._find_related_components(component, max_depth)
            group_key = ":".join(sorted(related))
            if group_key not in topology_groups:
                topology_groups[group_key] = []
            for related_comp in related:
                if related_comp in component_alerts:
                    topology_groups[group_key].extend(component_alerts[related_comp])
                    visited_components.add(related_comp)
        return topology_groups

    def _find_related_components(self, component: str, max_depth: int) -> Set[str]:
        related = {component}
        current_level = {component}
        for _ in range(max_depth):
            next_level = set()
            for comp in current_level:
                relations = self.db.query(ComponentRelation).filter(
                    (ComponentRelation.source_name == comp) | (ComponentRelation.target_name == comp)
                ).all()
                for rel in relations:
                    if rel.source_name not in related:
                        next_level.add(rel.source_name)
                    if rel.target_name not in related:
                        next_level.add(rel.target_name)
            if not next_level:
                break
            related.update(next_level)
            current_level = next_level
        return related
