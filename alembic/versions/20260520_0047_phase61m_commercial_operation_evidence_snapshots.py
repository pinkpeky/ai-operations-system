"""Phase 61M commercial operation evidence snapshots.

Revision ID: 0047_phase61m_evidence_snapshots
Revises: 0046_phase61l_opt_decisions
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0047_phase61m_evidence_snapshots"
down_revision = "0046_phase61l_opt_decisions"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_evidence_snapshots",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("deliverable_id", sa.Uuid(), nullable=False),
        sa.Column("content_draft_id", sa.Uuid(), nullable=False),
        sa.Column("output_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("evidence_type", sa.String(length=64), nullable=False, server_default="rag_snapshot"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("snapshot_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("knowledge_collection", sa.String(length=128), nullable=True),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.Column("relevance_notes", sa.Text(), nullable=True),
        sa.Column("source_document_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("source_links", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("evidence_items", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("coverage_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("snapshot_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
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
        sa.ForeignKeyConstraint(["content_draft_id"], ["commercial_operation_content_drafts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["deliverable_id"], ["commercial_operation_deliverables.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["output_artifact_id"], ["output_artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "deliverable_id",
        "content_draft_id",
        "output_artifact_id",
        "step_key",
        "channel",
        "evidence_type",
        "snapshot_status",
        "knowledge_collection",
        "created_by",
        "updated_by",
        "approved_by",
    ):
        op.create_index(
            f"ix_commercial_op_evidence_snapshots_{column}",
            "commercial_operation_evidence_snapshots",
            [column],
        )
    op.add_column(
        "commercial_operation_execution_requests",
        sa.Column("evidence_snapshot_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
    )
    op.add_column(
        "commercial_operation_execution_requests",
        sa.Column("operator_checklist", sa.JSON(), nullable=False, server_default=_json_default("[]")),
    )
    op.add_column(
        "commercial_operation_execution_runs",
        sa.Column("evidence_snapshot_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
    )
    op.add_column(
        "commercial_operation_execution_runs",
        sa.Column("operator_checklist_snapshot", sa.JSON(), nullable=False, server_default=_json_default("[]")),
    )


def downgrade() -> None:
    op.drop_column("commercial_operation_execution_runs", "operator_checklist_snapshot")
    op.drop_column("commercial_operation_execution_runs", "evidence_snapshot_ids")
    op.drop_column("commercial_operation_execution_requests", "operator_checklist")
    op.drop_column("commercial_operation_execution_requests", "evidence_snapshot_ids")
    op.drop_table("commercial_operation_evidence_snapshots")
