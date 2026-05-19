"""Phase 61B commercial operation links.

Revision ID: 0036_phase61b_commercial_links
Revises: 0035_phase61a_commercial_ops
Create Date: 2026-05-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0036_phase61b_commercial_links"
down_revision = "0035_phase61a_commercial_ops"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_links",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("link_type", sa.String(length=64), nullable=False, server_default="external"),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_name", sa.String(length=128), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "operation_id", "link_type", "target_type", "target_id", "source_name"):
        op.create_index(f"ix_commercial_operation_links_{column}", "commercial_operation_links", [column])


def downgrade() -> None:
    op.drop_table("commercial_operation_links")
