"""Phase 24 human-in-the-loop browser control.

Revision ID: 0017_phase24_human_control
Revises: 0016_phase23_profile_health
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0017_phase24_human_control"
down_revision = "0016_phase23_profile_health"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "browser_human_control_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("browser_session_id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=True),
        sa.Column("worker_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="requested"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["browser_session_id"], ["browser_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["browser_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["worker_id"], ["browser_workers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_human_control_sessions_workspace_id", "browser_human_control_sessions", ["workspace_id"])
    op.create_index("ix_browser_human_control_sessions_browser_session_id", "browser_human_control_sessions", ["browser_session_id"])
    op.create_index("ix_browser_human_control_sessions_profile_id", "browser_human_control_sessions", ["profile_id"])
    op.create_index("ix_browser_human_control_sessions_worker_id", "browser_human_control_sessions", ["worker_id"])
    op.create_index("ix_browser_human_control_sessions_status", "browser_human_control_sessions", ["status"])
    op.create_index("ix_browser_human_control_sessions_requested_by", "browser_human_control_sessions", ["requested_by"])
    op.create_index("ix_browser_human_control_sessions_approved_by", "browser_human_control_sessions", ["approved_by"])
    op.create_index("ix_browser_human_control_sessions_expires_at", "browser_human_control_sessions", ["expires_at"])

    op.create_table(
        "browser_human_control_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("control_session_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["control_session_id"], ["browser_human_control_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_human_control_events_workspace_id", "browser_human_control_events", ["workspace_id"])
    op.create_index("ix_browser_human_control_events_control_session_id", "browser_human_control_events", ["control_session_id"])
    op.create_index("ix_browser_human_control_events_event_type", "browser_human_control_events", ["event_type"])

    op.add_column("browser_sessions", sa.Column("human_control_status", sa.String(length=32), nullable=True))
    op.add_column("browser_sessions", sa.Column("human_control_session_id", sa.Uuid(), nullable=True))
    op.add_column("browser_sessions", sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("browser_sessions", sa.Column("resumed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_browser_sessions_human_control_status", "browser_sessions", ["human_control_status"])
    op.create_index("ix_browser_sessions_human_control_session_id", "browser_sessions", ["human_control_session_id"])
    op.create_foreign_key(
        "fk_browser_sessions_human_control_session_id",
        "browser_sessions",
        "browser_human_control_sessions",
        ["human_control_session_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_browser_sessions_human_control_session_id", "browser_sessions", type_="foreignkey")
    op.drop_index("ix_browser_sessions_human_control_session_id", table_name="browser_sessions")
    op.drop_index("ix_browser_sessions_human_control_status", table_name="browser_sessions")
    op.drop_column("browser_sessions", "resumed_at")
    op.drop_column("browser_sessions", "paused_at")
    op.drop_column("browser_sessions", "human_control_session_id")
    op.drop_column("browser_sessions", "human_control_status")

    op.drop_index("ix_browser_human_control_events_event_type", table_name="browser_human_control_events")
    op.drop_index("ix_browser_human_control_events_control_session_id", table_name="browser_human_control_events")
    op.drop_index("ix_browser_human_control_events_workspace_id", table_name="browser_human_control_events")
    op.drop_table("browser_human_control_events")

    op.drop_index("ix_browser_human_control_sessions_expires_at", table_name="browser_human_control_sessions")
    op.drop_index("ix_browser_human_control_sessions_approved_by", table_name="browser_human_control_sessions")
    op.drop_index("ix_browser_human_control_sessions_requested_by", table_name="browser_human_control_sessions")
    op.drop_index("ix_browser_human_control_sessions_status", table_name="browser_human_control_sessions")
    op.drop_index("ix_browser_human_control_sessions_worker_id", table_name="browser_human_control_sessions")
    op.drop_index("ix_browser_human_control_sessions_profile_id", table_name="browser_human_control_sessions")
    op.drop_index("ix_browser_human_control_sessions_browser_session_id", table_name="browser_human_control_sessions")
    op.drop_index("ix_browser_human_control_sessions_workspace_id", table_name="browser_human_control_sessions")
    op.drop_table("browser_human_control_sessions")
