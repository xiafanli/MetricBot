from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class AlertScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.running = False

    def start(self):
        if self.running:
            return
        self.scheduler.start()
        self._add_jobs()
        self.running = True
        logger.info("告警评估调度器已启动")

    def stop(self):
        if not self.running:
            return
        self.scheduler.shutdown()
        self.running = False
        logger.info("告警评估调度器已停止")

    def _add_jobs(self):
        self.scheduler.add_job(
            self._evaluate_critical,
            IntervalTrigger(seconds=15),
            id="evaluate_critical",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self._evaluate_warning,
            IntervalTrigger(seconds=30),
            id="evaluate_warning",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self._evaluate_info,
            IntervalTrigger(seconds=120),
            id="evaluate_info",
            replace_existing=True
        )

    def _evaluate_critical(self):
        from common.core.database import SessionLocal
        from .evaluator import AlertEvaluator
        from apps.alert.models import AlertRule
        
        db = SessionLocal()
        try:
            evaluator = AlertEvaluator(db)
            rules = db.query(AlertRule).filter(
                AlertRule.enabled == True,
                AlertRule.severity == "critical"
            ).all()
            
            for rule in rules:
                evaluator.evaluate_rule(rule)
        except Exception as e:
            logger.error(f"评估 critical 规则失败: {e}")
        finally:
            db.close()

    def _evaluate_warning(self):
        from common.core.database import SessionLocal
        from .evaluator import AlertEvaluator
        from apps.alert.models import AlertRule
        
        db = SessionLocal()
        try:
            evaluator = AlertEvaluator(db)
            rules = db.query(AlertRule).filter(
                AlertRule.enabled == True,
                AlertRule.severity == "warning"
            ).all()
            
            for rule in rules:
                evaluator.evaluate_rule(rule)
        except Exception as e:
            logger.error(f"评估 warning 规则失败: {e}")
        finally:
            db.close()

    def _evaluate_info(self):
        from common.core.database import SessionLocal
        from .evaluator import AlertEvaluator
        from apps.alert.models import AlertRule
        
        db = SessionLocal()
        try:
            evaluator = AlertEvaluator(db)
            rules = db.query(AlertRule).filter(
                AlertRule.enabled == True,
                AlertRule.severity == "info"
            ).all()
            
            for rule in rules:
                evaluator.evaluate_rule(rule)
        except Exception as e:
            logger.error(f"评估 info 规则失败: {e}")
        finally:
            db.close()


alert_scheduler = AlertScheduler()
