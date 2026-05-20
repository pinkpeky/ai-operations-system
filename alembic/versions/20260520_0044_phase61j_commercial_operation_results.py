"""Phase 61J commercial operation results.

Revision ID: 0044_phase61j_results
Revises: 0043_phase61i_exec_runs
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0044_phase61j_results"
down_revision = "0043_phase61i_exec_runs"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_results",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("execution_run_id", sa.Uuid(), nullable=False),
        sa.Column("execution_request_id", sa.Uuid(), nullable=False),
        sa.Column("deliverable_id", sa.Uuid(), nullable=False),
        sa.Column("output_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("result_type", sa.String(length=64), nullable=False, server_default="operator_report"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("result_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("outcome_summary", sa.Text(), nullable=True),
        sa.Column("observed_metrics", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("commercial_signals", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("evidence_links", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("follow_up_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("result_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("recommendation_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deliverable_id"], ["commercial_operation_deliverables.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["execution_request_id"], ["commercial_operation_execution_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["execution_run_id"], ["commercial_operation_execution_runs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["output_artifact_id"], ["output_artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "execution_run_id",
        "execution_request_id",
        "deliverable_id",
        "output_artifact_id",
        "step_key",
        "channel",
        "result_type",
        "result_status",
        "created_by",
        "updated_by",
        "approved_by",
    ):
        op.create_index(
            f"ix_commercial_operation_results_{column}",
            "commercial_operation_results",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_results")
