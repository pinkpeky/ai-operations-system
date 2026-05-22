"""Phase 62D ComfyUI runtime diagnostic snapshots.

Revision ID: 0058_phase62d_comfyui_snaps
Revises: 0057_phase61z_comfyui_active
Create Date: 2026-05-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0058_phase62d_comfyui_snaps"
down_revision = "0057_phase61z_comfyui_active"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "comfyui_runtime_diagnostic_snapshots",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("guarded", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("network_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_only_probe_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("base_url", sa.String(length=512), nullable=False),
        sa.Column("parsed_host", sa.String(length=255), nullable=True),
        sa.Column("scheme_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("host_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allowed_hosts", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("health_path", sa.String(length=255), nullable=False),
        sa.Column("health_path_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allowed_health_paths", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("read_only_probe_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("readiness_status", sa.String(length=64), nullable=False, server_default="blocked"),
        sa.Column("external_request_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("runtime_calls_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("blocking_reasons", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("recommended_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("diagnostics", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("forbidden_actions", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("snapshot_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("operator_note", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "user_id",
        "provider",
        "parsed_host",
        "read_only_probe_ready",
        "readiness_status",
        "created_at",
    ):
        op.create_index(
            f"ix_comfyui_runtime_diag_snapshots_{column}",
            "comfyui_runtime_diagnostic_snapshots",
            [column],
        )


def downgrade() -> None:
    op.drop_table("comfyui_runtime_diagnostic_snapshots")
