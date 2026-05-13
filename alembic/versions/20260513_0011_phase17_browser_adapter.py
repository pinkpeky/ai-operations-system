"""phase17 browser adapter foundation

Revision ID: 0011_phase17_browser
Revises: 0010_phase16_planning
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_phase17_browser"
down_revision = "0010_phase16_planning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Browser Adapter Foundation tables."""

    op.create_table(
        "browser_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="mock"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_browser_sessions_workspace_id", "browser_sessions", ["workspace_id"])
    op.create_index("ix_browser_sessions_user_id", "browser_sessions", ["user_id"])
    op.create_index("ix_browser_sessions_provider", "browser_sessions", ["provider"])
    op.create_index("ix_browser_sessions_status", "browser_sessions", ["status"])

    op.create_table(
        "browser_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("browser_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("target", sa.Text(), nullable=True),
        sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("output_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_browser_actions_workspace_id", "browser_actions", ["workspace_id"])
    op.create_index("ix_browser_actions_session_id", "browser_actions", ["session_id"])
    op.create_index("ix_browser_actions_action_type", "browser_actions", ["action_type"])
    op.create_index("ix_browser_actions_status", "browser_actions", ["status"])

    op.create_table(
        "browser_action_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("browser_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "action_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("browser_actions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("level", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_browser_action_logs_workspace_id", "browser_action_logs", ["workspace_id"])
    op.create_index("ix_browser_action_logs_session_id", "browser_action_logs", ["session_id"])
    op.create_index("ix_browser_action_logs_action_id", "browser_action_logs", ["action_id"])
    op.create_index("ix_browser_action_logs_level", "browser_action_logs", ["level"])


def downgrade() -> None:
    """Drop Browser Adapter Foundation tables."""

    op.drop_index("ix_browser_action_logs_level", table_name="browser_action_logs")
    op.drop_index("ix_browser_action_logs_action_id", table_name="browser_action_logs")
    op.drop_index("ix_browser_action_logs_session_id", table_name="browser_action_logs")
    op.drop_index("ix_browser_action_logs_workspace_id", table_name="browser_action_logs")
    op.drop_table("browser_action_logs")

    op.drop_index("ix_browser_actions_status", table_name="browser_actions")
    op.drop_index("ix_browser_actions_action_type", table_name="browser_actions")
    op.drop_index("ix_browser_actions_session_id", table_name="browser_actions")
    op.drop_index("ix_browser_actions_workspace_id", table_name="browser_actions")
    op.drop_table("browser_actions")

    op.drop_index("ix_browser_sessions_status", table_name="browser_sessions")
    op.drop_index("ix_browser_sessions_provider", table_name="browser_sessions")
    op.drop_index("ix_browser_sessions_user_id", table_name="browser_sessions")
    op.drop_index("ix_browser_sessions_workspace_id", table_name="browser_sessions")
    op.drop_table("browser_sessions")
