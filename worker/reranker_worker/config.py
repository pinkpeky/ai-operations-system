"""Configuration for the standalone local reranker runtime."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RerankerWorkerSettings(BaseSettings):
    """Settings for the local semantic reranker worker."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    reranker_runtime_host: str = Field(default="0.0.0.0", alias="RERANKER_RUNTIME_HOST")
    reranker_runtime_port: int = Field(default=8002, alias="RERANKER_RUNTIME_PORT")
    reranker_runtime_provider: str = Field(default="local", alias="RERANKER_RUNTIME_PROVIDER")
    reranker_runtime_engine: str = Field(default="ollama_embedding", alias="RERANKER_RUNTIME_ENGINE")
    reranker_runtime_model: str = Field(default="bge-m3-embedding-reranker", alias="RERANKER_RUNTIME_MODEL")
    reranker_runtime_embedding_base_url: str = Field(
        default="http://host.docker.internal:11434",
        alias="RERANKER_RUNTIME_EMBEDDING_BASE_URL",
    )
    reranker_runtime_embedding_model: str = Field(default="bge-m3", alias="RERANKER_RUNTIME_EMBEDDING_MODEL")
    reranker_runtime_timeout_seconds: float = Field(default=60.0, ge=1.0, le=600.0, alias="RERANKER_RUNTIME_TIMEOUT_SECONDS")
    reranker_runtime_max_documents: int = Field(default=64, ge=1, le=512, alias="RERANKER_RUNTIME_MAX_DOCUMENTS")
    reranker_runtime_max_document_chars: int = Field(default=4000, ge=128, le=32000, alias="RERANKER_RUNTIME_MAX_DOCUMENT_CHARS")
    reranker_runtime_embedding_concurrency: int = Field(default=4, ge=1, le=32, alias="RERANKER_RUNTIME_EMBEDDING_CONCURRENCY")


@lru_cache
def get_reranker_worker_settings() -> RerankerWorkerSettings:
    """Return cached reranker worker settings."""

    return RerankerWorkerSettings()
