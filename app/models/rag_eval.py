"""RAG Eval ORM 模型模块。

该模块记录 RAG 评估运行、检索结果、rerank 对比结果和最终回答链路。
"""

from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin


class RAGEvalRun(IdTimestampMixin, Base):
    """RAG 评估运行模型。"""

    __tablename__ = "rag_eval_runs"

    workspace_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True, comment="工作区 ID")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="评估名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="评估描述")
    collection_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True, comment="评估 collection")
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False, comment="Embedding Provider")
    embedding_model_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="Embedding 模型")
    llm_provider: Mapped[str] = mapped_column(String(64), nullable=False, comment="LLM Provider")
    llm_model: Mapped[str] = mapped_column(String(128), nullable=False, comment="LLM 模型")
    reranker_provider: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="Reranker Provider")
    reranker_model: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Reranker 模型")

    items: Mapped[list["RAGEvalItem"]] = relationship(back_populates="run", cascade="save-update, merge")


class RAGEvalItem(IdTimestampMixin, Base):
    """RAG 评估条目模型。"""

    __tablename__ = "rag_eval_items"

    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("rag_eval_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="评估运行 ID",
    )
    query: Mapped[str] = mapped_column(Text, nullable=False, comment="查询问题")
    expected_answer: Mapped[str | None] = mapped_column(Text, nullable=True, comment="期望答案")
    retrieved_chunks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="最终使用的 chunks",
    )
    final_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment="最终 Prompt")
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True, comment="最终答案")
    similarity_scores: Mapped[list[float]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="最终上下文相似度分数",
    )
    eval_mode: Mapped[str] = mapped_column(
        String(64),
        default="retrieval_rerank",
        nullable=False,
        comment="评估模式：retrieval_only / retrieval_rerank",
    )
    reranker_provider: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="Reranker Provider")
    reranker_model: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Reranker 模型")
    reranked_chunks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Reranker 精排后的 chunks",
    )
    rerank_scores: Mapped[list[float]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Reranker 精排分数",
    )
    retrieval_before_rerank: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Rerank 前的向量召回候选 chunks",
    )
    retrieval_after_rerank: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Rerank 后进入 prompt 的 chunks",
    )
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="链路耗时毫秒")
    manual_score: Mapped[float | None] = mapped_column(Float, nullable=True, comment="人工评分")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="人工备注")

    run: Mapped[RAGEvalRun] = relationship(back_populates="items")
