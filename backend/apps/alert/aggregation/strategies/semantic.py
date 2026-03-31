from typing import List, Dict
from sqlalchemy.orm import Session
from apps.alert.models import AlertEvent, AlertGroup, AggregationPolicy
from apps.alert.aggregation.engine import AggregationEngine
import hashlib


class SemanticStrategy:
    def __init__(self, db: Session):
        self.db = db

    def aggregate(self, alerts: List[AlertEvent], policy: AggregationPolicy) -> List[AlertGroup]:
        groups = []
        threshold = float(policy.similarity_threshold or 0.8)
        engine = AggregationEngine(self.db)
        similarity_groups = self._cluster_by_similarity(alerts, threshold)
        for group_key, alert_list in similarity_groups.items():
            if len(alert_list) > 1:
                first_alert = min(alert_list, key=lambda a: a.created_at)
                group = engine.create_group(first_alert, "semantic", group_key)
                for alert in alert_list[1:]:
                    engine.add_alert_to_group(group, alert)
                groups.append(group)
        return groups

    def _cluster_by_similarity(
        self, alerts: List[AlertEvent], threshold: float
    ) -> Dict[str, List[AlertEvent]]:
        clusters = {}
        alert_embeddings = [(a, self._get_embedding(a)) for a in alerts]
        for alert, embedding in alert_embeddings:
            assigned = False
            for cluster_key, cluster_alerts in clusters.items():
                if cluster_alerts:
                    sample_embedding = self._get_embedding(cluster_alerts[0])
                    similarity = self._cosine_similarity(embedding, sample_embedding)
                    if similarity >= threshold:
                        clusters[cluster_key].append(alert)
                        assigned = True
                        break
            if not assigned:
                cluster_key = self._hash_embedding(embedding)
                clusters[cluster_key] = [alert]
        return clusters

    def _get_embedding(self, alert: AlertEvent) -> List[float]:
        text = f"{alert.title} {alert.severity}"
        return self._text_to_embedding(text)

    def _text_to_embedding(self, text: str) -> List[float]:
        words = text.lower().split()
        embedding = [0.0] * 32
        for i, word in enumerate(words[:32]):
            embedding[i] = hash(word) % 1000 / 1000.0
        return embedding

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _hash_embedding(self, embedding: List[float]) -> str:
        return hashlib.md5(str(embedding).encode()).hexdigest()[:16]
