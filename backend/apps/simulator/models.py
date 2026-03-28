from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from common.core.database import Base


class SimulationEnvironment(Base):
    __tablename__ = "simulation_environments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    topology_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=False)
    pushgateway_url = Column(String(255), nullable=True)
    log_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    components = relationship("SimulationComponent", back_populates="environment", cascade="all, delete-orphan")
    relations = relationship("ComponentRelation", back_populates="environment", cascade="all, delete-orphan")


class SimulationComponent(Base):
    __tablename__ = "simulation_components"

    id = Column(Integer, primary_key=True, index=True)
    env_id = Column(Integer, ForeignKey("simulation_environments.id"), nullable=False)
    component_type = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    properties = Column(JSON, nullable=True)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    environment = relationship("SimulationEnvironment", back_populates="components")
    source_relations = relationship("ComponentRelation", foreign_keys="ComponentRelation.source_id", back_populates="source", cascade="all, delete-orphan")
    target_relations = relationship("ComponentRelation", foreign_keys="ComponentRelation.target_id", back_populates="target", cascade="all, delete-orphan")
    fault_instances = relationship("FaultInstance", back_populates="component", cascade="all, delete-orphan")


class ComponentRelation(Base):
    __tablename__ = "component_relations"

    id = Column(Integer, primary_key=True, index=True)
    env_id = Column(Integer, ForeignKey("simulation_environments.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("simulation_components.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("simulation_components.id"), nullable=False)
    relation_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    environment = relationship("SimulationEnvironment", back_populates="relations")
    source = relationship("SimulationComponent", foreign_keys=[source_id], back_populates="source_relations")
    target = relationship("SimulationComponent", foreign_keys=[target_id], back_populates="target_relations")


class MetricTemplate(Base):
    __tablename__ = "metric_templates"

    id = Column(Integer, primary_key=True, index=True)
    component_type = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(20), nullable=False)
    description = Column(String(255), nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    base_value = Column(Float, nullable=True)
    fluctuation = Column(Float, default=0.1)
    unit = Column(String(50), nullable=True)
    labels = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LogTemplate(Base):
    __tablename__ = "log_templates"

    id = Column(Integer, primary_key=True, index=True)
    component_type = Column(String(50), nullable=False)
    log_format = Column(String(50), default="log4j")
    log_levels = Column(JSON, nullable=True)
    template = Column(Text, nullable=True)
    frequency = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FaultScenario(Base):
    __tablename__ = "fault_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    fault_type = Column(String(50), nullable=False)
    target_component_type = Column(String(50), nullable=True)
    config = Column(JSON, nullable=True)
    probability = Column(Float, default=0.01)
    is_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fault_instances = relationship("FaultInstance", back_populates="scenario", cascade="all, delete-orphan")


class FaultInstance(Base):
    __tablename__ = "fault_instances"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("fault_scenarios.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("simulation_components.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="pending")
    impact_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scenario = relationship("FaultScenario", back_populates="fault_instances")
    component = relationship("SimulationComponent", back_populates="fault_instances")
