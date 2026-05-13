"""Multi-Agent ORM 模型。

Phase 15 只建立多 Agent 基础编排记录，不实现 autonomous planning、ReAct 或浏览器自动化。
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AgentHandoffStatus, AgentRunStatus


class AgentRun(Base):
    """一次 Multi-Agent run 的根记录。"""

    __tablename__ = "agent_runs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Agent run ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="用户 ID")
    session_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), index=True, nullable=True, comment="Memory session ID")
    root_agent: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="入口 Agent")
    status: Mapped[str] = mapped_column(
        String(32),
        default=AgentRunStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="run 状态",
    )
    run_input: Mapped[dict[str, Any]] = mapped_column("input", JSON, default=dict, nullable=False, comment="run 输入")
    run_output: Mapped[dict[str, Any] | None] = mapped_column("output", JSON, nullable=True, comment="run 输出")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="完成时间")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="耗时毫秒")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    messages: Mapped[list["AgentMessage"]] = relationship(back_populates="run", cascade="save-update, merge")
    handoffs: Mapped[list["AgentHandoff"]] = relationship(back_populates="run", cascade="save-update, merge")


class AgentMessage(Base):
    """Multi-Agent run 内部消息。"""

    __tablename__ = "agent_messages"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Agent message ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    run_id: Mapped[UUID] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    from_agent: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="发送 Agent")
    to_agent: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="接收 Agent")
    role: Mapped[str] = mapped_column(String(32), index=True, nullable=False, comment="消息角色")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    message_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="消息元数据",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    run: Mapped[AgentRun] = relationship(back_populates="messages")


class AgentHandoff(Base):
    """Agent 间固定链路 handoff 记录。"""

    __tablename__ = "agent_handoffs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Agent handoff ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    run_id: Mapped[UUID] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    from_agent: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="来源 Agent")
    to_agent: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="目标 Agent")
    reason: Mapped[str] = mapped_column(Text, nullable=False, comment="移交原因")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="移交载荷")
    status: Mapped[str] = mapped_column(
        String(32),
        default=AgentHandoffStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="handoff 状态",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    run: Mapped[AgentRun] = relationship(back_populates="handoffs")
