import random
import time
from typing import Dict, Any, List, Optional
from prometheus_client import Gauge, Counter, Histogram, CollectorRegistry, push_to_gateway
from sqlalchemy.orm import Session
from apps.simulator.models import SimulationEnvironment, SimulationComponent, MetricTemplate, FaultInstance


class MetricGenerator:
    def __init__(self, db: Session, pushgateway_url: str = "http://localhost:9091"):
        self.db = db
        self.pushgateway_url = pushgateway_url
        self.registry = CollectorRegistry()
        self.metrics = {}

    def generate_value(self, base_value: float, min_value: float, max_value: float, fluctuation: float, fault_impact: float = 1.0) -> float:
        fluctuation_range = base_value * fluctuation
        random_offset = random.uniform(-fluctuation_range, fluctuation_range)
        value = (base_value + random_offset) * fault_impact
        value = max(min_value, min(value, max_value))
        return value

    def get_fault_impact(self, component: SimulationComponent) -> Dict[str, float]:
        active_faults = self.db.query(FaultInstance).filter(
            FaultInstance.component_id == component.id,
            FaultInstance.status == "active",
        ).all()

        impact = {
            "cpu_usage": 1.0,
            "memory_usage": 1.0,
            "response_time": 1.0,
            "error_rate": 1.0,
        }

        for fault in active_faults:
            scenario = fault.scenario
            if scenario and scenario.config:
                fault_config = scenario.config
                for key, factor in fault_config.get("impact", {}).items():
                    if key in impact:
                        impact[key] *= factor

        return impact

    def generate_and_push(self, env_id: int):
        env = self.db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
        if not env:
            return

        components = self.db.query(SimulationComponent).filter(SimulationComponent.env_id == env_id).all()
        templates = self.db.query(MetricTemplate).all()

        template_map = {}
        for template in templates:
            if template.component_type not in template_map:
                template_map[template.component_type] = []
            template_map[template.component_type].append(template)

        job_name = f"simulation_env_{env_id}"
        timestamp = int(time.time())

        registry = CollectorRegistry()
        metrics = {}

        for component in components:
            impact = self.get_fault_impact(component)
            component_templates = template_map.get(component.component_type, [])

            for template in component_templates:
                metric_key = f"{component.id}_{template.metric_name}"
                metric_name = f"{template.component_type}_{template.metric_name}"

                if metric_key not in metrics:
                    labels = {"component_id": str(component.id), "component_name": component.name, "component_type": component.component_type}
                    if template.labels:
                        labels.update(template.labels)

                    if template.metric_type == "gauge":
                        metrics[metric_key] = Gauge(
                            metric_name,
                            template.description or "",
                            labelnames=list(labels.keys()),
                            registry=registry,
                        )
                    elif template.metric_type == "counter":
                        metrics[metric_key] = Counter(
                            metric_name,
                            template.description or "",
                            labelnames=list(labels.keys()),
                            registry=registry,
                        )

                base_value = template.base_value or 0.0
                min_value = template.min_value or 0.0
                max_value = template.max_value or 100.0

                fault_factor = 1.0
                if "cpu" in template.metric_name:
                    fault_factor = impact.get("cpu_usage", 1.0)
                elif "memory" in template.metric_name:
                    fault_factor = impact.get("memory_usage", 1.0)
                elif "response_time" in template.metric_name or "latency" in template.metric_name:
                    fault_factor = impact.get("response_time", 1.0)
                elif "error" in template.metric_name:
                    fault_factor = impact.get("error_rate", 1.0)

                value = self.generate_value(base_value, min_value, max_value, template.fluctuation, fault_factor)

                metric = metrics[metric_key]
                labels = {"component_id": str(component.id), "component_name": component.name, "component_type": component.component_type}
                if template.labels:
                    labels.update(template.labels)

                if template.metric_type == "gauge":
                    metric.labels(**labels).set(value)
                elif template.metric_type == "counter":
                    metric.labels(**labels).inc(value)

        try:
            push_url = env.pushgateway_url or self.pushgateway_url
            if push_url:
                push_to_gateway(push_url, job=job_name, registry=registry)
                print(f"Successfully pushed metrics to {push_url} for job {job_name}")
        except Exception as e:
            print(f"Failed to push metrics: {e}")
            import traceback
            traceback.print_exc()
