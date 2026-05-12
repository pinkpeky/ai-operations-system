"""phase8 rag eval trace

Revision ID: 0004_phase8
Revises: 0003_phase65
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_phase8"
down_revision: str | None = "0003_phase65"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """创建 RAG Eval 运行和条目数据表。"""

    op.create_table(
        "rag_eval_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, comment="工作区 ID"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="评估名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="评估描述"),
        sa.Column("collection_name", sa.String(length=128), nullable=False, comment="评估 collection"),
        sa.Column("embedding_provider", sa.String(length=64), nullable=False, comment="Embedding Provider"),
        sa.Column("embedding_model_name", sa.String(length=128), nullable=False, comment="Embedding 模型"),
        sa.Column("llm_provider", sa.String(length=64), nullable=False, comment="LLM Provider"),
        sa.Column("llm_model", sa.String(length=128), nullable=False, comment="LLM 模型"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rag_eval_runs_workspace_id", "rag_eval_runs", ["workspace_id"])
    op.create_index("ix_rag_eval_runs_collection_name", "rag_eval_runs", ["collection_name"])

    op.create_table(
        "rag_eval_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False, comment="评估运行 ID"),
        sa.Column("query", sa.Text(), nullable=False, comment="查询问题"),
        sa.Column("expected_answer", sa.Text(), nullable=True, comment="期望答案"),
        sa.Column("retrieved_chunks", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False, comment="检索命中的 chunks"),
        sa.Column("final_prompt", sa.Text(), nullable=True, comment="最终 Prompt"),
        sa.Column("final_answer", sa.Text(), nullable=True, comment="最终答案"),
        sa.Column("similarity_scores", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False, comment="相似度分数"),
        sa.Column("latency_ms", sa.Integer(), nullable=True, comment="链路耗时毫秒"),
        sa.Column("manual_score", sa.Float(), nullable=True, comment="人工评分"),
        sa.Column("notes", sa.Text(), nullable=True, comment="人工备注"),
        sa.ForeignKeyConstraint(["run_id"], ["rag_eval_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rag_eval_items_run_id", "rag_eval_items", ["run_id"])


def downgrade() -> None:
    """回滚 RAG Eval 数据表。"""

    op.drop_index("ix_rag_eval_items_run_id", table_name="rag_eval_items")
    op.drop_table("rag_eval_items")

    op.drop_index("ix_rag_eval_runs_collection_name", table_name="rag_eval_runs")
    op.drop_index("ix_rag_eval_runs_workspace_id", table_name="rag_eval_runs")
    op.drop_table("rag_eval_runs")
