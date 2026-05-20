"""Phase 61I commercial operation execution runs.

Revision ID: 0043_phase61i_exec_runs
Revises: 0042_phase61h_exec_requests
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0043_phase61i_exec_runs"
down_revision = "0042_phase61h_exec_requests"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_execution_runs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("execution_request_id", sa.Uuid(), nullable=False),
        sa.Column("deliverable_id", sa.Uuid(), nullable=False),
        sa.Column("output_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("execution_type", sa.String(length=64), nullable=False),
        sa.Column("execution_mode", sa.String(length=32), nullable=False),
        sa.Column("execution_target", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("run_status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("input_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("runbook_snapshot", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("readiness_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("expected_outputs", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("runtime_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("recovery_plan", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("operator_notes", sa.Text(), nullable=True),
        sa.Column("queued_by", sa.String(length=128), nullable=True),
        sa.Column("started_by", sa.String(length=128), nullable=True),
        sa.Column("completed_by", sa.String(length=128), nullable=True),
        sa.Column("cancelled_by", sa.String(length=128), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deliverable_id"], ["commercial_operation_deliverables.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["execution_request_id"], ["commercial_operation_execution_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["output_artifact_id"], ["output_artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "execution_request_id",
        "deliverable_id",
        "output_artifact_id",
        "step_key",
        "channel",
        "execution_type",
        "execution_mode",
        "execution_target",
        "run_status",
        "queued_by",
        "started_by",
        "completed_by",
        "cancelled_by",
    ):
        op.create_index(
            f"ix_commercial_operation_execution_runs_{column}",
            "commercial_operation_execution_runs",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_execution_runs")
