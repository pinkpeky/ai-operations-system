"""发布日志 ORM 模型模块。

publish_logs 表记录任务发布过程中的请求、响应和错误信息，便于审计与排障。
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import PublishLogStatus

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.task import Task


class PublishLog(IdTimestampMixin, Base):
    """发布日志数据模型。"""

    __tablename__ = "publish_logs"

    status: Mapped[str] = mapped_column(
        String(32),
        default=PublishLogStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="发布状态",
    )
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联任务 ID",
    )
    account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="关联账号 ID",
    )
    channel: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
        comment="发布渠道",
    )
    request_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="发布请求内容",
    )
    response_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="发布响应内容",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息",
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="发布时间",
    )

    task: Mapped["Task"] = relationship(back_populates="publish_logs")
    account: Mapped["Account | None"] = relationship(back_populates="publish_logs")
