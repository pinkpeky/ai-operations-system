"""Phase 66B ComfyUI video job loop.

Revision ID: 0063_phase66b_comfyui_video_jobs
Revises: 0062_phase62j_comfyui_probe_exec
Create Date: 2026-05-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0063_phase66b_comfyui_video_jobs"
down_revision = "0062_phase62j_comfyui_probe_exec"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "comfyui_runtime_video_jobs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("job_status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("media_type", sa.String(length=32), nullable=False, server_default="video"),
        sa.Column("resource_profile", sa.String(length=64), nullable=False, server_default="standard"),
        sa.Column("client_id", sa.String(length=200), nullable=True),
        sa.Column("prompt", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("workflow", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("extra_data", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("frames", sa.Integer(), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("estimated_vram_mb", sa.Integer(), nullable=True),
        sa.Column("reserve_vram_mb", sa.Integer(), nullable=True),
        sa.Column("resource_plan", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("selected_endpoint", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("selected_gpu", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("runtime_base_url", sa.String(length=512), nullable=True),
        sa.Column("runtime_prompt_id", sa.String(length=255), nullable=True),
        sa.Column("submit_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("submit_response", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("history_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("queue_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("outputs", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("external_request_attempted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("runtime_calls_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("prompt_submission_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("result_summary", sa.Text(), nullable=True),
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
        ("status", "job_status"),
        ("provider", "provider"),
        ("media", "media_type"),
        ("profile", "resource_profile"),
        ("runtime_base", "runtime_base_url"),
        ("prompt_id", "runtime_prompt_id"),
        ("created", "created_at"),
    ):
        op.create_index(f"ix_cui_video_jobs_{name}", "comfyui_runtime_video_jobs", [column])


def downgrade() -> None:
    op.drop_table("comfyui_runtime_video_jobs")
