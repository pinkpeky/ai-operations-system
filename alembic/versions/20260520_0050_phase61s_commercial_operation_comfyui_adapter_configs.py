"""Phase 61S commercial operation ComfyUI adapter configs.

Revision ID: 0050_phase61s_comfyui_configs
Revises: 0049_phase61r_comfyui_preflights
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0050_phase61s_comfyui_configs"
down_revision = "0049_phase61r_comfyui_preflights"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_comfyui_adapter_configs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("config_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("target_url", sa.String(length=512), nullable=True),
        sa.Column("auth_mode", sa.String(length=32), nullable=False, server_default="none"),
        sa.Column("secret_ref", sa.String(length=255), nullable=True),
        sa.Column("queue_name", sa.String(length=128), nullable=True),
        sa.Column("default_workflow_name", sa.String(length=128), nullable=True),
        sa.Column("allowed_workflows", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("model_inventory", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("runtime_limits", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("maintenance_notes", sa.Text(), nullable=True),
        sa.Column("validation_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("config_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("validated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
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
        "config_status",
        "auth_mode",
        "default_workflow_name",
        "created_by",
        "updated_by",
        "validated_by",
        "archived_by",
    ):
        op.create_index(
            f"ix_commercial_op_comfyui_configs_{column}",
            "commercial_operation_comfyui_adapter_configs",
            [column],
        )
    op.add_column(
        "commercial_operation_comfyui_preflights",
        sa.Column("adapter_config_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_commercial_op_comfyui_preflights_adapter_config_id",
        "commercial_operation_comfyui_preflights",
        "commercial_operation_comfyui_adapter_configs",
        ["adapter_config_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_commercial_op_comfyui_preflights_adapter_config_id",
        "commercial_operation_comfyui_preflights",
        ["adapter_config_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_commercial_op_comfyui_preflights_adapter_config_id",
        table_name="commercial_operation_comfyui_preflights",
    )
    op.drop_constraint(
        "fk_commercial_op_comfyui_preflights_adapter_config_id",
        "commercial_operation_comfyui_preflights",
        type_="foreignkey",
    )
    op.drop_column("commercial_operation_comfyui_preflights", "adapter_config_id")
    op.drop_table("commercial_operation_comfyui_adapter_configs")
