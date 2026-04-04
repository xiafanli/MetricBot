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
