"""工作区 ORM 模型模块。"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import WorkspaceMemberRole, WorkspaceMemberStatus, WorkspaceStatus

if TYPE_CHECKING:
    from app.models.api_key import APIKey
    from app.models.user import User


class Workspace(IdTimestampMixin, Base):
    """工作区模型。"""

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="工作区名称")
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True, comment="工作区 slug")
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkspaceStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="工作区状态",
    )

    members: Mapped[list["WorkspaceMember"]] = relationship(back_populates="workspace")
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="workspace")


class WorkspaceMember(IdTimestampMixin, Base):
    """工作区成员模型。"""

    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_members_workspace_user"),
    )

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
    role: Mapped[str] = mapped_column(
        String(32),
        default=WorkspaceMemberRole.MEMBER.value,
        nullable=False,
        comment="成员角色",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkspaceMemberStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="成员状态",
    )

    workspace: Mapped[Workspace] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")
