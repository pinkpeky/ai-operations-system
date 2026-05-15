"""Phase 34 remote browser runtime foundation.

Revision ID: 0022_phase34_browser_runtime
Revises: 0021_phase33_conversation
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0022_phase34_browser_runtime"
down_revision = "0021_phase33_conversation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "browser_runtime_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("worker_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="remote"),
        sa.Column("browser", sa.String(length=64), nullable=False, server_default="chromium"),
        sa.Column("session_status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.ForeignKeyConstraint(["worker_id"], ["browser_workers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_runtime_sessions_workspace_id", "browser_runtime_sessions", ["workspace_id"])
    op.create_index("ix_browser_runtime_sessions_worker_id", "browser_runtime_sessions", ["worker_id"])
    op.create_index("ix_browser_runtime_sessions_provider", "browser_runtime_sessions", ["provider"])
    op.create_index("ix_browser_runtime_sessions_browser", "browser_runtime_sessions", ["browser"])
    op.create_index("ix_browser_runtime_sessions_session_status", "browser_runtime_sessions", ["session_status"])
    op.create_index("ix_browser_runtime_sessions_last_activity_at", "browser_runtime_sessions", ["last_activity_at"])


def downgrade() -> None:
    op.drop_index("ix_browser_runtime_sessions_last_activity_at", table_name="browser_runtime_sessions")
    op.drop_index("ix_browser_runtime_sessions_session_status", table_name="browser_runtime_sessions")
    op.drop_index("ix_browser_runtime_sessions_browser", table_name="browser_runtime_sessions")
    op.drop_index("ix_browser_runtime_sessions_provider", table_name="browser_runtime_sessions")
    op.drop_index("ix_browser_runtime_sessions_worker_id", table_name="browser_runtime_sessions")
    op.drop_index("ix_browser_runtime_sessions_workspace_id", table_name="browser_runtime_sessions")
    op.drop_table("browser_runtime_sessions")
