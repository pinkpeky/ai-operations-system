"""Phase 62G ComfyUI runtime manual apply evidence.

Revision ID: 0060_phase62g_comfyui_apply
Revises: 0059_phase62f_comfyui_cfgreq
Create Date: 2026-05-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0060_phase62g_comfyui_apply"
down_revision = "0059_phase62f_comfyui_cfgreq"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "comfyui_runtime_manual_apply_evidence",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("config_change_request_id", sa.Uuid(), nullable=False),
        sa.Column("before_snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("after_snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("evidence_status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("readiness_status_before", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("readiness_status_after", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("read_only_probe_ready_before", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_only_probe_ready_after", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("external_request_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("runtime_calls_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("api_config_mutation_performed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("manual_config_applied", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("service_restart_reported", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("config_change_request_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("current_configuration_before", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("current_configuration_after", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("requested_changes", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("manual_apply_steps", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("restart_evidence", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("verification_results", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("diagnostics_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("rollback_notes", sa.Text(), nullable=True),
        sa.Column("verification_notes", sa.Text(), nullable=True),
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
        "config_change_request_id",
        "before_snapshot_id",
        "after_snapshot_id",
        "evidence_status",
        "provider",
        "readiness_status_before",
        "readiness_status_after",
        "read_only_probe_ready_after",
        "created_at",
    ):
        op.create_index(
            f"ix_comfyui_runtime_apply_evidence_{column}",
            "comfyui_runtime_manual_apply_evidence",
            [column],
        )


def downgrade() -> None:
    op.drop_table("comfyui_runtime_manual_apply_evidence")
