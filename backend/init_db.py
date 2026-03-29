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
                MetricTemplate(component_type="host", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="host", metric_name="disk_usage", metric_type="gauge", description="磁盘使用率", min_value=0, max_value=100, base_value=40, fluctuation=0.05, unit="%"),
                MetricTemplate(component_type="host", metric_name="network_in_bytes", metric_type="counter", description="入站网络流量", min_value=0, max_value=10000, base_value=1000, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="host", metric_name="network_out_bytes", metric_type="counter", description="出站网络流量", min_value=0, max_value=10000, base_value=800, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="host", metric_name="disk_read_bytes", metric_type="counter", description="磁盘读取速率", min_value=0, max_value=5000, base_value=500, fluctuation=0.2, unit="KB/s"),
                MetricTemplate(component_type="host", metric_name="disk_write_bytes", metric_type="counter", description="磁盘写入速率", min_value=0, max_value=5000, base_value=300, fluctuation=0.2, unit="KB/s"),

                MetricTemplate(component_type="client", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="client", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="client", metric_name="request_count", metric_type="counter", description="请求总数", min_value=0, max_value=500, base_value=100, fluctuation=0.3, unit="次/s"),
                MetricTemplate(component_type="client", metric_name="request_success_rate", metric_type="gauge", description="请求成功率", min_value=0, max_value=100, base_value=99, fluctuation=0.02, unit="%"),
                MetricTemplate(component_type="client", metric_name="response_time_avg", metric_type="gauge", description="平均响应时间", min_value=10, max_value=500, base_value=100, fluctuation=0.3, unit="ms"),
                MetricTemplate(component_type="client", metric_name="active_sessions", metric_type="gauge", description="活跃会话数", min_value=0, max_value=200, base_value=50, fluctuation=0.2, unit="个"),

                MetricTemplate(component_type="nginx", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="nginx", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="nginx", metric_name="connections_active", metric_type="gauge", description="活跃连接数", min_value=0, max_value=500, base_value=100, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="nginx", metric_name="connections_reading", metric_type="gauge", description="读取中连接", min_value=0, max_value=100, base_value=10, fluctuation=0.3, unit="个"),
                MetricTemplate(component_type="nginx", metric_name="connections_writing", metric_type="gauge", description="写入中连接", min_value=0, max_value=100, base_value=20, fluctuation=0.3, unit="个"),
                MetricTemplate(component_type="nginx", metric_name="connections_waiting", metric_type="gauge", description="等待中连接", min_value=0, max_value=200, base_value=50, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="nginx", metric_name="request_rate", metric_type="counter", description="请求速率", min_value=0, max_value=1000, base_value=200, fluctuation=0.25, unit="次/s"),
                MetricTemplate(component_type="nginx", metric_name="upstream_response_time", metric_type="gauge", description="上游响应时间", min_value=1, max_value=500, base_value=50, fluctuation=0.3, unit="ms"),
                MetricTemplate(component_type="nginx", metric_name="cache_hit_rate", metric_type="gauge", description="缓存命中率", min_value=0, max_value=100, base_value=80, fluctuation=0.1, unit="%"),
                MetricTemplate(component_type="nginx", metric_name="ssl_handshake_rate", metric_type="counter", description="SSL握手速率", min_value=0, max_value=200, base_value=50, fluctuation=0.2, unit="次/s"),

                MetricTemplate(component_type="app_server", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="app_server", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="app_server", metric_name="request_count", metric_type="counter", description="请求数", min_value=0, max_value=1000, base_value=150, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="app_server", metric_name="request_duration", metric_type="gauge", description="请求耗时", min_value=1, max_value=500, base_value=50, fluctuation=0.3, unit="ms"),
                MetricTemplate(component_type="app_server", metric_name="error_count", metric_type="counter", description="错误数", min_value=0, max_value=50, base_value=1, fluctuation=0.5, unit="次/s"),
                MetricTemplate(component_type="app_server", metric_name="error_rate", metric_type="gauge", description="错误率", min_value=0, max_value=100, base_value=1, fluctuation=0.5, unit="%"),
                MetricTemplate(component_type="app_server", metric_name="jvm_heap_used", metric_type="gauge", description="JVM堆内存使用", min_value=0, max_value=2048, base_value=512, fluctuation=0.15, unit="MB"),
                MetricTemplate(component_type="app_server", metric_name="jvm_heap_max", metric_type="gauge", description="JVM堆内存最大值", min_value=0, max_value=4096, base_value=1024, fluctuation=0, unit="MB"),
                MetricTemplate(component_type="app_server", metric_name="jvm_heap_usage", metric_type="gauge", description="JVM堆内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="app_server", metric_name="jvm_gc_pause_seconds", metric_type="gauge", description="GC暂停时间", min_value=0, max_value=1, base_value=0.1, fluctuation=0.5, unit="s"),
                MetricTemplate(component_type="app_server", metric_name="jvm_gc_count", metric_type="counter", description="GC次数", min_value=0, max_value=50, base_value=5, fluctuation=0.3, unit="次"),
                MetricTemplate(component_type="app_server", metric_name="jvm_threads_live", metric_type="gauge", description="活跃线程数", min_value=0, max_value=500, base_value=100, fluctuation=0.1, unit="个"),
                MetricTemplate(component_type="app_server", metric_name="jvm_threads_daemon", metric_type="gauge", description="守护线程数", min_value=0, max_value=400, base_value=80, fluctuation=0.1, unit="个"),
                MetricTemplate(component_type="app_server", metric_name="thread_pool_active", metric_type="gauge", description="线程池活跃线程", min_value=0, max_value=200, base_value=20, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="app_server", metric_name="thread_pool_queue_size", metric_type="gauge", description="线程池队列大小", min_value=0, max_value=100, base_value=5, fluctuation=0.3, unit="个"),
                MetricTemplate(component_type="app_server", metric_name="connection_pool_active", metric_type="gauge", description="连接池活跃连接", min_value=0, max_value=50, base_value=10, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="app_server", metric_name="connection_pool_idle", metric_type="gauge", description="连接池空闲连接", min_value=0, max_value=30, base_value=5, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="app_server", metric_name="connection_pool_pending", metric_type="gauge", description="连接池等待数", min_value=0, max_value=20, base_value=0, fluctuation=0.5, unit="个"),

                MetricTemplate(component_type="api_gateway", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="api_gateway", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="api_gateway", metric_name="request_count", metric_type="counter", description="请求数", min_value=0, max_value=1000, base_value=200, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="api_gateway", metric_name="request_duration", metric_type="gauge", description="请求耗时", min_value=1, max_value=200, base_value=30, fluctuation=0.3, unit="ms"),
                MetricTemplate(component_type="api_gateway", metric_name="route_count", metric_type="gauge", description="路由数量", min_value=0, max_value=200, base_value=50, fluctuation=0.05, unit="个"),
                MetricTemplate(component_type="api_gateway", metric_name="circuit_breaker_open", metric_type="gauge", description="熔断器开启数", min_value=0, max_value=10, base_value=0, fluctuation=0, unit="个"),
                MetricTemplate(component_type="api_gateway", metric_name="circuit_breaker_half_open", metric_type="gauge", description="熔断器半开数", min_value=0, max_value=10, base_value=0, fluctuation=0, unit="个"),
                MetricTemplate(component_type="api_gateway", metric_name="rate_limit_rejected", metric_type="counter", description="限流拒绝数", min_value=0, max_value=50, base_value=0, fluctuation=0.8, unit="次/s"),
                MetricTemplate(component_type="api_gateway", metric_name="retry_count", metric_type="counter", description="重试次数", min_value=0, max_value=20, base_value=2, fluctuation=0.5, unit="次/s"),

                MetricTemplate(component_type="firewall", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="firewall", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="firewall", metric_name="connection_count", metric_type="gauge", description="连接数", min_value=0, max_value=1000, base_value=200, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="firewall", metric_name="connection_rate", metric_type="counter", description="连接速率", min_value=0, max_value=200, base_value=50, fluctuation=0.3, unit="次/s"),
                MetricTemplate(component_type="firewall", metric_name="blocked_count", metric_type="counter", description="阻断次数", min_value=0, max_value=50, base_value=5, fluctuation=0.5, unit="次/s"),
                MetricTemplate(component_type="firewall", metric_name="blocked_rate", metric_type="gauge", description="阻断率", min_value=0, max_value=100, base_value=2, fluctuation=0.3, unit="%"),
                MetricTemplate(component_type="firewall", metric_name="rule_hit_count", metric_type="counter", description="规则命中次数", min_value=0, max_value=500, base_value=100, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="firewall", metric_name="rule_hit_rate", metric_type="gauge", description="规则命中率", min_value=0, max_value=100, base_value=95, fluctuation=0.05, unit="%"),
                MetricTemplate(component_type="firewall", metric_name="packet_in", metric_type="counter", description="入站数据包", min_value=0, max_value=5000, base_value=1000, fluctuation=0.3, unit="个/s"),
                MetricTemplate(component_type="firewall", metric_name="packet_out", metric_type="counter", description="出站数据包", min_value=0, max_value=5000, base_value=900, fluctuation=0.3, unit="个/s"),
                MetricTemplate(component_type="firewall", metric_name="packet_dropped", metric_type="counter", description="丢弃数据包", min_value=0, max_value=100, base_value=10, fluctuation=0.5, unit="个/s"),

                MetricTemplate(component_type="redis", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="redis", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="redis", metric_name="connected_clients", metric_type="gauge", description="连接客户端数", min_value=0, max_value=200, base_value=50, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="redis", metric_name="blocked_clients", metric_type="gauge", description="阻塞客户端数", min_value=0, max_value=50, base_value=0, fluctuation=0.5, unit="个"),
                MetricTemplate(component_type="redis", metric_name="used_memory", metric_type="gauge", description="使用内存", min_value=0, max_value=1024, base_value=256, fluctuation=0.15, unit="MB"),
                MetricTemplate(component_type="redis", metric_name="used_memory_rss", metric_type="gauge", description="RSS内存", min_value=0, max_value=2048, base_value=300, fluctuation=0.1, unit="MB"),
                MetricTemplate(component_type="redis", metric_name="memory_fragmentation_ratio", metric_type="gauge", description="内存碎片率", min_value=0, max_value=2, base_value=1.1, fluctuation=0.1, unit="比值"),
                MetricTemplate(component_type="redis", metric_name="keyspace_keys", metric_type="gauge", description="键总数", min_value=0, max_value=100000, base_value=10000, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="redis", metric_name="keyspace_expires", metric_type="gauge", description="过期键数", min_value=0, max_value=50000, base_value=5000, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="redis", metric_name="evicted_keys", metric_type="counter", description="驱逐键数", min_value=0, max_value=100, base_value=0, fluctuation=0.8, unit="个"),
                MetricTemplate(component_type="redis", metric_name="hit_rate", metric_type="gauge", description="缓存命中率", min_value=0, max_value=100, base_value=90, fluctuation=0.05, unit="%"),
                MetricTemplate(component_type="redis", metric_name="ops_per_sec", metric_type="counter", description="每秒操作数", min_value=0, max_value=2000, base_value=500, fluctuation=0.3, unit="次/s"),
                MetricTemplate(component_type="redis", metric_name="total_commands_processed", metric_type="counter", description="总命令数", min_value=0, max_value=1000000, base_value=100000, fluctuation=0.2, unit="次"),
                MetricTemplate(component_type="redis", metric_name="instantaneous_input_kbps", metric_type="gauge", description="输入速率", min_value=0, max_value=500, base_value=100, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="redis", metric_name="instantaneous_output_kbps", metric_type="gauge", description="输出速率", min_value=0, max_value=500, base_value=80, fluctuation=0.3, unit="KB/s"),

                MetricTemplate(component_type="config_center", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="config_center", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="config_center", metric_name="config_count", metric_type="gauge", description="配置项数量", min_value=0, max_value=500, base_value=100, fluctuation=0.1, unit="个"),
                MetricTemplate(component_type="config_center", metric_name="watch_count", metric_type="gauge", description="监听数量", min_value=0, max_value=200, base_value=50, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="config_center", metric_name="sync_success_count", metric_type="counter", description="同步成功次数", min_value=0, max_value=100, base_value=10, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="config_center", metric_name="sync_failed_count", metric_type="counter", description="同步失败次数", min_value=0, max_value=20, base_value=0, fluctuation=0.8, unit="次/s"),
                MetricTemplate(component_type="config_center", metric_name="sync_latency", metric_type="gauge", description="同步延迟", min_value=0, max_value=100, base_value=20, fluctuation=0.3, unit="ms"),
                MetricTemplate(component_type="config_center", metric_name="connection_count", metric_type="gauge", description="连接数", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="个"),

                MetricTemplate(component_type="mysql", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="mysql", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="mysql", metric_name="connections", metric_type="gauge", description="当前连接数", min_value=0, max_value=200, base_value=20, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="mysql", metric_name="max_connections", metric_type="gauge", description="最大连接数", min_value=0, max_value=500, base_value=100, fluctuation=0, unit="个"),
                MetricTemplate(component_type="mysql", metric_name="connection_errors", metric_type="counter", description="连接错误数", min_value=0, max_value=50, base_value=0, fluctuation=0.8, unit="次"),
                MetricTemplate(component_type="mysql", metric_name="queries", metric_type="counter", description="查询数", min_value=0, max_value=500, base_value=100, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="mysql", metric_name="questions", metric_type="counter", description="问题数", min_value=0, max_value=400, base_value=80, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="mysql", metric_name="slow_queries", metric_type="counter", description="慢查询数", min_value=0, max_value=20, base_value=1, fluctuation=0.5, unit="次/s"),
                MetricTemplate(component_type="mysql", metric_name="queries_in_cache", metric_type="gauge", description="缓存查询数", min_value=0, max_value=200, base_value=50, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="mysql", metric_name="buffer_pool_size", metric_type="gauge", description="缓冲池大小", min_value=0, max_value=4096, base_value=1024, fluctuation=0, unit="MB"),
                MetricTemplate(component_type="mysql", metric_name="buffer_pool_used", metric_type="gauge", description="缓冲池使用", min_value=0, max_value=4096, base_value=512, fluctuation=0.15, unit="MB"),
                MetricTemplate(component_type="mysql", metric_name="buffer_pool_hit_rate", metric_type="gauge", description="缓冲池命中率", min_value=0, max_value=100, base_value=95, fluctuation=0.05, unit="%"),
                MetricTemplate(component_type="mysql", metric_name="innodb_row_lock_waits", metric_type="counter", description="行锁等待", min_value=0, max_value=50, base_value=5, fluctuation=0.5, unit="次"),
                MetricTemplate(component_type="mysql", metric_name="innodb_row_lock_time_avg", metric_type="gauge", description="平均锁等待时间", min_value=0, max_value=100, base_value=10, fluctuation=0.5, unit="ms"),
                MetricTemplate(component_type="mysql", metric_name="table_locks_waited", metric_type="counter", description="表锁等待", min_value=0, max_value=20, base_value=2, fluctuation=0.5, unit="次"),
                MetricTemplate(component_type="mysql", metric_name="table_open_cache_hit_rate", metric_type="gauge", description="表缓存命中率", min_value=0, max_value=100, base_value=98, fluctuation=0.02, unit="%"),
                MetricTemplate(component_type="mysql", metric_name="threads_running", metric_type="gauge", description="运行线程数", min_value=0, max_value=50, base_value=5, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="mysql", metric_name="threads_connected", metric_type="gauge", description="连接线程数", min_value=0, max_value=100, base_value=15, fluctuation=0.2, unit="个"),
                MetricTemplate(component_type="mysql", metric_name="bytes_received", metric_type="counter", description="接收字节", min_value=0, max_value=1000, base_value=200, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="mysql", metric_name="bytes_sent", metric_type="counter", description="发送字节", min_value=0, max_value=2000, base_value=500, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="mysql", metric_name="com_select", metric_type="counter", description="SELECT次数", min_value=0, max_value=300, base_value=60, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="mysql", metric_name="com_insert", metric_type="counter", description="INSERT次数", min_value=0, max_value=100, base_value=20, fluctuation=0.3, unit="次/s"),
                MetricTemplate(component_type="mysql", metric_name="com_update", metric_type="counter", description="UPDATE次数", min_value=0, max_value=100, base_value=15, fluctuation=0.3, unit="次/s"),
                MetricTemplate(component_type="mysql", metric_name="com_delete", metric_type="counter", description="DELETE次数", min_value=0, max_value=50, base_value=5, fluctuation=0.4, unit="次/s"),

                MetricTemplate(component_type="kafka", metric_name="cpu_usage", metric_type="gauge", description="CPU使用率", min_value=0, max_value=100, base_value=30, fluctuation=0.2, unit="%"),
                MetricTemplate(component_type="kafka", metric_name="memory_usage", metric_type="gauge", description="内存使用率", min_value=0, max_value=100, base_value=50, fluctuation=0.15, unit="%"),
                MetricTemplate(component_type="kafka", metric_name="messages_in_rate", metric_type="counter", description="消息流入速率", min_value=0, max_value=5000, base_value=1000, fluctuation=0.3, unit="条/s"),
                MetricTemplate(component_type="kafka", metric_name="bytes_in_rate", metric_type="counter", description="字节流入速率", min_value=0, max_value=2000, base_value=500, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="kafka", metric_name="bytes_out_rate", metric_type="counter", description="字节流出速率", min_value=0, max_value=2000, base_value=400, fluctuation=0.3, unit="KB/s"),
                MetricTemplate(component_type="kafka", metric_name="partition_count", metric_type="gauge", description="分区数", min_value=0, max_value=50, base_value=10, fluctuation=0.1, unit="个"),
                MetricTemplate(component_type="kafka", metric_name="under_replicated_partitions", metric_type="gauge", description="副本不足分区", min_value=0, max_value=10, base_value=0, fluctuation=0, unit="个"),
                MetricTemplate(component_type="kafka", metric_name="offline_partitions_count", metric_type="gauge", description="离线分区数", min_value=0, max_value=10, base_value=0, fluctuation=0, unit="个"),
                MetricTemplate(component_type="kafka", metric_name="active_controller_count", metric_type="gauge", description="活跃控制器数", min_value=0, max_value=1, base_value=1, fluctuation=0, unit="个"),
                MetricTemplate(component_type="kafka", metric_name="leader_count", metric_type="gauge", description="Leader数", min_value=0, max_value=50, base_value=10, fluctuation=0.1, unit="个"),
                MetricTemplate(component_type="kafka", metric_name="producer_request_rate", metric_type="counter", description="生产者请求率", min_value=0, max_value=500, base_value=100, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="kafka", metric_name="producer_request_latency_avg", metric_type="gauge", description="生产者延迟", min_value=0, max_value=100, base_value=10, fluctuation=0.3, unit="ms"),
                MetricTemplate(component_type="kafka", metric_name="consumer_fetch_rate", metric_type="counter", description="消费者拉取率", min_value=0, max_value=400, base_value=80, fluctuation=0.2, unit="次/s"),
                MetricTemplate(component_type="kafka", metric_name="consumer_lag", metric_type="gauge", description="消费者延迟", min_value=0, max_value=1000, base_value=100, fluctuation=0.4, unit="条"),
                MetricTemplate(component_type="kafka", metric_name="consumer_group_lag", metric_type="gauge", description="消费组延迟", min_value=0, max_value=500, base_value=50, fluctuation=0.3, unit="条"),
                MetricTemplate(component_type="kafka", metric_name="log_size", metric_type="gauge", description="日志大小", min_value=0, max_value=10240, base_value=1024, fluctuation=0.2, unit="MB"),
                MetricTemplate(component_type="kafka", metric_name="log_end_offset", metric_type="gauge", description="日志结束偏移", min_value=0, max_value=1000000, base_value=100000, fluctuation=0.2, unit="个"),
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
