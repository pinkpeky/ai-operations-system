"""Agent Memory ORM 模型。

该模块提供 Phase 14 的会话、消息、Agent Memory 和 Memory 操作日志表。
当前 Memory 只做 PostgreSQL 文本检索基础层，不包含向量记忆或图记忆。
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import AgentMemoryType, ConversationRole, ConversationSessionStatus


class ConversationSession(IdTimestampMixin, Base):
    """会话 session 表。"""

    __tablename__ = "conversation_sessions"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="用户 ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="会话标题")
    status: Mapped[str] = mapped_column(
        String(32),
        default=ConversationSessionStatus.ACTIVE.value,
        index=True,
        nullable=False,
        comment="会话状态",
    )
    session_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="会话元数据",
    )

    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="session",
        cascade="save-update, merge",
    )


class ConversationMessage(Base):
    """会话消息表。"""

    __tablename__ = "conversation_messages"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="消息 ID")
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="会话 ID",
    )
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    role: Mapped[str] = mapped_column(
        String(32),
        default=ConversationRole.USER.value,
        index=True,
        nullable=False,
        comment="消息角色",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="粗略 token 数")
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

    session: Mapped[ConversationSession] = relationship(back_populates="messages")


class AgentMemory(Base):
    """Agent Memory 表。"""

    __tablename__ = "agent_memories"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Memory ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    agent_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Agent 名称")
    memory_type: Mapped[str] = mapped_column(
        String(64),
        default=AgentMemoryType.SHORT_TERM.value,
        index=True,
        nullable=False,
        comment="Memory 类型",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Memory 内容")
    memory_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Memory 元数据",
    )
    importance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False, comment="重要性分数")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )


class MemoryOperationLog(Base):
    """Memory 操作日志表。"""

    __tablename__ = "memory_operation_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Memory 操作日志 ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    session_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), index=True, nullable=True, comment="会话 ID")
    agent_name: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Agent 名称")
    memory_type: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True, comment="Memory 类型")
    operation: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="操作名称")
    success: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, comment="是否成功")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, comment="操作耗时毫秒")
    log_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="结构化操作元数据",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
