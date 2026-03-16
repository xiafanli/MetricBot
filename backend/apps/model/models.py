from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from common.core.database import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="模型名称")
    provider = Column(String(100), nullable=False, comment="提供商，如 OpenAI, Azure, Anthropic 等")
    base_model = Column(String(255), nullable=False, comment="基础模型名称")
    api_key = Column(String(500), nullable=True, comment="API Key（加密存储）")
    api_domain = Column(String(500), nullable=True, comment="API 域名/地址")
    protocol = Column(String(50), nullable=False, default="openai", comment="协议类型，如 openai, anthropic 等")
    config = Column(Text, nullable=True, comment="其他配置，JSON 格式")
    is_default = Column(Boolean, default=False, comment="是否为默认模型")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
