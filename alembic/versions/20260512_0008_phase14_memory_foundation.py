"""phase14 memory foundation

Revision ID: 0008_phase14_memory_foundation
Revises: 0007_phase13_tool_calling
Create Date: 2026-05-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_phase14_memory_foundation"
down_revision: str | None = "0007_phase13_tool_calling"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """新增 Memory Foundation 数据表。"""

    op.create_table(
        "conversation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="会话 ID"),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, comment="工作区 ID"),
        sa.Column("user_id", sa.String(length=128), nullable=True, comment="用户 ID"),
        sa.Column("title", sa.String(length=255), nullable=False, comment="会话标题"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active", comment="会话状态"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb"), comment="会话元数据"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_sessions_workspace_id", "conversation_sessions", ["workspace_id"])
    op.create_index("ix_conversation_sessions_user_id", "conversation_sessions", ["user_id"])
    op.create_index("ix_conversation_sessions_status", "conversation_sessions", ["status"])

    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="消息 ID"),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False, comment="会话 ID"),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, comment="工作区 ID"),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="user", comment="消息角色"),
        sa.Column("content", sa.Text(), nullable=False, comment="消息内容"),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0", comment="粗略 token 数"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb"), comment="消息元数据"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.ForeignKeyConstraint(["session_id"], ["conversation_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_messages_session_id", "conversation_messages", ["session_id"])
    op.create_index("ix_conversation_messages_workspace_id", "conversation_messages", ["workspace_id"])
    op.create_index("ix_conversation_messages_role", "conversation_messages", ["role"])

    op.create_table(
        "agent_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="Memory ID"),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, comment="工作区 ID"),
        sa.Column("agent_name", sa.String(length=128), nullable=False, comment="Agent 名称"),
        sa.Column("memory_type", sa.String(length=64), nullable=False, server_default="short_term", comment="Memory 类型"),
        sa.Column("content", sa.Text(), nullable=False, comment="Memory 内容"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb"), comment="Memory 元数据"),
        sa.Column("importance_score", sa.Float(), nullable=False, server_default="0.5", comment="重要性分数"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_memories_workspace_id", "agent_memories", ["workspace_id"])
    op.create_index("ix_agent_memories_agent_name", "agent_memories", ["agent_name"])
    op.create_index("ix_agent_memories_memory_type", "agent_memories", ["memory_type"])

    op.create_table(
        "memory_operation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="Memory 操作日志 ID"),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, comment="工作区 ID"),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True, comment="会话 ID"),
        sa.Column("agent_name", sa.String(length=128), nullable=True, comment="Agent 名称"),
        sa.Column("memory_type", sa.String(length=64), nullable=True, comment="Memory 类型"),
        sa.Column("operation", sa.String(length=64), nullable=False, comment="操作名称"),
        sa.Column("success", sa.Boolean(), nullable=False, comment="是否成功"),
        sa.Column("error", sa.Text(), nullable=True, comment="错误信息"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, comment="操作耗时毫秒"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb"), comment="操作元数据"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memory_operation_logs_workspace_id", "memory_operation_logs", ["workspace_id"])
    op.create_index("ix_memory_operation_logs_session_id", "memory_operation_logs", ["session_id"])
    op.create_index("ix_memory_operation_logs_agent_name", "memory_operation_logs", ["agent_name"])
    op.create_index("ix_memory_operation_logs_memory_type", "memory_operation_logs", ["memory_type"])
    op.create_index("ix_memory_operation_logs_operation", "memory_operation_logs", ["operation"])
    op.create_index("ix_memory_operation_logs_success", "memory_operation_logs", ["success"])


def downgrade() -> None:
    """回滚 Memory Foundation 数据表。"""

    op.drop_index("ix_memory_operation_logs_success", table_name="memory_operation_logs")
    op.drop_index("ix_memory_operation_logs_operation", table_name="memory_operation_logs")
    op.drop_index("ix_memory_operation_logs_memory_type", table_name="memory_operation_logs")
    op.drop_index("ix_memory_operation_logs_agent_name", table_name="memory_operation_logs")
    op.drop_index("ix_memory_operation_logs_session_id", table_name="memory_operation_logs")
    op.drop_index("ix_memory_operation_logs_workspace_id", table_name="memory_operation_logs")
    op.drop_table("memory_operation_logs")

    op.drop_index("ix_agent_memories_memory_type", table_name="agent_memories")
    op.drop_index("ix_agent_memories_agent_name", table_name="agent_memories")
    op.drop_index("ix_agent_memories_workspace_id", table_name="agent_memories")
    op.drop_table("agent_memories")

    op.drop_index("ix_conversation_messages_role", table_name="conversation_messages")
    op.drop_index("ix_conversation_messages_workspace_id", table_name="conversation_messages")
    op.drop_index("ix_conversation_messages_session_id", table_name="conversation_messages")
    op.drop_table("conversation_messages")

    op.drop_index("ix_conversation_sessions_status", table_name="conversation_sessions")
    op.drop_index("ix_conversation_sessions_user_id", table_name="conversation_sessions")
    op.drop_index("ix_conversation_sessions_workspace_id", table_name="conversation_sessions")
    op.drop_table("conversation_sessions")
