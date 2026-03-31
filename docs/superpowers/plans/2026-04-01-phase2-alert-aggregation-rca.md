# Phase 2 实现计划：告警聚合与根因分析

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现告警聚合与降噪、根因分析两大核心功能

**Architecture:** 采用独立模块方案，告警聚合模块和根因分析模块与现有告警引擎解耦。聚合模块支持时间窗口、拓扑关联、语义相似三种策略。根因分析模块支持随机游走、时序相关性、LLM推理三种分析器。

**Tech Stack:** Python FastAPI, SQLAlchemy, Vue 3, TypeScript, Element Plus

---

## Task 1: 数据库模型设计

**Files:**
- Modify: `backend/apps/alert/models.py`
- Create: `backend/apps/alert/aggregation/models.py`
- Create: `backend/apps/alert/rca/models.py`

- [ ] **Step 1: 在 models.py 中添加聚合相关表**

在 `backend/apps/alert/models.py` 中添加 AlertGroup、AlertGroupMember、AggregationPolicy 模型.

```python
class AlertGroup(Base):
    __tablename__ = "alert_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_key = Column(String(255), nullable=False)
    strategy = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    alert_count = Column(Integer, default=1)
    first_alert_id = Column(Integer, nullable=True)
    first_alert_time = Column(DateTime(timezone=True), nullable=True)
    last_alert_id = Column(Integer, nullable=True)
    last_alert_time = Column(DateTime(timezone=True), nullable=True)
    topology_path = Column(Text, nullable=True)
    affected_components = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class AlertGroupMember(Base):
    __tablename__ = "alert_group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("alert_groups.id"), nullable=False)
    alert_id = Column(Integer, ForeignKey("alert_events.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AggregationPolicy(Base):
    __tablename__ = "aggregation_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    strategy = Column(String(50), nullable=False)
    window_seconds = Column(Integer, default=300)
    group_by_fields = Column(JSON, nullable=True)
    max_depth = Column(Integer, default=3)
    similarity_threshold = Column(Numeric(3, 2), default=0.8)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 2: 添加根因分析相关表**

在 `backend/apps/alert/models.py` 中添加 RcaReport、RcaCandidate 模型.

```python
class RcaReport(Base):
    __tablename__ = "rca_reports"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("alert_groups.id"), nullable=True)
    status = Column(String(50), default="analyzing")
    root_causes = Column(JSON, nullable=True)
    analysis_path = Column(Text, nullable=True)
    confidence = Column(Numeric(3, 2), nullable=True)
    random_walk_result = Column(JSON, nullable=True)
    correlation_result = Column(JSON, nullable=True)
    llm_result = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class RcaCandidate(Base):
    __tablename__ = "rca_candidates"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("rca_reports.id"), nullable=False)
    component_name = Column(String(255), nullable=True)
    component_type = Column(String(50), nullable=True)
    score = Column(Numeric(5, 4), nullable=True)
    evidence = Column(JSON, nullable=True)
    analysis_method = Column(String(50), nullable=True)
    rank_order = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 3: 运行数据库迁移**

Run: `cd backend && alembic revision --autogenerate -m "add aggregation and rca tables"`

Expected: 生成迁移文件

- [ ] **Step 4: 执行迁移**

Run: `cd backend && alembic upgrade head`

Expected: 表创建成功

- [ ] **Step 5: 提交代码**

```bash
git add backend/apps/alert/models.py backend/alembic/versions/*.py
git commit -m "feat(alert): add aggregation and rca database models"
```

---

## Task 2: 告警聚合引擎实现

**Files:**
- Create: `backend/apps/alert/aggregation/__init__.py`
- Create: `backend/apps/alert/aggregation/engine.py`
- Create: `backend/apps/alert/aggregation/scheduler.py`

- [ ] **Step 1: 创建聚合引擎核心类**

创建 `backend/apps/alert/aggregation/engine.py`.

```python
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
```

- [ ] **Step 2: 创建聚合调度器**

创建 `backend/apps/alert/aggregation/scheduler.py`.

