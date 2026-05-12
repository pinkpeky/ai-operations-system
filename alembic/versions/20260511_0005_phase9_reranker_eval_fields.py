"""phase9 reranker eval fields

Revision ID: 0005_phase9
Revises: 0004_phase8
Create Date: 2026-05-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_phase9"
down_revision: str | None = "0004_phase8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """为 RAG Eval 增加 rerank 对比字段。"""

    op.add_column("rag_eval_runs", sa.Column("reranker_provider", sa.String(length=64), nullable=True, comment="Reranker Provider"))
    op.add_column("rag_eval_runs", sa.Column("reranker_model", sa.String(length=128), nullable=True, comment="Reranker 模型"))

    op.add_column(
        "rag_eval_items",
        sa.Column(
            "eval_mode",
            sa.String(length=64),
            server_default="retrieval_rerank",
            nullable=False,
            comment="评估模式",
        ),
    )
    op.add_column("rag_eval_items", sa.Column("reranker_provider", sa.String(length=64), nullable=True, comment="Reranker Provider"))
    op.add_column("rag_eval_items", sa.Column("reranker_model", sa.String(length=128), nullable=True, comment="Reranker 模型"))
    op.add_column(
        "rag_eval_items",
        sa.Column(
            "reranked_chunks",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
            comment="Reranker 精排后的 chunks",
        ),
    )
    op.add_column(
        "rag_eval_items",
        sa.Column(
            "rerank_scores",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
            comment="Reranker 精排分数",
        ),
    )
    op.add_column(
        "rag_eval_items",
        sa.Column(
            "retrieval_before_rerank",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
            comment="Rerank 前的向量召回候选 chunks",
        ),
    )
    op.add_column(
        "rag_eval_items",
        sa.Column(
            "retrieval_after_rerank",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
            comment="Rerank 后进入 prompt 的 chunks",
        ),
    )


def downgrade() -> None:
    """回滚 RAG Eval 的 rerank 对比字段。"""

    op.drop_column("rag_eval_items", "retrieval_after_rerank")
    op.drop_column("rag_eval_items", "retrieval_before_rerank")
    op.drop_column("rag_eval_items", "rerank_scores")
    op.drop_column("rag_eval_items", "reranked_chunks")
    op.drop_column("rag_eval_items", "reranker_model")
    op.drop_column("rag_eval_items", "reranker_provider")
    op.drop_column("rag_eval_items", "eval_mode")

    op.drop_column("rag_eval_runs", "reranker_model")
    op.drop_column("rag_eval_runs", "reranker_provider")
