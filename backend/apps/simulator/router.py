from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.core.database import get_db
from apps.simulator.models import (
    SimulationEnvironment,
    SimulationComponent,
    ComponentRelation,
    MetricTemplate,
    LogTemplate,
    FaultScenario,
    FaultInstance,
    ScenarioHistory,
    TopologyTemplate,
)
from apps.simulator.schemas import (
    SimulationEnvironmentCreate,
    SimulationEnvironmentUpdate,
    SimulationEnvironmentResponse,
    SimulationComponentCreate,
    SimulationComponentUpdate,
    SimulationComponentResponse,
    ComponentRelationCreate,
    ComponentRelationResponse,
    MetricTemplateCreate,
    MetricTemplateUpdate,
    MetricTemplateResponse,
    LogTemplateCreate,
    LogTemplateUpdate,
    LogTemplateResponse,
    FaultScenarioCreate,
    FaultScenarioUpdate,
    FaultScenarioResponse,
    FaultInstanceCreate,
    FaultInstanceUpdate,
    FaultInstanceResponse,
    EnvironmentActivateRequest,
    TopologyGenerateRequest,
    TopologyGenerateResponse,
    TopologyTypeResponse,
    TopologyScaleResponse,
    TopologyComponentTypeResponse,
    TopologyIPCheckResponse,
)
from apps.simulator.engine import TopologyManager
from apps.simulator.engine.topology_generator import TopologyGenerator
from apps.simulator.tasks import scheduler

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.get("/environments", response_model=List[SimulationEnvironmentResponse])
def get_environments(db: Session = Depends(get_db)):
    return db.query(SimulationEnvironment).all()


