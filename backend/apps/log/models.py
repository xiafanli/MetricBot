from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from common.core.database import Base


class LogSource(Base):
    __tablename__ = "log_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="日志源名称")
    type = Column(String(100), nullable=False, comment="日志源类型: Elasticsearch/StarRocks")
    
    # 连接配置
    url = Column(String(500), nullable=False, comment="地址")
    index_or_table = Column(String(255), nullable=True, comment="索引名/表名")
    username = Column(String(255), nullable=True, comment="用户名")
    password = Column(String(255), nullable=True, comment="密码")
    
    # 其他配置
    retention_days = Column(Integer, default=30, comment="保留天数")
    config = Column(Text, nullable=True, comment="其他配置，JSON 格式")
    enabled = Column(Boolean, default=True, comment="是否启用")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
