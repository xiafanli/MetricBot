"""
添加 alert_events 表的字段
执行方式：python -m apps.alert.migrations.add_alert_event_fields
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sqlalchemy import text
from common.core.database import engine


def upgrade():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE alert_events ADD COLUMN message TEXT NULL COMMENT '事件消息'"))
            print("✅ 添加 message 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠️  message 字段已存在")
            else:
                raise
        
        try:
            conn.execute(text("ALTER TABLE alert_events ADD COLUMN source VARCHAR(100) NULL COMMENT '事件来源'"))
            print("✅ 添加 source 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠️  source 字段已存在")
            else:
                raise
        
        try:
            conn.execute(text("ALTER TABLE alert_events ADD COLUMN labels JSON NULL COMMENT '标签'"))
            print("✅ 添加 labels 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠️  labels 字段已存在")
            else:
                raise
        
        print("\n🎉 迁移完成！")


if __name__ == "__main__":
    upgrade()
