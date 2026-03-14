import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from common.core.database import engine, Base, SessionLocal
from apps.auth.models import User
from apps.auth.security import get_password_hash

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
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
