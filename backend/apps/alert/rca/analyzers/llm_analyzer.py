from typing import List, Dict, Any
from sqlalchemy.orm import Session
from apps.alert.models import AlertGroup, AlertGroupMember, AlertEvent
import json
import logging
import re

logger = logging.getLogger(__name__)


class LlmAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def analyze(self, group: AlertGroup) -> Dict[str, Any]:
        members = self.db.query(AlertGroupMember).filter(AlertGroupMember.group_id == group.id).all()
        alert_ids = [m.alert_id for m in members]
        alerts = self.db.query(AlertEvent).filter(AlertEvent.id.in_(alert_ids)).all()
        alert_summary = self._build_alert_summary(alerts)
        topology_info = self._get_topology_info(alerts)
        prompt = self._build_prompt(alert_summary, topology_info)
        try:
            model_service = self._get_model_service()
            if not model_service:
                return {"candidates": [], "method": "llm", "error": "No model service available"}
            response = self._call_model(model_service, prompt)
            result = self._parse_response(response)
            return result
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {"candidates": [], "method": "llm", "error": str(e)}

    def _get_model_service(self):
        try:
            from apps.model.service import ModelService
            return ModelService(self.db)
        except ImportError:
            return None

    def _call_model(self, model_service, prompt: str) -> str:
        try:
            model = model_service.get_default_model()
            if not model:
                return ""
            return model_service.call_model(model, prompt)
        except Exception as e:
            logger.error(f"Model call failed: {e}")
            return ""

    def _build_alert_summary(self, alerts: List[AlertEvent]) -> str:
        summary_lines = []
        for alert in alerts[:10]:
            line = f"- [{alert.severity}] {alert.title}"
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
