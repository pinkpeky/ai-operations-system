"""Phase 61H commercial operation execution requests.

Revision ID: 0042_phase61h_exec_requests
Revises: 0041_phase61g_deliverables
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0042_phase61h_exec_requests"
down_revision = "0041_phase61g_deliverables"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_execution_requests",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("deliverable_id", sa.Uuid(), nullable=False),
        sa.Column("output_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("execution_type", sa.String(length=64), nullable=False, server_default="manual_handoff"),
        sa.Column("execution_mode", sa.String(length=32), nullable=False, server_default="metadata_only"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("request_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("execution_target", sa.String(length=128), nullable=True),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("runbook", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("readiness_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("expected_outputs", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("handoff_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("prepared_by", sa.String(length=128), nullable=True),
        sa.Column("cancelled_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("prepared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deliverable_id"], ["commercial_operation_deliverables.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["output_artifact_id"], ["output_artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "deliverable_id",
        "output_artifact_id",
        "step_key",
        "channel",
        "execution_type",
        "execution_mode",
        "request_status",
        "execution_target",
        "requested_by",
        "updated_by",
        "approved_by",
        "prepared_by",
        "cancelled_by",
    ):
        op.create_index(
            f"ix_commercial_operation_execution_requests_{column}",
            "commercial_operation_execution_requests",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_execution_requests")
