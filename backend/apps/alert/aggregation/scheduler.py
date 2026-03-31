import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apps.alert.models import AlertEvent, AlertGroup, AlertGroupMember, AggregationPolicy
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
                from apps.alert.aggregation.strategies.semantic import SemanticStrategy
                engine.register_strategy("time_window", TimeWindowStrategy)
                engine.register_strategy("topology", TopologyStrategy)
                engine.register_strategy("semantic", SemanticStrategy)
                for policy in policies:
                    cutoff_time = datetime.now() - timedelta(seconds=policy.window_seconds)
                    subquery = db.query(AlertGroupMember.alert_id).subquery()
                    ungrouped_alerts = db.query(AlertEvent).filter(
                        AlertEvent.created_at >= cutoff_time,
                        ~AlertEvent.id.in_(subquery),
                    ).all()
                    if ungrouped_alerts:
                        engine.aggregate(ungrouped_alerts, policy)
                        logger.info(f"Aggregated {len(ungrouped_alerts)} alerts with policy {policy.name}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Aggregation job error: {e}")


aggregation_scheduler = AggregationScheduler()
