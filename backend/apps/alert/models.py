from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL, JSON, Numeric, ForeignKey
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
    message = Column(Text, nullable=True, comment="事件消息")
    source = Column(String(100), nullable=True, comment="事件来源")
    labels = Column(JSON, nullable=True, comment="标签(JSON)")
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


class AlertGroup(Base):
    __tablename__ = "alert_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_key = Column(String(255), nullable=False, comment="聚合键")
    strategy = Column(String(50), nullable=False, comment="聚合策略: time_window/topology/semantic")
    severity = Column(String(50), nullable=False, comment="最高严重级别")
    status = Column(String(50), default="active", comment="状态: active/resolved/acknowledged")
    alert_count = Column(Integer, default=1, comment="告警数量")
    first_alert_id = Column(Integer, nullable=True, comment="首条告警ID")
    first_alert_time = Column(DateTime(timezone=True), nullable=True, comment="首条告警时间")
    last_alert_id = Column(Integer, nullable=True, comment="最后一条告警ID")
    last_alert_time = Column(DateTime(timezone=True), nullable=True, comment="最后一条告警时间")
    topology_path = Column(Text, nullable=True, comment="拓扑路径(JSON)")
    affected_components = Column(JSON, nullable=True, comment="受影响组件列表")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="解决时间")


class AlertGroupMember(Base):
    __tablename__ = "alert_group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("alert_groups.id"), nullable=False, comment="聚合组ID")
    alert_id = Column(Integer, ForeignKey("alert_events.id"), nullable=False, comment="告警ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AggregationPolicy(Base):
    __tablename__ = "aggregation_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="策略名称")
    strategy = Column(String(50), nullable=False, comment="策略类型: time_window/topology/semantic")
    window_seconds = Column(Integer, default=300, comment="时间窗口(秒)")
    group_by_fields = Column(JSON, nullable=True, comment="分组字段")
    max_depth = Column(Integer, default=3, comment="最大拓扑深度")
    similarity_threshold = Column(Numeric(3, 2), default=0.8, comment="相似度阈值")
    enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RcaReport(Base):
    __tablename__ = "rca_reports"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("alert_groups.id"), nullable=True, comment="聚合组ID")
    status = Column(String(50), default="analyzing", comment="状态: analyzing/completed/failed")
    root_causes = Column(JSON, nullable=True, comment="根因列表")
    analysis_path = Column(Text, nullable=True, comment="分析路径(JSON)")
    confidence = Column(Numeric(3, 2), nullable=True, comment="置信度")
    random_walk_result = Column(JSON, nullable=True, comment="随机游走结果")
    correlation_result = Column(JSON, nullable=True, comment="时序相关性结果")
    llm_result = Column(JSON, nullable=True, comment="LLM分析结果")
    recommendations = Column(JSON, nullable=True, comment="排查建议")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")


class RcaCandidate(Base):
    __tablename__ = "rca_candidates"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("rca_reports.id"), nullable=False, comment="报告ID")
    component_name = Column(String(255), nullable=True, comment="组件名称")
    component_type = Column(String(50), nullable=True, comment="组件类型")
    score = Column(Numeric(5, 4), nullable=True, comment="根因得分")
    evidence = Column(JSON, nullable=True, comment="支持证据")
    analysis_method = Column(String(50), nullable=True, comment="分析方法")
    rank_order = Column(Integer, nullable=True, comment="排名")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
