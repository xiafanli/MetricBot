from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ModelBase(BaseModel):
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    base_model: str = Field(..., description="基础模型名称")
    api_key: Optional[str] = Field(None, description="API Key")
    api_domain: Optional[str] = Field(None, description="API 域名")
    protocol: str = Field("openai", description="协议类型")
    config: Optional[Dict[str, Any]] = Field(None, description="其他配置")
    is_default: bool = Field(False, description="是否为默认模型")
    is_enabled: bool = Field(True, description="是否启用")


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    base_model: Optional[str] = None
    api_key: Optional[str] = None
    api_domain: Optional[str] = None
    protocol: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_enabled: Optional[bool] = None


class ModelResponse(ModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
