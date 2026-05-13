"""Phase 23 browser profile health and recovery.

Revision ID: 0016_phase23_profile_health
Revises: 0015_phase22_profiles
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0016_phase23_profile_health"
down_revision = "0015_phase22_profiles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "browser_profiles",
        sa.Column("health_status", sa.String(length=32), nullable=False, server_default="healthy"),
    )
    op.add_column("browser_profiles", sa.Column("last_health_check_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("browser_profiles", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column("browser_profiles", sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("browser_profiles", sa.Column("corrupted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("browser_profiles", sa.Column("backup_path", sa.Text(), nullable=True))
    op.add_column("browser_profiles", sa.Column("last_backup_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_browser_profiles_health_status", "browser_profiles", ["health_status"])

    op.create_table(
        "browser_profile_usage_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["browser_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["browser_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_profile_usage_logs_workspace_id", "browser_profile_usage_logs", ["workspace_id"])
    op.create_index("ix_browser_profile_usage_logs_profile_id", "browser_profile_usage_logs", ["profile_id"])
    op.create_index("ix_browser_profile_usage_logs_session_id", "browser_profile_usage_logs", ["session_id"])
    op.create_index("ix_browser_profile_usage_logs_action", "browser_profile_usage_logs", ["action"])


def downgrade() -> None:
    op.drop_index("ix_browser_profile_usage_logs_action", table_name="browser_profile_usage_logs")
    op.drop_index("ix_browser_profile_usage_logs_session_id", table_name="browser_profile_usage_logs")
    op.drop_index("ix_browser_profile_usage_logs_profile_id", table_name="browser_profile_usage_logs")
    op.drop_index("ix_browser_profile_usage_logs_workspace_id", table_name="browser_profile_usage_logs")
    op.drop_table("browser_profile_usage_logs")

    op.drop_index("ix_browser_profiles_health_status", table_name="browser_profiles")
    op.drop_column("browser_profiles", "last_backup_at")
    op.drop_column("browser_profiles", "backup_path")
    op.drop_column("browser_profiles", "corrupted_at")
    op.drop_column("browser_profiles", "usage_count")
    op.drop_column("browser_profiles", "last_error")
    op.drop_column("browser_profiles", "last_health_check_at")
    op.drop_column("browser_profiles", "health_status")
