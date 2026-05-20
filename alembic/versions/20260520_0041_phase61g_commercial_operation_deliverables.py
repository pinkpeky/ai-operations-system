"""Phase 61G commercial operation deliverables.

Revision ID: 0041_phase61g_deliverables
Revises: 0040_phase61f_asset_requests
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0041_phase61g_deliverables"
down_revision = "0040_phase61f_asset_requests"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_deliverables",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("content_draft_id", sa.Uuid(), nullable=False),
        sa.Column("output_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("deliverable_type", sa.String(length=64), nullable=False, server_default="content_package"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("deliverable_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("delivery_notes", sa.Text(), nullable=True),
        sa.Column("asset_request_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("quality_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("package_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("packaged_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("packaged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["content_draft_id"], ["commercial_operation_content_drafts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["output_artifact_id"], ["output_artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "content_draft_id",
        "output_artifact_id",
        "step_key",
        "channel",
        "deliverable_type",
        "deliverable_status",
        "created_by",
        "updated_by",
        "approved_by",
        "packaged_by",
    ):
        op.create_index(
            f"ix_commercial_operation_deliverables_{column}",
            "commercial_operation_deliverables",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_deliverables")
