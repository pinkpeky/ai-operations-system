"""phase18 playwright local provider

Revision ID: 0012_phase18_playwright
Revises: 0011_phase17_browser
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0012_phase18_playwright"
down_revision = "0011_phase17_browser"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Playwright runtime metadata columns."""

    op.add_column("browser_sessions", sa.Column("browser_id", sa.String(length=128), nullable=True))
    op.add_column("browser_sessions", sa.Column("page_id", sa.String(length=128), nullable=True))
    op.add_column(
        "browser_sessions",
        sa.Column(
            "provider_session_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_index("ix_browser_sessions_browser_id", "browser_sessions", ["browser_id"])
    op.create_index("ix_browser_sessions_page_id", "browser_sessions", ["page_id"])

    op.add_column("browser_actions", sa.Column("selector", sa.Text(), nullable=True))
    op.add_column("browser_actions", sa.Column("target_url", sa.Text(), nullable=True))
    op.add_column("browser_actions", sa.Column("screenshot_path", sa.Text(), nullable=True))
    op.add_column("browser_actions", sa.Column("page_title", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove Playwright runtime metadata columns."""

    op.drop_column("browser_actions", "page_title")
    op.drop_column("browser_actions", "screenshot_path")
    op.drop_column("browser_actions", "target_url")
    op.drop_column("browser_actions", "selector")

    op.drop_index("ix_browser_sessions_page_id", table_name="browser_sessions")
    op.drop_index("ix_browser_sessions_browser_id", table_name="browser_sessions")
    op.drop_column("browser_sessions", "provider_session_metadata")
    op.drop_column("browser_sessions", "page_id")
    op.drop_column("browser_sessions", "browser_id")
