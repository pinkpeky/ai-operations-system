"""Phase 61T commercial operation ComfyUI job requests.

Revision ID: 0051_phase61t_comfyui_jobs
Revises: 0050_phase61s_comfyui_configs
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0051_phase61t_comfyui_jobs"
down_revision = "0050_phase61s_comfyui_configs"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_comfyui_job_requests",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("preflight_id", sa.Uuid(), nullable=False),
        sa.Column("handoff_id", sa.Uuid(), nullable=False),
        sa.Column("adapter_config_id", sa.Uuid(), nullable=True),
        sa.Column("asset_request_id", sa.Uuid(), nullable=False),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("job_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default="normal"),
        sa.Column("target_url", sa.String(length=512), nullable=True),
        sa.Column("queue_name", sa.String(length=128), nullable=True),
        sa.Column("workflow_name", sa.String(length=128), nullable=False),
        sa.Column("connection_mode", sa.String(length=32), nullable=False, server_default="metadata_only"),
        sa.Column("prompt_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("workflow_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("runtime_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("safety_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("output_expectations", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("recovery_plan", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("job_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("queued_by", sa.String(length=128), nullable=True),
        sa.Column("cancelled_by", sa.String(length=128), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["adapter_config_id"], ["commercial_operation_comfyui_adapter_configs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["asset_request_id"], ["commercial_operation_asset_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["handoff_id"], ["commercial_operation_comfyui_handoffs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["preflight_id"], ["commercial_operation_comfyui_preflights.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "preflight_id",
        "handoff_id",
        "adapter_config_id",
        "asset_request_id",
        "step_key",
        "job_status",
        "priority",
        "workflow_name",
        "connection_mode",
        "requested_by",
        "updated_by",
        "approved_by",
        "queued_by",
        "cancelled_by",
        "archived_by",
    ):
        op.create_index(
            f"ix_commercial_op_comfyui_jobs_{column}",
            "commercial_operation_comfyui_job_requests",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_comfyui_job_requests")