```python
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apps.alert.models import AlertEvent, AlertGroup, AggregationPolicy
from apps.alert.aggregation.engine import AggregationEngine
from common.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


class AggregationScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.engine: Optional[AggregationEngine] = None

    def start(self):
        self.scheduler.add_job(self._aggregate_job, "interval", seconds=30, id="aggregation_job")
        self.scheduler.start()
        logger.info("Aggregation scheduler started")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("Aggregation scheduler stopped")

    def _get_db(self) -> Session:
        return SessionLocal()

    async def _aggregate_job(self):
        try:
            db = self._get_db()
            try:
                policies = db.query(AggregationPolicy).filter(AggregationPolicy.enabled == True).all()
                if not policies:
                    return
                engine = AggregationEngine(db)
                from apps.alert.aggregation.strategies.time_window import TimeWindowStrategy
                from apps.alert.aggregation.strategies.topology import TopologyStrategy
                engine.register_strategy("time_window", TimeWindowStrategy)
                engine.register_strategy("topology", TopologyStrategy)
                for policy in policies:
                    cutoff_time = datetime.now() - timedelta(seconds=policy.window_seconds)
                    ungrouped_alerts = db.query(AlertEvent).filter(
                        AlertEvent.created_at >= cutoff_time,
                        ~AlertEvent.id.in_(
                            db.query(AlertGroupMember.alert_id)
                        ),
                    ).all()
                    if ungrouped_alerts:
                        engine.aggregate(ungrouped_alerts, policy)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Aggregation job error: {e}")
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/apps/alert/aggregation/
git commit -m "feat(alert): add aggregation engine and scheduler"
```

---

## Task 3: 时间窗口聚合策略

**Files:**
- Create: `backend/apps/alert/aggregation/strategies/__init__.py`
- Create: `backend/apps/alert/aggregation/strategies/time_window.py`

- [ ] **Step 1: 创建时间窗口聚合策略**

创建 `backend/apps/alert/aggregation/strategies/time_window.py`.

```python
from typing import List, Dict, Any
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
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/apps/alert/aggregation/strategies/
git commit -m "feat(alert): add time window aggregation strategy"
```

---

## Task 4: 拓扑关联聚合策略

**Files:**
- Create: `backend/apps/alert/aggregation/strategies/topology.py`

- [ ] **Step 1: 创建拓扑关联聚合策略**

创建 `backend/apps/alert/aggregation/strategies/topology.py`.

```python
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta
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
                group.affected_components = json.dumps(list(set(a.labels.get("host", "unknown") for a in alert_list)))
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

    def _find_topology_groups(self, component_alerts: Dict[str, List[AlertEvent]], max_depth: int) -> Dict[str, List[AlertEvent]]:
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
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/apps/alert/aggregation/strategies/topology.py
git commit -m "feat(alert): add topology aggregation strategy"
```

---

## Task 5: 语义相似聚合策略

**Files:**
- Create: `backend/apps/alert/aggregation/strategies/semantic.py`

- [ ] **Step 1: 创建语义相似聚合策略**

创建 `backend/apps/alert/aggregation/strategies/semantic.py`.

```python
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apps.alert.models import AlertEvent, AlertGroup, AggregationPolicy
from apps.alert.aggregation.engine import AggregationEngine
import hashlib
import json


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

    def _cluster_by_similarity(self, alerts: List[AlertEvent], threshold: float) -> Dict[str, List[AlertEvent]]:
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
        text = f"{alert.rule_name} {alert.message} {alert.severity}"
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
        norm_b = sum(x * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _hash_embedding(self, embedding: List[float]) -> str:
        return hashlib.md5(str(embedding).encode()).hexdigest()[:16]
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/apps/alert/aggregation/strategies/semantic.py
git commit -m "feat(alert): add semantic similarity aggregation strategy"
```

---

## Task 6: 根因分析引擎实现

**Files:**
- Create: `backend/apps/alert/rca/__init__.py`
- Create: `backend/apps/alert/rca/engine.py`

- [ ] **Step 1: 创建根因分析引擎**

创建 `backend/apps/alert/rca/engine.py`.

```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from apps.alert.models import AlertGroup, RcaReport, RcaCandidate
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
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/apps/alert/rca/
git commit -m "feat(alert): add RCA engine"
```

---

## Task 7: 随机游走分析器

**Files:**
- Create: `backend/apps/alert/rca/analyzers/__init__.py`
- Create: `backend/apps/alert/rca/analyzers/random_walk.py`

- [ ] **Step 1: 创建随机游走分析器**

创建 `backend/apps/alert/rca/analyzers/random_walk.py`.

```python
import random
from typing import List, Dict, Any, Set
from collections import defaultdict
from sqlalchemy.orm import Session
from apps.alert.models import AlertGroup, AlertGroupMember, AlertEvent
from apps.simulator.models import SimulationComponent, ComponentRelation
import json


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
            for _ in range(self.num_walks // len(alert_components)):
                current = component
                for _ in range(self.walk_length):
                    visit_counts[current] += 1
                    neighbors = adjacency.get(current, [])
                    if not neighbors:
                        break
                    current = random.choice(neighbors)
        sorted_nodes = sorted(visit_counts.items(), key=lambda x: x[1], reverse=True)
        candidates = []
        for node, count in sorted_nodes[:10]:
            candidates.append({
                "component": node,
                "score": count / (self.num_walks * self.walk_length / len(alert_components)),
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
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/apps/alert/rca/analyzers/
git commit -m "feat(alert): add random walk analyzer"
```

