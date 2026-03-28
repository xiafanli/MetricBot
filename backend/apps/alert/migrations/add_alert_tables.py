from sqlalchemy import text
from common.core.database import engine

def upgrade():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alert_events (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL COMMENT '事件标题',
                severity VARCHAR(50) NOT NULL COMMENT '严重程度',
                alert_ids TEXT COMMENT '关联告警ID列表(JSON)',
                status VARCHAR(50) DEFAULT 'active' COMMENT '状态',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME NULL COMMENT '恢复时间',
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS diagnosis_reports (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alert_id INT NOT NULL COMMENT '告警ID',
                report TEXT COMMENT '诊断报告内容',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_alert_id (alert_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS diagnosis_conversations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alert_id INT NOT NULL COMMENT '告警ID',
                user_id INT NOT NULL COMMENT '用户ID',
                messages TEXT COMMENT '对话消息列表(JSON)',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_alert_id (alert_id),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
    print("数据库表创建成功！")

if __name__ == "__main__":
    upgrade()
