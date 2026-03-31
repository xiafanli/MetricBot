import os
import random
import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from faker import Faker
from sqlalchemy.orm import Session
from apps.simulator.models import (
    SimulationEnvironment,
    SimulationComponent,
    ComponentRelation,
    LogTemplate,
    FaultInstance,
)


class RequestContext:
    def __init__(
        self,
        trace_id: str,
        client_ip: str,
        method: str,
        path: str,
        user_agent: str,
        timestamp: datetime,
    ):
        self.trace_id = trace_id
        self.client_ip = client_ip
        self.method = method
        self.path = path
        self.user_agent = user_agent
        self.timestamp = timestamp
        self.response_time_ms: int = 0
        self.status_code: int = 200
        self.db_query: Optional[str] = None
        self.db_query_time_ms: int = 0
        self.cache_hit: bool = False
        self.error_message: Optional[str] = None


class LogGenerator:
    COMPONENT_LOG_FORMATS = {
        "nginx": "nginx_combined",
        "mysql": "mysql_general",
        "redis": "redis_log",
        "app_server": "log4j",
        "api_gateway": "log4j",
        "client": "access_log",
        "firewall": "syslog",
        "config_center": "log4j",
        "host": "syslog",
    }

    LAYER_ORDER = {
        "client": 0,
        "nginx": 1,
        "load_balancer": 1,
        "api_gateway": 2,
        "app_server": 2,
        "firewall": 2,
        "redis": 3,
        "cache": 3,
        "mysql": 4,
        "database": 4,
        "config_center": 2,
    }

    def __init__(self, db: Session, base_log_path: str = "simulator/logs"):
        self.db = db
        self.base_log_path = base_log_path
        self.fake = Faker()
        self._ensure_directories()

    def _ensure_directories(self):
        directories = [
            os.path.join(self.base_log_path, "nginx"),
            os.path.join(self.base_log_path, "app"),
            os.path.join(self.base_log_path, "database"),
            os.path.join(self.base_log_path, "cache"),
            os.path.join(self.base_log_path, "client"),
            os.path.join(self.base_log_path, "gateway"),
            os.path.join(self.base_log_path, "firewall"),
            os.path.join(self.base_log_path, "config"),
            os.path.join(self.base_log_path, "host"),
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_log_path(self, component: SimulationComponent) -> str:
        type_dir_map = {
            "nginx": "nginx",
            "load_balancer": "nginx",
            "app_server": "app",
            "api_gateway": "gateway",
            "mysql": "database",
            "database": "database",
            "redis": "cache",
            "cache": "cache",
            "client": "client",
            "firewall": "firewall",
            "config_center": "config",
            "host": "host",
        }
        dir_name = type_dir_map.get(component.component_type, "host")
        filename = f"{component.name}.log"
        return os.path.join(self.base_log_path, dir_name, filename)

    def get_component_layer(self, component: SimulationComponent) -> int:
        return self.LAYER_ORDER.get(component.component_type, 99)

    def has_active_fault(self, component: SimulationComponent) -> bool:
        active_faults = self.db.query(FaultInstance).filter(
            FaultInstance.component_id == component.id,
            FaultInstance.status == "active",
        ).count()
        return active_faults > 0

    def get_fault_for_component(self, component: SimulationComponent) -> Optional[FaultInstance]:
        return self.db.query(FaultInstance).filter(
            FaultInstance.component_id == component.id,
            FaultInstance.status == "active",
        ).first()

    def get_downstream_components(self, component: SimulationComponent) -> List[SimulationComponent]:
        relations = self.db.query(ComponentRelation).filter(
            ComponentRelation.source_id == component.id,
        ).all()
        downstream = []
        for rel in relations:
            target = self.db.query(SimulationComponent).filter(
                SimulationComponent.id == rel.target_id
            ).first()
            if target:
                downstream.append(target)
        return downstream

    def get_upstream_components(self, component: SimulationComponent) -> List[SimulationComponent]:
        relations = self.db.query(ComponentRelation).filter(
            ComponentRelation.target_id == component.id,
        ).all()
        upstream = []
        for rel in relations:
            source = self.db.query(SimulationComponent).filter(
                SimulationComponent.id == rel.source_id
            ).first()
            if source:
                upstream.append(source)
        return upstream

    def generate_trace_id(self) -> str:
        return uuid.uuid4().hex[:16].upper()

    def generate_request_context(self) -> RequestContext:
        return RequestContext(
            trace_id=self.generate_trace_id(),
            client_ip=self.fake.ipv4(),
            method=random.choice(["GET", "GET", "GET", "POST", "PUT", "DELETE"]),
            path="/" + "/".join([self.fake.word() for _ in range(random.randint(1, 3))]),
            user_agent=self.fake.user_agent(),
            timestamp=datetime.now(),
        )

    def generate_nginx_log(self, component: SimulationComponent, ctx: RequestContext, fault_active: bool) -> str:
        timestamp = ctx.timestamp.strftime("%d/%b/%Y:%H:%M:%S +0800")
        protocol = "HTTP/1.1"
        size = random.randint(100, 50000)

        if fault_active:
            status_codes = [200, 200, 500, 502, 503, 504, 404]
            ctx.status_code = random.choice(status_codes)
        else:
            ctx.status_code = random.choice([200, 200, 200, 201, 301, 302])

        referer = "-" if random.random() < 0.3 else f'"{self.fake.uri()}"'
        upstream_addr = "-"
        upstream_time = "-"
        request_time = round(ctx.response_time_ms / 1000, 3) if ctx.response_time_ms else round(random.uniform(0.01, 0.5), 3)

        log_line = (
            f'{ctx.client_ip} - - [{timestamp}] "{ctx.method} {ctx.path} {protocol}" '
            f'{ctx.status_code} {size} {referer} "{ctx.user_agent}" '
            f'upstream_addr="{upstream_addr}" upstream_response_time="{upstream_time}" '
            f'request_time="{request_time}" trace_id="{ctx.trace_id}"'
        )
        return log_line

    def generate_log4j_log(self, component: SimulationComponent, ctx: RequestContext, fault_active: bool) -> str:
        levels = {
            "DEBUG": 0.1,
            "INFO": 0.7,
            "WARN": 0.15,
            "ERROR": 0.05,
        }

        if fault_active:
            levels = {
                "DEBUG": 0.05,
                "INFO": 0.3,
                "WARN": 0.35,
                "ERROR": 0.3,
            }

        level = random.choices(list(levels.keys()), weights=list(levels.values()))[0]

        timestamp = ctx.timestamp.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        thread_name = self.fake.word().capitalize() + "-" + str(random.randint(1, 10))
        logger_name = f"com.example.{component.name.replace('-', '.')}"

        messages = {
            "DEBUG": [
                f"[trace:{ctx.trace_id}] Query executed: SELECT * FROM {self.fake.word()}",
                f"[trace:{ctx.trace_id}] Cache lookup for key: {self.fake.uuid4()[:8]}",
                f"[trace:{ctx.trace_id}] Processing request from {ctx.client_ip}",
                f"[trace:{ctx.trace_id}] Session attributes: {{userId={random.randint(1000, 9999)}}}",
            ],
            "INFO": [
                f"[trace:{ctx.trace_id}] Request {ctx.method} {ctx.path} processed in {ctx.response_time_ms}ms",
                f"[trace:{ctx.trace_id}] User {self.fake.user_name()} logged in successfully",
                f"[trace:{ctx.trace_id}] Service {self.fake.word()} started",
                f"[trace:{ctx.trace_id}] API response: status={ctx.status_code}, size={random.randint(100, 5000)}bytes",
            ],
            "WARN": [
                f"[trace:{ctx.trace_id}] Cache miss for key: {self.fake.uuid4()[:8]}",
                f"[trace:{ctx.trace_id}] Slow query detected: {ctx.db_query_time_ms}ms - {ctx.db_query or 'SELECT ...'}",
                f"[trace:{ctx.trace_id}] Connection pool usage high: {random.randint(70, 90)}%",
                f"[trace:{ctx.trace_id}] Memory usage warning: {random.randint(70, 90)}%",
            ],
            "ERROR": [
                f"[trace:{ctx.trace_id}] NullPointerException at line {random.randint(1, 100)}",
                f"[trace:{ctx.trace_id}] Database connection timeout after {random.randint(5, 30)}s",
                f"[trace:{ctx.trace_id}] Failed to process request: {ctx.error_message or self.fake.sentence()}",
                f"[trace:{ctx.trace_id}] OutOfMemoryError: Java heap space",
                f"[trace:{ctx.trace_id}] GC overhead limit exceeded",
            ],
        }

        message = random.choice(messages[level])
        return f"{timestamp} {level:5} [{thread_name}] {logger_name} - {message}"

    def generate_mysql_general_log(self, component: SimulationComponent, ctx: RequestContext, fault_active: bool) -> str:
        timestamp = ctx.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        thread_id = random.randint(1000, 9999)

        query_types = [
            ("Query", f"SELECT * FROM {self.fake.word()} WHERE id = {random.randint(1, 1000)}"),
            ("Query", f"UPDATE {self.fake.word()} SET status = 'active' WHERE id = {random.randint(1, 1000)}"),
            ("Query", f"INSERT INTO {self.fake.word()} (name, created_at) VALUES ('{self.fake.word()}', NOW())"),
            ("Connect", f"root@localhost on {self.fake.word()} using TCP/IP"),
            ("Quit", ""),
        ]

        if fault_active:
            query_types.extend([
                ("Query", f"SELECT * FROM {self.fake.word()} WHERE name LIKE '%{self.fake.word()}%' -- slow query"),
                ("Query", f"LOCK TABLES {self.fake.word()} WRITE"),
            ])

        command, argument = random.choice(query_types)

        log_line = f"{timestamp}\t{thread_id}\t{command}\t\t{argument}  /* trace_id: {ctx.trace_id} */"
        return log_line

    def generate_mysql_slow_log(self, component: SimulationComponent, ctx: RequestContext, fault_active: bool) -> str:
        query_time = round(random.uniform(1.0, 10.0), 6) if fault_active else round(random.uniform(0.5, 3.0), 6)
        lock_time = round(random.uniform(0.0, 0.1), 6)
        rows_sent = random.randint(1, 1000)
        rows_examined = random.randint(1000, 100000)

        timestamp = ctx.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        query = ctx.db_query or f"SELECT * FROM {self.fake.word()} WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)"

        log_lines = [
            f"# Time: {timestamp}",
            f"# User@Host: root[root] @ localhost []  Id: {random.randint(1000, 9999)}",
            f"# Query_time: {query_time}  Lock_time: {lock_time}  Rows_sent: {rows_sent}  Rows_examined: {rows_examined}",
            f"SET timestamp={int(ctx.timestamp.timestamp())};",
            f"{query};  /* trace_id: {ctx.trace_id} */",
            "",
        ]
        return "\n".join(log_lines)

    def generate_redis_log(self, component: SimulationComponent, ctx: RequestContext, fault_active: bool) -> str:
        timestamp = ctx.timestamp.strftime("%d %b %Y %H:%M:%S.%f")[:-3]
        pid = random.randint(1000, 9999)

        if fault_active:
            messages = [
                f"[{pid}] SLOW LOG: {random.randint(10, 100)}ms command: GET {self.fake.uuid4()[:8]}",
                f"[{pid}] WARNING: overcommit_memory is set to 0",
                f"[{pid}] WARNING: you have Transparent Huge Pages (THP) support enabled",
                f"[{pid}] Connection refused: max clients reached",
            ]
        else:
            messages = [
                f"[{pid}] Accepted {ctx.client_ip}:{random.randint(30000, 60000)}",
                f"[{pid}] DB loaded from disk: {random.uniform(0.01, 0.5):.3f} seconds",
                f"[{pid}] Ready to accept connections  /* trace_id: {ctx.trace_id} */",
                f"[{pid}] Client closed connection  /* trace_id: {ctx.trace_id} */",
            ]

        log_line = f"{timestamp} {random.choice(messages)}"
        return log_line

    def generate_client_log(self, component: SimulationComponent, ctx: RequestContext, fault_active: bool) -> str:
        timestamp = ctx.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if fault_active:
            messages = [
                f"[ERROR] [{ctx.trace_id}] Request failed: Connection timeout after {random.randint(5, 30)}s",
                f"[ERROR] [{ctx.trace_id}] Request failed: HTTP {random.choice([500, 502, 503, 504])}",
                f"[WARN]  [{ctx.trace_id}] Retry attempt {random.randint(1, 3)} for {ctx.method} {ctx.path}",
            ]
        else:
            messages = [
                f"[INFO]  [{ctx.trace_id}] Request {ctx.method} {ctx.path} -> {ctx.status_code} ({ctx.response_time_ms}ms)",
                f"[INFO]  [{ctx.trace_id}] Session started for user {self.fake.user_name()}",
                f"[DEBUG] [{ctx.trace_id}] Response headers: content-type=application/json",
            ]

        return f"{timestamp} {random.choice(messages)}"

    def generate_firewall_log(self, component: SimulationComponent, ctx: RequestContext, fault_active: bool) -> str:
        timestamp = ctx.timestamp.strftime("%b %d %H:%M:%S")
        hostname = component.name

        if fault_active:
            actions = ["BLOCK", "DROP", "REJECT"]
            action = random.choice(actions)
            messages = [
                f"{action}: IN=eth0 OUT= SRC={ctx.client_ip} DST={self.fake.ipv4()} PROTO=TCP SPT={random.randint(30000, 60000)} DPT={random.choice([80, 443, 3306, 6379])}",
                f"RATE_LIMIT: {ctx.client_ip} exceeded connection limit",
            ]
        else:
            actions = ["ACCEPT", "PASS"]
            action = random.choice(actions)
            messages = [
                f"{action}: IN=eth0 OUT= SRC={ctx.client_ip} DST={self.fake.ipv4()} PROTO=TCP SPT={random.randint(30000, 60000)} DPT={random.choice([80, 443])}  /* trace_id: {ctx.trace_id} */",
                f"ALLOW: {ctx.client_ip} -> {ctx.path}",
            ]

        return f"{timestamp} {hostname} kernel: [{action}] {random.choice(messages)}"

    def generate_log_for_component(
        self,
        component: SimulationComponent,
        ctx: RequestContext,
        fault_active: bool,
    ) -> str:
        log_format = self.COMPONENT_LOG_FORMATS.get(component.component_type, "log4j")

        generators = {
            "nginx_combined": self.generate_nginx_log,
            "log4j": self.generate_log4j_log,
            "mysql_general": self.generate_mysql_general_log,
            "mysql_slow": self.generate_mysql_slow_log,
            "redis_log": self.generate_redis_log,
            "access_log": self.generate_client_log,
            "syslog": self.generate_firewall_log,
        }

        generator = generators.get(log_format, self.generate_log4j_log)
        return generator(component, ctx, fault_active)

    def simulate_request_chain(
        self,
        components: List[SimulationComponent],
        start_component: SimulationComponent,
        ctx: RequestContext,
        fault_map: Dict[int, bool],
        logs: List[Tuple[SimulationComponent, str]],
    ):
        downstream = self.get_downstream_components(start_component)

        if start_component.component_type in ["nginx", "load_balancer"]:
            if not downstream:
                return
            target = random.choice(downstream)
            ctx.response_time_ms = random.randint(10, 100)
            fault_active = fault_map.get(start_component.id, False)
            log_line = self.generate_log_for_component(start_component, ctx, fault_active)
            logs.append((start_component, log_line))
            self.simulate_request_chain(components, target, ctx, fault_map, logs)

        elif start_component.component_type in ["app_server", "api_gateway"]:
            fault_active = fault_map.get(start_component.id, False)
            ctx.response_time_ms += random.randint(20, 200)

            if random.random() < 0.3:
                ctx.db_query = f"SELECT * FROM {self.fake.word()} WHERE id = {random.randint(1, 1000)}"
                ctx.db_query_time_ms = random.randint(5, 50)
                ctx.response_time_ms += ctx.db_query_time_ms

            if random.random() < 0.2:
                ctx.cache_hit = True

            log_line = self.generate_log_for_component(start_component, ctx, fault_active)
            logs.append((start_component, log_line))

            for target in downstream:
                if target.component_type in ["mysql", "database", "redis", "cache"]:
                    self.simulate_request_chain(components, target, ctx, fault_map, logs)

        elif start_component.component_type in ["mysql", "database"]:
            fault_active = fault_map.get(start_component.id, False)
            log_line = self.generate_log_for_component(start_component, ctx, fault_active)
            logs.append((start_component, log_line))

        elif start_component.component_type in ["redis", "cache"]:
            fault_active = fault_map.get(start_component.id, False)
            log_line = self.generate_log_for_component(start_component, ctx, fault_active)
            logs.append((start_component, log_line))

        elif start_component.component_type in ["client"]:
            if not downstream:
                return
            for target in downstream:
                self.simulate_request_chain(components, target, ctx, fault_map, logs)

        else:
            for target in downstream:
                self.simulate_request_chain(components, target, ctx, fault_map, logs)

    def generate_and_write(self, env_id: int):
        env = self.db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
        if not env:
            return

        components = self.db.query(SimulationComponent).filter(SimulationComponent.env_id == env_id).all()
        if not components:
            return

        fault_map = {}
        for comp in components:
            fault_map[comp.id] = self.has_active_fault(comp)

        entry_points = [c for c in components if c.component_type in ["nginx", "load_balancer", "client"]]
        if not entry_points:
            entry_points = [c for c in components if self.get_component_layer(c) == 0]
        if not entry_points:
            entry_points = [components[0]]

        templates = self.db.query(LogTemplate).all()
        template_map = {}
        for template in templates:
            if template.component_type not in template_map:
                template_map[template.component_type] = template

        all_logs: Dict[int, List[str]] = {comp.id: [] for comp in components}

        request_count = 5
        for template in templates:
            if template.component_type in ["nginx", "load_balancer", "client"]:
                request_count = max(request_count, template.frequency)
                break

        for _ in range(request_count):
            ctx = self.generate_request_context()
            entry = random.choice(entry_points)

            logs: List[Tuple[SimulationComponent, str]] = []
            self.simulate_request_chain(components, entry, ctx, fault_map, logs)

            for comp, log_line in logs:
                all_logs[comp.id].append(log_line)

        for comp in components:
            if comp.id not in all_logs or not all_logs[comp.id]:
                continue

            log_path = self.get_log_path(comp)
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    for line in all_logs[comp.id]:
                        f.write(line + "\n")
            except Exception as e:
                print(f"Failed to write log for {comp.name}: {e}")