@router.get("/environments/{id}", response_model=SimulationEnvironmentResponse)
def get_environment(id: int, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return env


@router.post("/environments", response_model=SimulationEnvironmentResponse, status_code=status.HTTP_201_CREATED)
def create_environment(data: SimulationEnvironmentCreate, db: Session = Depends(get_db)):
    env = SimulationEnvironment(**data.dict())
    db.add(env)
    db.commit()
    db.refresh(env)
    return env


@router.put("/environments/{id}", response_model=SimulationEnvironmentResponse)
def update_environment(id: int, data: SimulationEnvironmentUpdate, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(env, field, value)

    db.commit()
    db.refresh(env)
    return env


@router.delete("/environments/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(id: int, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    scheduler.stop_environment(id)
    db.delete(env)
    db.commit()


@router.post("/environments/{id}/activate")
def activate_environment(id: int, data: EnvironmentActivateRequest, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    if data.pushgateway_url:
        env.pushgateway_url = data.pushgateway_url
    if data.log_path:
        env.log_path = data.log_path

    env.is_active = True
    db.commit()

    scheduler.start_environment(id)

    return {"message": "Environment activated", "id": id}


@router.post("/environments/{id}/deactivate")
def deactivate_environment(id: int, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    env.is_active = False
    db.commit()

    scheduler.stop_environment(id)

    return {"message": "Environment deactivated", "id": id}


@router.get("/environments/{id}/status")
def get_environment_status(id: int, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    components = db.query(SimulationComponent).filter(SimulationComponent.env_id == id).all()

    active_faults = db.query(FaultInstance).join(FaultScenario).join(SimulationComponent).filter(
        SimulationComponent.env_id == id,
        FaultInstance.status == "active"
    ).all()

    faulty_component_ids = {f.component_id for f in active_faults}

    component_statuses = []
    active_count = 0
    for c in components:
        status = "error" if c.id in faulty_component_ids else "active"
        if status == "active":
            active_count += 1
        props = c.properties or {}
        component_statuses.append({
            "id": c.id,
            "name": c.name,
            "type": c.component_type,
            "status": status,
            "ip_address": props.get("ip_address", ""),
        })

    status = {
        "total_components": len(components),
        "active_components": active_count,
        "inactive_components": len(components) - active_count,
        "active_faults": len(active_faults),
        "components": component_statuses,
        "faults": [
            {
                "id": f.id,
                "component_id": f.component_id,
                "component_name": f.component.name if f.component else None,
                "scenario_name": f.scenario.name if f.scenario else None,
                "start_time": f.start_time.isoformat() if f.start_time else None,
                "end_time": f.end_time.isoformat() if f.end_time else None,
            }
            for f in active_faults
        ],
    }

    return status


@router.post("/environments/{id}/sync-to-hosts")
def sync_to_hosts(id: int, db: Session = Depends(get_db)):
    manager = TopologyManager(db)
    return manager.sync_to_hosts(id)


@router.get("/environments/{id}/components", response_model=List[SimulationComponentResponse])
def get_components(id: int, db: Session = Depends(get_db)):
    return db.query(SimulationComponent).filter(SimulationComponent.env_id == id).all()


@router.post("/environments/{id}/components", response_model=SimulationComponentResponse, status_code=status.HTTP_201_CREATED)
def create_component(id: int, data: SimulationComponentCreate, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    component = SimulationComponent(**data.dict())
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


@router.put("/components/{id}", response_model=SimulationComponentResponse)
def update_component(id: int, data: SimulationComponentUpdate, db: Session = Depends(get_db)):
    component = db.query(SimulationComponent).filter(SimulationComponent.id == id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(component, field, value)

    db.commit()
    db.refresh(component)
    return component


@router.delete("/components/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_component(id: int, db: Session = Depends(get_db)):
    component = db.query(SimulationComponent).filter(SimulationComponent.id == id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    db.delete(component)
    db.commit()


@router.get("/components/{id}/relations")
def get_component_relations(id: int, db: Session = Depends(get_db)):
    component = db.query(SimulationComponent).filter(SimulationComponent.id == id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    outgoing = db.query(ComponentRelation).filter(ComponentRelation.source_id == id).all()
    incoming = db.query(ComponentRelation).filter(ComponentRelation.target_id == id).all()

    relations = []
    for rel in outgoing:
        target = db.query(SimulationComponent).filter(SimulationComponent.id == rel.target_id).first()
        if target:
            relations.append({
                "id": target.id,
                "name": target.name,
                "relation_type": rel.relation_type,
                "direction": "outgoing"
            })

    for rel in incoming:
        source = db.query(SimulationComponent).filter(SimulationComponent.id == rel.source_id).first()
        if source:
            relations.append({
                "id": source.id,
                "name": source.name,
                "relation_type": rel.relation_type,
                "direction": "incoming"
            })

    return relations


@router.get("/environments/{id}/relations", response_model=List[ComponentRelationResponse])
def get_relations(id: int, db: Session = Depends(get_db)):
    return db.query(ComponentRelation).filter(ComponentRelation.env_id == id).all()


@router.post("/environments/{id}/relations", response_model=ComponentRelationResponse, status_code=status.HTTP_201_CREATED)
def create_relation(id: int, data: ComponentRelationCreate, db: Session = Depends(get_db)):
    env = db.query(SimulationEnvironment).filter(SimulationEnvironment.id == id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    relation = ComponentRelation(**data.dict())
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation


@router.delete("/relations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation(id: int, db: Session = Depends(get_db)):
    relation = db.query(ComponentRelation).filter(ComponentRelation.id == id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")

    db.delete(relation)
    db.commit()


@router.get("/metric-templates", response_model=List[MetricTemplateResponse])
def get_metric_templates(db: Session = Depends(get_db)):
    return db.query(MetricTemplate).all()


@router.post("/metric-templates", response_model=MetricTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_metric_template(data: MetricTemplateCreate, db: Session = Depends(get_db)):
    template = MetricTemplate(**data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/metric-templates/{id}", response_model=MetricTemplateResponse)
def update_metric_template(id: int, data: MetricTemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(MetricTemplate).filter(MetricTemplate.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Metric template not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/metric-templates/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric_template(id: int, db: Session = Depends(get_db)):
    template = db.query(MetricTemplate).filter(MetricTemplate.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Metric template not found")

    db.delete(template)
    db.commit()


@router.get("/log-templates", response_model=List[LogTemplateResponse])
def get_log_templates(db: Session = Depends(get_db)):
    return db.query(LogTemplate).all()


@router.post("/log-templates", response_model=LogTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_log_template(data: LogTemplateCreate, db: Session = Depends(get_db)):
    template = LogTemplate(**data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/log-templates/{id}", response_model=LogTemplateResponse)
def update_log_template(id: int, data: LogTemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(LogTemplate).filter(LogTemplate.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Log template not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/log-templates/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log_template(id: int, db: Session = Depends(get_db)):
    template = db.query(LogTemplate).filter(LogTemplate.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Log template not found")

    db.delete(template)
    db.commit()


@router.get("/fault-scenarios", response_model=List[FaultScenarioResponse])
def get_fault_scenarios(db: Session = Depends(get_db)):
    return db.query(FaultScenario).all()


@router.post("/fault-scenarios", response_model=FaultScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_fault_scenario(data: FaultScenarioCreate, db: Session = Depends(get_db)):
    scenario = FaultScenario(**data.dict())
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.put("/fault-scenarios/{id}", response_model=FaultScenarioResponse)
def update_fault_scenario(id: int, data: FaultScenarioUpdate, db: Session = Depends(get_db)):
    scenario = db.query(FaultScenario).filter(FaultScenario.id == id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Fault scenario not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(scenario, field, value)

    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/fault-scenarios/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fault_scenario(id: int, db: Session = Depends(get_db)):
    scenario = db.query(FaultScenario).filter(FaultScenario.id == id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Fault scenario not found")

    db.delete(scenario)
    db.commit()


@router.post("/fault-scenarios/{id}/trigger")
def trigger_fault(id: int, component_id: int, db: Session = Depends(get_db)):
    from apps.simulator.engine import FaultEngine
    engine = FaultEngine(db)
    fault = engine.trigger_manual(id, component_id)
    return {"message": "Fault triggered", "fault_id": fault.id}


@router.get("/fault-instances", response_model=List[FaultInstanceResponse])
def get_fault_instances(db: Session = Depends(get_db)):
    return db.query(FaultInstance).order_by(FaultInstance.created_at.desc()).limit(100).all()


@router.get("/fault-instances/{id}", response_model=FaultInstanceResponse)
def get_fault_instance(id: int, db: Session = Depends(get_db)):
    fault = db.query(FaultInstance).filter(FaultInstance.id == id).first()
    if not fault:
        raise HTTPException(status_code=404, detail="Fault instance not found")
    return fault


@router.post("/fault-instances/{id}/recover")
def recover_fault_instance(id: int, db: Session = Depends(get_db)):
    fault = db.query(FaultInstance).filter(FaultInstance.id == id).first()
    if not fault:
        raise HTTPException(status_code=404, detail="Fault instance not found")
    
    if fault.status != "active":
        raise HTTPException(status_code=400, detail="Fault instance is not active")
    
    from datetime import datetime
    fault.status = "recovered"
    fault.end_time = datetime.utcnow()
    db.commit()
    
    return {"message": "Fault instance recovered", "id": id}


@router.post("/environments/generate", response_model=TopologyGenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_environment(data: TopologyGenerateRequest, db: Session = Depends(get_db)):
    generator = TopologyGenerator(db)
    try:
        result = generator.generate(
            name=data.name,
            topology_type=data.topology_type,
            scale=data.scale,
            ip_prefix=data.ip_prefix,
            description=data.description,
            pushgateway_url=data.pushgateway_url,
            log_path=data.log_path,
            include_components=data.include_components,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/topology/types", response_model=List[TopologyTypeResponse])
def get_topology_types(db: Session = Depends(get_db)):
    generator = TopologyGenerator(db)
    return generator.get_topology_types()


@router.get("/topology/scales", response_model=List[TopologyScaleResponse])
def get_topology_scales(db: Session = Depends(get_db)):
    generator = TopologyGenerator(db)
    return generator.get_scales()


@router.get("/topology/components", response_model=List[TopologyComponentTypeResponse])
def get_topology_components(db: Session = Depends(get_db)):
    generator = TopologyGenerator(db)
    return generator.get_component_types()


@router.post("/topology/check-ip", response_model=TopologyIPCheckResponse)
def check_ip_prefix(ip_prefix: str, db: Session = Depends(get_db)):
    generator = TopologyGenerator(db)
    return generator.check_ip_conflict(ip_prefix)


@router.get("/scenario-history")
def get_scenario_history(env_id: int = None, db: Session = Depends(get_db)):
    query = db.query(ScenarioHistory).order_by(ScenarioHistory.created_at.desc())
    if env_id:
        query = query.filter(ScenarioHistory.env_id == env_id)
    histories = query.limit(50).all()
    return [
        {
            "id": h.id,
            "env_id": h.env_id,
            "name": h.name,
            "description": h.description,
            "start_time": h.start_time.isoformat() if h.start_time else None,
            "end_time": h.end_time.isoformat() if h.end_time else None,
            "status": h.status,
            "snapshot_data": h.snapshot_data,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }
        for h in histories
    ]


@router.post("/scenario-history")
def create_scenario_history(data: dict, db: Session = Depends(get_db)):
    from datetime import datetime

    history = ScenarioHistory(
        env_id=data.get("env_id"),
        name=data.get("name"),
        description=data.get("description"),
        start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else datetime.now(),
        end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
        status=data.get("status", "completed"),
        snapshot_data=data.get("snapshot_data"),
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return {
        "id": history.id,
        "env_id": history.env_id,
        "name": history.name,
        "description": history.description,
        "start_time": history.start_time.isoformat() if history.start_time else None,
        "end_time": history.end_time.isoformat() if history.end_time else None,
        "status": history.status,
        "snapshot_data": history.snapshot_data,
        "created_at": history.created_at.isoformat() if history.created_at else None,
    }


@router.get("/scenario-history/{id}")
def get_scenario_history_detail(id: int, db: Session = Depends(get_db)):
    history = db.query(ScenarioHistory).filter(ScenarioHistory.id == id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Scenario history not found")
    return {
        "id": history.id,
        "env_id": history.env_id,
        "name": history.name,
        "description": history.description,
        "start_time": history.start_time.isoformat() if history.start_time else None,
        "end_time": history.end_time.isoformat() if history.end_time else None,
        "status": history.status,
        "snapshot_data": history.snapshot_data,
        "created_at": history.created_at.isoformat() if history.created_at else None,
    }


@router.delete("/scenario-history/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario_history(id: int, db: Session = Depends(get_db)):
    history = db.query(ScenarioHistory).filter(ScenarioHistory.id == id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Scenario history not found")
    db.delete(history)
    db.commit()


@router.post("/scenario-history/{id}/replay")
def replay_scenario_history(id: int, db: Session = Depends(get_db)):
    history = db.query(ScenarioHistory).filter(ScenarioHistory.id == id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Scenario history not found")

    if not history.snapshot_data:
        raise HTTPException(status_code=400, detail="No snapshot data available for replay")

    return {
        "message": "Scenario replay started",
        "snapshot_data": history.snapshot_data,
    }


@router.get("/topology-templates")
def get_topology_templates(db: Session = Depends(get_db)):
    templates = db.query(TopologyTemplate).order_by(TopologyTemplate.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "topology_type": t.topology_type,
            "scale": t.scale,
            "components_config": t.components_config,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }
        for t in templates
    ]


@router.post("/topology-templates")
def create_topology_template(data: dict, db: Session = Depends(get_db)):
    template = TopologyTemplate(
        name=data.get("name"),
        description=data.get("description"),
        topology_type=data.get("topology_type"),
        scale=data.get("scale"),
        components_config=data.get("components_config"),
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "topology_type": template.topology_type,
        "scale": template.scale,
        "components_config": template.components_config,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
    }


@router.get("/topology-templates/{id}")
def get_topology_template(id: int, db: Session = Depends(get_db)):
    template = db.query(TopologyTemplate).filter(TopologyTemplate.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Topology template not found")
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "topology_type": template.topology_type,
        "scale": template.scale,
        "components_config": template.components_config,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
    }


@router.delete("/topology-templates/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topology_template(id: int, db: Session = Depends(get_db)):
    template = db.query(TopologyTemplate).filter(TopologyTemplate.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Topology template not found")
    db.delete(template)
    db.commit()


@router.post("/topology-templates/{id}/apply")
def apply_topology_template(id: int, data: dict, db: Session = Depends(get_db)):
    template = db.query(TopologyTemplate).filter(TopologyTemplate.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Topology template not found")

    generator = TopologyGenerator(db)
    try:
        result = generator.generate(
            name=data.get("name", f"从模板创建-{template.name}"),
            topology_type=template.topology_type,
            scale=template.scale,
            ip_prefix=data.get("ip_prefix"),
            description=data.get("description", template.description),
            pushgateway_url=data.get("pushgateway_url"),
            log_path=data.get("log_path"),
            include_components=template.components_config,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
