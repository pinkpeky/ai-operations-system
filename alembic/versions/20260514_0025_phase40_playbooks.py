"""Phase 40 conversation execution playbooks.

Revision ID: 0025_phase40_playbooks
Revises: 0024_phase39_approvals
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0025_phase40_playbooks"
down_revision = "0024_phase39_approvals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_playbooks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("steps", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("default_inputs", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "name", name="uq_conversation_playbooks_workspace_name"),
    )
    op.create_index("ix_conversation_playbooks_workspace_id", "conversation_playbooks", ["workspace_id"])
    op.create_index("ix_conversation_playbooks_name", "conversation_playbooks", ["name"])
    op.create_index("ix_conversation_playbooks_category", "conversation_playbooks", ["category"])
    op.create_index("ix_conversation_playbooks_status", "conversation_playbooks", ["status"])
    op.create_index("ix_conversation_playbooks_risk_level", "conversation_playbooks", ["risk_level"])

    op.create_table(
        "conversation_playbook_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("playbook_id", sa.Uuid(), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("input_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("output_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["playbook_id"], ["conversation_playbooks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["thread_id"], ["conversation_threads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_playbook_runs_workspace_id", "conversation_playbook_runs", ["workspace_id"])
    op.create_index("ix_conversation_playbook_runs_playbook_id", "conversation_playbook_runs", ["playbook_id"])
    op.create_index("ix_conversation_playbook_runs_thread_id", "conversation_playbook_runs", ["thread_id"])
    op.create_index("ix_conversation_playbook_runs_status", "conversation_playbook_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_conversation_playbook_runs_status", table_name="conversation_playbook_runs")
    op.drop_index("ix_conversation_playbook_runs_thread_id", table_name="conversation_playbook_runs")
    op.drop_index("ix_conversation_playbook_runs_playbook_id", table_name="conversation_playbook_runs")
    op.drop_index("ix_conversation_playbook_runs_workspace_id", table_name="conversation_playbook_runs")
    op.drop_table("conversation_playbook_runs")

    op.drop_index("ix_conversation_playbooks_risk_level", table_name="conversation_playbooks")
    op.drop_index("ix_conversation_playbooks_status", table_name="conversation_playbooks")
    op.drop_index("ix_conversation_playbooks_category", table_name="conversation_playbooks")
    op.drop_index("ix_conversation_playbooks_name", table_name="conversation_playbooks")
    op.drop_index("ix_conversation_playbooks_workspace_id", table_name="conversation_playbooks")
    op.drop_table("conversation_playbooks")
