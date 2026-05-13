"""用户 ORM 模型模块。"""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import UserStatus

if TYPE_CHECKING:
    from app.models.api_key import APIKey
    from app.models.workspace import WorkspaceMember


class User(IdTimestampMixin, Base):
    """系统用户模型。

    当前阶段只作为隔离基础，不承载完整认证登录流程。
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True, comment="用户名")
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True, comment="邮箱")
    status: Mapped[str] = mapped_column(
        String(32),
        default=UserStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="用户状态",
    )

    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(back_populates="user")
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="user")
