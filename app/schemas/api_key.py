"""API Key API 数据模型模块。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.api_key import APIKey


class APIKeyCreateRequest(BaseModel):
    """创建 API Key 请求。"""

    workspace_id: UUID = Field(description="所属工作区 ID")
    user_id: UUID = Field(description="所属用户 ID")
    name: str = Field(min_length=1, max_length=128, description="API Key 名称")


class APIKeyResponse(BaseModel):
    """API Key 响应，不包含明文。"""

    id: UUID
    workspace_id: UUID
    user_id: UUID
    name: str
    status: str
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, api_key: APIKey) -> "APIKeyResponse":
        """从 ORM 对象构建响应。"""

        return cls(
            id=api_key.id,
            workspace_id=api_key.workspace_id,
            user_id=api_key.user_id,
            name=api_key.name,
            status=api_key.status,
            last_used_at=api_key.last_used_at,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
        )


class APIKeyCreateResponse(APIKeyResponse):
    """API Key 创建响应，明文仅返回一次。"""

    api_key: str
