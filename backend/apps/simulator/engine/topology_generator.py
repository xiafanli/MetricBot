from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from apps.simulator.models import SimulationEnvironment, SimulationComponent, ComponentRelation


class TopologyGenerator:
    TOPOLOGY_CONFIGS = {
        "standard": {
            "name": "标准架构",
            "description": "客户端-负载均衡-应用-缓存-数据库",
            "layers": ["client", "nginx", "app_server", "redis", "mysql"],
        },
        "microservice": {
            "name": "微服务架构",
            "description": "包含网关、消息队列、配置中心的完整微服务架构",
            "layers": ["client", "nginx", "api_gateway", "app_server", "firewall", "redis", "config_center", "mysql", "kafka"],
        },
        "monolithic": {
            "name": "单体架构",
            "description": "简化的单体应用架构",
            "layers": ["client", "nginx", "app_server", "mysql"],
        },
    }

    SCALE_CONFIGS = {
        "small": {
            "client": 1,
            "nginx": 1,
            "app_server": 2,
            "api_gateway": 1,
            "firewall": 1,
            "redis": 1,
            "mysql": 1,
            "kafka": 1,
            "config_center": 1,
        },
        "medium": {
            "client": 2,
            "nginx": 2,
            "app_server": 3,
            "api_gateway": 2,
            "firewall": 2,
            "redis": 2,
            "mysql": 2,
            "kafka": 3,
            "config_center": 1,
        },
        "large": {
            "client": 5,
            "nginx": 3,
            "app_server": 5,
            "api_gateway": 3,
            "firewall": 2,
            "redis": 3,
            "mysql": 3,
            "kafka": 5,
            "config_center": 3,
        },
    }

    IP_RANGES = {
        "client": (10, 19),
        "nginx": (20, 29),
        "firewall_app": (25, 26),
        "app_server": (30, 39),
        "api_gateway": (35, 36),
        "redis": (40, 44),
        "config_center": (45, 45),
        "firewall_db": (55, 56),
        "mysql": (50, 54),
        "kafka": (57, 59),
    }

    COMPONENT_NAMES = {
        "client": "client",
        "nginx": "nginx-lb",
        "app_server": "app-server",
        "api_gateway": "api-gateway",
        "firewall": "firewall",
        "redis": "redis-cache",
        "config_center": "config-center",
        "mysql": "mysql",
        "kafka": "kafka",
    }

    COMPONENT_LAYERS = {
        "client": 1,
        "nginx": 2,
        "app_server": 3,
        "api_gateway": 3,
        "firewall": 3,
        "redis": 4,
        "config_center": 4,
        "mysql": 5,
        "kafka": 5,
    }

    COMPONENT_PORTS = {
        "client": None,
        "nginx": 80,
        "app_server": 8080,
        "api_gateway": 8000,
        "firewall": None,
        "redis": 6379,
        "config_center": 8848,
        "mysql": 3306,
        "kafka": 9092,
    }

    def __init__(self, db: Session):
        self.db = db
        self._ip_cache: Dict[str, int] = {}

    def generate(
        self,
        name: str,
        topology_type: str = "standard",
        scale: str = "medium",
        ip_prefix: str = "192.168.1",
        description: Optional[str] = None,
        pushgateway_url: str = "http://localhost:9091",
        log_path: str = "simulator/logs",
        include_components: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if topology_type not in self.TOPOLOGY_CONFIGS:
            raise ValueError(f"不支持的拓扑类型: {topology_type}")
        if scale not in self.SCALE_CONFIGS:
            raise ValueError(f"不支持的规模: {scale}")

        topology_config = self.TOPOLOGY_CONFIGS[topology_type]
        scale_config = self.SCALE_CONFIGS[scale]

        components_to_create = include_components if include_components else topology_config["layers"]

        env = SimulationEnvironment(
            name=name,
            description=description or f"{topology_config['name']} - {scale}规模",
            pushgateway_url=pushgateway_url,
            log_path=log_path,
            is_active=False,
        )
        self.db.add(env)
        self.db.flush()

        self._ip_cache = {}
        components = self._generate_components(
            env.id, components_to_create, scale_config, ip_prefix
        )
        relations = self._generate_relations(env.id, components, topology_type)

        self.db.commit()
        self.db.refresh(env)

        return {
            "environment": {
                "id": env.id,
                "name": env.name,
                "description": env.description,
                "is_active": env.is_active,
            },
            "components": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.component_type,
                    "ip": c.properties.get("ip") if c.properties else None,
                    "layer": self.COMPONENT_LAYERS.get(c.component_type, 0),
                }
                for c in components
            ],
            "relations": [
                {
                    "id": r.id,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "type": r.relation_type,
                }
                for r in relations
            ],
            "summary": {
                "total_components": len(components),
                "total_relations": len(relations),
                "topology_type": topology_type,
                "scale": scale,
                "ip_prefix": ip_prefix,
            },
        }

    def _generate_components(
        self,
        env_id: int,
        component_types: List[str],
        scale_config: Dict[str, int],
        ip_prefix: str,
    ) -> List[SimulationComponent]:
        components = []

        for component_type in component_types:
            count = scale_config.get(component_type, 1)
            for i in range(count):
                ip = self._allocate_ip(component_type, ip_prefix)
                name = self._generate_name(component_type, i, count)

                properties = {
                    "ip": ip,
                    "port": self.COMPONENT_PORTS.get(component_type),
                    "layer": self.COMPONENT_LAYERS.get(component_type, 0),
                    "os": "linux",
                }

                if component_type == "app_server":
                    properties.update({
                        "jvm_heap_max": 1024,
                        "thread_pool_max": 200,
                        "connection_pool_max": 50,
                    })
                elif component_type == "mysql":
                    properties.update({
                        "is_master": i == 0,
                        "buffer_pool_size": 1024,
                        "max_connections": 100,
                    })
                elif component_type == "redis":
                    properties.update({
                        "max_memory": 256,
                        "max_clients": 100,
                    })
                elif component_type == "kafka":
                    properties.update({
                        "partitions": 10,
                        "replication_factor": 2,
                    })

                component = SimulationComponent(
                    env_id=env_id,
                    component_type=component_type,
                    name=name,
                    properties=properties,
                )
                self.db.add(component)
                components.append(component)

        self.db.flush()
        return components

    def _generate_relations(
        self,
        env_id: int,
        components: List[SimulationComponent],
        topology_type: str,
    ) -> List[ComponentRelation]:
        relations = []
        component_map = {c.component_type: [] for c in components}
        for c in components:
            component_map[c.component_type].append(c)

        for c in component_map.values():
            c.sort(key=lambda x: x.name)

        def create_relation(source: SimulationComponent, target: SimulationComponent, relation_type: str):
            relation = ComponentRelation(
                env_id=env_id,
                source_id=source.id,
                target_id=target.id,
                relation_type=relation_type,
            )
            self.db.add(relation)
            relations.append(relation)

        if "client" in component_map and "nginx" in component_map:
            for client in component_map["client"]:
                for nginx in component_map["nginx"]:
                    create_relation(client, nginx, "connects_to")

        if "nginx" in component_map:
            nginx_list = component_map["nginx"]
            if "api_gateway" in component_map:
                for nginx in nginx_list:
                    for api_gw in component_map["api_gateway"]:
                        create_relation(nginx, api_gw, "routes_to")
            elif "app_server" in component_map:
                for nginx in nginx_list:
                    for app in component_map["app_server"]:
                        create_relation(nginx, app, "routes_to")

        if "api_gateway" in component_map and "app_server" in component_map:
            for api_gw in component_map["api_gateway"]:
                for app in component_map["app_server"]:
                    create_relation(api_gw, app, "routes_to")

        if "firewall" in component_map:
            firewall_list = component_map["firewall"]
            if len(firewall_list) >= 1:
                app_firewall = firewall_list[0]
                for app in component_map.get("app_server", []):
                    create_relation(app, app_firewall, "protected_by")
                for api_gw in component_map.get("api_gateway", []):
                    create_relation(api_gw, app_firewall, "protected_by")

            if len(firewall_list) >= 2:
                db_firewall = firewall_list[1]
                for mysql in component_map.get("mysql", []):
                    create_relation(mysql, db_firewall, "protected_by")

        if "app_server" in component_map:
            for app in component_map["app_server"]:
                if "redis" in component_map:
                    for redis in component_map["redis"]:
                        create_relation(app, redis, "depends_on")

                if "mysql" in component_map:
                    mysql_list = component_map["mysql"]
                    master = mysql_list[0] if mysql_list else None
                    if master:
                        create_relation(app, master, "depends_on")

                if "kafka" in component_map:
                    for kafka in component_map["kafka"]:
                        create_relation(app, kafka, "publishes_to")

                if "config_center" in component_map:
                    for config in component_map["config_center"]:
                        create_relation(app, config, "depends_on")

        if "mysql" in component_map and len(component_map["mysql"]) > 1:
            mysql_list = component_map["mysql"]
            master = mysql_list[0]
            for slave in mysql_list[1:]:
                create_relation(master, slave, "replicates_to")

        self.db.flush()
        return relations

    def _allocate_ip(self, component_type: str, ip_prefix: str) -> str:
        ip_range = self.IP_RANGES.get(component_type, (10, 19))
        cache_key = f"{ip_prefix}_{component_type}"

        if cache_key not in self._ip_cache:
            self._ip_cache[cache_key] = ip_range[0]
        else:
            self._ip_cache[cache_key] += 1
            if self._ip_cache[cache_key] > ip_range[1]:
                self._ip_cache[cache_key] = ip_range[0]

        third_octet = self._ip_cache[cache_key]
        return f"{ip_prefix}.{third_octet}"

    def _generate_name(self, component_type: str, index: int, total: int) -> str:
        base_name = self.COMPONENT_NAMES.get(component_type, component_type)
        if total == 1:
            if component_type == "mysql":
                return f"{base_name}-master"
            return base_name
        else:
            if component_type == "mysql":
                role = "master" if index == 0 else f"slave-{index}"
                return f"{base_name}-{role}"
            return f"{base_name}-{index + 1:02d}"

    def check_ip_conflict(self, ip_prefix: str) -> Dict[str, Any]:
        existing_ips = set()
        components = self.db.query(SimulationComponent).all()
        for c in components:
            if c.properties and "ip" in c.properties:
                existing_ips.add(c.properties["ip"])

        test_ip = f"{ip_prefix}.10.1"
        has_conflict = any(ip.startswith(ip_prefix) for ip in existing_ips)

        return {
            "ip_prefix": ip_prefix,
            "has_conflict": has_conflict,
            "existing_count": len([ip for ip in existing_ips if ip.startswith(ip_prefix)]),
            "message": "IP前缀已存在冲突" if has_conflict else "IP前缀可用",
        }

    def get_topology_types(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": key,
                "name": config["name"],
                "description": config["description"],
                "layers": config["layers"],
            }
            for key, config in self.TOPOLOGY_CONFIGS.items()
        ]

    def get_scales(self) -> List[Dict[str, Any]]:
        return [
            {
                "scale": key,
                "name": {"small": "小型", "medium": "中型", "large": "大型"}.get(key, key),
                "description": {
                    "small": "适合测试和开发环境",
                    "medium": "适合预生产环境",
                    "large": "适合生产环境模拟",
                }.get(key, ""),
                "config": config,
            }
            for key, config in self.SCALE_CONFIGS.items()
        ]

    def get_component_types(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": key,
                "name": self.COMPONENT_NAMES.get(key, key),
                "layer": self.COMPONENT_LAYERS.get(key, 0),
                "port": self.COMPONENT_PORTS.get(key),
            }
            for key in self.COMPONENT_NAMES.keys()
        ]
