"""Phase 61E commercial operation content drafts.

Revision ID: 0039_phase61e_content_drafts
Revises: 0038_phase61d_op_dry_runs
Create Date: 2026-05-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0039_phase61e_content_drafts"
down_revision = "0038_phase61d_op_dry_runs"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_content_drafts",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("content_format", sa.String(length=64), nullable=False, server_default="copy"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("draft_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("audience_segment", sa.Text(), nullable=True),
        sa.Column("content_body", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("call_to_action", sa.Text(), nullable=True),
        sa.Column("source_materials", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("asset_requests", sa.JSON(), nullable=False, server_default=_json_default("[]")),
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
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "step_key",
        "channel",
        "content_format",
        "draft_status",
        "created_by",
        "updated_by",
        "approved_by",
    ):
        op.create_index(
            f"ix_commercial_operation_content_drafts_{column}",
            "commercial_operation_content_drafts",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_content_drafts")
