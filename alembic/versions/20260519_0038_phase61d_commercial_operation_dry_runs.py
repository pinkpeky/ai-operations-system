"""Phase 61D commercial operation dry-runs.

Revision ID: 0038_phase61d_op_dry_runs
Revises: 0037_phase61c_op_approvals
Create Date: 2026-05-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0038_phase61d_op_dry_runs"
down_revision = "0037_phase61c_op_approvals"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_dry_runs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("approval_id", sa.Uuid(), nullable=False),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("dry_run_status", sa.String(length=32), nullable=False, server_default="created"),
        sa.Column("execution_mode", sa.String(length=32), nullable=False, server_default="metadata_only"),
        sa.Column("execution_target", sa.String(length=128), nullable=True),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("runbook", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("expected_outputs", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("readiness_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(length=128), nullable=True),
        sa.Column("completed_by", sa.String(length=128), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["approval_id"], ["commercial_operation_approvals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "approval_id",
        "step_key",
        "dry_run_status",
        "execution_mode",
        "execution_target",
        "requested_by",
        "completed_by",
    ):
        op.create_index(f"ix_commercial_operation_dry_runs_{column}", "commercial_operation_dry_runs", [column])


def downgrade() -> None:
    op.drop_table("commercial_operation_dry_runs")
