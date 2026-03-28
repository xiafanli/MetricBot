from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SimulationEnvironmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    topology_data: Optional[Dict[str, Any]] = None
    pushgateway_url: Optional[str] = Field(None, max_length=255)
    log_path: Optional[str] = Field(None, max_length=255)


class SimulationEnvironmentCreate(SimulationEnvironmentBase):
    pass


class SimulationEnvironmentUpdate(SimulationEnvironmentBase):
    name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class SimulationEnvironmentResponse(SimulationEnvironmentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SimulationComponentBase(BaseModel):
    env_id: int
    component_type: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    properties: Optional[Dict[str, Any]] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class SimulationComponentCreate(SimulationComponentBase):
    pass


class SimulationComponentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    properties: Optional[Dict[str, Any]] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class SimulationComponentResponse(SimulationComponentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ComponentRelationBase(BaseModel):
    env_id: int
    source_id: int
    target_id: int
    relation_type: str = Field(..., max_length=50)


class ComponentRelationCreate(ComponentRelationBase):
    pass


class ComponentRelationResponse(ComponentRelationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MetricTemplateBase(BaseModel):
    component_type: str = Field(..., max_length=50)
    metric_name: str = Field(..., max_length=100)
    metric_type: str = Field(..., max_length=20)
    description: Optional[str] = Field(None, max_length=255)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    base_value: Optional[float] = None
    fluctuation: float = 0.1
    unit: Optional[str] = Field(None, max_length=50)
    labels: Optional[Dict[str, Any]] = None


class MetricTemplateCreate(MetricTemplateBase):
    pass


class MetricTemplateUpdate(MetricTemplateBase):
    component_type: Optional[str] = Field(None, max_length=50)
    metric_name: Optional[str] = Field(None, max_length=100)
    metric_type: Optional[str] = Field(None, max_length=20)


class MetricTemplateResponse(MetricTemplateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LogTemplateBase(BaseModel):
    component_type: str = Field(..., max_length=50)
    log_format: str = Field("log4j", max_length=50)
    log_levels: Optional[Dict[str, Any]] = None
    template: Optional[str] = None
    frequency: int = 10


class LogTemplateCreate(LogTemplateBase):
    pass


class LogTemplateUpdate(LogTemplateBase):
    component_type: Optional[str] = Field(None, max_length=50)


class LogTemplateResponse(LogTemplateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FaultScenarioBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    fault_type: str = Field(..., max_length=50)
    target_component_type: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = None
    probability: float = 0.01
    is_enabled: bool = False


class FaultScenarioCreate(FaultScenarioBase):
    pass


class FaultScenarioUpdate(FaultScenarioBase):
    name: Optional[str] = Field(None, max_length=100)
    fault_type: Optional[str] = Field(None, max_length=50)


class FaultScenarioResponse(FaultScenarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FaultInstanceBase(BaseModel):
    scenario_id: int
    component_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = Field("pending", max_length=20)
    impact_data: Optional[Dict[str, Any]] = None


class FaultInstanceCreate(FaultInstanceBase):
    pass


class FaultInstanceUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)
    impact_data: Optional[Dict[str, Any]] = None


class FaultInstanceResponse(FaultInstanceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PrometheusSyncRequest(BaseModel):
    datasource_id: int


class EnvironmentActivateRequest(BaseModel):
    pushgateway_url: Optional[str] = None
    log_path: Optional[str] = None
