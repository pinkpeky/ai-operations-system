"""Phase 61A commercial operations foundation.

Revision ID: 0035_phase61a_commercial_ops
Revises: 0034_phase49_workflow_obs
Create Date: 2026-05-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0035_phase61a_commercial_ops"
down_revision = "0034_phase49_workflow_obs"
branch_labels = None
depends_on = None


def _json_default(value: str) -> sa.TextClause:
    return sa.text(f"'{value}'::json")


def upgrade() -> None:
    op.create_table(
        "commercial_operations",
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("channels", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="normal"),
        sa.Column("risk_level", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("budget_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("budget_currency", sa.String(length=16), nullable=False, server_default="CNY"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("knowledge_collection", sa.String(length=128), nullable=True),
        sa.Column("success_metrics", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("constraints", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("plan_outline", sa.JSON(), nullable=False, server_default=_json_default("[]")),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=_json_default("{}")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("workspace_id", "user_id", "status", "priority", "risk_level"):
        op.create_index(f"ix_commercial_operations_{column}", "commercial_operations", [column])


def downgrade() -> None:
    op.drop_table("commercial_operations")
