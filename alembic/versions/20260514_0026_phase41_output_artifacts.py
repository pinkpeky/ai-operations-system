"""Phase 41 output artifacts.

Revision ID: 0026_phase41_output_artifacts
Revises: 0025_phase40_playbooks
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0026_phase41_output_artifacts"
down_revision = "0025_phase40_playbooks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "output_artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=True),
        sa.Column("playbook_run_id", sa.Uuid(), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("artifact_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["playbook_run_id"], ["conversation_playbook_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["thread_id"], ["conversation_threads.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_output_artifacts_workspace_id", "output_artifacts", ["workspace_id"])
    op.create_index("ix_output_artifacts_thread_id", "output_artifacts", ["thread_id"])
    op.create_index("ix_output_artifacts_playbook_run_id", "output_artifacts", ["playbook_run_id"])
    op.create_index("ix_output_artifacts_source_type", "output_artifacts", ["source_type"])
    op.create_index("ix_output_artifacts_artifact_type", "output_artifacts", ["artifact_type"])
    op.create_index("ix_output_artifacts_status", "output_artifacts", ["status"])
    op.create_index("ix_output_artifacts_created_by", "output_artifacts", ["created_by"])


def downgrade() -> None:
    op.drop_index("ix_output_artifacts_created_by", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_status", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_artifact_type", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_source_type", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_playbook_run_id", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_thread_id", table_name="output_artifacts")
    op.drop_index("ix_output_artifacts_workspace_id", table_name="output_artifacts")
    op.drop_table("output_artifacts")
