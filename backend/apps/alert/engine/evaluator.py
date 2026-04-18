import httpx
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from apps.alert.models import AlertRule, Alert
from apps.datasource.models import Datasource


class AlertEvaluator:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_rule(self, rule: AlertRule) -> Optional[Alert]:
        datasource = self.db.query(Datasource).filter(Datasource.id == rule.datasource_id).first()
        if not datasource:
            print(f"数据源不存在: {rule.datasource_id}")
            return None

        metric_value = self._query_metric(datasource, rule.metric_query)
        if metric_value is None:
            return None

        threshold = float(rule.threshold) if rule.threshold else 0
        triggered = self._check_condition(rule.condition_type, metric_value, threshold)

        if triggered:
            existing_alert = self.db.query(Alert).filter(
                Alert.rule_id == rule.id,
                Alert.resolved == False
            ).first()
            
            if existing_alert:
                existing_alert.metric_value = metric_value
                self.db.commit()
                return existing_alert

            alert = Alert(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                metric_value=metric_value,
                threshold=rule.threshold,
                message=f"{rule.name}: {metric_value} 触发阈值 {rule.threshold}",
                resolved=False,
                datasource_id=rule.datasource_id
            )
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            self._broadcast_alert(alert)
            
            return alert
        else:
            existing_alert = self.db.query(Alert).filter(
                Alert.rule_id == rule.id,
                Alert.resolved == False
            ).first()
            
            if existing_alert:
                existing_alert.resolved = True
                existing_alert.resolved_at = datetime.now()
                self.db.commit()
                self._broadcast_alert_resolved(existing_alert)
            
            return None

    def _broadcast_alert(self, alert: Alert):
        try:
            import asyncio
            from common.core.websocket import manager
            
            alert_data = {
                "id": alert.id,
                "rule_id": alert.rule_id,
                "rule_name": alert.rule_name,
                "severity": alert.severity,
                "metric_value": float(alert.metric_value) if alert.metric_value else None,
                "threshold": float(alert.threshold) if alert.threshold else None,
                "message": alert.message,
                "resolved": alert.resolved,
                "created_at": alert.created_at.isoformat() if alert.created_at else None
            }
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(manager.broadcast_alert(alert_data))
            loop.close()
        except Exception as e:
            print(f"广播告警失败: {e}")

    def _broadcast_alert_resolved(self, alert: Alert):
        try:
            import asyncio
            from common.core.websocket import manager
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(manager.broadcast_alert_update(alert.id, "resolved"))
            loop.close()
        except Exception as e:
            print(f"广播告警恢复失败: {e}")

    def _query_metric(self, datasource: Datasource, query: str) -> Optional[float]:
        try:
            if datasource.type == "prometheus":
                url = f"{datasource.url}/api/v1/query"
                params = {"query": query}
                
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                if data.get("status") == "success" and data.get("data", {}).get("result"):
                    results = data["data"]["result"]
                    if results:
                        value = results[0].get("value", [None, 0])[1]
                        return float(value)
                
                return None
            else:
                print(f"不支持的数据源类型: {datasource.type}")
                return None
        except Exception as e:
            print(f"查询指标失败: {e}")
            return None

    def _check_condition(self, condition_type: str, value: float, threshold: float) -> bool:
        if condition_type == "greater_than":
            return value > threshold
        elif condition_type == "less_than":
            return value < threshold
        elif condition_type == "equal_to":
            return value == threshold
        return False

    def evaluate_all_rules(self) -> List[Alert]:
        rules = self.db.query(AlertRule).filter(AlertRule.enabled == True).all()
        new_alerts = []
        
        for rule in rules:
            alert = self.evaluate_rule(rule)
            if alert:
                new_alerts.append(alert)
        
        return new_alerts