---

## Task 8: 时序相关性分析器

**Files:**
- Create: `backend/apps/alert/rca/analyzers/correlation.py`

- [ ] **Step 1: 创建时序相关性分析器**

创建 `backend/apps/alert/rca/analyzers/correlation.py`.

```python
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
        bucket_count = int(duration / 60)
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
            correlations[comp_a] = np.mean(scores) if scores else 0.0
        return correlations

    def _pearson_correlation(self, a: List[int], b: List[int]) -> float:
        a_arr = np.array(a)
        b_arr = np.array(b)
        if np.std(a_arr) == 0 or np.std(b_arr) == 0:
            return 0.0
        return float(np.corrcoef(a_arr, b_arr)[0, 1])
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/apps/alert/rca/analyzers/correlation.py
git commit -m "feat(alert): add time series correlation analyzer"
```

---

## Task 9: LLM 推理分析器

**Files:**
- Create: `backend/apps/alert/rca/analyzers/llm_analyzer.py`

- [ ] **Step 1: 创建 LLM 推理分析器**

创建 `backend/apps/alert/rca/analyzers/llm_analyzer.py`.

```python
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from apps.alert.models import AlertGroup, AlertGroupMember, AlertEvent
from apps.model.service import ModelService
import json
import logging

logger = logging.getLogger(__name__)


class LlmAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self.model_service = ModelService(db)

    def analyze(self, group: AlertGroup) -> Dict[str, Any]:
        members = self.db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group.id).all()
        alert_ids = [m.alert_id for m in members]
        alerts = self.db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
        alert_summary = self._build_alert_summary(alerts)
        topology_info = self._get_topology_info(alerts)
        prompt = self._build_prompt(alert_summary, topology_info)
        try:
            model = self.model_service.get_default_model()
            if not model:
                return {"candidates": [], "method": "llm", "error": "No default model configured"}
            response = self.model_service.call_model(model, prompt)
            result = self._parse_response(response)
            return result
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {"candidates": [], "method": "llm", "error": str(e)}

    def _build_alert_summary(self, alerts: List[AlertEvent]) -> str:
        summary_lines = []
        for alert in alerts[:10]:
            line = f"- [{alert.severity}] {alert.rule_name}: {alert.message}"
            if alert.labels:
                host = alert.labels.get("host")
                if host:
                    line += f" (host: {host})"
            summary_lines.append(line)
        return "\n".join(summary_lines)

    def _get_topology_info(self, alerts: List[AlertEvent]) -> str:
        components = set()
        for alert in alerts:
            if alert.labels:
                host = alert.labels.get("host")
                if host:
                    components.add(host)
        return f"涉及组件: {', '.join(components)}"

    def _build_prompt(self, alert_summary: str, topology_info: str) -> str:
        return f"""你是一位经验丰富的运维专家。请分析以下告警并找出最可能的根因。

【告警列表】
{alert_summary}

【拓扑信息】
{topology_info}

请按以下JSON格式输出分析结果：
{{
  "root_causes": [
    {{
      "component": "组件名称",
      "score": 0.0-1.0的置信度分数,
      "reason": "判断理由"
    }}
  ],
  "recommendations": [
    "排查建议1",
    "排查建议2"
  ]
}}"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        try:
            import re
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
                candidates = []
                for rc in data.get("root_causes", []):
                    candidates.append({
                        "component": rc.get("component", "unknown"),
                        "score": float(rc.get("score", 0.5)),
                        "evidence": {"reason": rc.get("reason", "")},
                        "method": "llm",
                        "type": "unknown",
                    })
                return {
                    "candidates": candidates,
                    "recommendations": data.get("recommendations", []),
                    "method": "llm",
                }
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
        return {"candidates": [], "method": "llm", "error": "Failed to parse response"}
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/apps/alert/rca/analyzers/llm_analyzer.py
git commit -m "feat(alert): add LLM inference analyzer"
```

---

## Task 10: API 接口实现

**Files:**
- Modify: `backend/apps/alert/router.py`
- Modify: `backend/apps/alert/schemas.py`

- [ ] **Step 1: 添加 Schemas**

在 `backend/apps/alert/schemas.py` 中添加请求/响应模型.

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class AlertGroupBase(BaseModel):
    group_key: str
    strategy: str
    severity: str
    status: str = "active"
    alert_count: int = 1


