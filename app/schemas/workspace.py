"""工作区 API 数据模型模块。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workspace import Workspace


class WorkspaceCreateRequest(BaseModel):
    """创建工作区请求。"""

    name: str = Field(min_length=1, max_length=128, description="工作区名称")
    slug: str = Field(min_length=1, max_length=128, description="工作区 slug")


class WorkspaceResponse(BaseModel):
    """工作区响应。"""

    id: UUID
    name: str
    slug: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, workspace: Workspace) -> "WorkspaceResponse":
        """从 ORM 对象构建响应。"""

        return cls(
            id=workspace.id,
            name=workspace.name,
            slug=workspace.slug,
            status=workspace.status,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        )


class WorkspaceListResponse(BaseModel):
    """工作区列表响应。"""

    items: list[WorkspaceResponse]
