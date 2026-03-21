import os
import json
from dotenv import load_dotenv
from common.core.database import engine, Base, SessionLocal
from apps.auth.models import User
from apps.auth.security import get_password_hash
from apps.host.models import Host, HostRelation

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
            
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
