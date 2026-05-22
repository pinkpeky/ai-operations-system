"""Phase 62F ComfyUI runtime configuration change requests.

Revision ID: 0059_phase62f_comfyui_cfgreq
Revises: 0058_phase62d_comfyui_snaps
Create Date: 2026-05-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0059_phase62f_comfyui_cfgreq"
down_revision = "0058_phase62d_comfyui_snaps"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "comfyui_runtime_config_change_requests",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("change_status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("readiness_status", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("read_only_probe_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("external_request_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("runtime_calls_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("config_mutation_performed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("current_configuration", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("requested_changes", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("runbook_steps", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("recovery_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("disabled_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("runbook_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column("operator_note", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "user_id",
        "change_status",
        "provider",
        "readiness_status",
        "read_only_probe_ready",
        "created_at",
    ):
        op.create_index(
            f"ix_comfyui_runtime_cfg_change_{column}",
            "comfyui_runtime_config_change_requests",
            [column],
        )


def downgrade() -> None:
    op.drop_table("comfyui_runtime_config_change_requests")
