"""phase19 remote browser worker foundation

Revision ID: 0013_phase19_browser_worker
Revises: 0012_phase18_playwright
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0013_phase19_browser_worker"
down_revision = "0012_phase18_playwright"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create remote browser worker metadata tables."""

    op.create_table(
        "browser_workers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("worker_name", sa.String(length=128), nullable=False),
        sa.Column("worker_type", sa.String(length=64), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="offline"),
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_workers_workspace_id", "browser_workers", ["workspace_id"])
    op.create_index("ix_browser_workers_worker_name", "browser_workers", ["worker_name"])
    op.create_index("ix_browser_workers_worker_type", "browser_workers", ["worker_type"])
    op.create_index("ix_browser_workers_status", "browser_workers", ["status"])

    op.create_table(
        "browser_worker_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("worker_id", sa.Uuid(), nullable=False),
        sa.Column("remote_session_id", sa.String(length=128), nullable=False),
        sa.Column("local_browser_session_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["worker_id"], ["browser_workers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["local_browser_session_id"], ["browser_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_worker_sessions_workspace_id", "browser_worker_sessions", ["workspace_id"])
    op.create_index("ix_browser_worker_sessions_worker_id", "browser_worker_sessions", ["worker_id"])
    op.create_index("ix_browser_worker_sessions_remote_session_id", "browser_worker_sessions", ["remote_session_id"])
    op.create_index("ix_browser_worker_sessions_local_browser_session_id", "browser_worker_sessions", ["local_browser_session_id"])
    op.create_index("ix_browser_worker_sessions_status", "browser_worker_sessions", ["status"])

    op.create_table(
        "browser_worker_actions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("worker_id", sa.Uuid(), nullable=False),
        sa.Column("worker_session_id", sa.Uuid(), nullable=False),
        sa.Column("local_action_id", sa.Uuid(), nullable=True),
        sa.Column("remote_action_id", sa.String(length=128), nullable=True),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["worker_id"], ["browser_workers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["worker_session_id"], ["browser_worker_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["local_action_id"], ["browser_actions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_worker_actions_workspace_id", "browser_worker_actions", ["workspace_id"])
    op.create_index("ix_browser_worker_actions_worker_id", "browser_worker_actions", ["worker_id"])
    op.create_index("ix_browser_worker_actions_worker_session_id", "browser_worker_actions", ["worker_session_id"])
    op.create_index("ix_browser_worker_actions_local_action_id", "browser_worker_actions", ["local_action_id"])
    op.create_index("ix_browser_worker_actions_remote_action_id", "browser_worker_actions", ["remote_action_id"])
    op.create_index("ix_browser_worker_actions_action_type", "browser_worker_actions", ["action_type"])
    op.create_index("ix_browser_worker_actions_status", "browser_worker_actions", ["status"])


def downgrade() -> None:
    """Drop remote browser worker metadata tables."""

    op.drop_index("ix_browser_worker_actions_status", table_name="browser_worker_actions")
    op.drop_index("ix_browser_worker_actions_action_type", table_name="browser_worker_actions")
    op.drop_index("ix_browser_worker_actions_remote_action_id", table_name="browser_worker_actions")
    op.drop_index("ix_browser_worker_actions_local_action_id", table_name="browser_worker_actions")
    op.drop_index("ix_browser_worker_actions_worker_session_id", table_name="browser_worker_actions")
    op.drop_index("ix_browser_worker_actions_worker_id", table_name="browser_worker_actions")
    op.drop_index("ix_browser_worker_actions_workspace_id", table_name="browser_worker_actions")
    op.drop_table("browser_worker_actions")

    op.drop_index("ix_browser_worker_sessions_status", table_name="browser_worker_sessions")
    op.drop_index("ix_browser_worker_sessions_local_browser_session_id", table_name="browser_worker_sessions")
    op.drop_index("ix_browser_worker_sessions_remote_session_id", table_name="browser_worker_sessions")
    op.drop_index("ix_browser_worker_sessions_worker_id", table_name="browser_worker_sessions")
    op.drop_index("ix_browser_worker_sessions_workspace_id", table_name="browser_worker_sessions")
    op.drop_table("browser_worker_sessions")

    op.drop_index("ix_browser_workers_status", table_name="browser_workers")
    op.drop_index("ix_browser_workers_worker_type", table_name="browser_workers")
    op.drop_index("ix_browser_workers_worker_name", table_name="browser_workers")
    op.drop_index("ix_browser_workers_workspace_id", table_name="browser_workers")
    op.drop_table("browser_workers")
