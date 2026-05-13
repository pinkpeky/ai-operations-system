"""phase12 task reliability observability

Revision ID: 0006_phase12_task_observability
Revises: 0005_phase9
Create Date: 2026-05-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_phase12_task_observability"
down_revision: str | None = "0005_phase9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """新增任务事件、任务日志和任务耗时字段。"""

    op.add_column(
        "tasks",
        sa.Column("duration_ms", sa.Integer(), nullable=True, comment="任务执行耗时毫秒数"),
    )

    op.create_table(
        "task_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="事件 ID"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联任务 ID"),
        sa.Column("workspace_id", sa.String(length=128), nullable=True, comment="工作区 ID"),
        sa.Column("event_type", sa.String(length=64), nullable=False, comment="事件类型"),
        sa.Column("message", sa.Text(), nullable=False, comment="事件说明"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="事件结构化载荷"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_events_task_id", "task_events", ["task_id"])
    op.create_index("ix_task_events_workspace_id", "task_events", ["workspace_id"])
    op.create_index("ix_task_events_event_type", "task_events", ["event_type"])

    op.create_table(
        "task_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="日志 ID"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联任务 ID"),
        sa.Column("workspace_id", sa.String(length=128), nullable=True, comment="工作区 ID"),
        sa.Column("level", sa.String(length=32), nullable=False, comment="日志级别"),
        sa.Column("message", sa.Text(), nullable=False, comment="日志内容"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="结构化日志元数据"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_logs_task_id", "task_logs", ["task_id"])
    op.create_index("ix_task_logs_workspace_id", "task_logs", ["workspace_id"])
    op.create_index("ix_task_logs_level", "task_logs", ["level"])


def downgrade() -> None:
    """回滚任务可观测性结构。"""

    op.drop_index("ix_task_logs_level", table_name="task_logs")
    op.drop_index("ix_task_logs_workspace_id", table_name="task_logs")
    op.drop_index("ix_task_logs_task_id", table_name="task_logs")
    op.drop_table("task_logs")

    op.drop_index("ix_task_events_event_type", table_name="task_events")
    op.drop_index("ix_task_events_workspace_id", table_name="task_events")
    op.drop_index("ix_task_events_task_id", table_name="task_events")
    op.drop_table("task_events")

    op.drop_column("tasks", "duration_ms")
