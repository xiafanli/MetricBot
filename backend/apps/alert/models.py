from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL
from sqlalchemy.sql import func
from common.core.database import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="规则名称")
    description = Column(Text, nullable=True, comment="描述")

    datasource_id = Column(Integer, nullable=False, comment="数据源ID")
    datasource_type = Column(String(50), nullable=False, comment="数据源类型: Prometheus/Zabbix")
    metric_query = Column(String(500), nullable=False, comment="指标查询语句")

    condition_type = Column(String(50), nullable=False, default="greater_than",
                          comment="条件类型: greater_than/less_than/equal_to/anomaly")
    threshold = Column(DECIMAL(10, 2), nullable=True, comment="阈值")

    severity = Column(String(50), nullable=False, default="warning",
                   comment="级别: info/warning/critical")

    evaluation_interval = Column(Integer, default=30, comment="评估间隔(秒)")
    enabled = Column(Boolean, default=True, comment="是否启用")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, nullable=False, comment="规则ID")
    rule_name = Column(String(255), nullable=True, comment="规则名称（快照）")

    severity = Column(String(50), nullable=False, comment="级别")
    metric_value = Column(DECIMAL(10, 2), nullable=True, comment="指标值")
    threshold = Column(DECIMAL(10, 2), nullable=True, comment="阈值")
    message = Column(Text, nullable=True, comment="告警消息")

    resolved = Column(Boolean, default=False, comment="是否已恢复")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="恢复时间")

    datasource_id = Column(Integer, nullable=True, comment="数据源ID")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="事件标题")
    severity = Column(String(50), nullable=False, comment="严重程度")
    alert_ids = Column(Text, nullable=True, comment="关联告警ID列表(JSON)")
    status = Column(String(50), default="active", comment="状态: active/resolved")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="恢复时间")


class DiagnosisReport(Base):
    __tablename__ = "diagnosis_reports"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=False, index=True, comment="告警ID")
    report = Column(Text, nullable=True, comment="诊断报告内容")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiagnosisConversation(Base):
    __tablename__ = "diagnosis_conversations"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=False, index=True, comment="告警ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    messages = Column(Text, nullable=True, comment="对话消息列表(JSON)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
