from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from common.core.database import Base


class Datasource(Base):
    __tablename__ = "datasources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="数据源名称")
    type = Column(String(100), nullable=False, comment="数据源类型：Prometheus/Zabbix/Grafana/Datadog/HTTP")
    url = Column(String(500), nullable=False, comment="数据源地址")
    auth_type = Column(String(50), nullable=False, default="none", comment="认证方式：none/basic/token")
    auth_value = Column(String(500), nullable=True, comment="认证值（用户名/Token）")
    password = Column(String(500), nullable=True, comment="密码（仅 Basic Auth）")
    config = Column(Text, nullable=True, comment="其他配置，JSON 格式")
    enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
