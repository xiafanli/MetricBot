import os
import random
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from faker import Faker
from sqlalchemy.orm import Session
from apps.simulator.models import SimulationEnvironment, SimulationComponent, LogTemplate, FaultInstance


class LogGenerator:
    def __init__(self, db: Session, base_log_path: str = "simulator/logs"):
        self.db = db
        self.base_log_path = base_log_path
        self.fake = Faker()
        self._ensure_directories()

    def _ensure_directories(self):
        directories = [
            os.path.join(self.base_log_path, "java"),
            os.path.join(self.base_log_path, "nginx"),
            os.path.join(self.base_log_path, "database"),
            os.path.join(self.base_log_path, "host"),
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_log_path(self, component: SimulationComponent) -> str:
        type_dir_map = {
            "java_app": "java",
            "nginx": "nginx",
            "database": "database",
            "host": "host",
            "container": "host",
        }
        dir_name = type_dir_map.get(component.component_type, "host")
        filename = f"{component.name}.log"
        return os.path.join(self.base_log_path, dir_name, filename)

    def has_active_fault(self, component: SimulationComponent) -> bool:
        active_faults = self.db.query(FaultInstance).filter(
            FaultInstance.component_id == component.id,
            FaultInstance.status == "active",
        ).count()
        return active_faults > 0

    def generate_log4j(self, component: SimulationComponent, template: LogTemplate, fault_active: bool) -> str:
        levels = template.log_levels or {
            "DEBUG": 0.1,
            "INFO": 0.7,
            "WARN": 0.15,
            "ERROR": 0.05,
        }

        if fault_active:
            levels["ERROR"] = 0.3
            levels["WARN"] = 0.3
            levels["INFO"] = 0.3
            levels["DEBUG"] = 0.1

        level = random.choices(list(levels.keys()), weights=list(levels.values()))[0]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        thread_name = self.fake.word().capitalize() + "-" + str(random.randint(1, 10))
        logger_name = f"com.example.{component.name.replace('-', '.')}"

        messages = {
            "DEBUG": [
                f"Query executed: SELECT * FROM {self.fake.word()}",
                f"Cache lookup for key: {self.fake.uuid4()}",
                f"Processing request from {self.fake.ipv4()}",
            ],
            "INFO": [
                f"Request processed in {random.randint(10, 500)}ms",
                f"User {self.fake.user_name()} logged in",
                f"Service {self.fake.word()} started successfully",
                f"Scheduled job {self.fake.word()} executed",
            ],
            "WARN": [
                f"Cache miss for key: {self.fake.uuid4()}",
                f"Slow query detected: {random.randint(1000, 5000)}ms",
                f"Connection pool usage: {random.randint(70, 90)}%",
                f"High memory usage: {random.randint(70, 90)}%",
            ],
            "ERROR": [
                f"NullPointerException at line {random.randint(1, 100)}",
                f"Database connection timeout after {random.randint(5, 30)}s",
                f"Failed to process request: {self.fake.sentence()}",
                f"Out Of Memory Error (OOM)",
                f"GC overhead limit exceeded",
            ],
        }

        message = random.choice(messages[level])

        return f"{timestamp} {level:5} [{thread_name}] {logger_name} - {message}"

    def generate_nginx(self, component: SimulationComponent, template: LogTemplate, fault_active: bool) -> str:
        ip = self.fake.ipv4()
        timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0800")

        methods = ["GET", "POST", "PUT", "DELETE"]
        method = random.choice(methods)
        path = "/" + "/".join([self.fake.word() for _ in range(random.randint(1, 3))])
        protocol = "HTTP/1.1"

        if fault_active:
            status_codes = [200, 200, 500, 502, 503, 504, 404, 403]
        else:
            status_codes = [200, 200, 200, 201, 301, 302, 404]
        status = random.choice(status_codes)

        size = random.randint(100, 10000)
        referer = "-" if random.random() < 0.3 else f'"{self.fake.uri()}"'
        user_agent = f'"{self.fake.user_agent()}"'

        return f'{ip} - - [{timestamp}] "{method} {path} {protocol}" {status} {size} {referer} {user_agent}'

    def generate_log_line(self, component: SimulationComponent, template: LogTemplate, fault_active: bool) -> str:
        if template.log_format == "log4j":
            return self.generate_log4j(component, template, fault_active)
        elif template.log_format == "nginx":
            return self.generate_nginx(component, template, fault_active)
        else:
            return self.generate_log4j(component, template, fault_active)

    def generate_and_write(self, env_id: int):
        env = self.db.query(SimulationEnvironment).filter(SimulationEnvironment.id == env_id).first()
        if not env:
            return

        components = self.db.query(SimulationComponent).filter(SimulationComponent.env_id == env_id).all()
        templates = self.db.query(LogTemplate).all()

        template_map = {}
        for template in templates:
            if template.component_type not in template_map:
                template_map[template.component_type] = []
            template_map[template.component_type].append(template)

        for component in components:
            fault_active = self.has_active_fault(component)
            component_templates = template_map.get(component.component_type, [])

            if not component_templates:
                continue

            template = component_templates[0]
            log_path = self.get_log_path(component)

            lines = []
            for _ in range(template.frequency):
                line = self.generate_log_line(component, template, fault_active)
                lines.append(line)

            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    for line in lines:
                        f.write(line + "\n")
            except Exception as e:
                print(f"Failed to write log: {e}")
