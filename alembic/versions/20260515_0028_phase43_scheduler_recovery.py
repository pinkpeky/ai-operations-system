"""Phase 43 task scheduler persistence and recovery.

Revision ID: 0028_phase43_scheduler_recovery
Revises: 0027_phase42_task_orchestration
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0028_phase43_scheduler_recovery"
down_revision = "0027_phase42_task_orchestration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("task_runs", sa.Column("lease_owner", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column("lease_token", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("task_runs", sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("task_runs", sa.Column("recovery_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("task_runs", sa.Column("last_recovered_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("task_runs", sa.Column("recovery_reason", sa.Text(), nullable=True))
    op.add_column("task_runs", sa.Column("failure_category", sa.String(length=64), nullable=True))
    op.add_column("task_runs", sa.Column("failure_reason", sa.Text(), nullable=True))
    op.add_column("task_runs", sa.Column("recoverable", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("task_runs", sa.Column("suggested_action", sa.Text(), nullable=True))
    op.add_column("task_runs", sa.Column("last_event_summary", sa.Text(), nullable=True))
    op.create_index("ix_task_runs_lease_owner", "task_runs", ["lease_owner"])
    op.create_index("ix_task_runs_lease_token", "task_runs", ["lease_token"])
    op.create_index("ix_task_runs_lease_expires_at", "task_runs", ["lease_expires_at"])
    op.create_index("ix_task_runs_heartbeat_at", "task_runs", ["heartbeat_at"])
    op.create_index("ix_task_runs_failure_category", "task_runs", ["failure_category"])

    op.create_table(
        "task_scheduler_state",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("scheduler_name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_scan_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active_task_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("recovered_task_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_scheduler_state_workspace_id", "task_scheduler_state", ["workspace_id"])
    op.create_index("ix_task_scheduler_state_scheduler_name", "task_scheduler_state", ["scheduler_name"])
    op.create_index("ix_task_scheduler_state_status", "task_scheduler_state", ["status"])
    op.create_index("ix_task_scheduler_state_heartbeat_at", "task_scheduler_state", ["heartbeat_at"])
    op.create_index("ix_task_scheduler_state_last_scan_at", "task_scheduler_state", ["last_scan_at"])


def downgrade() -> None:
    op.drop_index("ix_task_scheduler_state_last_scan_at", table_name="task_scheduler_state")
    op.drop_index("ix_task_scheduler_state_heartbeat_at", table_name="task_scheduler_state")
    op.drop_index("ix_task_scheduler_state_status", table_name="task_scheduler_state")
    op.drop_index("ix_task_scheduler_state_scheduler_name", table_name="task_scheduler_state")
    op.drop_index("ix_task_scheduler_state_workspace_id", table_name="task_scheduler_state")
    op.drop_table("task_scheduler_state")

    op.drop_index("ix_task_runs_failure_category", table_name="task_runs")
    op.drop_index("ix_task_runs_heartbeat_at", table_name="task_runs")
    op.drop_index("ix_task_runs_lease_expires_at", table_name="task_runs")
    op.drop_index("ix_task_runs_lease_token", table_name="task_runs")
    op.drop_index("ix_task_runs_lease_owner", table_name="task_runs")
    op.drop_column("task_runs", "last_event_summary")
    op.drop_column("task_runs", "suggested_action")
    op.drop_column("task_runs", "recoverable")
    op.drop_column("task_runs", "failure_reason")
    op.drop_column("task_runs", "failure_category")
    op.drop_column("task_runs", "recovery_reason")
    op.drop_column("task_runs", "last_recovered_at")
    op.drop_column("task_runs", "recovery_count")
    op.drop_column("task_runs", "heartbeat_at")
    op.drop_column("task_runs", "lease_expires_at")
    op.drop_column("task_runs", "lease_token")
    op.drop_column("task_runs", "lease_owner")
