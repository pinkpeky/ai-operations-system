"""phase13 tool calling foundation

Revision ID: 0007_phase13_tool_calling
Revises: 0006_phase12_task_observability
Create Date: 2026-05-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_phase13_tool_calling"
down_revision: str | None = "0006_phase12_task_observability"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """新增工具调用日志表。"""

    op.create_table(
        "tool_call_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="工具调用日志 ID"),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, comment="工作区 ID"),
        sa.Column("agent_name", sa.String(length=128), nullable=True, comment="触发调用的 Agent 名称"),
        sa.Column("tool_name", sa.String(length=128), nullable=False, comment="工具名称"),
        sa.Column(
            "tool_input",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
            comment="工具输入",
        ),
        sa.Column(
            "tool_output",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
            comment="工具输出",
        ),
        sa.Column("success", sa.Boolean(), nullable=False, comment="是否执行成功"),
        sa.Column("error", sa.Text(), nullable=True, comment="错误信息"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, comment="工具执行耗时毫秒"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tool_call_logs_workspace_id", "tool_call_logs", ["workspace_id"])
    op.create_index("ix_tool_call_logs_agent_name", "tool_call_logs", ["agent_name"])
    op.create_index("ix_tool_call_logs_tool_name", "tool_call_logs", ["tool_name"])
    op.create_index("ix_tool_call_logs_success", "tool_call_logs", ["success"])


def downgrade() -> None:
    """回滚工具调用日志表。"""

    op.drop_index("ix_tool_call_logs_success", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_tool_name", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_agent_name", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_workspace_id", table_name="tool_call_logs")
    op.drop_table("tool_call_logs")
