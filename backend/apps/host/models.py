from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from common.core.database import Base


class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="主机名称")
    ip = Column(String(100), nullable=False, comment="主机IP")
    hostname = Column(String(255), nullable=True, comment="主机名")
    
    # 主机信息
    os = Column(String(100), nullable=True, comment="操作系统")
    os_version = Column(String(100), nullable=True, comment="操作系统版本")
    cpu_cores = Column(Integer, nullable=True, comment="CPU核心数")
    memory_gb = Column(DECIMAL(10, 2), nullable=True, comment="内存(GB)")
    disk_gb = Column(DECIMAL(10, 2), nullable=True, comment="磁盘(GB)")
    
    # 元数据
    tags = Column(Text, nullable=True, comment="标签，JSON数组")
    metadata = Column(Text, nullable=True, comment="元数据，JSON格式")
    source = Column(String(100), nullable=True, default="manual", comment="来源：manual/api/auto")
    
    enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HostRelation(Base):
    __tablename__ = "host_relations"

    id = Column(Integer, primary_key=True, index=True)
    source_host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False, comment="源主机ID")
    target_host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False, comment="目标主机ID")
    
    relation_type = Column(String(100), nullable=False, comment="关系类型: depends_on/calls/connects_to")
    description = Column(Text, nullable=True, comment="关系描述")
    
    metadata = Column(Text, nullable=True, comment="元数据，JSON格式")
    source = Column(String(100), nullable=True, default="manual", comment="来源：manual/api/auto")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
