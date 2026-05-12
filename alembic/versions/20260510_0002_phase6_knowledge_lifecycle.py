"""phase6 knowledge lifecycle

Revision ID: 0002_phase6
Revises: 0001_phase2
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_phase6"
down_revision: str | None = "0001_phase2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """创建知识库文档生命周期数据表。"""

    op.create_table(
        "collections_metadata",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("collection_name", sa.String(length=128), nullable=False, comment="Qdrant collection 名称"),
        sa.Column("workspace_id", sa.String(length=128), nullable=True, comment="预留工作区 ID"),
        sa.Column("embedding_provider", sa.String(length=64), nullable=False, comment="Embedding Provider 名称"),
        sa.Column("embedding_model_name", sa.String(length=128), nullable=False, comment="Embedding 模型名称"),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False, comment="Embedding 向量维度"),
        sa.Column("distance_metric", sa.String(length=32), nullable=False, comment="向量距离度量"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="Collection 元数据状态"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_name", name="uq_collections_metadata_collection_name"),
    )
    op.create_index("ix_collections_metadata_collection_name", "collections_metadata", ["collection_name"])
    op.create_index("ix_collections_metadata_workspace_id", "collections_metadata", ["workspace_id"])
    op.create_index("ix_collections_metadata_status", "collections_metadata", ["status"])

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("workspace_id", sa.String(length=128), nullable=True, comment="预留工作区 ID"),
        sa.Column("user_id", sa.String(length=128), nullable=True, comment="预留用户 ID"),
        sa.Column("source_id", sa.String(length=255), nullable=False, comment="外部来源 ID"),
        sa.Column("source_name", sa.String(length=255), nullable=True, comment="来源名称"),
        sa.Column("source_type", sa.String(length=64), nullable=False, comment="来源类型"),
        sa.Column("file_hash", sa.String(length=128), nullable=True, comment="内容哈希"),
        sa.Column("version", sa.Integer(), nullable=False, comment="同一 source_id 的版本号"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="文档生命周期状态"),
        sa.Column("collection_name", sa.String(length=128), nullable=False, comment="Qdrant collection 名称"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="文档元数据"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, comment="chunk 数量"),
        sa.Column("ingest_status", sa.String(length=32), nullable=False, comment="写入状态"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="写入错误信息"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_workspace_id", "documents", ["workspace_id"])
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_source_id", "documents", ["source_id"])
    op.create_index("ix_documents_file_hash", "documents", ["file_hash"])
    op.create_index("ix_documents_status", "documents", ["status"])
    op.create_index("ix_documents_collection_name", "documents", ["collection_name"])
    op.create_index("ix_documents_ingest_status", "documents", ["ingest_status"])

    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="更新时间"),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联文档 ID"),
        sa.Column("collection_name", sa.String(length=128), nullable=False, comment="Qdrant collection 名称"),
        sa.Column("chunk_index", sa.Integer(), nullable=False, comment="文档内 chunk 序号"),
        sa.Column("text", sa.Text(), nullable=False, comment="chunk 文本"),
        sa.Column("qdrant_point_id", sa.String(length=128), nullable=False, comment="Qdrant point ID"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False, comment="chunk 元数据"),
        sa.Column("status", sa.String(length=32), nullable=False, comment="chunk 生命周期状态"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_document_chunks_collection_name", "document_chunks", ["collection_name"])
    op.create_index("ix_document_chunks_qdrant_point_id", "document_chunks", ["qdrant_point_id"])
    op.create_index("ix_document_chunks_status", "document_chunks", ["status"])


def downgrade() -> None:
    """回滚知识库文档生命周期数据表。"""

    op.drop_index("ix_document_chunks_status", table_name="document_chunks")
    op.drop_index("ix_document_chunks_qdrant_point_id", table_name="document_chunks")
    op.drop_index("ix_document_chunks_collection_name", table_name="document_chunks")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")

    op.drop_index("ix_documents_ingest_status", table_name="documents")
    op.drop_index("ix_documents_collection_name", table_name="documents")
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_file_hash", table_name="documents")
    op.drop_index("ix_documents_source_id", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_index("ix_documents_workspace_id", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_collections_metadata_status", table_name="collections_metadata")
    op.drop_index("ix_collections_metadata_workspace_id", table_name="collections_metadata")
    op.drop_index("ix_collections_metadata_collection_name", table_name="collections_metadata")
    op.drop_table("collections_metadata")
