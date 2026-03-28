import logging
from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from common.core.database import SessionLocal
from apps.simulator.engine import MetricGenerator, LogGenerator, FaultEngine
from apps.simulator.models import SimulationEnvironment

logger = logging.getLogger(__name__)


class SimulatorScheduler:
    _instance = None
    _scheduler: AsyncIOScheduler = None
    _jobs: Dict[int, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._scheduler = AsyncIOScheduler()
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_db(self):
        return SessionLocal()

    def _metric_job(self, env_id: int):
        try:
            db = self._get_db()
            try:
                env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
                if env and env.is_active:
                    generator = MetricGenerator(db, env.pushgateway_url)
                    generator.generate_and_push(env_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Metric job error for env {env_id}: {e}")

    def _log_job(self, env_id: int):
        try:
            db = self._get_db()
            try:
                env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
                if env and env.is_active:
                    log_path = env.log_path or "simulator/logs"
                    generator = LogGenerator(db, log_path)
                    generator.generate_and_write(env_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Log job error for env {env_id}: {e}")

    def _fault_check_job(self):
        try:
            db = self._get_db()
            try:
                engine = FaultEngine(db)
                engine.check_and_recover()

                active_envs = db.query(SimulationEnvironment).filter(SimulationEnvironment.is_active == True).all()
                for env in active_envs:
                    engine.check_and_trigger(env.id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Fault check job error: {e}")

    def start_environment(self, env_id: int):
        if env_id in self._jobs:
            return

        job_id_metric = f"env_{env_id}_metric"
        job_id_log = f"env_{env_id}_log"

        self._scheduler.add_job(
            self._metric_job,
            trigger=IntervalTrigger(minutes=1),
            id=job_id_metric,
            args=[env_id],
            replace_existing=True,
        )

        self._scheduler.add_job(
            self._log_job,
            trigger=IntervalTrigger(minutes=1),
            id=job_id_log,
            args=[env_id],
            replace_existing=True,
        )

        self._jobs[env_id] = {
            "metric_job_id": job_id_metric,
            "log_job_id": job_id_log,
        }

    def stop_environment(self, env_id: int):
        if env_id not in self._jobs:
            return

        jobs = self._jobs[env_id]
        self._scheduler.remove_job(jobs["metric_job_id"])
        self._scheduler.remove_job(jobs["log_job_id"])
        del self._jobs[env_id]

    def start(self):
        if not self._scheduler.running:
            self._scheduler.add_job(
                self._fault_check_job,
                trigger=IntervalTrigger(seconds=10),
                id="fault_check",
                replace_existing=True,
            )
            self._scheduler.start()
            logger.info("Simulator scheduler started")

    def shutdown(self):
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("Simulator scheduler shutdown")


scheduler = SimulatorScheduler.get_instance()
