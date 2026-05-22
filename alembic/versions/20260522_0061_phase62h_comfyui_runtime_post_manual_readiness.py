"""Phase 62H ComfyUI runtime post-manual readiness checks.

Revision ID: 0061_phase62h_comfyui_ready
Revises: 0060_phase62g_comfyui_apply
Create Date: 2026-05-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0061_phase62h_comfyui_ready"
down_revision = "0060_phase62g_comfyui_apply"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "comfyui_runtime_post_manual_readiness_checks",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("manual_apply_evidence_id", sa.Uuid(), nullable=False),
        sa.Column("config_change_request_id", sa.Uuid(), nullable=False),
        sa.Column("check_status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("comparison_status", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("readiness_status_before", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("readiness_status_after_evidence", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("readiness_status_current", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("read_only_probe_ready_before", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_only_probe_ready_after_evidence", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_only_probe_ready_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("guarded_probe_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("manual_evidence_status", sa.String(length=64), nullable=False, server_default="verified"),
        sa.Column("manual_config_applied", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("service_restart_reported", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("external_request_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("runtime_calls_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("health_probe_executed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("api_config_mutation_performed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("requested_changes", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("manual_apply_steps", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("restart_evidence", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("evidence_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("current_diagnostics_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("comparison_results", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("blocking_reasons", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("recommended_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("next_operator_action", sa.Text(), nullable=True),
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
        ("evidence", "manual_apply_evidence_id"),
        ("config_request", "config_change_request_id"),
        ("check_status", "check_status"),
        ("comparison", "comparison_status"),
        ("provider", "provider"),
        ("current_ready", "readiness_status_current"),
        ("probe_ready", "read_only_probe_ready_current"),
        ("guarded_probe", "guarded_probe_ready"),
        ("evidence_status", "manual_evidence_status"),
        ("created", "created_at"),
    ):
        op.create_index(
            f"ix_cui_pmrc_{name}",
            "comfyui_runtime_post_manual_readiness_checks",
            [column],
        )


def downgrade() -> None:
    op.drop_table("comfyui_runtime_post_manual_readiness_checks")
