"""phase26 browser worker security and access control

Revision ID: 0019_phase26_browser_security
Revises: 0018_phase25_browser_ui_access
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0019_phase26_browser_security"
down_revision = "0018_phase25_browser_ui_access"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("browser_workers", sa.Column("worker_secret_hash", sa.String(length=128), nullable=True))
    op.add_column("browser_workers", sa.Column("api_key_hash", sa.String(length=128), nullable=True))
    op.add_column("browser_workers", sa.Column("last_auth_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("browser_workers", sa.Column("auth_status", sa.String(length=32), nullable=False, server_default="unverified"))
    op.add_column("browser_workers", sa.Column("allowed_actions", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("browser_workers", sa.Column("allowed_domains", sa.JSON(), nullable=False, server_default="[]"))
    op.create_index("ix_browser_workers_worker_secret_hash", "browser_workers", ["worker_secret_hash"])
    op.create_index("ix_browser_workers_api_key_hash", "browser_workers", ["api_key_hash"])
    op.create_index("ix_browser_workers_auth_status", "browser_workers", ["auth_status"])

    op.add_column("browser_ui_access_sessions", sa.Column("scopes", sa.JSON(), nullable=False, server_default='["view"]'))
    op.add_column("browser_ui_access_sessions", sa.Column("one_time", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("browser_ui_access_sessions", sa.Column("used_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("browser_ui_access_sessions", sa.Column("revoked_reason", sa.Text(), nullable=True))
    op.add_column("browser_ui_access_sessions", sa.Column("client_ip", sa.String(length=128), nullable=True))
    op.add_column("browser_ui_access_sessions", sa.Column("user_agent", sa.Text(), nullable=True))

    op.create_table(
        "browser_security_audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("actor_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=128), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=128), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_browser_security_audit_logs_workspace_id", "browser_security_audit_logs", ["workspace_id"])
    op.create_index("ix_browser_security_audit_logs_actor_type", "browser_security_audit_logs", ["actor_type"])
    op.create_index("ix_browser_security_audit_logs_actor_id", "browser_security_audit_logs", ["actor_id"])
    op.create_index("ix_browser_security_audit_logs_event_type", "browser_security_audit_logs", ["event_type"])
    op.create_index("ix_browser_security_audit_logs_target_type", "browser_security_audit_logs", ["target_type"])
    op.create_index("ix_browser_security_audit_logs_target_id", "browser_security_audit_logs", ["target_id"])


def downgrade() -> None:
    op.drop_index("ix_browser_security_audit_logs_target_id", table_name="browser_security_audit_logs")
    op.drop_index("ix_browser_security_audit_logs_target_type", table_name="browser_security_audit_logs")
    op.drop_index("ix_browser_security_audit_logs_event_type", table_name="browser_security_audit_logs")
    op.drop_index("ix_browser_security_audit_logs_actor_id", table_name="browser_security_audit_logs")
    op.drop_index("ix_browser_security_audit_logs_actor_type", table_name="browser_security_audit_logs")
    op.drop_index("ix_browser_security_audit_logs_workspace_id", table_name="browser_security_audit_logs")
    op.drop_table("browser_security_audit_logs")

    op.drop_column("browser_ui_access_sessions", "user_agent")
    op.drop_column("browser_ui_access_sessions", "client_ip")
    op.drop_column("browser_ui_access_sessions", "revoked_reason")
    op.drop_column("browser_ui_access_sessions", "used_at")
    op.drop_column("browser_ui_access_sessions", "one_time")
    op.drop_column("browser_ui_access_sessions", "scopes")

    op.drop_index("ix_browser_workers_auth_status", table_name="browser_workers")
    op.drop_index("ix_browser_workers_api_key_hash", table_name="browser_workers")
    op.drop_index("ix_browser_workers_worker_secret_hash", table_name="browser_workers")
    op.drop_column("browser_workers", "allowed_domains")
    op.drop_column("browser_workers", "allowed_actions")
    op.drop_column("browser_workers", "auth_status")
    op.drop_column("browser_workers", "last_auth_at")
    op.drop_column("browser_workers", "api_key_hash")
    op.drop_column("browser_workers", "worker_secret_hash")
