"""API Key ORM 模型模块。"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import APIKeyStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workspace import Workspace


class APIKey(IdTimestampMixin, Base):
    """API Key 模型。

    只存储哈希值，明文 key 仅在创建接口响应中返回一次。
    """

    __tablename__ = "api_keys"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="工作区 ID",
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户 ID",
    )
    key_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True, comment="API Key 哈希")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="API Key 名称")
    status: Mapped[str] = mapped_column(
        String(32),
        default=APIKeyStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="API Key 状态",
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="最后使用时间")

    workspace: Mapped["Workspace"] = relationship(back_populates="api_keys")
    user: Mapped["User"] = relationship(back_populates="api_keys")
