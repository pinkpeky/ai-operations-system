"""Phase 45 workflow state and agent memory foundation.

Revision ID: 0030_phase45_workflow_state
Revises: 0029_phase44_artifacts
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0030_phase45_workflow_state"
down_revision = "0029_phase44_artifacts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_runs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("conversation_thread_id", sa.Uuid(), nullable=True),
        sa.Column("playbook_run_id", sa.Uuid(), nullable=True),
        sa.Column("task_run_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("variables", sa.JSON(), nullable=False),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("checkpoints", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_thread_id"], ["conversation_threads.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["playbook_run_id"], ["conversation_playbook_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["task_run_id"], ["task_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "source_type",
        "source_id",
        "conversation_thread_id",
        "playbook_run_id",
        "task_run_id",
        "status",
    ):
        op.create_index(f"ix_workflow_runs_{column}", "workflow_runs", [column])

    op.create_table(
        "workflow_steps",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("step_name", sa.String(length=255), nullable=False),
        sa.Column("step_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "workflow_run_id", "step_index", "step_type", "status"):
        op.create_index(f"ix_workflow_steps_{column}", "workflow_steps", [column])

    op.create_table(
        "workflow_checkpoints",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("checkpoint_name", sa.String(length=255), nullable=False),
        sa.Column("checkpoint_type", sa.String(length=32), nullable=False, server_default="auto"),
        sa.Column("state_payload", sa.JSON(), nullable=False),
        sa.Column("variables_snapshot", sa.JSON(), nullable=False),
        sa.Column("context_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "workflow_run_id", "checkpoint_type", "created_by"):
        op.create_index(f"ix_workflow_checkpoints_{column}", "workflow_checkpoints", [column])

    op.create_table(
        "agent_memory_snapshots",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column("conversation_thread_id", sa.Uuid(), nullable=True),
        sa.Column("task_run_id", sa.Uuid(), nullable=True),
        sa.Column("memory_type", sa.String(length=64), nullable=False, server_default="task_context"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("memory_payload", sa.JSON(), nullable=False),
        sa.Column("source_event_ids", sa.JSON(), nullable=False),
        sa.Column("source_artifact_ids", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_thread_id"], ["conversation_threads.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["task_run_id"], ["task_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "workflow_run_id", "conversation_thread_id", "task_run_id", "memory_type"):
        op.create_index(f"ix_agent_memory_snapshots_{column}", "agent_memory_snapshots", [column])

    for column, target_table in (
        ("workflow_run_id", "workflow_runs"),
        ("workflow_step_id", "workflow_steps"),
        ("checkpoint_id", "workflow_checkpoints"),
        ("memory_snapshot_id", "agent_memory_snapshots"),
    ):
        op.add_column("output_artifacts", sa.Column(column, sa.Uuid(), nullable=True))
        op.create_index(f"ix_output_artifacts_{column}", "output_artifacts", [column])
        op.create_foreign_key(
            f"fk_output_artifacts_{column}",
            "output_artifacts",
            target_table,
            [column],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    for column in ("memory_snapshot_id", "checkpoint_id", "workflow_step_id", "workflow_run_id"):
        op.drop_constraint(f"fk_output_artifacts_{column}", "output_artifacts", type_="foreignkey")
        op.drop_index(f"ix_output_artifacts_{column}", table_name="output_artifacts")
        op.drop_column("output_artifacts", column)

    for column in ("memory_type", "task_run_id", "conversation_thread_id", "workflow_run_id", "workspace_id"):
        op.drop_index(f"ix_agent_memory_snapshots_{column}", table_name="agent_memory_snapshots")
    op.drop_table("agent_memory_snapshots")

    for column in ("created_by", "checkpoint_type", "workflow_run_id", "workspace_id"):
        op.drop_index(f"ix_workflow_checkpoints_{column}", table_name="workflow_checkpoints")
    op.drop_table("workflow_checkpoints")

    for column in ("status", "step_type", "step_index", "workflow_run_id", "workspace_id"):
        op.drop_index(f"ix_workflow_steps_{column}", table_name="workflow_steps")
    op.drop_table("workflow_steps")

    for column in (
        "status",
        "task_run_id",
        "playbook_run_id",
        "conversation_thread_id",
        "source_id",
        "source_type",
        "workspace_id",
    ):
        op.drop_index(f"ix_workflow_runs_{column}", table_name="workflow_runs")
    op.drop_table("workflow_runs")
