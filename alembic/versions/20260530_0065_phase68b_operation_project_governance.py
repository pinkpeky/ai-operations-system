"""Phase 68B operation project governance.

Revision ID: 0065_phase68b_op_project
Revises: 0064_phase67a_digital_human
Create Date: 2026-05-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0065_phase68b_op_project"
down_revision = "0064_phase67a_digital_human"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def _common_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "commercial_operation_plans",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("plan_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("plan_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("objective_summary", sa.Text(), nullable=False),
        sa.Column("audience_strategy", sa.Text(), nullable=True),
        sa.Column("channel_strategy", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("content_strategy", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("production_scope", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("material_requirements", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("kpis", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("publish_schedule", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("risk_notes", sa.Text(), nullable=True),
        sa.Column("source_goal", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("status", "plan_status"),
        ("created_by", "created_by"),
        ("approved_by", "approved_by"),
    ):
        op.create_index(f"ix_commercial_operation_plans_{suffix}", "commercial_operation_plans", [column])

    op.create_table(
        "commercial_operation_production_tasks",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("operation_plan_id", sa.Uuid(), nullable=True),
        sa.Column("task_type", sa.String(length=32), nullable=False),
        sa.Column("media_subtype", sa.String(length=64), nullable=True),
        sa.Column("channel", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("task_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("brief", sa.Text(), nullable=True),
        sa.Column("source_material_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("output_requirements", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("target_specs", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("workflow_selection_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("assigned_agent", sa.String(length=128), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("completed_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operation_plan_id"], ["commercial_operation_plans.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("plan", "operation_plan_id"),
        ("type", "task_type"),
        ("media", "media_subtype"),
        ("status", "task_status"),
        ("channel", "channel"),
    ):
        op.create_index(f"ix_commercial_operation_tasks_{suffix}", "commercial_operation_production_tasks", [column])

    op.create_table(
        "commercial_operation_project_materials",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("production_task_id", sa.Uuid(), nullable=True),
        sa.Column("material_type", sa.String(length=64), nullable=False),
        sa.Column("material_status", sa.String(length=32), nullable=False, server_default="available"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_uri", sa.Text(), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=True),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("authorization_status", sa.String(length=64), nullable=False, server_default="unverified"),
        sa.Column("usage_scope", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("linked_task_ids", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("uploaded_by", sa.String(length=128), nullable=True),
        sa.Column("reviewed_by", sa.String(length=128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_task_id"], ["commercial_operation_production_tasks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("task", "production_task_id"),
        ("type", "material_type"),
        ("status", "material_status"),
        ("checksum", "checksum"),
        ("auth", "authorization_status"),
    ):
        op.create_index(f"ix_commercial_operation_materials_{suffix}", "commercial_operation_project_materials", [column])

    op.create_table(
        "commercial_operation_workflow_selections",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("production_task_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_source", sa.String(length=64), nullable=False, server_default="comfyui"),
        sa.Column("workflow_name", sa.String(length=255), nullable=False),
        sa.Column("workflow_kind", sa.String(length=128), nullable=True),
        sa.Column("output_type", sa.String(length=64), nullable=False),
        sa.Column("selection_status", sa.String(length=32), nullable=False, server_default="recommended"),
        sa.Column("candidate_summary", sa.Text(), nullable=True),
        sa.Column("input_requirements", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("expected_outputs", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("estimated_duration_seconds", sa.Float(), nullable=True),
        sa.Column("estimated_vram_mb", sa.Integer(), nullable=True),
        sa.Column("risk_notes", sa.Text(), nullable=True),
        sa.Column("validation_status", sa.String(length=64), nullable=False, server_default="not_checked"),
        sa.Column("selected_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_task_id"], ["commercial_operation_production_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("task", "production_task_id"),
        ("source", "workflow_source"),
        ("kind", "workflow_kind"),
        ("output", "output_type"),
        ("status", "selection_status"),
        ("validation", "validation_status"),
    ):
        op.create_index(f"ix_commercial_operation_workflow_selections_{suffix}", "commercial_operation_workflow_selections", [column])

    op.create_table(
        "commercial_operation_output_candidates",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("production_task_id", sa.Uuid(), nullable=True),
        sa.Column("workflow_selection_id", sa.Uuid(), nullable=True),
        sa.Column("output_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("candidate_type", sa.String(length=64), nullable=False),
        sa.Column("candidate_status", sa.String(length=32), nullable=False, server_default="generated"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("preview_uri", sa.Text(), nullable=True),
        sa.Column("source_uri", sa.Text(), nullable=True),
        sa.Column("thumbnail_uri", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("generation_summary", sa.Text(), nullable=True),
        sa.Column("quality_checks", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("selected_by", sa.String(length=128), nullable=True),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_task_id"], ["commercial_operation_production_tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workflow_selection_id"], ["commercial_operation_workflow_selections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["output_artifact_id"], ["output_artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("task", "production_task_id"),
        ("workflow", "workflow_selection_id"),
        ("artifact", "output_artifact_id"),
        ("type", "candidate_type"),
        ("status", "candidate_status"),
    ):
        op.create_index(f"ix_commercial_operation_output_candidates_{suffix}", "commercial_operation_output_candidates", [column])

    op.create_table(
        "commercial_operation_final_selections",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("production_task_id", sa.Uuid(), nullable=True),
        sa.Column("output_candidate_id", sa.Uuid(), nullable=False),
        sa.Column("final_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("selection_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("selection_reason", sa.Text(), nullable=True),
        sa.Column("platform_targets", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("selected_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_task_id"], ["commercial_operation_production_tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["output_candidate_id"], ["commercial_operation_output_candidates.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("task", "production_task_id"),
        ("candidate", "output_candidate_id"),
        ("type", "final_type"),
        ("status", "selection_status"),
    ):
        op.create_index(f"ix_commercial_operation_final_selections_{suffix}", "commercial_operation_final_selections", [column])

    op.create_table(
        "commercial_operation_publish_packages",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("final_selection_id", sa.Uuid(), nullable=True),
        sa.Column("platform", sa.String(length=128), nullable=False),
        sa.Column("account_ref", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("package_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("hashtags", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("cover_candidate_id", sa.Uuid(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("publish_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("risk_notes", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("prepared_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("prepared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["final_selection_id"], ["commercial_operation_final_selections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["cover_candidate_id"], ["commercial_operation_output_candidates.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("selection", "final_selection_id"),
        ("platform", "platform"),
        ("account", "account_ref"),
        ("status", "package_status"),
        ("cover", "cover_candidate_id"),
    ):
        op.create_index(f"ix_commercial_operation_publish_packages_{suffix}", "commercial_operation_publish_packages", [column])

    op.create_table(
        "commercial_operation_platform_metric_snapshots",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("publish_package_id", sa.Uuid(), nullable=True),
        sa.Column("platform", sa.String(length=128), nullable=False),
        sa.Column("platform_content_id", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False, server_default="manual"),
        sa.Column("snapshot_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metric_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("collected_by", sa.String(length=128), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        *_common_columns(),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["publish_package_id"], ["commercial_operation_publish_packages.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for suffix, column in (
        ("workspace", "workspace_id"),
        ("operation", "operation_id"),
        ("package", "publish_package_id"),
        ("platform", "platform"),
        ("content", "platform_content_id"),
        ("source", "source_type"),
        ("status", "snapshot_status"),
    ):
        op.create_index(f"ix_commercial_operation_metric_snapshots_{suffix}", "commercial_operation_platform_metric_snapshots", [column])


def downgrade() -> None:
    op.drop_table("commercial_operation_platform_metric_snapshots")
    op.drop_table("commercial_operation_publish_packages")
    op.drop_table("commercial_operation_final_selections")
    op.drop_table("commercial_operation_output_candidates")
    op.drop_table("commercial_operation_workflow_selections")
    op.drop_table("commercial_operation_project_materials")
    op.drop_table("commercial_operation_production_tasks")
    op.drop_table("commercial_operation_plans")
