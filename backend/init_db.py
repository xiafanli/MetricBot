import os
import json
from dotenv import load_dotenv
from common.core.database import engine, Base, SessionLocal
from apps.auth.models import User
from apps.auth.security import get_password_hash
from apps.host.models import Host, HostRelation
from apps.simulator.models import MetricTemplate, LogTemplate, FaultScenario

load_dotenv()


def init_db():
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")
    
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("默认管理员用户创建成功！")
            print("用户名: admin")
            print("密码: admin123")
        else:
            print("管理员用户已存在，跳过创建。")
        
        # 添加 Demo 主机数据
        existing_hosts = db.query(Host).count()
        if existing_hosts == 0:
            print("\n正在添加 Demo 主机数据...")
            
            host1 = Host(
                name="prod-web-01",
                ip="192.168.1.10",
                hostname="prod-web-01.example.com",
                os="Ubuntu",
                os_version="22.04 LTS",
                cpu_cores=8,
                memory_gb=16.0,
                disk_gb=200.0,
                tags=json.dumps(["web", "production", "nginx"]),
                source="manual",
                from_type="manual",
                from_name="demo",
                enabled=True
            )
            
            host2 = Host(
                name="prod-db-01",
                ip="192.168.1.20",
                hostname="prod-db-01.example.com",
                os="CentOS",
                os_version="7.9",
                cpu_cores=16,
                memory_gb=64.0,
                disk_gb=1000.0,
                tags=json.dumps(["database", "production", "mysql"]),
                source="manual",
                from_type="manual",
                from_name="demo",
                enabled=True
            )
            
            host3 = Host(
                name="prod-redis-01",
                ip="192.168.1.30",
                hostname="prod-redis-01.example.com",
                os="Debian",
                os_version="11",
                cpu_cores=4,
                memory_gb=32.0,
                disk_gb=100.0,
                tags=json.dumps(["cache", "production", "redis"]),
                source="manual",
                from_type="manual",
                from_name="demo",
                enabled=True
            )
            
            db.add_all([host1, host2, host3])
            db.commit()
            print("Demo 主机数据创建成功！")
            
            # 添加 Demo 关系数据
            print("\n正在添加 Demo 关系数据...")
            
            rel1 = HostRelation(
                source_host_id=host1.id,
                target_host_id=host2.id,
                relation_type="depends_on",
                description="Web 服务器依赖数据库",
                source="manual"
            )
            
            rel2 = HostRelation(
                source_host_id=host1.id,
                target_host_id=host3.id,
                relation_type="calls",
                description="Web 服务器调用 Redis 缓存",
                source="manual"
            )
            
            db.add_all([rel1, rel2])
            db.commit()
            print("Demo 关系数据创建成功！")
        else:
            print("Demo 数据已存在，跳过创建。")
        
        # 添加模拟器默认数据
        if db.query(MetricTemplate).count() == 0:
            print("\n正在添加模拟器默认指标模板...")
            default_metrics = [
                MetricTemplate(component_type="host", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="host", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=60, fluctuation=0.1, unit="%"),
                MetricTemplate(component_type="host", metric_name="disk_usage", metric_type="gauge", description="磁盘使用率", min_value=0, max_value=100, base_value=40, fluctuation=0.05, unit="%"),
                MetricTemplate(component_type="host", metric_name="network_in", metric_type="counter", description="入站网络流量", min_value=0, max_value=10000, base_value=1000, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="host", metric_name="network_out", metric_type="counter", description="出站网络流量", min_value=0, max_value=10000, base_value=800, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="java_app", metric_name="request_count", metric_type="counter", description="请求数", min_value=0, max_value=1000, base_value=100, fluctuation=0.2),
                MetricTemplate(component_type="java_app", metric_name="error_rate", metric_type="gauge", description="错误率", min_value=0, max_value=100, base_value=1, fluctuation=0.5, unit="%"),
                MetricTemplate(component_type="java_app", metric_name="response_time", metric_type="gauge", description="响应时间", min_value=10, max_value=500, base_value=50, fluctuation=0.3, unit="ms"),
                MetricTemplate(component_type="java_app", metric_name="jvm_heap_used", metric_type="gauge", description="JVM堆内存使用", min_value=0, max_value=2048, base_value=512, fluctuation=0.15, unit="MB"),
                MetricTemplate(component_type="java_app", metric_name="jvm_gc_count", metric_type="counter", description="JVM GC次数", min_value=0, max_value=100, base_value=5, fluctuation=0.4),
                MetricTemplate(component_type="database", metric_name="connection_count", metric_type="gauge", description="连接数", min_value=0, max_value=100, base_value=20, fluctuation=0.1),
                MetricTemplate(component_type="database", metric_name="query_response_time", metric_type="gauge", description="查询响应时间", min_value=1, max_value=1000, base_value=10, fluctuation=0.5, unit="ms"),
                MetricTemplate(component_type="database", metric_name="cache_hit_rate", metric_type="gauge", description="缓存命中率", min_value=0, max_value=100, base_value=90, fluctuation=0.05, unit="%"),
                MetricTemplate(component_type="database", metric_name="lock_wait_time", metric_type="gauge", description="锁等待时间", min_value=0, max_value=1000, base_value=5, fluctuation=0.8, unit="ms"),
                MetricTemplate(component_type="nginx", metric_name="request_throughput", metric_type="counter", description="请求吞吐量", min_value=0, max_value=2000, base_value=200, fluctuation=0.25),
                MetricTemplate(component_type="nginx", metric_name="connection_count", metric_type="gauge", description="连接数", min_value=0, max_value=500, base_value=50, fluctuation=0.15),
                MetricTemplate(component_type="nginx", metric_name="cache_hit_rate", metric_type="gauge", description="缓存命中率", min_value=0, max_value=100, base_value=80, fluctuation=0.1, unit="%"),
            ]
            db.add_all(default_metrics)
            db.commit()
            print("模拟器默认指标模板创建成功！")

        if db.query(LogTemplate).count() == 0:
            print("\n正在添加模拟器默认日志模板...")
            default_logs = [
                LogTemplate(component_type="host", log_format="log4j", frequency=5),
                LogTemplate(component_type="java_app", log_format="log4j", frequency=10),
                LogTemplate(component_type="database", log_format="log4j", frequency=8),
                LogTemplate(component_type="nginx", log_format="nginx", frequency=15),
            ]
            db.add_all(default_logs)
            db.commit()
            print("模拟器默认日志模板创建成功！")

        if db.query(FaultScenario).count() == 0:
            print("\n正在添加模拟器默认故障场景...")
            default_faults = [
                FaultScenario(
                    name="CPU 过载",
                    fault_type="host_cpu_overload",
                    target_component_type="host",
                    config={"duration_minutes": 10, "impact": {"cpu_usage": 3.0, "response_time": 2.0}},
                    probability=0.01,
                    is_enabled=True,
                ),
                FaultScenario(
                    name="内存泄漏",
                    fault_type="java_memory_leak",
                    target_component_type="java_app",
                    config={"duration_minutes": 15, "impact": {"memory_usage": 2.0, "error_rate": 3.0}},
                    probability=0.005,
                    is_enabled=True,
                ),
                FaultScenario(
                    name="慢查询",
                    fault_type="database_slow_query",
                    target_component_type="database",
                    config={"duration_minutes": 8, "impact": {"response_time": 10.0, "error_rate": 2.0}},
                    probability=0.008,
                    is_enabled=True,
                ),
                FaultScenario(
                    name="GC 异常",
                    fault_type="java_gc_overhead",
                    target_component_type="java_app",
                    config={"duration_minutes": 5, "impact": {"response_time": 3.0, "error_rate": 2.0}},
                    probability=0.006,
                    is_enabled=True,
                ),
                FaultScenario(
                    name="网络延迟",
                    fault_type="host_network_latency",
                    target_component_type="host",
                    config={"duration_minutes": 7, "impact": {"response_time": 2.0, "error_rate": 5.0}},
                    probability=0.007,
                    is_enabled=True,
                ),
            ]
            db.add_all(default_faults)
            db.commit()
            print("模拟器默认故障场景创建成功！")
            
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
