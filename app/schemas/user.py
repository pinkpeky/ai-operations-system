"""用户 API 数据模型模块。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.user import User


class UserCreateRequest(BaseModel):
    """创建用户请求。"""

    username: str = Field(min_length=1, max_length=128, description="用户名")
    email: str = Field(min_length=3, max_length=255, description="邮箱")


class UserResponse(BaseModel):
    """用户响应。"""

    id: UUID
    username: str
    email: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, user: User) -> "UserResponse":
        """从 ORM 对象构建响应。"""

        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserListResponse(BaseModel):
    """用户列表响应。"""

    items: list[UserResponse]
