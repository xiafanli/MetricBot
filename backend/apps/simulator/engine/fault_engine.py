import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from apps.simulator.models import SimulationEnvironment, SimulationComponent, FaultScenario, FaultInstance


class FaultEngine:
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
