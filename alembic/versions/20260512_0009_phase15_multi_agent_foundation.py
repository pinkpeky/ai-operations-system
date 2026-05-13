"""phase15 multi agent foundation

Revision ID: 0009_phase15_multi_agent
Revises: 0008_phase14_memory_foundation
Create Date: 2026-05-12
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_phase15_multi_agent"
down_revision = "0008_phase14_memory_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 Multi-Agent run/message/handoff 表。"""

    op.create_table(
        "agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("root_agent", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("input", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_agent_runs_workspace_id", "agent_runs", ["workspace_id"])
    op.create_index("ix_agent_runs_user_id", "agent_runs", ["user_id"])
    op.create_index("ix_agent_runs_session_id", "agent_runs", ["session_id"])
    op.create_index("ix_agent_runs_root_agent", "agent_runs", ["root_agent"])
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"])

    op.create_table(
        "agent_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_agent", sa.String(length=128), nullable=True),
        sa.Column("to_agent", sa.String(length=128), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_agent_messages_workspace_id", "agent_messages", ["workspace_id"])
    op.create_index("ix_agent_messages_run_id", "agent_messages", ["run_id"])
    op.create_index("ix_agent_messages_from_agent", "agent_messages", ["from_agent"])
    op.create_index("ix_agent_messages_to_agent", "agent_messages", ["to_agent"])
    op.create_index("ix_agent_messages_role", "agent_messages", ["role"])

    op.create_table(
        "agent_handoffs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_agent", sa.String(length=128), nullable=False),
        sa.Column("to_agent", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_agent_handoffs_workspace_id", "agent_handoffs", ["workspace_id"])
    op.create_index("ix_agent_handoffs_run_id", "agent_handoffs", ["run_id"])
    op.create_index("ix_agent_handoffs_from_agent", "agent_handoffs", ["from_agent"])
    op.create_index("ix_agent_handoffs_to_agent", "agent_handoffs", ["to_agent"])
    op.create_index("ix_agent_handoffs_status", "agent_handoffs", ["status"])


def downgrade() -> None:
    """回滚 Multi-Agent 表。"""

    op.drop_index("ix_agent_handoffs_status", table_name="agent_handoffs")
    op.drop_index("ix_agent_handoffs_to_agent", table_name="agent_handoffs")
    op.drop_index("ix_agent_handoffs_from_agent", table_name="agent_handoffs")
    op.drop_index("ix_agent_handoffs_run_id", table_name="agent_handoffs")
    op.drop_index("ix_agent_handoffs_workspace_id", table_name="agent_handoffs")
    op.drop_table("agent_handoffs")
    op.drop_index("ix_agent_messages_role", table_name="agent_messages")
    op.drop_index("ix_agent_messages_to_agent", table_name="agent_messages")
    op.drop_index("ix_agent_messages_from_agent", table_name="agent_messages")
    op.drop_index("ix_agent_messages_run_id", table_name="agent_messages")
    op.drop_index("ix_agent_messages_workspace_id", table_name="agent_messages")
    op.drop_table("agent_messages")
    op.drop_index("ix_agent_runs_status", table_name="agent_runs")
    op.drop_index("ix_agent_runs_root_agent", table_name="agent_runs")
    op.drop_index("ix_agent_runs_session_id", table_name="agent_runs")
    op.drop_index("ix_agent_runs_user_id", table_name="agent_runs")
    op.drop_index("ix_agent_runs_workspace_id", table_name="agent_runs")
    op.drop_table("agent_runs")
