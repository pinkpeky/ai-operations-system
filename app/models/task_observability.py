"""任务可观测性 ORM 模型。

该模块记录任务生命周期事件和结构化执行日志，供任务控制 API、执行器和后续监控面板复用。
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TaskEvent(Base):
    """任务生命周期事件表。"""

    __tablename__ = "task_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="事件 ID")
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="关联任务 ID",
    )
    workspace_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="工作区 ID")
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="事件类型")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="事件说明")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="事件结构化载荷")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )


class TaskLog(Base):
    """任务结构化日志表。"""

    __tablename__ = "task_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="日志 ID")
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="关联任务 ID",
    )
    workspace_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="工作区 ID")
    level: Mapped[str] = mapped_column(String(32), index=True, nullable=False, comment="日志级别")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="日志内容")
    log_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="结构化日志元数据",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
