"""知识库文档 ORM 模型模块。

documents 和 document_chunks 记录 RAG 文档生命周期，Qdrant 只保存可检索向量。
"""

from typing import Any, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import DocumentIngestStatus, DocumentStatus

if TYPE_CHECKING:
    from app.models.collection_metadata import CollectionMetadata


class Document(IdTimestampMixin, Base):
    """知识库文档模型。"""

    __tablename__ = "documents"

    workspace_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True, comment="预留工作区 ID")
    user_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True, comment="预留用户 ID")
    source_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True, comment="外部来源 ID")
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="来源名称")
    source_type: Mapped[str] = mapped_column(String(64), default="text", nullable=False, comment="来源类型")
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True, comment="内容哈希")
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False, comment="同一 source_id 的版本号")
    status: Mapped[str] = mapped_column(
        String(32),
        default=DocumentStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="文档生命周期状态",
    )
    collection_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True, comment="Qdrant collection 名称")
    document_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="文档元数据",
    )
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="chunk 数量")
    ingest_status: Mapped[str] = mapped_column(
        String(32),
        default=DocumentIngestStatus.PENDING.value,
        nullable=False,
        index=True,
        comment="写入状态",
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="写入错误信息")

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="save-update, merge",
    )


class DocumentChunk(IdTimestampMixin, Base):
    """知识库文档 chunk 模型。"""

    __tablename__ = "document_chunks"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联文档 ID",
    )
    collection_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True, comment="Qdrant collection 名称")
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, comment="文档内 chunk 序号")
    text: Mapped[str] = mapped_column(Text, nullable=False, comment="chunk 文本")
    qdrant_point_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True, comment="Qdrant point ID")
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="chunk 元数据",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=DocumentStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="chunk 生命周期状态",
    )

    document: Mapped[Document] = relationship(back_populates="chunks")
