"""Phase 62J ComfyUI guarded read-only probe executions.

Revision ID: 0062_phase62j_comfyui_probe_exec
Revises: 0061_phase62h_comfyui_ready
Create Date: 2026-05-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0062_phase62j_comfyui_probe_exec"
down_revision = "0061_phase62h_comfyui_ready"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "comfyui_runtime_guarded_probe_executions",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("post_manual_readiness_check_id", sa.Uuid(), nullable=False),
        sa.Column("manual_apply_evidence_id", sa.Uuid(), nullable=False),
        sa.Column("config_change_request_id", sa.Uuid(), nullable=False),
        sa.Column("execution_status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("readiness_status_current", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("read_only_probe_ready_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("guarded_probe_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("base_url", sa.String(length=512), nullable=False),
        sa.Column("health_path", sa.String(length=255), nullable=False),
        sa.Column("allowed_hosts", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("allowed_health_paths", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("external_request_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("runtime_calls_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("health_probe_executed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_only_probe_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("api_config_mutation_performed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("probe_status_code", sa.Integer(), nullable=True),
        sa.Column("probe_latency_ms", sa.Float(), nullable=True),
        sa.Column("probe_result_status", sa.String(length=64), nullable=False, server_default="not_started"),
        sa.Column("readiness_check_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("current_diagnostics_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("probe_request", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("probe_response", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("blocking_reasons", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("recommended_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("disabled_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("operator_note", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, column in (
        ("workspace", "workspace_id"),
        ("user", "user_id"),
        ("readiness_check", "post_manual_readiness_check_id"),
        ("evidence", "manual_apply_evidence_id"),
        ("config_request", "config_change_request_id"),
        ("execution_status", "execution_status"),
        ("provider", "provider"),
        ("current_ready", "readiness_status_current"),
        ("probe_ready", "read_only_probe_ready_current"),
        ("guarded_probe", "guarded_probe_ready"),
        ("probe_result", "probe_result_status"),
        ("created", "created_at"),
    ):
        op.create_index(
            f"ix_cui_gpe_{name}",
            "comfyui_runtime_guarded_probe_executions",
            [column],
        )


def downgrade() -> None:
    op.drop_table("comfyui_runtime_guarded_probe_executions")
