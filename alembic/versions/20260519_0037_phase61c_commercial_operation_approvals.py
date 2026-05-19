"""Phase 61C commercial operation approvals.

Revision ID: 0037_phase61c_op_approvals
Revises: 0036_phase61b_commercial_links
Create Date: 2026-05-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0037_phase61c_op_approvals"
down_revision = "0036_phase61b_commercial_links"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operation_approvals",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("step_key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("requested_action", sa.Text(), nullable=True),
        sa.Column("approval_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("risk_level", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("requested_by", sa.String(length=128), nullable=True),
        sa.Column("reviewer_user_id", sa.String(length=128), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["operation_id"], ["commercial_operations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "workspace_id",
        "operation_id",
        "step_key",
        "approval_status",
        "risk_level",
        "requested_by",
        "reviewer_user_id",
    ):
        op.create_index(f"ix_commercial_operation_approvals_{column}", "commercial_operation_approvals", [column])


def downgrade() -> None:
    op.drop_table("commercial_operation_approvals")
