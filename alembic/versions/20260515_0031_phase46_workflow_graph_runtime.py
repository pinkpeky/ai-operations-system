"""Phase 46 workflow graph runtime and conditional execution.

Revision ID: 0031_phase46_workflow_graph
Revises: 0030_phase45_workflow_state
Create Date: 2026-05-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0031_phase46_workflow_graph"
down_revision = "0030_phase45_workflow_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_graphs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=64), nullable=False, server_default="1"),
        sa.Column("graph_definition", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("entry_node", sa.String(length=128), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "name"):
        op.create_index(f"ix_workflow_graphs_{column}", "workflow_graphs", [column])

    op.create_table(
        "workflow_graph_nodes",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_graph_id", sa.Uuid(), nullable=False),
        sa.Column("node_key", sa.String(length=128), nullable=False),
        sa.Column("node_type", sa.String(length=64), nullable=False, server_default="no_op"),
        sa.Column("execution_mode", sa.String(length=32), nullable=False, server_default="sync"),
        sa.Column("configuration", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("retry_policy", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("timeout_seconds", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_graph_id"], ["workflow_graphs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "workflow_graph_id", "node_key", "node_type", "execution_mode"):
        op.create_index(f"ix_workflow_graph_nodes_{column}", "workflow_graph_nodes", [column])

    op.create_table(
        "workflow_graph_edges",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_graph_id", sa.Uuid(), nullable=False),
        sa.Column("source_node_key", sa.String(length=128), nullable=False),
        sa.Column("target_node_key", sa.String(length=128), nullable=False),
        sa.Column("edge_type", sa.String(length=32), nullable=False, server_default="success"),
        sa.Column("condition_expression", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_graph_id"], ["workflow_graphs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "workflow_graph_id", "source_node_key", "target_node_key", "edge_type", "priority"):
        op.create_index(f"ix_workflow_graph_edges_{column}", "workflow_graph_edges", [column])

    op.add_column("workflow_runs", sa.Column("workflow_graph_id", sa.Uuid(), nullable=True))
    op.add_column("workflow_runs", sa.Column("graph_execution", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("workflow_runs", sa.Column("current_node_key", sa.String(length=128), nullable=True))
    op.add_column("workflow_runs", sa.Column("planned_next_nodes", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")))
    op.add_column("workflow_runs", sa.Column("skipped_nodes", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")))
    op.add_column("workflow_runs", sa.Column("retry_state", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))
    op.add_column("workflow_runs", sa.Column("fallback_state", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))
    op.create_foreign_key("fk_workflow_runs_workflow_graph_id", "workflow_runs", "workflow_graphs", ["workflow_graph_id"], ["id"], ondelete="SET NULL")
    for column in ("workflow_graph_id", "graph_execution", "current_node_key"):
        op.create_index(f"ix_workflow_runs_{column}", "workflow_runs", [column])

    op.add_column("workflow_steps", sa.Column("node_key", sa.String(length=128), nullable=True))
    op.add_column("workflow_steps", sa.Column("parent_node_key", sa.String(length=128), nullable=True))
    op.add_column("workflow_steps", sa.Column("dependency_state", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))
    for column in ("node_key", "parent_node_key"):
        op.create_index(f"ix_workflow_steps_{column}", "workflow_steps", [column])

    op.add_column("agent_memory_snapshots", sa.Column("node_key", sa.String(length=128), nullable=True))
    op.create_index("ix_agent_memory_snapshots_node_key", "agent_memory_snapshots", ["node_key"])

    op.add_column("output_artifacts", sa.Column("producing_node_key", sa.String(length=128), nullable=True))
    op.add_column("output_artifacts", sa.Column("replay_source", sa.String(length=128), nullable=True))
    op.add_column("output_artifacts", sa.Column("graph_lineage", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))
    op.create_index("ix_output_artifacts_producing_node_key", "output_artifacts", ["producing_node_key"])
    op.create_index("ix_output_artifacts_replay_source", "output_artifacts", ["replay_source"])

    op.create_table(
        "workflow_replays",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("replay_source_checkpoint_id", sa.Uuid(), nullable=True),
        sa.Column("replay_reason", sa.Text(), nullable=True),
        sa.Column("replay_status", sa.String(length=32), nullable=False, server_default="created"),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["replay_source_checkpoint_id"], ["workflow_checkpoints.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "workflow_run_id", "replay_source_checkpoint_id", "replay_status"):
        op.create_index(f"ix_workflow_replays_{column}", "workflow_replays", [column])


def downgrade() -> None:
    for column in ("workspace_id", "workflow_run_id", "replay_source_checkpoint_id", "replay_status"):
        op.drop_index(f"ix_workflow_replays_{column}", table_name="workflow_replays")
    op.drop_table("workflow_replays")

    op.drop_index("ix_output_artifacts_replay_source", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_producing_node_key", table_name="output_artifacts")
    op.drop_column("output_artifacts", "graph_lineage")
    op.drop_column("output_artifacts", "replay_source")
    op.drop_column("output_artifacts", "producing_node_key")

    op.drop_index("ix_agent_memory_snapshots_node_key", table_name="agent_memory_snapshots")
    op.drop_column("agent_memory_snapshots", "node_key")

    for column in ("parent_node_key", "node_key"):
        op.drop_index(f"ix_workflow_steps_{column}", table_name="workflow_steps")
    op.drop_column("workflow_steps", "dependency_state")
    op.drop_column("workflow_steps", "parent_node_key")
    op.drop_column("workflow_steps", "node_key")

    for column in ("current_node_key", "graph_execution", "workflow_graph_id"):
        op.drop_index(f"ix_workflow_runs_{column}", table_name="workflow_runs")
    op.drop_constraint("fk_workflow_runs_workflow_graph_id", "workflow_runs", type_="foreignkey")
    op.drop_column("workflow_runs", "fallback_state")
    op.drop_column("workflow_runs", "retry_state")
    op.drop_column("workflow_runs", "skipped_nodes")
    op.drop_column("workflow_runs", "planned_next_nodes")
    op.drop_column("workflow_runs", "current_node_key")
    op.drop_column("workflow_runs", "graph_execution")
    op.drop_column("workflow_runs", "workflow_graph_id")

    for column in ("workspace_id", "workflow_graph_id", "source_node_key", "target_node_key", "edge_type", "priority"):
        op.drop_index(f"ix_workflow_graph_edges_{column}", table_name="workflow_graph_edges")
    op.drop_table("workflow_graph_edges")

    for column in ("workspace_id", "workflow_graph_id", "node_key", "node_type", "execution_mode"):
        op.drop_index(f"ix_workflow_graph_nodes_{column}", table_name="workflow_graph_nodes")
    op.drop_table("workflow_graph_nodes")

    for column in ("workspace_id", "name"):
        op.drop_index(f"ix_workflow_graphs_{column}", table_name="workflow_graphs")
    op.drop_table("workflow_graphs")
