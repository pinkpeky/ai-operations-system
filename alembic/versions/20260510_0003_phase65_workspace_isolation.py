"""phase65 workspace isolation foundation

Revision ID: 0003_phase65
Revises: 0002_phase6
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_phase65"
down_revision: str | None = "0002_phase6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """创建用户/工作区/API Key 表，并让任务和 collection 元数据参与工作区隔离。"""

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("username", sa.String(length=128), nullable=False, comment="用户名"),
        sa.Column("email", sa.String(length=255), nullable=False, comment="邮箱"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="用户状态"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_status", "users", ["status"])

    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("name", sa.String(length=128), nullable=False, comment="工作区名称"),
        sa.Column("slug", sa.String(length=128), nullable=False, comment="工作区 slug"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="工作区状态"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_workspaces_slug", "workspaces", ["slug"])
    op.create_index("ix_workspaces_status", "workspaces", ["status"])

    op.create_table(
        "workspace_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False, comment="工作区 ID"),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, comment="用户 ID"),
        sa.Column("role", sa.String(length=32), nullable=False, comment="成员角色"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="成员状态"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_members_workspace_user"),
    )
    op.create_index("ix_workspace_members_workspace_id", "workspace_members", ["workspace_id"])
    op.create_index("ix_workspace_members_user_id", "workspace_members", ["user_id"])
    op.create_index("ix_workspace_members_status", "workspace_members", ["status"])

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False, comment="工作区 ID"),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, comment="用户 ID"),
        sa.Column("key_hash", sa.Text(), nullable=False, comment="API Key 哈希"),
        sa.Column("name", sa.String(length=128), nullable=False, comment="API Key 名称"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="API Key 状态"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True, comment="最后使用时间"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_index("ix_api_keys_workspace_id", "api_keys", ["workspace_id"])
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index("ix_api_keys_status", "api_keys", ["status"])

    op.add_column("tasks", sa.Column("workspace_id", sa.String(length=128), nullable=True, comment="隔离工作区 ID"))
    op.add_column("tasks", sa.Column("user_id", sa.String(length=128), nullable=True, comment="任务创建用户 ID"))
    op.create_index("ix_tasks_workspace_id", "tasks", ["workspace_id"])
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"])

    op.drop_constraint("uq_collections_metadata_collection_name", "collections_metadata", type_="unique")
    op.create_unique_constraint(
        "uq_collections_metadata_workspace_collection",
        "collections_metadata",
        ["workspace_id", "collection_name"],
    )


def downgrade() -> None:
    """回滚用户/工作区/API Key 隔离基础层。"""

    op.drop_constraint("uq_collections_metadata_workspace_collection", "collections_metadata", type_="unique")
    op.create_unique_constraint(
        "uq_collections_metadata_collection_name",
        "collections_metadata",
        ["collection_name"],
    )

    op.drop_index("ix_tasks_user_id", table_name="tasks")
    op.drop_index("ix_tasks_workspace_id", table_name="tasks")
    op.drop_column("tasks", "user_id")
    op.drop_column("tasks", "workspace_id")

    op.drop_index("ix_api_keys_status", table_name="api_keys")
    op.drop_index("ix_api_keys_user_id", table_name="api_keys")
    op.drop_index("ix_api_keys_workspace_id", table_name="api_keys")
    op.drop_table("api_keys")

    op.drop_index("ix_workspace_members_status", table_name="workspace_members")
    op.drop_index("ix_workspace_members_user_id", table_name="workspace_members")
    op.drop_index("ix_workspace_members_workspace_id", table_name="workspace_members")
    op.drop_table("workspace_members")

    op.drop_index("ix_workspaces_status", table_name="workspaces")
    op.drop_index("ix_workspaces_slug", table_name="workspaces")
    op.drop_table("workspaces")

    op.drop_index("ix_users_status", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
