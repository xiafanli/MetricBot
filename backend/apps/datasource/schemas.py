from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DatasourceBase(BaseModel):
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    url: str = Field(..., description="数据源地址")
    auth_type: str = Field("none", description="认证方式")
    auth_value: Optional[str] = Field(None, description="认证值")
    password: Optional[str] = Field(None, description="密码")
    config: Optional[Dict[str, Any]] = Field(None, description="其他配置")
    enabled: bool = Field(True, description="是否启用")


class DatasourceCreate(DatasourceBase):
    pass


class DatasourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    auth_type: Optional[str] = None
    auth_value: Optional[str] = None
    password: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class DatasourceResponse(DatasourceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
