"""Phase 39 conversation execution approvals.

Revision ID: 0024_phase39_approvals
Revises: 0023_phase35a_browser_runtime
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0024_phase39_approvals"
down_revision = "0023_phase35a_browser_runtime"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_approvals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column("message_id", sa.Uuid(), nullable=True),
        sa.Column("route_name", sa.String(length=64), nullable=False),
        sa.Column("selected_tool", sa.String(length=128), nullable=True),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("approval_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("proposed_action", sa.String(length=255), nullable=False),
        sa.Column("proposed_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["conversation_messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["thread_id"], ["conversation_threads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_approvals_workspace_id", "conversation_approvals", ["workspace_id"])
    op.create_index("ix_conversation_approvals_thread_id", "conversation_approvals", ["thread_id"])
    op.create_index("ix_conversation_approvals_message_id", "conversation_approvals", ["message_id"])
    op.create_index("ix_conversation_approvals_route_name", "conversation_approvals", ["route_name"])
    op.create_index("ix_conversation_approvals_selected_tool", "conversation_approvals", ["selected_tool"])
    op.create_index("ix_conversation_approvals_risk_level", "conversation_approvals", ["risk_level"])
    op.create_index("ix_conversation_approvals_approval_status", "conversation_approvals", ["approval_status"])
    op.create_index("ix_conversation_approvals_expires_at", "conversation_approvals", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_conversation_approvals_expires_at", table_name="conversation_approvals")
    op.drop_index("ix_conversation_approvals_approval_status", table_name="conversation_approvals")
    op.drop_index("ix_conversation_approvals_risk_level", table_name="conversation_approvals")
    op.drop_index("ix_conversation_approvals_selected_tool", table_name="conversation_approvals")
    op.drop_index("ix_conversation_approvals_route_name", table_name="conversation_approvals")
    op.drop_index("ix_conversation_approvals_message_id", table_name="conversation_approvals")
    op.drop_index("ix_conversation_approvals_thread_id", table_name="conversation_approvals")
    op.drop_index("ix_conversation_approvals_workspace_id", table_name="conversation_approvals")
    op.drop_table("conversation_approvals")
