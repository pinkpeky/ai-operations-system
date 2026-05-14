"""Phase 33 conversation runtime foundation.

Revision ID: 0021_phase33_conversation
Revises: 0020_phase28_openclaw_adapter
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0021_phase33_conversation"
down_revision = "0020_phase28_openclaw_adapter"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_threads",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_threads_workspace_id", "conversation_threads", ["workspace_id"])
    op.create_index("ix_conversation_threads_user_id", "conversation_threads", ["user_id"])
    op.create_index("ix_conversation_threads_status", "conversation_threads", ["status"])

    op.add_column("conversation_messages", sa.Column("thread_id", sa.Uuid(), nullable=True))
    op.alter_column("conversation_messages", "session_id", existing_type=sa.Uuid(), nullable=True)
    op.create_index("ix_conversation_messages_thread_id", "conversation_messages", ["thread_id"])
    op.create_foreign_key(
        "fk_conversation_messages_thread_id",
        "conversation_messages",
        "conversation_threads",
        ["thread_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_table(
        "conversation_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["thread_id"], ["conversation_threads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_events_workspace_id", "conversation_events", ["workspace_id"])
    op.create_index("ix_conversation_events_thread_id", "conversation_events", ["thread_id"])
    op.create_index("ix_conversation_events_event_type", "conversation_events", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_conversation_events_event_type", table_name="conversation_events")
    op.drop_index("ix_conversation_events_thread_id", table_name="conversation_events")
    op.drop_index("ix_conversation_events_workspace_id", table_name="conversation_events")
    op.drop_table("conversation_events")

    op.drop_constraint("fk_conversation_messages_thread_id", "conversation_messages", type_="foreignkey")
    op.drop_index("ix_conversation_messages_thread_id", table_name="conversation_messages")
    op.drop_column("conversation_messages", "thread_id")
    op.alter_column("conversation_messages", "session_id", existing_type=sa.Uuid(), nullable=False)

    op.drop_index("ix_conversation_threads_status", table_name="conversation_threads")
    op.drop_index("ix_conversation_threads_user_id", table_name="conversation_threads")
    op.drop_index("ix_conversation_threads_workspace_id", table_name="conversation_threads")
    op.drop_table("conversation_threads")
