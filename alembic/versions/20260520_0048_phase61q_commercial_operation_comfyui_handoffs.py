"""Phase 61Q commercial operation ComfyUI handoffs.

Revision ID: 0048_phase61q_comfyui_handoff
Revises: 0047_phase61m_evidence_snapshots
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0048_phase61q_comfyui_handoff"
down_revision = "0047_phase61m_evidence_snapshots"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_comfyui_handoffs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("asset_request_id", sa.Uuid(), nullable=False),
        sa.Column("content_draft_id", sa.Uuid(), nullable=True),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("asset_type", sa.String(length=64), nullable=False, server_default="image"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("handoff_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("workflow_name", sa.String(length=128), nullable=False, server_default="future_comfyui_handoff"),
        sa.Column("dimensions", sa.String(length=128), nullable=True),
        sa.Column("generation_prompt", sa.Text(), nullable=True),
        sa.Column("negative_prompt", sa.Text(), nullable=True),
        sa.Column("workflow_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("prompt_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("source_materials", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("readiness_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("handoff_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("prepared_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("prepared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_request_id"], ["commercial_operation_asset_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["content_draft_id"], ["commercial_operation_content_drafts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "asset_request_id",
        "content_draft_id",
        "step_key",
        "channel",
        "asset_type",
        "handoff_status",
        "workflow_name",
        "requested_by",
        "updated_by",
        "approved_by",
        "prepared_by",
    ):
        op.create_index(
            f"ix_commercial_op_comfyui_handoffs_{column}",
            "commercial_operation_comfyui_handoffs",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_comfyui_handoffs")
