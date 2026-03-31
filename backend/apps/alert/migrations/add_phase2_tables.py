from sqlalchemy import text
from common.core.database import engine

def upgrade():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alert_groups (
                id INT PRIMARY KEY AUTO_INCREMENT,
                group_key VARCHAR(255) NOT NULL COMMENT '聚合键',
                strategy VARCHAR(50) NOT NULL COMMENT '聚合策略: time_window/topology/semantic',
                severity VARCHAR(50) NOT NULL COMMENT '最高严重级别',
                status VARCHAR(50) DEFAULT 'active' COMMENT '状态: active/resolved/acknowledged',
                alert_count INT DEFAULT 1 COMMENT '告警数量',
                first_alert_id INT NULL COMMENT '首条告警ID',
                first_alert_time DATETIME NULL COMMENT '首条告警时间',
                last_alert_id INT NULL COMMENT '最后一条告警ID',
                last_alert_time DATETIME NULL COMMENT '最后一条告警时间',
                topology_path TEXT NULL COMMENT '拓扑路径(JSON)',
                affected_components JSON NULL COMMENT '受影响组件列表',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
                resolved_at DATETIME NULL COMMENT '解决时间',
                INDEX idx_group_key (group_key),
                INDEX idx_status (status),
                INDEX idx_strategy (strategy)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alert_group_members (
                id INT PRIMARY KEY AUTO_INCREMENT,
                group_id INT NOT NULL COMMENT '聚合组ID',
                alert_id INT NOT NULL COMMENT '告警ID',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_group_alert (group_id, alert_id),
                INDEX idx_group_id (group_id),
                INDEX idx_alert_id (alert_id),
                FOREIGN KEY (group_id) REFERENCES alert_groups(id),
                FOREIGN KEY (alert_id) REFERENCES alert_events(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS aggregation_policies (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL COMMENT '策略名称',
                strategy VARCHAR(50) NOT NULL COMMENT '策略类型: time_window/topology/semantic',
                window_seconds INT DEFAULT 300 COMMENT '时间窗口(秒)',
                group_by_fields JSON NULL COMMENT '分组字段',
                max_depth INT DEFAULT 3 COMMENT '最大拓扑深度',
                similarity_threshold DECIMAL(3,2) DEFAULT 0.80 COMMENT '相似度阈值',
                enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_strategy (strategy),
                INDEX idx_enabled (enabled)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rca_reports (
                id INT PRIMARY KEY AUTO_INCREMENT,
                group_id INT NULL COMMENT '聚合组ID',
                status VARCHAR(50) DEFAULT 'analyzing' COMMENT '状态: analyzing/completed/failed',
                root_causes JSON NULL COMMENT '根因列表',
                analysis_path TEXT NULL COMMENT '分析路径(JSON)',
                confidence DECIMAL(3,2) NULL COMMENT '置信度',
                random_walk_result JSON NULL COMMENT '随机游走结果',
                correlation_result JSON NULL COMMENT '时序相关性结果',
                llm_result JSON NULL COMMENT 'LLM分析结果',
                recommendations JSON NULL COMMENT '排查建议',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME NULL COMMENT '完成时间',
                INDEX idx_group_id (group_id),
                INDEX idx_status (status),
                FOREIGN KEY (group_id) REFERENCES alert_groups(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rca_candidates (
                id INT PRIMARY KEY AUTO_INCREMENT,
                report_id INT NOT NULL COMMENT '报告ID',
                component_name VARCHAR(255) NULL COMMENT '组件名称',
                component_type VARCHAR(50) NULL COMMENT '组件类型',
                score DECIMAL(5,4) NULL COMMENT '根因得分',
                evidence JSON NULL COMMENT '支持证据',
                analysis_method VARCHAR(50) NULL COMMENT '分析方法',
                rank_order INT NULL COMMENT '排名',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_report_id (report_id),
                FOREIGN KEY (report_id) REFERENCES rca_reports(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
    print("Phase 2 数据库表创建成功！")

if __name__ == "__main__":
    upgrade()
