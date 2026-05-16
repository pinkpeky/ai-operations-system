"""Phase 44 output artifact pipeline and export system.

Revision ID: 0029_phase44_artifacts
Revises: 0028_phase43_scheduler_recovery
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0029_phase44_artifacts"
down_revision = "0028_phase43_scheduler_recovery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("output_artifacts", sa.Column("parent_artifact_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("root_artifact_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("source_task_run_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("source_playbook_run_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("source_conversation_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("source_runtime_session_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("artifact_role", sa.String(length=64), nullable=True))
    op.add_column("output_artifacts", sa.Column("artifact_stage", sa.String(length=32), server_default="processed", nullable=False))
    op.add_column("output_artifacts", sa.Column("generated_by", sa.String(length=128), nullable=True))
    op.add_column("output_artifacts", sa.Column("exportable", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column("output_artifacts", sa.Column("retention_policy", sa.String(length=32), server_default="standard", nullable=False))
    op.add_column("output_artifacts", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))

    op.create_foreign_key(
        "fk_output_artifacts_parent_artifact_id",
        "output_artifacts",
        "output_artifacts",
        ["parent_artifact_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_output_artifacts_root_artifact_id",
        "output_artifacts",
        "output_artifacts",
        ["root_artifact_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_output_artifacts_source_task_run_id",
        "output_artifacts",
        "task_runs",
        ["source_task_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_output_artifacts_source_playbook_run_id",
        "output_artifacts",
        "conversation_playbook_runs",
        ["source_playbook_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_output_artifacts_source_conversation_id",
        "output_artifacts",
        "conversation_threads",
        ["source_conversation_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_output_artifacts_source_runtime_session_id",
        "output_artifacts",
        "browser_runtime_sessions",
        ["source_runtime_session_id"],
        ["id"],
        ondelete="SET NULL",
    )

    for column in (
        "parent_artifact_id",
        "root_artifact_id",
        "source_task_run_id",
        "source_playbook_run_id",
        "source_conversation_id",
        "source_runtime_session_id",
        "artifact_role",
        "artifact_stage",
        "generated_by",
        "exportable",
        "retention_policy",
        "expires_at",
    ):
        op.create_index(f"ix_output_artifacts_{column}", "output_artifacts", [column])

    op.execute("UPDATE output_artifacts SET source_task_run_id = task_run_id WHERE source_task_run_id IS NULL")
    op.execute("UPDATE output_artifacts SET source_playbook_run_id = playbook_run_id WHERE source_playbook_run_id IS NULL")
    op.execute("UPDATE output_artifacts SET source_conversation_id = thread_id WHERE source_conversation_id IS NULL")
    op.execute("UPDATE output_artifacts SET root_artifact_id = id WHERE root_artifact_id IS NULL")

    op.create_table(
        "artifact_relationships",
        sa.Column("parent_artifact_id", sa.Uuid(), nullable=False),
        sa.Column("child_artifact_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_type", sa.String(length=64), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_artifact_id"], ["output_artifacts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_artifact_id"], ["output_artifacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_artifact_relationships_parent_artifact_id", "artifact_relationships", ["parent_artifact_id"])
    op.create_index("ix_artifact_relationships_child_artifact_id", "artifact_relationships", ["child_artifact_id"])
    op.create_index("ix_artifact_relationships_relationship_type", "artifact_relationships", ["relationship_type"])


def downgrade() -> None:
    op.drop_index("ix_artifact_relationships_relationship_type", table_name="artifact_relationships")
    op.drop_index("ix_artifact_relationships_child_artifact_id", table_name="artifact_relationships")
    op.drop_index("ix_artifact_relationships_parent_artifact_id", table_name="artifact_relationships")
    op.drop_table("artifact_relationships")

    for column in reversed(
        (
            "parent_artifact_id",
            "root_artifact_id",
            "source_task_run_id",
            "source_playbook_run_id",
            "source_conversation_id",
            "source_runtime_session_id",
            "artifact_role",
            "artifact_stage",
            "generated_by",
            "exportable",
            "retention_policy",
            "expires_at",
        )
    ):
        op.drop_index(f"ix_output_artifacts_{column}", table_name="output_artifacts")

    op.drop_constraint("fk_output_artifacts_source_runtime_session_id", "output_artifacts", type_="foreignkey")
    op.drop_constraint("fk_output_artifacts_source_conversation_id", "output_artifacts", type_="foreignkey")
    op.drop_constraint("fk_output_artifacts_source_playbook_run_id", "output_artifacts", type_="foreignkey")
    op.drop_constraint("fk_output_artifacts_source_task_run_id", "output_artifacts", type_="foreignkey")
    op.drop_constraint("fk_output_artifacts_root_artifact_id", "output_artifacts", type_="foreignkey")
    op.drop_constraint("fk_output_artifacts_parent_artifact_id", "output_artifacts", type_="foreignkey")

    for column in (
        "expires_at",
        "retention_policy",
        "exportable",
        "generated_by",
        "artifact_stage",
        "artifact_role",
        "source_runtime_session_id",
        "source_conversation_id",
        "source_playbook_run_id",
        "source_task_run_id",
        "root_artifact_id",
        "parent_artifact_id",
    ):
        op.drop_column("output_artifacts", column)
