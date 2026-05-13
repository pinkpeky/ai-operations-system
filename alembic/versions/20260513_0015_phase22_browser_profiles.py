"""phase22 browser profiles

Revision ID: 0015_phase22_profiles
Revises: 0014_phase21_worker_reliability
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0015_phase22_profiles"
down_revision = "0014_phase21_worker_reliability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create browser profile lifecycle table and link browser sessions."""

    op.create_table(
        "browser_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("profile_name", sa.String(length=128), nullable=False),
        sa.Column("profile_type", sa.String(length=64), nullable=False, server_default="persistent"),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="remote"),
        sa.Column("profile_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="available"),
        sa.Column("locked_by_session_id", sa.Uuid(), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["locked_by_session_id"], ["browser_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_profiles_workspace_id", "browser_profiles", ["workspace_id"])
    op.create_index("ix_browser_profiles_user_id", "browser_profiles", ["user_id"])
    op.create_index("ix_browser_profiles_profile_name", "browser_profiles", ["profile_name"])
    op.create_index("ix_browser_profiles_profile_type", "browser_profiles", ["profile_type"])
    op.create_index("ix_browser_profiles_provider", "browser_profiles", ["provider"])
    op.create_index("ix_browser_profiles_status", "browser_profiles", ["status"])
    op.create_index("ix_browser_profiles_locked_by_session_id", "browser_profiles", ["locked_by_session_id"])

    op.add_column("browser_sessions", sa.Column("profile_id", sa.Uuid(), nullable=True))
    op.add_column("browser_sessions", sa.Column("profile_path", sa.Text(), nullable=True))
    op.add_column(
        "browser_sessions",
        sa.Column("persistent_context_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_browser_sessions_profile_id", "browser_sessions", ["profile_id"])
    op.create_foreign_key(
        "fk_browser_sessions_profile_id_browser_profiles",
        "browser_sessions",
        "browser_profiles",
        ["profile_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Remove browser profile lifecycle table and session links."""

    op.drop_constraint("fk_browser_sessions_profile_id_browser_profiles", "browser_sessions", type_="foreignkey")
    op.drop_index("ix_browser_sessions_profile_id", table_name="browser_sessions")
    op.drop_column("browser_sessions", "persistent_context_enabled")
    op.drop_column("browser_sessions", "profile_path")
    op.drop_column("browser_sessions", "profile_id")

    op.drop_index("ix_browser_profiles_locked_by_session_id", table_name="browser_profiles")
    op.drop_index("ix_browser_profiles_status", table_name="browser_profiles")
    op.drop_index("ix_browser_profiles_provider", table_name="browser_profiles")
    op.drop_index("ix_browser_profiles_profile_type", table_name="browser_profiles")
    op.drop_index("ix_browser_profiles_profile_name", table_name="browser_profiles")
    op.drop_index("ix_browser_profiles_user_id", table_name="browser_profiles")
    op.drop_index("ix_browser_profiles_workspace_id", table_name="browser_profiles")
    op.drop_table("browser_profiles")
