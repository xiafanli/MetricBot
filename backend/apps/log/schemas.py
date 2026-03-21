from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class LogSourceBase(BaseModel):
    name: str = Field(..., description="日志源名称")
    type: str = Field(..., description="日志源类型: Elasticsearch/StarRocks")
    url: str = Field(..., description="地址")
    index_or_table: Optional[str] = Field(None, description="索引名/表名")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    retention_days: int = Field(30, description="保留天数")
    config: Optional[Dict[str, Any]] = Field(None, description="其他配置")
    enabled: bool = Field(True, description="是否启用")


class LogSourceCreate(LogSourceBase):
    pass


class LogSourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    index_or_table: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    retention_days: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class LogSourceResponse(LogSourceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LogTestRequest(BaseModel):
    name: str
    type: str
    url: str
    index_or_table: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class LogTestResponse(BaseModel):
    success: bool
    message: str
