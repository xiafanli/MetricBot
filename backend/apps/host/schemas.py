from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HostBase(BaseModel):
    name: str = Field(..., description="主机名称")
    ip: str = Field(..., description="主机IP")
    hostname: Optional[str] = Field(None, description="主机名")
    os: Optional[str] = Field(None, description="操作系统")
    os_version: Optional[str] = Field(None, description="操作系统版本")
    cpu_cores: Optional[int] = Field(None, description="CPU核心数")
    memory_gb: Optional[float] = Field(None, description="内存(GB)")
    disk_gb: Optional[float] = Field(None, description="磁盘(GB)")
    tags: Optional[List[str]] = Field(None, description="标签")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    source: Optional[str] = Field("manual", description="来源")
    from_type: Optional[str] = Field("manual", description="来源类型")
    from_name: Optional[str] = Field(None, description="来源名称")
    enabled: Optional[bool] = Field(True, description="是否启用")


class HostCreate(HostBase):
    pass


class HostUpdate(BaseModel):
    name: Optional[str] = None
    ip: Optional[str] = None
    hostname: Optional[str] = None
    os: Optional[str] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[float] = None
    disk_gb: Optional[float] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    enabled: Optional[bool] = None


class HostResponse(HostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HostRelationBase(BaseModel):
    source_host_id: int = Field(..., description="源主机ID")
    target_host_id: int = Field(..., description="目标主机ID")
    relation_type: str = Field(..., description="关系类型: depends_on/calls/connects_to")
    description: Optional[str] = Field(None, description="关系描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    source: Optional[str] = Field("manual", description="来源")


class HostRelationCreate(HostRelationBase):
    pass


class HostRelationUpdate(BaseModel):
    source_host_id: Optional[int] = None
    target_host_id: Optional[int] = None
    relation_type: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    source: Optional[str] = None


class HostRelationResponse(HostRelationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PrometheusSyncRequest(BaseModel):
    datasource_id: int = Field(..., description="Prometheus 数据源 ID")
    metric: str = Field(..., description="指标名")
    label: str = Field(..., description="标签名")
    preview_only: bool = Field(True, description="只预览不导入")


class PrometheusSyncPreviewResponse(BaseModel):
    preview: List[str] = Field(..., description="预览标签值")
    total: int = Field(..., description="总数")


class PrometheusSyncImportResponse(BaseModel):
    imported: int = Field(..., description="已导入数量")
    hosts: List[HostResponse] = Field(..., description="已导入的主机列表")
