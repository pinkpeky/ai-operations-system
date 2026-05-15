"""Conversation Runtime ORM 模型。

Phase 33 在现有 Memory conversation_messages 表上增加 thread 关联，
并新增 thread / event 表，用于前端对话运行时和事件轮询。
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import ConversationApprovalStatus, ConversationPlaybookRunStatus, ConversationPlaybookStatus, ConversationThreadStatus


class ConversationThread(IdTimestampMixin, Base):
    """对话线程表。

    线程是前端 Chat 面板的会话容器，和 Phase 14 的 Memory session 分开建模，
    但消息复用 conversation_messages 表以避免重复消息存储。
    """

    __tablename__ = "conversation_threads"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="用户 ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="线程标题")
    status: Mapped[str] = mapped_column(
        String(32),
        default=ConversationThreadStatus.ACTIVE.value,
        index=True,
        nullable=False,
        comment="线程状态",
    )
    thread_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="线程元数据",
    )

    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="thread",
        cascade="save-update, merge",
    )
    events: Mapped[list["ConversationEvent"]] = relationship(
        back_populates="thread",
        cascade="save-update, merge",
    )
    approvals: Mapped[list["ConversationApproval"]] = relationship(
        back_populates="thread",
        cascade="save-update, merge",
    )
    playbook_runs: Mapped[list["ConversationPlaybookRun"]] = relationship(
        back_populates="thread",
        cascade="save-update, merge",
    )


class ConversationEvent(Base):
    """对话事件表。

    事件用于 polling event feed。当前不实现 WebSocket/SSE，只保存可查询事件。
    """

    __tablename__ = "conversation_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="事件 ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    thread_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation_threads.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="对话线程 ID",
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="事件类型")
    message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="事件摘要")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="事件载荷")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    thread: Mapped[ConversationThread] = relationship(back_populates="events")


class ConversationApproval(IdTimestampMixin, Base):
    """Execution approval record for Conversation Runtime.

    Approval records keep proposed tool/agent actions separate from execution
    so medium/high risk routes can be reviewed before the bridge runs them.
    """

    __tablename__ = "conversation_approvals"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    thread_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation_threads.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Conversation thread ID",
    )
    message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_messages.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Source user message ID",
    )
    route_name: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Selected route")
    selected_tool: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Selected tool")
    risk_level: Mapped[str] = mapped_column(String(16), index=True, nullable=False, comment="low / medium / high")
    approval_status: Mapped[str] = mapped_column(
        String(32),
        default=ConversationApprovalStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="Approval status",
    )
    proposed_action: Mapped[str] = mapped_column(String(255), nullable=False, comment="Human-readable proposed action")
    proposed_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Proposed payload")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    approved_by: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Approver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    approval_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Approval metadata",
    )

    thread: Mapped[ConversationThread] = relationship(back_populates="approvals")


class ConversationPlaybook(IdTimestampMixin, Base):
    """Reusable conversation execution template.

    Playbooks keep common multi-step flows explicit. Built-in templates are
    seeded per workspace on demand and can be disabled without removing history.
    """

    __tablename__ = "conversation_playbooks"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Unique playbook name")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Playbook description")
    category: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True, comment="Playbook category")
    status: Mapped[str] = mapped_column(
        String(32),
        default=ConversationPlaybookStatus.ACTIVE.value,
        index=True,
        nullable=False,
        comment="active / disabled / archived",
    )
    risk_level: Mapped[str] = mapped_column(String(16), index=True, nullable=False, comment="low / medium / high")
    steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Step definitions")
    default_inputs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Default inputs")
    playbook_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Playbook metadata",
    )

    runs: Mapped[list["ConversationPlaybookRun"]] = relationship(
        back_populates="playbook",
        cascade="save-update, merge",
    )


class ConversationPlaybookRun(IdTimestampMixin, Base):
    """One execution instance of a conversation playbook."""

    __tablename__ = "conversation_playbook_runs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    playbook_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation_playbooks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Playbook ID",
    )
    thread_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation_threads.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Conversation thread ID",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=ConversationPlaybookRunStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="Run status",
    )
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Run input")
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Run output")
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Current step index")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Run error")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    playbook: Mapped[ConversationPlaybook] = relationship(back_populates="runs")
    thread: Mapped[ConversationThread] = relationship(back_populates="playbook_runs")
