"""Phase 61V commercial operation ComfyUI connection probes.

Revision ID: 0053_phase61v_comfyui_probes
Revises: 0052_phase61u_comfyui_plans
Create Date: 2026-05-21
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0053_phase61v_comfyui_probes"
down_revision = "0052_phase61u_comfyui_plans"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_comfyui_connection_probes",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("execution_plan_id", sa.Uuid(), nullable=False),
        sa.Column("job_request_id", sa.Uuid(), nullable=False),
        sa.Column("preflight_id", sa.Uuid(), nullable=False),
        sa.Column("handoff_id", sa.Uuid(), nullable=False),
        sa.Column("adapter_config_id", sa.Uuid(), nullable=True),
        sa.Column("asset_request_id", sa.Uuid(), nullable=False),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("probe_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("target_url", sa.String(length=512), nullable=True),
        sa.Column("queue_name", sa.String(length=128), nullable=True),
        sa.Column("workflow_name", sa.String(length=128), nullable=False),
        sa.Column("probe_mode", sa.String(length=32), nullable=False, server_default="metadata_only"),
        sa.Column("health_endpoint", sa.String(length=128), nullable=False, server_default="/system_stats"),
        sa.Column("queue_endpoint", sa.String(length=128), nullable=False, server_default="/queue"),
        sa.Column("expected_routes", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("readiness_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("probe_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("health_snapshot", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("queue_snapshot", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("response_schema", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("probe_plan_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("planned_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("probed_by", sa.String(length=128), nullable=True),
        sa.Column("cancelled_by", sa.String(length=128), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("probed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["adapter_config_id"], ["commercial_operation_comfyui_adapter_configs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["asset_request_id"], ["commercial_operation_asset_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["execution_plan_id"], ["commercial_operation_comfyui_execution_plans.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["handoff_id"], ["commercial_operation_comfyui_handoffs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["job_request_id"], ["commercial_operation_comfyui_job_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["preflight_id"], ["commercial_operation_comfyui_preflights.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "execution_plan_id",
        "job_request_id",
        "preflight_id",
        "handoff_id",
        "adapter_config_id",
        "asset_request_id",
        "step_key",
        "probe_status",
        "queue_name",
        "workflow_name",
        "probe_mode",
        "planned_by",
        "updated_by",
        "approved_by",
        "probed_by",
        "cancelled_by",
        "archived_by",
    ):
        op.create_index(
            f"ix_commercial_op_comfyui_probes_{column}",
            "commercial_operation_comfyui_connection_probes",
            [column],
        )


def downgrade() -> None:
    op.drop_table("commercial_operation_comfyui_connection_probes")
