from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AlertRuleBase(BaseModel):
    name: str = Field(..., description="规则名称")
    description: Optional[str] = Field(None, description="描述")
    datasource_id: int = Field(..., description="数据源ID")
    datasource_type: str = Field(..., description="数据源类型")
    metric_query: str = Field(..., description="指标查询语句")
    condition_type: str = Field("greater_than", description="条件类型")
    threshold: Optional[float] = Field(None, description="阈值")
    severity: str = Field("warning", description="级别")
    evaluation_interval: int = Field(30, description="评估间隔(秒)")
    enabled: bool = Field(True, description="是否启用")


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    datasource_id: Optional[int] = None
    datasource_type: Optional[str] = None
    metric_query: Optional[str] = None
    condition_type: Optional[str] = None
    threshold: Optional[float] = None
    severity: Optional[str] = None
    evaluation_interval: Optional[int] = None
    enabled: Optional[bool] = None


class AlertRuleResponse(AlertRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    rule_id: int = Field(..., description="规则ID")
    rule_name: Optional[str] = Field(None, description="规则名称")
    severity: str = Field(..., description="级别")
    metric_value: Optional[float] = Field(None, description="指标值")
    threshold: Optional[float] = Field(None, description="阈值")
    message: Optional[str] = Field(None, description="告警消息")
    resolved: bool = Field(False, description="是否已恢复")
    datasource_id: Optional[int] = Field(None, description="数据源ID")


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None


class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertTestRequest(BaseModel):
    test_value: float = Field(..., description="测试值")


class AlertTestResponse(BaseModel):
    triggered: bool = Field(..., description="是否触发")
    test_value: float = Field(..., description="测试值")
    threshold: Optional[float] = Field(None, description="阈值")
    severity: str = Field(..., description="级别")
    message: str = Field(..., description="消息")


class AlertStatsResponse(BaseModel):
    total: int = Field(0, description="总数")
    critical: int = Field(0, description="严重")
    warning: int = Field(0, description="警告")
    info: int = Field(0, description="信息")
    resolved: int = Field(0, description="已恢复")
    active: int = Field(0, description="进行中")


class AlertEventBase(BaseModel):
    title: str = Field(..., description="事件标题")
    severity: str = Field(..., description="严重程度")
    alert_ids: Optional[List[int]] = Field(None, description="关联告警ID列表")
    status: str = Field("active", description="状态")


class AlertEventCreate(AlertEventBase):
    pass


class AlertEventResponse(AlertEventBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiagnosisReportBase(BaseModel):
    alert_id: int = Field(..., description="告警ID")
    report: Optional[str] = Field(None, description="诊断报告")


class DiagnosisReportCreate(DiagnosisReportBase):
    pass


class DiagnosisReportResponse(DiagnosisReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DiagnosisChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")


class DiagnosisChatResponse(BaseModel):
    id: int
    alert_id: int
    message: str
    created_at: datetime


class DiagnosisContext(BaseModel):
    alert_id: int
    rule_name: str
    severity: str
    metric_value: Optional[float]
    threshold: Optional[float]
    message: Optional[str]
    created_at: datetime
