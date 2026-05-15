"""Phase 42 task orchestration.

Revision ID: 0027_phase42_task_orchestration
Revises: 0026_phase41_output_artifacts
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0027_phase42_task_orchestration"
down_revision = "0026_phase41_output_artifacts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("priority", sa.String(length=16), server_default="normal", nullable=False),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("max_retries", sa.Integer(), server_default="3", nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_step", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("input_payload", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=False),
        sa.Column("output_payload", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=False),
        sa.Column("metadata", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_runs_workspace_id", "task_runs", ["workspace_id"])
    op.create_index("ix_task_runs_task_type", "task_runs", ["task_type"])
    op.create_index("ix_task_runs_source_type", "task_runs", ["source_type"])
    op.create_index("ix_task_runs_source_id", "task_runs", ["source_id"])
    op.create_index("ix_task_runs_status", "task_runs", ["status"])
    op.create_index("ix_task_runs_priority", "task_runs", ["priority"])
    op.create_index("ix_task_runs_scheduled_at", "task_runs", ["scheduled_at"])
    op.create_index("ix_task_runs_created_by", "task_runs", ["created_by"])

    op.create_table(
        "task_run_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("task_run_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["task_run_id"], ["task_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_run_events_workspace_id", "task_run_events", ["workspace_id"])
    op.create_index("ix_task_run_events_task_run_id", "task_run_events", ["task_run_id"])
    op.create_index("ix_task_run_events_event_type", "task_run_events", ["event_type"])
    op.create_index("ix_task_run_events_status", "task_run_events", ["status"])

    op.add_column("output_artifacts", sa.Column("task_run_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_output_artifacts_task_run_id_task_runs",
        "output_artifacts",
        "task_runs",
        ["task_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_output_artifacts_task_run_id", "output_artifacts", ["task_run_id"])


def downgrade() -> None:
    op.drop_index("ix_output_artifacts_task_run_id", table_name="output_artifacts")
    op.drop_constraint("fk_output_artifacts_task_run_id_task_runs", "output_artifacts", type_="foreignkey")
    op.drop_column("output_artifacts", "task_run_id")

    op.drop_index("ix_task_run_events_status", table_name="task_run_events")
    op.drop_index("ix_task_run_events_event_type", table_name="task_run_events")
    op.drop_index("ix_task_run_events_task_run_id", table_name="task_run_events")
    op.drop_index("ix_task_run_events_workspace_id", table_name="task_run_events")
    op.drop_table("task_run_events")

    op.drop_index("ix_task_runs_created_by", table_name="task_runs")
    op.drop_index("ix_task_runs_scheduled_at", table_name="task_runs")
    op.drop_index("ix_task_runs_priority", table_name="task_runs")
    op.drop_index("ix_task_runs_status", table_name="task_runs")
    op.drop_index("ix_task_runs_source_id", table_name="task_runs")
    op.drop_index("ix_task_runs_source_type", table_name="task_runs")
    op.drop_index("ix_task_runs_task_type", table_name="task_runs")
    op.drop_index("ix_task_runs_workspace_id", table_name="task_runs")
    op.drop_table("task_runs")
