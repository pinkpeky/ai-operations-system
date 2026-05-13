"""Phase 25 browser worker UI access placeholder.

Revision ID: 0018_phase25_browser_ui_access
Revises: 0017_phase24_human_control
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0018_phase25_browser_ui_access"
down_revision = "0017_phase24_human_control"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "browser_ui_access_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("browser_session_id", sa.Uuid(), nullable=False),
        sa.Column("human_control_session_id", sa.Uuid(), nullable=True),
        sa.Column("worker_id", sa.Uuid(), nullable=True),
        sa.Column("access_token_hash", sa.String(length=128), nullable=False),
        sa.Column("remote_control_url", sa.Text(), nullable=False),
        sa.Column("live_view_url", sa.Text(), nullable=False),
        sa.Column("devtools_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="requested"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["browser_session_id"], ["browser_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["human_control_session_id"], ["browser_human_control_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["worker_id"], ["browser_workers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_ui_access_sessions_workspace_id", "browser_ui_access_sessions", ["workspace_id"])
    op.create_index("ix_browser_ui_access_sessions_browser_session_id", "browser_ui_access_sessions", ["browser_session_id"])
    op.create_index(
        "ix_browser_ui_access_sessions_human_control_session_id",
        "browser_ui_access_sessions",
        ["human_control_session_id"],
    )
    op.create_index("ix_browser_ui_access_sessions_worker_id", "browser_ui_access_sessions", ["worker_id"])
    op.create_index("ix_browser_ui_access_sessions_access_token_hash", "browser_ui_access_sessions", ["access_token_hash"])
    op.create_index("ix_browser_ui_access_sessions_status", "browser_ui_access_sessions", ["status"])
    op.create_index("ix_browser_ui_access_sessions_expires_at", "browser_ui_access_sessions", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_browser_ui_access_sessions_expires_at", table_name="browser_ui_access_sessions")
    op.drop_index("ix_browser_ui_access_sessions_status", table_name="browser_ui_access_sessions")
    op.drop_index("ix_browser_ui_access_sessions_access_token_hash", table_name="browser_ui_access_sessions")
    op.drop_index("ix_browser_ui_access_sessions_worker_id", table_name="browser_ui_access_sessions")
    op.drop_index("ix_browser_ui_access_sessions_human_control_session_id", table_name="browser_ui_access_sessions")
    op.drop_index("ix_browser_ui_access_sessions_browser_session_id", table_name="browser_ui_access_sessions")
    op.drop_index("ix_browser_ui_access_sessions_workspace_id", table_name="browser_ui_access_sessions")
    op.drop_table("browser_ui_access_sessions")
