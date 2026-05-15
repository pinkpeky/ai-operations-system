"""Phase 35A browser runtime observability and replay.

Revision ID: 0023_phase35a_browser_runtime
Revises: 0022_phase34_browser_runtime
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0023_phase35a_browser_runtime"
down_revision = "0022_phase34_browser_runtime"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "browser_runtime_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("runtime_session_id", sa.Uuid(), nullable=False),
        sa.Column("worker_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["runtime_session_id"], ["browser_runtime_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["worker_id"], ["browser_workers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_runtime_events_workspace_id", "browser_runtime_events", ["workspace_id"])
    op.create_index("ix_browser_runtime_events_runtime_session_id", "browser_runtime_events", ["runtime_session_id"])
    op.create_index("ix_browser_runtime_events_worker_id", "browser_runtime_events", ["worker_id"])
    op.create_index("ix_browser_runtime_events_event_type", "browser_runtime_events", ["event_type"])
    op.create_index("ix_browser_runtime_events_status", "browser_runtime_events", ["status"])
    op.create_index("ix_browser_runtime_events_created_at", "browser_runtime_events", ["created_at"])

    op.create_table(
        "browser_runtime_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("runtime_session_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_type", sa.String(length=32), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("page_title", sa.Text(), nullable=True),
        sa.Column("html_path", sa.Text(), nullable=True),
        sa.Column("text_path", sa.Text(), nullable=True),
        sa.Column("screenshot_path", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["runtime_session_id"], ["browser_runtime_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_runtime_snapshots_workspace_id", "browser_runtime_snapshots", ["workspace_id"])
    op.create_index("ix_browser_runtime_snapshots_runtime_session_id", "browser_runtime_snapshots", ["runtime_session_id"])
    op.create_index("ix_browser_runtime_snapshots_snapshot_type", "browser_runtime_snapshots", ["snapshot_type"])
    op.create_index("ix_browser_runtime_snapshots_created_at", "browser_runtime_snapshots", ["created_at"])

    op.create_table(
        "browser_runtime_replays",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("runtime_session_id", sa.Uuid(), nullable=False),
        sa.Column("replay_status", sa.String(length=32), nullable=False, server_default="created"),
        sa.Column("replay_steps", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("source_event_ids", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("source_snapshot_ids", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["runtime_session_id"], ["browser_runtime_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_runtime_replays_workspace_id", "browser_runtime_replays", ["workspace_id"])
    op.create_index("ix_browser_runtime_replays_runtime_session_id", "browser_runtime_replays", ["runtime_session_id"])
    op.create_index("ix_browser_runtime_replays_replay_status", "browser_runtime_replays", ["replay_status"])
    op.create_index("ix_browser_runtime_replays_created_at", "browser_runtime_replays", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_browser_runtime_replays_created_at", table_name="browser_runtime_replays")
    op.drop_index("ix_browser_runtime_replays_replay_status", table_name="browser_runtime_replays")
    op.drop_index("ix_browser_runtime_replays_runtime_session_id", table_name="browser_runtime_replays")
    op.drop_index("ix_browser_runtime_replays_workspace_id", table_name="browser_runtime_replays")
    op.drop_table("browser_runtime_replays")

    op.drop_index("ix_browser_runtime_snapshots_created_at", table_name="browser_runtime_snapshots")
    op.drop_index("ix_browser_runtime_snapshots_snapshot_type", table_name="browser_runtime_snapshots")
    op.drop_index("ix_browser_runtime_snapshots_runtime_session_id", table_name="browser_runtime_snapshots")
    op.drop_index("ix_browser_runtime_snapshots_workspace_id", table_name="browser_runtime_snapshots")
    op.drop_table("browser_runtime_snapshots")

    op.drop_index("ix_browser_runtime_events_created_at", table_name="browser_runtime_events")
    op.drop_index("ix_browser_runtime_events_status", table_name="browser_runtime_events")
    op.drop_index("ix_browser_runtime_events_event_type", table_name="browser_runtime_events")
    op.drop_index("ix_browser_runtime_events_worker_id", table_name="browser_runtime_events")
    op.drop_index("ix_browser_runtime_events_runtime_session_id", table_name="browser_runtime_events")
    op.drop_index("ix_browser_runtime_events_workspace_id", table_name="browser_runtime_events")
    op.drop_table("browser_runtime_events")
