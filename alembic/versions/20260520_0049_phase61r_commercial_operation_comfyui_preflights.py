"""Phase 61R commercial operation ComfyUI preflights.

Revision ID: 0049_phase61r_comfyui_preflights
Revises: 0048_phase61q_comfyui_handoff
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0049_phase61r_comfyui_preflights"
down_revision = "0048_phase61q_comfyui_handoff"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_comfyui_preflights",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("handoff_id", sa.Uuid(), nullable=False),
        sa.Column("asset_request_id", sa.Uuid(), nullable=False),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("preflight_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("target_url", sa.String(length=512), nullable=True),
        sa.Column("connection_mode", sa.String(length=32), nullable=False, server_default="metadata_only"),
        sa.Column("queue_name", sa.String(length=128), nullable=True),
        sa.Column("workflow_name", sa.String(length=128), nullable=False),
        sa.Column("model_refs", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("adapter_config", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("check_items", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("preflight_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("checked_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_request_id"], ["commercial_operation_asset_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["handoff_id"], ["commercial_operation_comfyui_handoffs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "handoff_id",
        "asset_request_id",
        "step_key",
        "preflight_status",
        "connection_mode",
        "workflow_name",
        "checked_by",
        "updated_by",
        "archived_by",
    ):
        op.create_index(
            f"ix_commercial_op_comfyui_preflights_{column}",
            "commercial_operation_comfyui_preflights",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_comfyui_preflights")
