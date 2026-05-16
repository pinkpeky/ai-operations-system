"""Phase 49 workflow observability and replay center.

Revision ID: 0034_phase49_workflow_obs
Revises: 0033_phase48_template_governance
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0034_phase49_workflow_obs"
down_revision = "0033_phase48_template_governance"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "workflow_execution_traces",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_step_id", sa.Uuid(), nullable=True),
        sa.Column("node_key", sa.String(length=128), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("execution_phase", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("input_snapshot", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("output_snapshot", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("planner_snapshot", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fallback_triggered", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_step_id"], ["workflow_steps.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "workflow_run_id",
        "workflow_step_id",
        "node_key",
        "event_type",
        "execution_phase",
        "status",
        "fallback_triggered",
    ):
        op.create_index(f"ix_workflow_execution_traces_{column}", "workflow_execution_traces", [column])

    op.create_table(
        "workflow_runtime_diagnostics",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("diagnostic_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="info"),
        sa.Column("summary", sa.String(length=512), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("suggested_action", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "workflow_run_id", "diagnostic_type", "severity"):
        op.create_index(f"ix_workflow_runtime_diagnostics_{column}", "workflow_runtime_diagnostics", [column])

    op.create_table(
        "workflow_replay_sessions",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("replay_source_checkpoint_id", sa.Uuid(), nullable=True),
        sa.Column("replay_source_node_key", sa.String(length=128), nullable=True),
        sa.Column("replay_status", sa.String(length=32), nullable=False, server_default="created"),
        sa.Column("replay_mode", sa.String(length=32), nullable=False, server_default="metadata_only"),
        sa.Column("initiated_by", sa.String(length=128), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["replay_source_checkpoint_id"], ["workflow_checkpoints.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "workflow_run_id",
        "replay_source_checkpoint_id",
        "replay_source_node_key",
        "replay_status",
        "replay_mode",
        "initiated_by",
    ):
        op.create_index(f"ix_workflow_replay_sessions_{column}", "workflow_replay_sessions", [column])

    op.add_column("agent_memory_snapshots", sa.Column("replay_session_id", sa.Uuid(), nullable=True))
    op.add_column("agent_memory_snapshots", sa.Column("diagnostic_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_agent_memory_snapshots_replay_session_id",
        "agent_memory_snapshots",
        "workflow_replay_sessions",
        ["replay_session_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_agent_memory_snapshots_diagnostic_id",
        "agent_memory_snapshots",
        "workflow_runtime_diagnostics",
        ["diagnostic_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_agent_memory_snapshots_replay_session_id", "agent_memory_snapshots", ["replay_session_id"])
    op.create_index("ix_agent_memory_snapshots_diagnostic_id", "agent_memory_snapshots", ["diagnostic_id"])

    op.add_column("output_artifacts", sa.Column("trace_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("replay_session_id", sa.Uuid(), nullable=True))
    op.add_column("output_artifacts", sa.Column("diagnostic_reference", sa.String(length=128), nullable=True))
    op.create_foreign_key(
        "fk_output_artifacts_trace_id",
        "output_artifacts",
        "workflow_execution_traces",
        ["trace_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_output_artifacts_replay_session_id",
        "output_artifacts",
        "workflow_replay_sessions",
        ["replay_session_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_output_artifacts_trace_id", "output_artifacts", ["trace_id"])
    op.create_index("ix_output_artifacts_replay_session_id", "output_artifacts", ["replay_session_id"])
    op.create_index("ix_output_artifacts_diagnostic_reference", "output_artifacts", ["diagnostic_reference"])


def downgrade() -> None:
    op.drop_index("ix_output_artifacts_diagnostic_reference", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_replay_session_id", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_trace_id", table_name="output_artifacts")
    op.drop_constraint("fk_output_artifacts_replay_session_id", "output_artifacts", type_="foreignkey")
    op.drop_constraint("fk_output_artifacts_trace_id", "output_artifacts", type_="foreignkey")
    op.drop_column("output_artifacts", "diagnostic_reference")
    op.drop_column("output_artifacts", "replay_session_id")
    op.drop_column("output_artifacts", "trace_id")

    op.drop_index("ix_agent_memory_snapshots_diagnostic_id", table_name="agent_memory_snapshots")
    op.drop_index("ix_agent_memory_snapshots_replay_session_id", table_name="agent_memory_snapshots")
    op.drop_constraint("fk_agent_memory_snapshots_diagnostic_id", "agent_memory_snapshots", type_="foreignkey")
    op.drop_constraint("fk_agent_memory_snapshots_replay_session_id", "agent_memory_snapshots", type_="foreignkey")
    op.drop_column("agent_memory_snapshots", "diagnostic_id")
    op.drop_column("agent_memory_snapshots", "replay_session_id")

    op.drop_table("workflow_replay_sessions")
    op.drop_table("workflow_runtime_diagnostics")
    op.drop_table("workflow_execution_traces")
