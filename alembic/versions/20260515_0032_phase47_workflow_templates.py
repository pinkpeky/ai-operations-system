"""Phase 47 workflow template registry and versioning.

Revision ID: 0032_phase47_workflow_templates
Revises: 0031_phase46_workflow_graph
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0032_phase47_workflow_templates"
down_revision = "0031_phase46_workflow_graph"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "workflow_templates",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("template_key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("current_version", sa.String(length=64), nullable=True),
        sa.Column("latest_version", sa.String(length=64), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=False, server_default="low"),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "template_key", name="uq_workflow_templates_workspace_key"),
    )
    for column in ("workspace_id", "template_key", "name", "category", "status", "current_version", "latest_version", "risk_level"):
        op.create_index(f"ix_workflow_templates_{column}", "workflow_templates", [column])

    op.create_table(
        "workflow_template_versions",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("template_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("graph_definition", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("entry_node", sa.String(length=128), nullable=False),
        sa.Column("input_schema", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("output_schema", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("compatibility", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("validation_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("validation_errors", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["workflow_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("template_id", "version", name="uq_workflow_template_versions_template_version"),
    )
    for column in ("workspace_id", "template_id", "version", "validation_status", "created_by"):
        op.create_index(f"ix_workflow_template_versions_{column}", "workflow_template_versions", [column])

    op.create_table(
        "workflow_template_runs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("template_id", sa.Uuid(), nullable=False),
        sa.Column("template_version_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=True),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("input_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("output_payload", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["workflow_templates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_version_id"], ["workflow_template_versions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "template_id", "template_version_id", "workflow_run_id", "source_type", "source_id", "status"):
        op.create_index(f"ix_workflow_template_runs_{column}", "workflow_template_runs", [column])

    for table in ("task_runs", "output_artifacts", "agent_memory_snapshots"):
        op.add_column(table, sa.Column("workflow_template_id", sa.Uuid(), nullable=True))
        op.add_column(table, sa.Column("workflow_template_version_id", sa.Uuid(), nullable=True))
        op.add_column(table, sa.Column("workflow_template_run_id", sa.Uuid(), nullable=True))
        op.create_foreign_key(f"fk_{table}_workflow_template_id", table, "workflow_templates", ["workflow_template_id"], ["id"], ondelete="SET NULL")
        op.create_foreign_key(
            f"fk_{table}_workflow_template_version_id",
            table,
            "workflow_template_versions",
            ["workflow_template_version_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_foreign_key(
            f"fk_{table}_workflow_template_run_id",
            table,
            "workflow_template_runs",
            ["workflow_template_run_id"],
            ["id"],
            ondelete="SET NULL",
        )
        for column in ("workflow_template_id", "workflow_template_version_id", "workflow_template_run_id"):
            op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade() -> None:
    for table in ("agent_memory_snapshots", "output_artifacts", "task_runs"):
        for column in ("workflow_template_run_id", "workflow_template_version_id", "workflow_template_id"):
            op.drop_index(f"ix_{table}_{column}", table_name=table)
        op.drop_constraint(f"fk_{table}_workflow_template_run_id", table, type_="foreignkey")
        op.drop_constraint(f"fk_{table}_workflow_template_version_id", table, type_="foreignkey")
        op.drop_constraint(f"fk_{table}_workflow_template_id", table, type_="foreignkey")
        op.drop_column(table, "workflow_template_run_id")
        op.drop_column(table, "workflow_template_version_id")
        op.drop_column(table, "workflow_template_id")

    for column in ("workspace_id", "template_id", "template_version_id", "workflow_run_id", "source_type", "source_id", "status"):
        op.drop_index(f"ix_workflow_template_runs_{column}", table_name="workflow_template_runs")
    op.drop_table("workflow_template_runs")

    for column in ("workspace_id", "template_id", "version", "validation_status", "created_by"):
        op.drop_index(f"ix_workflow_template_versions_{column}", table_name="workflow_template_versions")
    op.drop_table("workflow_template_versions")

    for column in ("workspace_id", "template_key", "name", "category", "status", "current_version", "latest_version", "risk_level"):
        op.drop_index(f"ix_workflow_templates_{column}", table_name="workflow_templates")
    op.drop_table("workflow_templates")
