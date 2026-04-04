import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from apps.simulator.models import SimulationEnvironment, SimulationComponent, FaultScenario, FaultInstance, FaultType


class FaultEngine:
    FAULT_IMPACT_MAP = {
        FaultType.HOST_CPU_OVERLOAD: {
            "cpu_usage": 3.0,
            "response_time": 2.0,
        },
        FaultType.HOST_MEMORY_EXHAUST: {
            "memory_usage": 2.5,
            "swap_usage": 5.0,
        },
        FaultType.HOST_DISK_FULL: {
            "disk_usage": 1.5,
            "io_wait": 3.0,
        },
        FaultType.HOST_NETWORK_LATENCY: {
            "response_time": 2.0,
            "error_rate": 5.0,
        },
        FaultType.NGINX_CONNECTION_OVERFLOW: {
            "nginx_connection_count": 2.0,
            "nginx_request_rate": 0.5,
        },
        FaultType.NGINX_UPSTREAM_TIMEOUT: {
            "nginx_upstream_response_time": 3.0,
            "nginx_error_rate": 5.0,
        },
        FaultType.NGINX_CACHE_MISS: {
            "nginx_cache_miss_rate": 3.0,
            "nginx_response_time": 1.5,
        },
        FaultType.APP_MEMORY_LEAK: {
            "memory_usage": 2.0,
            "error_rate": 3.0,
        },
        FaultType.APP_GC_OVERHEAD: {
            "response_time": 3.0,
            "error_rate": 2.0,
        },
        FaultType.APP_THREAD_BLOCK: {
            "thread_count": 2.0,
            "response_time": 4.0,
        },
        FaultType.APP_API_TIMEOUT: {
            "response_time": 5.0,
            "error_rate": 8.0,
        },
        FaultType.API_GATEWAY_CIRCUIT_BREAK: {
            "api_gateway_circuit_breaker_open": 1.0,
            "api_gateway_error_rate": 5.0,
        },
        FaultType.API_GATEWAY_RATE_LIMIT: {
            "api_gateway_rate_limit_rejected": 10.0,
            "api_gateway_request_success_rate": 0.7,
        },
        FaultType.REDIS_CONNECTION_EXHAUST: {
            "redis_connected_clients": 1.5,
            "redis_blocked_clients": 10.0,
        },
        FaultType.REDIS_MEMORY_OVERFLOW: {
            "redis_used_memory": 1.2,
            "redis_evicted_keys": 100.0,
        },
        FaultType.REDIS_CACHE_PENETRATION: {
            "redis_cache_hit_rate": 0.5,
            "redis_request_rate": 2.0,
        },
        FaultType.MYSQL_CONNECTION_EXHAUST: {
            "mysql_threads_connected": 1.5,
            "mysql_connection_errors": 10.0,
        },
        FaultType.MYSQL_SLOW_QUERY: {
            "mysql_slow_queries": 10.0,
            "mysql_query_time": 10.0,
        },
        FaultType.MYSQL_DEADLOCK: {
            "mysql_table_locks_waited": 5.0,
            "mysql_innodb_row_lock_waits": 10.0,
        },
        FaultType.MYSQL_REPLICATION_LAG: {
            "mysql_replication_lag": 10.0,
            "mysql_slave_status": 0.0,
        },
        FaultType.FIREWALL_RULE_BLOCK: {
            "firewall_blocked_connections": 5.0,
            "firewall_rule_hits": 2.0,
        },
        FaultType.FIREWALL_CONNECTION_OVERFLOW: {
            "firewall_connection_count": 2.0,
            "firewall_dropped_packets": 10.0,
        },
        FaultType.KAFKA_PARTITION_UNBALANCE: {
            "kafka_partition_imbalance": 1.0,
            "kafka_consumer_lag": 5.0,
        },
        FaultType.KAFKA_CONSUMER_LAG: {
            "kafka_consumer_lag": 10.0,
            "kafka_message_rate": 0.5,
        },
        FaultType.CONFIG_CENTER_SYNC_FAIL: {
            "config_sync_errors": 10.0,
            "config_update_failures": 5.0,
        },
    }

    def __init__(self, db: Session):
        self.db = db

    def check_and_trigger(self, env_id: int):
        env = self.db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
        if not env or not env.is_active:
            return

        components = self.db.query(SimulationComponent).filter(SimulationComponent.env_id == env_id).all()
        scenarios = self.db.query(FaultScenario).filter(FaultScenario.is_enabled == True).all()

        triggered = []

        for scenario in scenarios:
            for component in components:
                if scenario.target_component_type and scenario.target_component_type != component.component_type:
                    continue

                active_fault = self.db.query(FaultInstance).filter(
                    FaultInstance.component_id == component.id,
                    FaultInstance.status == "active",
                ).first()

                if active_fault:
                    continue

                if random.random() < scenario.probability:
                    fault = self._create_fault_instance(scenario, component)
                    triggered.append(fault)

        return triggered

    def _create_fault_instance(self, scenario: FaultScenario, component: SimulationComponent) -> FaultInstance:
        now = datetime.now()
        duration_minutes = scenario.config.get("duration_minutes", 5) if scenario.config else 5
        end_time = now + timedelta(minutes=duration_minutes)

        fault = FaultInstance(
            scenario_id=scenario.id,
            component_id=component.id,
            start_time=now,
            end_time=end_time,
            status="active",
            impact_data=scenario.config.get("impact", {}) if scenario.config else {},
        )

        self.db.add(fault)
        self.db.commit()
        self.db.refresh(fault)

        return fault

    def check_and_recover(self):
        now = datetime.now()
        active_faults = self.db.query(FaultInstance).filter(
            FaultInstance.status == "active",
            FaultInstance.end_time <= now,
        ).all()

        recovered = []
        for fault in active_faults:
            fault.status = "completed"
            recovered.append(fault)

        if recovered:
            self.db.commit()

        return recovered

    def trigger_manual(self, scenario_id: int, component_id: int) -> FaultInstance:
        scenario = self.db.query(FaultScenario).filter(FaultScenario.id == scenario_id).first()
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        component = self.db.query(SimulationComponent).filter(SimulationComponent.id == component_id).first()
        if not component:
            raise ValueError(f"Component {component_id} not found")

        return self._create_fault_instance(scenario, component)

    def get_fault_impact(self, fault_type: str) -> Dict[str, Any]:
        return self.FAULT_IMPACT_MAP.get(fault_type, {})

    def get_active_faults_for_component(self, component_id: int) -> List[FaultInstance]:
        return self.db.query(FaultInstance).filter(
            FaultInstance.component_id == component_id,
            FaultInstance.status == "active",
        ).all()

    def get_component_impact(self, component_id: int) -> Dict[str, float]:
        active_faults = self.get_active_faults_for_component(component_id)
        total_impact: Dict[str, float] = {}

        for fault in active_faults:
            scenario = self.db.query(FaultScenario).filter(FaultScenario.id == fault.scenario_id).first()
            if scenario:
                impact = self.get_fault_impact(scenario.fault_type)
                for metric, multiplier in impact.items():
                    if metric in total_impact:
                        total_impact[metric] *= multiplier
                    else:
                        total_impact[metric] = multiplier

        return total_impact
