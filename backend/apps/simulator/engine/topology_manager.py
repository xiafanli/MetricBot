import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from apps.simulator.models import SimulationEnvironment, SimulationComponent, ComponentRelation
from apps.host.models import Host, HostRelation
from apps.host.schemas import HostCreate, HostRelationCreate


class TopologyManager:
    def __init__(self, db: Session):
        self.db = db

    def sync_to_hosts(self, env_id: int) -> Dict[str, Any]:
        env = self.db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
        if not env:
            raise ValueError(f"Environment {env_id} not found")

        components = self.db.query(SimulationComponent).filter(SimulationComponent.env_id == env_id).all()
        relations = self.db.query(ComponentRelation).filter(ComponentRelation.env_id == env_id).all()

        host_map = {}
        imported_hosts = []
        imported_relations = []

        for component in components:
            host_data = HostCreate(
                name=component.name,
                ip=component.properties.get("ip", "127.0.0.1") if component.properties else "127.0.0.1",
                hostname=component.name,
                os=component.properties.get("os", "linux") if component.properties else "linux",
                os_version=component.properties.get("os_version") if component.properties else None,
                cpu_cores=component.properties.get("cpu_cores") if component.properties else None,
                memory_gb=component.properties.get("memory_gb") if component.properties else None,
                disk_gb=component.properties.get("disk_gb") if component.properties else None,
                from_type="simulator",
                from_name=f"env_{env_id}",
                tags=[component.component_type],
            )

            existing_host = self.db.query(Host).filter(Host.from_type == "simulator", Host.from_name == f"env_{env_id}", Host.name == component.name).first()

            if existing_host:
                for field, value in host_data.model_dump(exclude_unset=True).items():
                    setattr(existing_host, field, value)
                host = existing_host
            else:
                host = Host(**host_data.model_dump())
                self.db.add(host)

            self.db.flush()
            host_map[component.id] = host.id
            imported_hosts.append({
                "id": host.id,
                "name": host.name,
                "component_id": component.id,
            })

        for relation in relations:
            source_host_id = host_map.get(relation.source_id)
            target_host_id = host_map.get(relation.target_id)

            if source_host_id and target_host_id:
                relation_data = HostRelationCreate(
                    source_id=source_host_id,
                    target_id=target_host_id,
                    relation_type=relation.relation_type,
                    description=f"From simulation environment {env_id}",
                )

                existing_relation = self.db.query(HostRelation).filter(
                    HostRelation.source_id == source_host_id,
                    HostRelation.target_id == target_host_id,
                ).first()

                if existing_relation:
                    existing_relation.relation_type = relation_data.relation_type
                    existing_relation.description = relation_data.description
                else:
                    hr = HostRelation(**relation_data.model_dump())
                    self.db.add(hr)

                imported_relations.append({
                    "source_component_id": relation.source_id,
                    "target_component_id": relation.target_id,
                    "source_host_id": source_host_id,
                    "target_host_id": target_host_id,
                })

        self.db.commit()

        return {
            "imported_hosts": imported_hosts,
            "imported_relations": imported_relations,
        }
