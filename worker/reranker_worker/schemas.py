"""Schemas for the standalone local reranker runtime."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RerankRequest(BaseModel):
    """Request accepted by POST /api/rerank."""

    model: str | None = None
    query: str = Field(min_length=1)
    documents: list[str] = Field(min_length=1)
    top_n: int | None = Field(default=None, ge=1, le=512)


class RerankResponse(BaseModel):
    """Rerank response compatible with LocalRerankerProvider."""

    provider: str
    model: str
    engine: str
    embedding_model: str
    scores: list[float]
    ranked_indices: list[int]
    top_n: int


class RerankerRuntimeHealthResponse(BaseModel):
    """Health response for the local reranker runtime."""

    provider: str
    model: str
    engine: str
    embedding_model: str
    reachable: bool
    enabled: bool
    dimension: int | None = None
    error: str | None = None
