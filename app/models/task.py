"""任务 ORM 模型模块。

tasks 表是 AI 中央任务系统的核心表，负责记录待调度、运行中、重试和失败的任务。
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import TaskStatus

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.publish_log import PublishLog


class Task(IdTimestampMixin, Base):
    """中央任务数据模型。"""

    __tablename__ = "tasks"

    status: Mapped[str] = mapped_column(
        String(32),
        default=TaskStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="任务状态",
    )
    account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="关联账号 ID",
    )
    workspace_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
        comment="隔离工作区 ID",
    )
    user_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
        comment="任务创建用户 ID",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="任务标题",
    )
    task_type: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
        comment="任务类型",
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="任务负载",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="已重试次数",
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
        comment="最大重试次数",
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="计划执行时间",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="开始执行时间",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间",
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="任务执行耗时毫秒数",
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="最近一次错误信息",
    )

    account: Mapped["Account | None"] = relationship(back_populates="tasks")
    publish_logs: Mapped[list["PublishLog"]] = relationship(
        back_populates="task",
        cascade="save-update, merge",
    )
