"""Phase 48 workflow template governance and marketplace foundation.

Revision ID: 0033_phase48_template_governance
Revises: 0032_phase47_workflow_templates
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0033_phase48_template_governance"
down_revision = "0032_phase47_workflow_templates"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.add_column("workflow_templates", sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("workflow_templates", sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("workflow_templates", sa.Column("recommended", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("workflow_templates", sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("workflow_templates", sa.Column("success_rate", sa.Float(), nullable=False, server_default="0"))
    op.add_column("workflow_templates", sa.Column("average_runtime_ms", sa.Float(), nullable=False, server_default="0"))
    op.add_column("workflow_templates", sa.Column("average_step_count", sa.Float(), nullable=False, server_default="0"))
    for column in ("featured", "verified", "recommended"):
        op.create_index(f"ix_workflow_templates_{column}", "workflow_templates", [column])

    op.add_column("workflow_runs", sa.Column("template_governance_state", sa.String(length=64), nullable=True))
    op.add_column("workflow_runs", sa.Column("compatibility_snapshot", sa.JSON(), nullable=False, server_default=_json_default("{}")))
    op.create_index("ix_workflow_runs_template_governance_state", "workflow_runs", ["template_governance_state"])

    op.create_table(
        "workflow_template_reviews",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("template_id", sa.Uuid(), nullable=False),
        sa.Column("template_version_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer_id", sa.String(length=128), nullable=True),
        sa.Column("review_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("risk_assessment", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("compatibility_report", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["workflow_templates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_version_id"], ["workflow_template_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "template_id", "template_version_id", "reviewer_id", "review_status"):
        op.create_index(f"ix_workflow_template_reviews_{column}", "workflow_template_reviews", [column])

    op.create_table(
        "workflow_template_promotions",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("template_id", sa.Uuid(), nullable=False),
        sa.Column("from_version_id", sa.Uuid(), nullable=True),
        sa.Column("to_version_id", sa.Uuid(), nullable=True),
        sa.Column("promotion_type", sa.String(length=32), nullable=False),
        sa.Column("promotion_reason", sa.Text(), nullable=True),
        sa.Column("promoted_by", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["workflow_templates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["from_version_id"], ["workflow_template_versions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_version_id"], ["workflow_template_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "template_id", "from_version_id", "to_version_id", "promotion_type", "promoted_by"):
        op.create_index(f"ix_workflow_template_promotions_{column}", "workflow_template_promotions", [column])

    op.create_table(
        "workflow_template_audit_logs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("template_id", sa.Uuid(), nullable=True),
        sa.Column("template_version_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("previous_state", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("new_state", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["workflow_templates.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_version_id"], ["workflow_template_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "template_id", "template_version_id", "action", "actor_id"):
        op.create_index(f"ix_workflow_template_audit_logs_{column}", "workflow_template_audit_logs", [column])

    op.create_table(
        "workflow_template_compatibility_matrix",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("template_version_id", sa.Uuid(), nullable=False),
        sa.Column("runtime_capability", sa.String(length=128), nullable=False),
        sa.Column("supported", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_version_id"], ["workflow_template_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "template_version_id", "runtime_capability", name="uq_workflow_template_matrix_capability"),
    )
    for column in ("workspace_id", "template_version_id", "runtime_capability", "supported"):
        op.create_index(f"ix_workflow_template_compatibility_matrix_{column}", "workflow_template_compatibility_matrix", [column])

    op.add_column("output_artifacts", sa.Column("source_template_review_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("governance_state", sa.String(length=64), nullable=True))
    op.create_foreign_key(
        "fk_output_artifacts_source_template_review_id",
        "output_artifacts",
        "workflow_template_reviews",
        ["source_template_review_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_output_artifacts_source_template_review_id", "output_artifacts", ["source_template_review_id"])
    op.create_index("ix_output_artifacts_governance_state", "output_artifacts", ["governance_state"])


def downgrade() -> None:
    op.drop_index("ix_output_artifacts_governance_state", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_source_template_review_id", table_name="output_artifacts")
    op.drop_constraint("fk_output_artifacts_source_template_review_id", "output_artifacts", type_="foreignkey")
    op.drop_column("output_artifacts", "governance_state")
    op.drop_column("output_artifacts", "source_template_review_id")

    for column in ("workspace_id", "template_version_id", "runtime_capability", "supported"):
        op.drop_index(f"ix_workflow_template_compatibility_matrix_{column}", table_name="workflow_template_compatibility_matrix")
    op.drop_table("workflow_template_compatibility_matrix")

    for column in ("workspace_id", "template_id", "template_version_id", "action", "actor_id"):
        op.drop_index(f"ix_workflow_template_audit_logs_{column}", table_name="workflow_template_audit_logs")
    op.drop_table("workflow_template_audit_logs")

    for column in ("workspace_id", "template_id", "from_version_id", "to_version_id", "promotion_type", "promoted_by"):
        op.drop_index(f"ix_workflow_template_promotions_{column}", table_name="workflow_template_promotions")
    op.drop_table("workflow_template_promotions")

    for column in ("workspace_id", "template_id", "template_version_id", "reviewer_id", "review_status"):
        op.drop_index(f"ix_workflow_template_reviews_{column}", table_name="workflow_template_reviews")
    op.drop_table("workflow_template_reviews")

    op.drop_index("ix_workflow_runs_template_governance_state", table_name="workflow_runs")
    op.drop_column("workflow_runs", "compatibility_snapshot")
    op.drop_column("workflow_runs", "template_governance_state")

    for column in ("featured", "verified", "recommended"):
        op.drop_index(f"ix_workflow_templates_{column}", table_name="workflow_templates")
    for column in (
        "average_step_count",
        "average_runtime_ms",
        "success_rate",
        "usage_count",
        "recommended",
        "verified",
        "featured",
    ):
        op.drop_column("workflow_templates", column)