class AlertGroupResponse(AlertGroupBase):
    id: int
    first_alert_time: Optional[datetime]
    last_alert_time: Optional[datetime]
    affected_components: Optional[List[str]]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertGroupListResponse(BaseModel):
    items: List[AlertGroupResponse]
    total: int


class AggregationPolicyBase(BaseModel):
    name: str
    strategy: str
    window_seconds: int = 300
    group_by_fields: Optional[List[str]] = None
    max_depth: int = 3
    similarity_threshold: float = 0.8
    enabled: bool = True


class AggregationPolicyResponse(AggregationPolicyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RcaCandidateResponse(BaseModel):
    id: int
    component_name: Optional[str]
    component_type: Optional[str]
    score: Optional[float]
    evidence: Optional[Dict[str, Any]]
    analysis_method: Optional[str]
    rank_order: Optional[int]


class RcaReportResponse(BaseModel):
    id: int
    group_id: Optional[int]
    status: str
    root_causes: Optional[List[Dict[str, Any]]]
    confidence: Optional[float]
    recommendations: Optional[List[Dict[str, Any]]]
    candidates: List[RcaCandidateResponse]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 添加 API 路由**

在 `backend/apps/alert/router.py` 中添加路由.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from apps.alert.models import AlertGroup, AlertGroupMember, AlertEvent, AggregationPolicy, RcaReport, RcaCandidate
from apps.alert.schemas import (
    AlertGroupResponse, AlertGroupListResponse,
    AggregationPolicyBase, AggregationPolicyResponse,
    RcaReportResponse, RcaCandidateResponse,
)
from apps.alert.aggregation.engine import AggregationEngine
from apps.alert.rca.engine import RcaEngine
from common.core.database import get_db
import json

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/groups", response_model=AlertGroupListResponse)
def get_alert_groups(
    status: Optional[str] = None,
    strategy: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(AlertGroup)
    if status:
        query = query.filter(AlertGroup.status == status)
    if strategy:
        query = query.filter(AlertGroup.strategy == strategy)
    total = query.count()
    groups = query.order_by(AlertGroup.created_at.desc()).offset(skip).limit(limit).all()
    return AlertGroupListResponse(
        items=[AlertGroupResponse(
            id=g.id,
            group_key=g.group_key,
            strategy=g.strategy,
            severity=g.severity,
            status=g.status,
            alert_count=g.alert_count,
            first_alert_time=g.first_alert_time,
            last_alert_time=g.last_alert_time,
            affected_components=json.loads(g.affected_components) if g.affected_components else None,
            created_at=g.created_at,
            resolved_at=g.resolved_at,
        ) for g in groups],
        total=total,
    )


@router.get("/groups/{group_id}", response_model=AlertGroupResponse)
def get_alert_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Alert group not found")
    return AlertGroupResponse(
        id=group.id,
        group_key=group.group_key,
        strategy=group.strategy,
        severity=group.severity,
        status=group.status,
        alert_count=group.alert_count,
        first_alert_time=group.first_alert_time,
        last_alert_time=group.last_alert_time,
        affected_components=json.loads(group.affected_components) if group.affected_components else None,
        created_at=group.created_at,
        resolved_at=group.resolved_at,
    )


@router.post("/groups/{group_id}/acknowledge")
def acknowledge_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Alert group not found")
    group.status = "acknowledged"
    db.commit()
    return {"message": "Group acknowledged"}


@router.post("/groups/{group_id}/resolve")
def resolve_group(group_id: int, db: Session = Depends(get_db)):
    engine = AggregationEngine(db)
    group = engine.resolve_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Alert group not found")
    return {"message": "Group resolved"}


@router.get("/groups/{group_id}/alerts")
def get_group_alerts(group_id: int, db: Session = Depends(get_db)):
    members = db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group_id).all()
    alert_ids = [m.alert_id for m in members]
    alerts = db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
    return alerts


@router.get("/aggregation/policies", response_model=List[AggregationPolicyResponse])
def get_aggregation_policies(db: Session = Depends(get_db)):
    policies = db.query(AggregationPolicy).all()
    return [AggregationPolicyResponse(
        id=p.id,
        name=p.name,
        strategy=p.strategy,
        window_seconds=p.window_seconds,
        group_by_fields=json.loads(p.group_by_fields) if p.group_by_fields else None,
        max_depth=p.max_depth,
        similarity_threshold=float(p.similarity_threshold) if p.similarity_threshold else 0.8,
        enabled=p.enabled,
        created_at=p.created_at,
    ) for p in policies]


@router.post("/aggregation/policies", response_model=AggregationPolicyResponse)
def create_aggregation_policy(data: AggregationPolicyBase, db: Session = Depends(get_db)):
    policy = AggregationPolicy(
        name=data.name,
        strategy=data.strategy,
        window_seconds=data.window_seconds,
        group_by_fields=json.dumps(data.group_by_fields) if data.group_by_fields else None,
        max_depth=data.max_depth,
        similarity_threshold=data.similarity_threshold,
        enabled=data.enabled,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return AggregationPolicyResponse(
        id=policy.id,
        name=policy.name,
        strategy=policy.strategy,
        window_seconds=policy.window_seconds,
        group_by_fields=data.group_by_fields,
        max_depth=policy.max_depth,
        similarity_threshold=float(policy.similarity_threshold),
        enabled=policy.enabled,
        created_at=policy.created_at,
    )


@router.post("/rca/analyze")
def trigger_rca_analysis(group_id: int, db: Session = Depends(get_db)):
    group = db.query(AlertGroup).filter(AlertGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Alert group not found")
    engine = RcaEngine(db)
    from apps.alert.rca.analyzers.random_walk import RandomWalkAnalyzer
    from apps.alert.rca.analyzers.correlation import CorrelationAnalyzer
    from apps.alert.rca.analyzers.llm_analyzer import LlmAnalyzer
    engine.register_analyzer("random_walk", RandomWalkAnalyzer)
    engine.register_analyzer("correlation", CorrelationAnalyzer)
    engine.register_analyzer("llm", LlmAnalyzer)
    report = engine.analyze(group)
    return {"report_id": report.id, "status": report.status}


@router.get("/groups/{group_id}/rca", response_model=RcaReportResponse)
def get_group_rca(group_id: int, db: Session = Depends(get_db)):
    report = db.query(RcaReport).filter(RcaReport.group_id == group_id).order_by(RcaReport.created_at.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="RCA report not found")
    candidates = db.query(RcaCandidate).filter(RcaCandidate.report_id == report.id).order_by(RcaCandidate.rank_order).all()
    return RcaReportResponse(
        id=report.id,
        group_id=report.group_id,
        status=report.status,
        root_causes=json.loads(report.root_causes) if report.root_causes else None,
        confidence=float(report.confidence) if report.confidence else None,
        recommendations=json.loads(report.recommendations) if report.recommendations else None,
        candidates=[RcaCandidateResponse(
            id=c.id,
            component_name=c.component_name,
            component_type=c.component_type,
            score=float(c.score) if c.score else None,
            evidence=json.loads(c.evidence) if c.evidence else None,
            analysis_method=c.analysis_method,
            rank_order=c.rank_order,
        ) for c in candidates],
        created_at=report.created_at,
        completed_at=report.completed_at,
    )
```

- [ ] **Step 3: 运行后端服务测试**

Run: `cd backend && python -c "from apps.alert.router import router; print('Router loaded successfully')"`

Expected: 输出 "Router loaded successfully"

- [ ] **Step 4: 提交代码**

```bash
git add backend/apps/alert/router.py backend/apps/alert/schemas.py
git commit -m "feat(alert): add aggregation and RCA API endpoints"
```

---

## Task 11: 前端页面实现

**Files:**
- Create: `frontend/src/views/alert/AlertGroups.vue`
- Create: `frontend/src/views/alert/AlertGroupDetail.vue`
- Create: `frontend/src/views/alert/AggregationPolicies.vue`
- Create: `frontend/src/views/alert/RcaReportDialog.vue`
- Modify: `frontend/src/api/alert.ts`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/views/Layout.vue`

- [ ] **Step 1: 添加 API 接口**

在 `frontend/src/api/alert.ts` 中添加.

```typescript
export function getAlertGroups(params?: any) {
  return request.get('/alerts/groups', { params })
}

export function getAlertGroup(id: number) {
  return request.get(`/alerts/groups/${id}`)
}

export function getAlertGroupAlerts(id: number) {
  return request.get(`/alerts/groups/${id}/alerts`)
}

export function acknowledgeGroup(id: number) {
  return request.post(`/alerts/groups/${id}/acknowledge`)
}

export function resolveGroup(id: number) {
  return request.post(`/alerts/groups/${id}/resolve`)
}

export function getAggregationPolicies() {
  return request.get('/alerts/aggregation/policies')
}

export function createAggregationPolicy(data: any) {
  return request.post('/alerts/aggregation/policies', data)
}

export function getRcaReport(groupId: number) {
  return request.get(`/alerts/groups/${groupId}/rca`)
}

export function triggerRcaAnalysis(groupId: number) {
  return request.post('/alerts/rca/analyze', { group_id: groupId })
}

export function getRcaReports(params?: any) {
  return request.get('/alerts/rca/reports', { params })
}
```

- [ ] **Step 2: 添加路由**

在 `frontend/src/router/index.ts` 中添加路由配置.

```typescript
{
  path: '/alerts/groups',
  name: 'AlertGroups',
  component: () => import('@/views/alert/AlertGroups.vue'),
  meta: { title: '聚合告警' }
},
{
  path: '/alerts/groups/:id',
  name: 'AlertGroupDetail',
  component: () => import('@/views/alert/AlertGroupDetail.vue'),
  meta: { title: '告警组详情' }
},
{
  path: '/alerts/aggregation',
  name: 'AggregationPolicies',
  component: () => import('@/views/alert/AggregationPolicies.vue'),
  meta: { title: '聚合策略' }
}
```

- [ ] **Step 3: 创建 AlertGroups.vue**

创建 `frontend/src/views/alert/AlertGroups.vue`.

```vue
<template>
  <div class="alert-groups">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>聚合告警列表</span>
          <el-button type="primary" @click="fetchData">刷新</el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable @change="fetchData">
            <el-option label="活跃" value="active" />
            <el-option label="已确认" value="acknowledged" />
            <el-option label="已解决" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略">
          <el-select v-model="filters.strategy" placeholder="全部" clearable @change="fetchData">
            <el-option label="时间窗口" value="time_window" />
            <el-option label="拓扑关联" value="topology" />
            <el-option label="语义相似" value="semantic" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="groups" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="strategy" label="策略" width="120">
          <template #default="{ row }">
            <el-tag :type="getStrategyType(row.strategy)">{{ getStrategyLabel(row.strategy) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_count" label="告警数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row.id)">详情</el-button>
            <el-button v-if="row.status === 'active'" type="warning" link @click="acknowledge(row)">确认</el-button>
            <el-button v-if="row.status !== 'resolved'" type="success" link @click="resolve(row)">解决</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAlertGroups, acknowledgeGroup, resolveGroup } from '@/api/alert'

const router = useRouter()
const loading = ref(false)
const groups = ref<any[]>([])

const filters = reactive({
  status: '',
  strategy: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getAlertGroups({
      status: filters.status || undefined,
      strategy: filters.strategy || undefined,
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    })
    groups.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (id: number) => {
  router.push(`/alerts/groups/${id}`)
}

const acknowledge = async (row: any) => {
  try {
    await acknowledgeGroup(row.id)
    ElMessage.success('已确认')
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resolve = async (row: any) => {
  try {
    await resolveGroup(row.id)
    ElMessage.success('已解决')
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const getStrategyType = (strategy: string) => {
  const map: Record<string, string> = {
    time_window: 'primary',
    topology: 'success',
    semantic: 'warning'
  }
  return map[strategy] || 'info'
}

const getStrategyLabel = (strategy: string) => {
  const map: Record<string, string> = {
    time_window: '时间窗口',
    topology: '拓扑关联',
    semantic: '语义相似'
  }
  return map[strategy] || strategy
}

const getSeverityType = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return map[severity] || 'info'
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    active: 'danger',
    acknowledged: 'warning',
    resolved: 'success'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    active: '活跃',
    acknowledged: '已确认',
    resolved: '已解决'
  }
  return map[status] || status
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.alert-groups {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-form {
  margin-bottom: 20px;
}
</style>
```

- [ ] **Step 4: 创建 AlertGroupDetail.vue**

创建 `frontend/src/views/alert/AlertGroupDetail.vue`.

```vue
<template>
  <div class="alert-group-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button @click="router.back()">返回</el-button>
          <span>告警组详情 #{{ groupId }}</span>
          <div>
            <el-button v-if="group?.status === 'active'" type="warning" @click="acknowledge">确认</el-button>
            <el-button v-if="group?.status !== 'resolved'" type="success" @click="resolve">解决</el-button>
            <el-button type="primary" @click="startRca">根因分析</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="group">
        <el-descriptions-item label="策略">
          <el-tag :type="getStrategyType(group.strategy)">{{ getStrategyLabel(group.strategy) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(group.status)">{{ getStatusLabel(group.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="严重级别">
          <el-tag :type="getSeverityType(group.severity)">{{ group.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="告警数量">{{ group.alert_count }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(group.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="最后更新">{{ formatDate(group.last_alert_time) }}</el-descriptions-item>
        <el-descriptions-item label="受影响组件" :span="2">
          <el-tag v-for="comp in group.affected_components" :key="comp" style="margin-right: 5px">{{ comp }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">组内告警</el-divider>

      <el-table :data="alerts" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="rule_name" label="规则名称" />
        <el-table-column prop="severity" label="严重级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <RcaReportDialog v-if="showRcaDialog" :group-id="groupId" @close="showRcaDialog = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAlertGroup, getAlertGroupAlerts, acknowledgeGroup, resolveGroup } from '@/api/alert'
import RcaReportDialog from './RcaReportDialog.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const group = ref<any>(null)
const alerts = ref<any[]>([])
const showRcaDialog = ref(false)

const groupId = computed(() => Number(route.params.id))

const fetchData = async () => {
  loading.value = true
  try {
    const [groupRes, alertsRes] = await Promise.all([
      getAlertGroup(groupId.value),
      getAlertGroupAlerts(groupId.value)
    ])
    group.value = groupRes.data
    alerts.value = alertsRes.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const acknowledge = async () => {
  try {
    await acknowledgeGroup(groupId.value)
    ElMessage.success('已确认')
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resolve = async () => {
  try {
    await resolveGroup(groupId.value)
    ElMessage.success('已解决')
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const startRca = () => {
  showRcaDialog.value = true
}

const getStrategyType = (strategy: string) => {
  const map: Record<string, string> = { time_window: 'primary', topology: 'success', semantic: 'warning' }
  return map[strategy] || 'info'
}

const getStrategyLabel = (strategy: string) => {
  const map: Record<string, string> = { time_window: '时间窗口', topology: '拓扑关联', semantic: '语义相似' }
  return map[strategy] || strategy
}

const getSeverityType = (severity: string) => {
  const map: Record<string, string> = { critical: 'danger', warning: 'warning', info: 'info' }
  return map[severity] || 'info'
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = { active: 'danger', acknowledged: 'warning', resolved: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { active: '活跃', acknowledged: '已确认', resolved: '已解决' }
  return map[status] || status
}

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

onMounted(() => fetchData())
</script>

<style scoped>
.alert-group-detail { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
```

- [ ] **Step 5: 创建 AggregationPolicies.vue**

创建 `frontend/src/views/alert/AggregationPolicies.vue`.

```vue
<template>
  <div class="aggregation-policies">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>聚合策略配置</span>
          <el-button type="primary" @click="showCreateDialog">新建策略</el-button>
        </div>
      </template>

      <el-table :data="policies" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="strategy" label="策略" width="120">
          <template #default="{ row }">
            <el-tag :type="getStrategyType(row.strategy)">{{ getStrategyLabel(row.strategy) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="window_seconds" label="时间窗口(秒)" width="120" />
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" title="新建聚合策略" width="500px">
      <el-form :model="createForm" label-width="120px">
        <el-form-item label="名称">
          <el-input v-model="createForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="createForm.strategy" placeholder="请选择策略">
            <el-option label="时间窗口" value="time_window" />
            <el-option label="拓扑关联" value="topology" />
            <el-option label="语义相似" value="semantic" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间窗口(秒)">
          <el-input-number v-model="createForm.window_seconds" :min="60" :max="3600" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="createForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createPolicy">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAggregationPolicies, createAggregationPolicy } from '@/api/alert'

const loading = ref(false)
const policies = ref<any[]>([])
const createDialogVisible = ref(false)

const createForm = reactive({
  name: '',
  strategy: 'time_window',
  window_seconds: 300,
  enabled: true
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getAggregationPolicies()
    policies.value = res.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  createForm.name = ''
  createForm.strategy = 'time_window'
  createForm.window_seconds = 300
  createForm.enabled = true
  createDialogVisible.value = true
}

const createPolicy = async () => {
  try {
    await createAggregationPolicy(createForm)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const getStrategyType = (strategy: string) => {
  const map: Record<string, string> = { time_window: 'primary', topology: 'success', semantic: 'warning' }
  return map[strategy] || 'info'
}

const getStrategyLabel = (strategy: string) => {
  const map: Record<string, string> = { time_window: '时间窗口', topology: '拓扑关联', semantic: '语义相似' }
  return map[strategy] || strategy
}

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

onMounted(() => fetchData())
</script>

<style scoped>
.aggregation-policies { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
```

- [ ] **Step 6: 创建 RcaReportDialog.vue**

创建 `frontend/src/views/alert/RcaReportDialog.vue`.

```vue
<template>
  <el-dialog v-model="visible" title="根因分析报告" width="800px" @close="emit('close')">
    <div v-loading="loading">
      <template v-if="report">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="report.status === 'completed' ? 'success' : 'warning'">
              {{ report.status === 'completed' ? '分析完成' : '分析中' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="置信度">{{ (report.confidence * 100).toFixed(1) }}%</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">根因候选</el-divider>

        <el-table :data="report.candidates" stripe>
          <el-table-column prop="rank_order" label="排名" width="80" />
          <el-table-column prop="component_name" label="组件" />
          <el-table-column prop="component_type" label="类型" width="120" />
          <el-table-column prop="score" label="得分" width="100">
            <template #default="{ row }">{{ (row.score * 100).toFixed(1) }}%</template>
          </el-table-column>
          <el-table-column prop="analysis_method" label="分析方法" width="120" />
        </el-table>

        <el-divider content-position="left">排查建议</el-divider>

        <el-timeline v-if="report.recommendations">
          <el-timeline-item v-for="(rec, index) in report.recommendations" :key="index" :type="rec.priority === 'high' ? 'danger' : 'primary'">
            <p><strong>{{ rec.component }}</strong>: {{ rec.action }}</p>
          </el-timeline-item>
        </el-timeline>
      </template>

      <el-empty v-else description="暂无分析报告">
        <el-button type="primary" @click="startAnalysis">开始分析</el-button>
      </el-empty>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRcaReport, triggerRcaAnalysis } from '@/api/alert'

const props = defineProps<{ groupId: number }>()
const emit = defineEmits(['close'])

const visible = ref(true)
const loading = ref(false)
const report = ref<any>(null)

const fetchReport = async () => {
  loading.value = true
  try {
    const res = await getRcaReport(props.groupId)
    report.value = res.data
  } catch (error) {
    report.value = null
  } finally {
    loading.value = false
  }
}

const startAnalysis = async () => {
  loading.value = true
  try {
    await triggerRcaAnalysis(props.groupId)
    ElMessage.success('分析已启动，请稍后刷新查看结果')
    setTimeout(fetchReport, 2000)
  } catch (error) {
    ElMessage.error('启动分析失败')
    loading.value = false
  }
}

onMounted(() => fetchReport())
</script>
```

- [ ] **Step 7: 更新侧边栏菜单**

在 `frontend/src/views/Layout.vue` 的菜单配置中添加新菜单项.

找到菜单配置数组，添加以下项:

```typescript
{
  index: '/alerts/groups',
  title: '聚合告警',
  icon: 'Collection'
},
{
  index: '/alerts/aggregation',
  title: '聚合策略',
  icon: 'Setting'
}
```

- [ ] **Step 8: 运行前端测试**

Run: `cd frontend && npm run dev`

- [ ] **Step 9: 提交代码**

```bash
git add frontend/src/views/alert/*.vue frontend/src/api/alert.ts frontend/src/router/index.ts
git commit -m "feat(alert): add aggregation and RCA frontend pages"
```

---

## Task 12: 更新文档

**Files:**
- Modify: `docs/ALERT_MODULE_PROGRESS.md`
- Modify: `README.md`
- Modify: `README_cn.md`

- [ ] **Step 1: 更新进度文档**

在 `docs/ALERT_MODULE_PROGRESS.md` 中添加 Phase 2 完成记录.

```markdown
## Phase 2: 告警聚合与根因分析 (已完成)

### 完成时间
2026-04-01

### 实现功能

#### 告警聚合模块
- ✅ 时间窗口聚合策略
- ✅ 拓扑关联聚合策略
- ✅ 语义相似聚合策略
- ✅ 聚合告警组管理 API
- ✅ 聚合策略配置 API

#### 根因分析模块
- ✅ 随机游走分析器
- ✅ 时序相关性分析器
- ✅ LLM 推理分析器
- ✅ 根因分析报告 API

#### 前端页面
- ✅ 聚合告警列表页
- ✅ 聚合告警详情页
- ✅ 聚合策略配置页
- ✅ 根因分析报告弹窗
```

- [ ] **Step 2: 更新 README**

在 `README.md` 和 `README_cn.md` 中更新功能模块状态.

将 Phase 2 部分从:

```markdown
### Phase 2 (计划中)
- 🔲 告警聚合与降噪
- 🔲 根因分析
```

修改为:

```markdown
### Phase 2 (已完成)
- ✅ 告警聚合与降噪
  - 时间窗口聚合
  - 拓扑关联聚合
  - 语义相似聚合
- ✅ 根因分析
  - 随机游走分析
  - 时序相关性分析
  - LLM 推理分析
```

- [ ] **Step 3: 提交代码**

```bash
git add docs/ALERT_MODULE_PROGRESS.md README.md README_cn.md
git commit -m "docs: update Phase 2 completion status"
```

---

## 执行选项

Plan complete. Choose execution approach:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, with two-stage review
   - Best for: Independent tasks, parallelizable work, clear checkpoints
   - Required sub-skill: `superpowers:subagent-driven-development`

**2. Inline Execution** - Execute tasks in this session, with review checkpoints
   - Best for: Sequential tasks, debugging needed, learning the codebase
   - Required sub-skill: `superpowers:executing-plans`
