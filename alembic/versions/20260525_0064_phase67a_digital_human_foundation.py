"""Phase 67A digital human foundation.

Revision ID: 0064_phase67a_digital_human
Revises: 0063_phase66b_comfyui_video_jobs
Create Date: 2026-05-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0064_phase67a_digital_human"
down_revision = "0063_phase66b_comfyui_video_jobs"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "digital_human_assets",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("asset_type", sa.String(length=64), nullable=False),
        sa.Column("asset_status", sa.String(length=64), nullable=False, server_default="available"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_uri", sa.String(length=1024), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=True),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("consent_status", sa.String(length=64), nullable=False, server_default="unverified"),
        sa.Column("usage_scope", sa.String(length=255), nullable=True),
        sa.Column("operator_note", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, column in (
        ("workspace", "workspace_id"),
        ("user", "user_id"),
        ("type", "asset_type"),
        ("status", "asset_status"),
        ("checksum", "checksum"),
        ("consent", "consent_status"),
        ("created", "created_at"),
    ):
        op.create_index(f"ix_digital_human_assets_{name}", "digital_human_assets", [column])

    op.create_table(
        "digital_human_video_jobs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("job_status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="mock"),
        sa.Column("execution_mode", sa.String(length=64), nullable=False, server_default="plan_only"),
        sa.Column("avatar_asset_id", sa.Uuid(), nullable=True),
        sa.Column("material_asset_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("reference_asset_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("script", sa.Text(), nullable=False),
        sa.Column("target_channels", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("voice_profile", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("aspect_ratio", sa.String(length=32), nullable=False, server_default="9:16"),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("scene_plan", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("provider_request", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("provider_response", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("outputs", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("approval_status", sa.String(length=64), nullable=False, server_default="pending"),
        sa.Column("consent_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("consent_status", sa.String(length=64), nullable=False, server_default="unverified"),
        sa.Column("external_request_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("provider_calls_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("operator_note", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["avatar_asset_id"], ["digital_human_assets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, column in (
        ("workspace", "workspace_id"),
        ("user", "user_id"),
        ("status", "job_status"),
        ("provider", "provider"),
        ("execution", "execution_mode"),
        ("avatar", "avatar_asset_id"),
        ("approval", "approval_status"),
        ("consent", "consent_status"),
        ("created", "created_at"),
    ):
        op.create_index(f"ix_digital_human_jobs_{name}", "digital_human_video_jobs", [column])


def downgrade() -> None:
    op.drop_table("digital_human_video_jobs")
    op.drop_table("digital_human_assets")
