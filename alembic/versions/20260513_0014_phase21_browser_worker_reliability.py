"""phase21 browser worker reliability

Revision ID: 0014_phase21_worker_reliability
Revises: 0013_phase19_browser_worker
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0014_phase21_worker_reliability"
down_revision = "0013_phase19_browser_worker"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add worker capacity and action retry fields."""

    op.add_column("browser_workers", sa.Column("max_sessions", sa.Integer(), nullable=False, server_default="5"))
    op.add_column("browser_workers", sa.Column("active_sessions", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("browser_workers", sa.Column("max_actions_per_minute", sa.Integer(), nullable=False, server_default="60"))
    op.add_column("browser_workers", sa.Column("current_load", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("browser_workers", sa.Column("priority", sa.Integer(), nullable=False, server_default="100"))
    op.add_column("browser_workers", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_index("ix_browser_workers_current_load", "browser_workers", ["current_load"])
    op.create_index("ix_browser_workers_priority", "browser_workers", ["priority"])

    op.add_column("browser_worker_actions", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("browser_worker_actions", sa.Column("max_retries", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    """Remove worker reliability fields."""

    op.drop_column("browser_worker_actions", "max_retries")
    op.drop_column("browser_worker_actions", "retry_count")

    op.drop_index("ix_browser_workers_priority", table_name="browser_workers")
    op.drop_index("ix_browser_workers_current_load", table_name="browser_workers")
    op.drop_column("browser_workers", "error_message")
    op.drop_column("browser_workers", "priority")
    op.drop_column("browser_workers", "current_load")
    op.drop_column("browser_workers", "max_actions_per_minute")
    op.drop_column("browser_workers", "active_sessions")
    op.drop_column("browser_workers", "max_sessions")
