"""phase16 planning foundation

Revision ID: 0010_phase16_planning
Revises: 0009_phase15_multi_agent
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_phase16_planning"
down_revision = "0009_phase15_multi_agent"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 Planning Foundation 相关表。"""

    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("root_goal", sa.Text(), nullable=False),
        sa.Column("planner_agent", sa.String(length=128), nullable=False, server_default="simple_planner"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_plans_workspace_id", "plans", ["workspace_id"])
    op.create_index("ix_plans_session_id", "plans", ["session_id"])
    op.create_index("ix_plans_status", "plans", ["status"])

    op.create_table(
        "plan_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("agent_name", sa.String(length=128), nullable=True),
        sa.Column("tool_name", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("output_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_plan_steps_workspace_id", "plan_steps", ["workspace_id"])
    op.create_index("ix_plan_steps_plan_id", "plan_steps", ["plan_id"])
    op.create_index("ix_plan_steps_agent_name", "plan_steps", ["agent_name"])
    op.create_index("ix_plan_steps_tool_name", "plan_steps", ["tool_name"])
    op.create_index("ix_plan_steps_status", "plan_steps", ["status"])

    op.create_table(
        "plan_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_agent", sa.String(length=128), nullable=False, server_default="review_agent"),
        sa.Column("review_result", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_plan_reviews_workspace_id", "plan_reviews", ["workspace_id"])
    op.create_index("ix_plan_reviews_plan_id", "plan_reviews", ["plan_id"])


def downgrade() -> None:
    """回滚 Planning Foundation 表。"""

    op.drop_index("ix_plan_reviews_plan_id", table_name="plan_reviews")
    op.drop_index("ix_plan_reviews_workspace_id", table_name="plan_reviews")
    op.drop_table("plan_reviews")

    op.drop_index("ix_plan_steps_status", table_name="plan_steps")
    op.drop_index("ix_plan_steps_tool_name", table_name="plan_steps")
    op.drop_index("ix_plan_steps_agent_name", table_name="plan_steps")
    op.drop_index("ix_plan_steps_plan_id", table_name="plan_steps")
    op.drop_index("ix_plan_steps_workspace_id", table_name="plan_steps")
    op.drop_table("plan_steps")

    op.drop_index("ix_plans_status", table_name="plans")
    op.drop_index("ix_plans_session_id", table_name="plans")
    op.drop_index("ix_plans_workspace_id", table_name="plans")
    op.drop_table("plans")
