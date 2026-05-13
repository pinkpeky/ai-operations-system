"""phase28 openclaw worker adapter foundation

Revision ID: 0020_phase28_openclaw_adapter
Revises: 0019_phase26_browser_security
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0020_phase28_openclaw_adapter"
down_revision = "0019_phase26_browser_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "openclaw_action_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("worker_id", sa.Uuid(), nullable=True),
        sa.Column("action_type", sa.String(length=128), nullable=False),
        sa.Column("target", sa.Text(), nullable=True),
        sa.Column("input_payload", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("output_payload", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="mock"),
        sa.Column("mock", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["worker_id"], ["browser_workers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_openclaw_action_logs_workspace_id", "openclaw_action_logs", ["workspace_id"])
    op.create_index("ix_openclaw_action_logs_worker_id", "openclaw_action_logs", ["worker_id"])
    op.create_index("ix_openclaw_action_logs_action_type", "openclaw_action_logs", ["action_type"])
    op.create_index("ix_openclaw_action_logs_success", "openclaw_action_logs", ["success"])
    op.create_index("ix_openclaw_action_logs_provider", "openclaw_action_logs", ["provider"])
    op.create_index("ix_openclaw_action_logs_mock", "openclaw_action_logs", ["mock"])


def downgrade() -> None:
    op.drop_index("ix_openclaw_action_logs_mock", table_name="openclaw_action_logs")
    op.drop_index("ix_openclaw_action_logs_provider", table_name="openclaw_action_logs")
    op.drop_index("ix_openclaw_action_logs_success", table_name="openclaw_action_logs")
    op.drop_index("ix_openclaw_action_logs_action_type", table_name="openclaw_action_logs")
    op.drop_index("ix_openclaw_action_logs_worker_id", table_name="openclaw_action_logs")
    op.drop_index("ix_openclaw_action_logs_workspace_id", table_name="openclaw_action_logs")
    op.drop_table("openclaw_action_logs")
