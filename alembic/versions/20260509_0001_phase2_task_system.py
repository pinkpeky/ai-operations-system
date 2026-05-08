"""phase2 task system

Revision ID: 0001_phase2
Revises:
Create Date: 2026-05-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_phase2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """创建 Phase 2 中央任务系统数据表。"""

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="账号状态"),
        sa.Column("name", sa.String(length=128), nullable=False, comment="账号名称"),
        sa.Column("platform", sa.String(length=64), nullable=False, comment="平台标识"),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="账号配置"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_accounts_status", "accounts", ["status"])
    op.create_index("ix_accounts_platform", "accounts", ["platform"])

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="任务状态"),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True, comment="关联账号 ID"),
        sa.Column("title", sa.String(length=255), nullable=False, comment="任务标题"),
        sa.Column("task_type", sa.String(length=64), nullable=False, comment="任务类型"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="任务负载"),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False, comment="已重试次数"),
        sa.Column("max_retries", sa.Integer(), server_default="3", nullable=False, comment="最大重试次数"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True, comment="计划执行时间"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True, comment="开始执行时间"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True, comment="完成时间"),
        sa.Column("last_error", sa.Text(), nullable=True, comment="最近一次错误信息"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_account_id", "tasks", ["account_id"])
    op.create_index("ix_tasks_task_type", "tasks", ["task_type"])
    op.create_index("ix_tasks_scheduled_at", "tasks", ["scheduled_at"])

    op.create_table(
        "publish_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="发布状态"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联任务 ID"),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True, comment="关联账号 ID"),
        sa.Column("channel", sa.String(length=64), nullable=False, comment="发布渠道"),
        sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="发布请求内容"),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="发布响应内容"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="错误信息"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True, comment="发布时间"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_publish_logs_status", "publish_logs", ["status"])
    op.create_index("ix_publish_logs_task_id", "publish_logs", ["task_id"])
    op.create_index("ix_publish_logs_account_id", "publish_logs", ["account_id"])
    op.create_index("ix_publish_logs_channel", "publish_logs", ["channel"])


def downgrade() -> None:
    """回滚 Phase 2 中央任务系统数据表。"""

    op.drop_index("ix_publish_logs_channel", table_name="publish_logs")
    op.drop_index("ix_publish_logs_account_id", table_name="publish_logs")
    op.drop_index("ix_publish_logs_task_id", table_name="publish_logs")
    op.drop_index("ix_publish_logs_status", table_name="publish_logs")
    op.drop_table("publish_logs")

    op.drop_index("ix_tasks_scheduled_at", table_name="tasks")
    op.drop_index("ix_tasks_task_type", table_name="tasks")
    op.drop_index("ix_tasks_account_id", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_accounts_platform", table_name="accounts")
    op.drop_index("ix_accounts_status", table_name="accounts")
    op.drop_table("accounts")
